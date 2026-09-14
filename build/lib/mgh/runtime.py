"""One visible loop: compile → model → persist → tools → repeat."""

from __future__ import annotations

import asyncio
from uuid import uuid4

from .context import ContextCompiler, ContextConfig
from .store import Store, canonical
from .tools import Tool, ToolContext, basic_tools, string_parameter
from .durable import DurableRuntime
from .reducer import reduce_operation
from .hooks import Hooks, Watch


class Harness(DurableRuntime):
    def __init__(
        self,
        store: Store,
        provider,
        tools: list[Tool] | None = None,
        max_steps: int = 12,
        max_attempts: int = 3,
        drive: str = "automatic",
    ):
        self.store, self.provider = store, provider
        self.compiler = ContextCompiler(store)
        self.tools = {t.name: t for t in (basic_tools() if tools is None else tools)}
        self.max_steps = max_steps
        self.max_attempts = max_attempts
        if drive not in {"automatic", "manual"} or max_attempts < 1:
            raise ValueError("Invalid drive or retry policy")
        self.drive = drive
        self.effects = {}
        self.closed = False
        self.fault = None
        self.hooks = Hooks()
        self.running: dict[str, asyncio.Task] = {}
        self.approvals: dict[str, tuple[str, asyncio.Future]] = {}
        self.tool_contexts: dict[str, ToolContext] = {}
        self.schemas = [t.schema() for t in self.tools.values()] + [
            dict(
                type="function",
                function=dict(
                    name="context_read",
                    description="Recover an exact context source by ctx:// reference; temporary read only.",
                    parameters=string_parameter("ref"),
                ),
            )
        ]

    def create(self, config: ContextConfig | None = None):
        return self.store.create((config or ContextConfig()).to_dict())

    def watch(self, sid):
        return Watch(
            self.store,
            sid,
            {
                "session": self.store.session(sid),
                "events": self.store.events(sid),
                "operation": self.store.open_operation(sid),
                "running": sid in self.running,
            },
        )

    def resolve_approval(self, sid: str, approval_id: str, allow: bool):
        owner, future = self.approvals[approval_id]
        if owner != sid or future.done():
            raise KeyError(approval_id)
        future.set_result(bool(allow))

    async def _authorize(self, sid, turn, tool: Tool, call, args, config):
        if tool.risk == "read":
            return
        if config.permission_mode == "read_only":
            raise PermissionError("This session is read-only")
        if tool.risk == "write" and config.permission_mode == "allow_edits":
            return
        approval_id = uuid4().hex
        future = asyncio.get_running_loop().create_future()
        self.approvals[approval_id] = (sid, future)
        self.store.append(
            sid,
            "approval_required",
            {
                "approval_id": approval_id,
                "tool_call_id": call["id"],
                "tool": tool.name,
                "risk": tool.risk,
                "arguments": args,
            },
            turn,
        )
        try:
            allowed = await future
        finally:
            self.approvals.pop(approval_id, None)
        self.store.append(
            sid,
            "approval_resolved",
            {"approval_id": approval_id, "allowed": allowed},
            turn,
        )
        if not allowed:
            raise PermissionError("User denied this tool call")

    def _close_turn(self, sid, turn, status):
        events = [e for e in self.store.events(sid) if e["turn"] == turn]
        resolved_approvals = {
            e["data"]["approval_id"] for e in events if e["kind"] == "approval_resolved"
        }
        for e in events:
            if (
                e["kind"] == "approval_required"
                and e["data"]["approval_id"] not in resolved_approvals
            ):
                self.store.append(
                    sid,
                    "approval_resolved",
                    {
                        "approval_id": e["data"]["approval_id"],
                        "allowed": False,
                        "reason": status,
                    },
                    turn,
                )
        results = {
            e["data"].get("tool_call_id")
            for e in events
            if e["kind"] == "message" and e["data"]["role"] == "tool"
        }
        for e in events:
            if e["kind"] != "message":
                continue
            for c in e["data"].get("tool_calls", []):
                if c["id"] not in results:
                    self.store.append(
                        sid,
                        "message",
                        dict(
                            role="tool",
                            tool_call_id=c["id"],
                            content=canonical(
                                {
                                    "error": "Interrupted; execution outcome may be unknown. Not replayed automatically."
                                }
                            ),
                        ),
                        turn,
                    )
                    results.add(c["id"])
        self.compiler.prepare(sid, turn)
        ending = [("turn_end", dict(status=status))]
        if self.store.open_operation(sid):
            ending.append(
                (
                    "operation_finished",
                    {
                        "outcome": "aborted" if status == "cancelled" else status,
                        "status": status,
                    },
                )
            )
        self.store.append_batch(sid, ending, turn)

    def recover(self):
        """Discover durable suspended runs; close only legacy untracked turns."""
        for session in self.store.sessions():
            if op := self.store.open_operation(session["id"]):
                reduce_operation(self.store.operation_events(session["id"], op["turn"]))
            for turn in self.store.legacy_unclosed_turns(session["id"]):
                self._close_turn(session["id"], turn, "interrupted")
        return self.suspended()

    def start(self, sid: str, text: str, attachments: list[dict] | None = None):
        self._check_open()
        self.store.session(sid)
        if sid in self.running:
            raise RuntimeError("This session already has a running turn")
        if self.store.open_operation(sid):
            raise RuntimeError(
                "This session has suspended work; resume or abort it first"
            )
        if not text.strip():
            raise ValueError("Message is empty")
        # A normal stage change is a turn-boundary event. Persist it before the
        # next turn starts so trajectory consumers never have to pretend that a
        # SWITCH embedded inside a user turn happened between turns.
        self.compiler.transition(sid)
        turn = uuid4().hex
        # Admission is durable before returning to the HTTP caller.
        attachments = attachments or []
        attachment_items = [("attachment", item) for item in attachments]
        attachment_note = ""
        if attachments:
            attachment_note = "\n\nAttached files:\n" + "\n".join(
                f"--- {item['name']} ---\n{item.get('text', '[binary attachment]')}"
                for item in attachments
            )
        model_text = text + attachment_note
        self.store.append_batch(
            sid,
            [
                (
                    "operation_started",
                    {
                        "model": self.provider.model,
                        "max_attempts": self.max_attempts,
                        "max_steps": self.max_steps,
                        "config": self.store.session(sid)["config"],
                    },
                ),
                (
                    "turn_start",
                    {"text": text, "attachments": [a["name"] for a in attachments]},
                ),
                *[
                    part
                    for item in self._pending(sid, turn, {"next_run"})
                    for part in (
                        ("message", item["data"]["message"]),
                        ("queue_consumed", {"id": item["data"]["id"]}),
                    )
                ],
                *attachment_items,
                ("message", dict(role="user", content=model_text)),
            ],
            turn,
        )
        if self.store.session(sid)["title"] == "新对话":
            self.store.rename(sid, text)
        return self._launch(sid, turn)

    async def run(self, sid: str, text: str, attachments: list[dict] | None = None):
        return await self.start(sid, text, attachments)
