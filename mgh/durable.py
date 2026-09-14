"""Durable single-writer operations, checkpoints and safe-boundary resume.

The journal is the reducer's source of truth. A model attempt or tool intent is
committed before its effect; entry ids close attempts independently of adjacency.
"""

import asyncio
import json
import sqlite3
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import httpx

from .context import BudgetExceeded, ContextConfig, units
from .tokenizer import tokens
from .effects import Effects, HarnessClosed, HarnessFault
from .provider import ProviderError, usage_metrics
from .store import canonical
from .tools import ToolContext
from .reducer import reduce_operation


class DurableRuntime:
    async def _overflow(self, fx, sid, turn):
        events = self.store.operation_events(sid, turn)
        newest_input = max(
            (
                e["seq"]
                for e in events
                if e["kind"] == "message" and e["data"].get("role") == "user"
            ),
            default=0,
        )
        if any(
            e["kind"] == "overflow_recovery" and e["seq"] > newest_input for e in events
        ):
            raise ProviderError("Context overflow persisted after one recovery")
        await self._write(
            fx, sid, "overflow_recovery", {"input_seq": newest_input}, turn
        )
        if not await fx.call(
            "transition", lambda: self.compiler.transition(sid, force=True)
        ):
            raise ProviderError(
                "Context overflow cannot be recovered with the protected Hot tail"
            )

    def compact(self, sid):
        from .compaction import accept_compaction

        return accept_compaction(self, sid)

    def _check_open(self):
        if self.fault:
            raise self.fault
        if self.closed:
            raise HarnessClosed("Harness is closed")

    def suspended(self):
        return [
            {"session": s["id"], "operation": op, "status": "suspended"}
            for s in self.store.sessions()
            if (op := self.store.open_operation(s["id"]))
            and s["id"] not in self.running
        ]

    def append_message(self, sid, text):
        """Accept a fact while running; apply it only at a checkpoint."""
        self._check_open()
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Message is empty")
        op = self.store.open_operation(sid)
        message = {"role": "user", "content": text}
        if op:
            if op["data"].get("kind") == "compaction":
                raise RuntimeError("Cannot append messages during compaction")
            return self.store.append(
                sid,
                "write_deferred",
                {"id": uuid4().hex, "message": message},
                op["turn"],
            )
        return self.store.append(sid, "message", message)

    def record_usage(self, sid, usage):
        self._check_open()
        return self.store.append(sid, "usage", {"cause": "adjustment", "usage": usage})

    def _apply_writes(self, sid, turn):
        events = self.store.operation_events(sid, turn)
        applied = {e["data"]["id"] for e in events if e["kind"] == "write_applied"}
        items = [
            e
            for e in events
            if e["kind"] == "write_deferred" and e["data"]["id"] not in applied
        ]
        if items:
            self.store.append_batch(
                sid,
                [
                    part
                    for item in items
                    for part in (
                        ("message", item["data"]["message"]),
                        ("write_applied", {"id": item["data"]["id"]}),
                    )
                ],
                turn,
            )
        return bool(items)

    def _try_finish(self, sid, turn, status):
        if self._pending(sid, turn, {"steer", "follow_up"}):
            return False
        self._finish(sid, turn, "cancelled" if self._aborting(sid, turn) else status)
        return True

    def _launch(self, sid, turn):
        fx = Effects(self.drive == "manual")
        self.effects[sid] = fx
        task = asyncio.create_task(self._durable_run(sid, turn, fx))
        self.running[sid] = task
        task.add_done_callback(lambda _: fx.changed.set())
        return task

    def resume(self, sid):
        self._check_open()
        if sid in self.running:
            raise RuntimeError("Session is running")
        op = self.store.open_operation(sid)
        if op is None:
            raise RuntimeError("Nothing to resume")
        reduce_operation(self.store.operation_events(sid, op["turn"]))
        if op["data"]["model"] != self.provider.model:
            raise RuntimeError("Restore the operation's model before resuming")
        if (
            "config" in op["data"]
            and op["data"]["config"] != self.store.session(sid)["config"]
        ):
            raise RuntimeError("Restore the operation's configuration before resuming")
        return self._launch(sid, op["turn"])

    async def close(self):
        self.closed = True
        tasks = list(self.running.values())
        for fx in self.effects.values():
            fx.close()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.running.clear()

    async def peek_action(self, sid):
        return await self.effects[sid].peek(self.running[sid])

    async def execute_action(self, sid):
        return await self.effects[sid].execute(self.running[sid])

    async def run_to_completion(self, sid):
        task = self.running[sid]
        fx = self.effects[sid]
        while await fx.peek(task) is not None:
            await fx.execute(task)
        return await task

    def enqueue(self, sid, text, queue="steer"):
        self._check_open()
        if queue not in {"steer", "follow_up", "next_run"} or not text.strip():
            raise ValueError("Invalid queue or empty message")
        op = self.store.open_operation(sid)
        if op and op["data"].get("kind") == "compaction" and queue != "next_run":
            raise RuntimeError("Cannot steer compaction")
        if queue != "next_run" and (op is None or self._aborting(sid, op["turn"])):
            raise RuntimeError("No active run")
        ident = uuid4().hex
        self.store.append(
            sid,
            "queue_enqueued",
            {
                "id": ident,
                "queue": queue,
                "message": {"role": "user", "content": text},
            },
            op["turn"] if queue != "next_run" else None,
        )
        return ident

    def cancel_queued(self, sid, ident):
        events = self.store.events(sid)
        item = next(
            (
                e
                for e in events
                if e["kind"] == "queue_enqueued" and e["data"]["id"] == ident
            ),
            None,
        )
        if item is None:
            raise KeyError(ident)
        if any(
            e["kind"] == "queue_consumed" and e["data"]["id"] == ident for e in events
        ):
            return "already_consumed"
        if any(
            e["kind"] == "queue_cancelled" and e["data"]["id"] == ident for e in events
        ):
            return "already_cleared"
        self.store.append(sid, "queue_cancelled", {"id": ident}, item["turn"])
        return "cancelled"

    def _pending(self, sid, turn, queues):
        events = self.store.events(sid)
        settled = {
            e["data"]["id"]
            for e in events
            if e["kind"] in {"queue_consumed", "queue_cancelled"}
        }
        return [
            e
            for e in events
            if e["kind"] == "queue_enqueued"
            and e["data"]["id"] not in settled
            and e["data"]["queue"] in queues
            and e["turn"] in {turn, None}
        ]

    def _aborting(self, sid, turn):
        return any(
            e["kind"] == "abort_requested"
            for e in self.store.operation_events(sid, turn)
        )

    async def cancel(self, sid):
        self._check_open()
        op = self.store.open_operation(sid)
        if op is None:
            return
        turn = op["turn"]
        if not self._aborting(sid, turn):
            self.store.append_batch(
                sid,
                [
                    ("abort_requested", {}),
                    *[
                        ("queue_cancelled", {"id": e["data"]["id"]})
                        for e in self._pending(sid, turn, {"steer", "follow_up"})
                    ],
                ],
                turn,
            )
        task = self.running.get(sid)
        if task:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        # Cancellation before a task's first instruction must reconcile too.
        if self.store.open_operation(sid):
            self._finish(sid, turn, "cancelled")
        self.running.pop(sid, None)

    def _finish(self, sid, turn, status):
        if not self.store.open_operation(sid):
            return
        if self.store.open_operation(sid)["data"].get("kind") == "compaction":
            self.store.append(
                sid, "operation_finished", {"status": status, "outcome": status}, turn
            )
            return
        self._apply_writes(sid, turn)
        self._close_turn(sid, turn, status)

    async def _write(self, fx, sid, kind, data, turn):
        async def commit():
            try:
                return self.store.append(sid, kind, data, turn)
            except Exception as exc:
                self.fault = HarnessFault("Durable write failed; reopen the Harness")
                for key, task in self.running.items():
                    if task is not asyncio.current_task():
                        task.cancel()
                raise self.fault from exc

        return await fx.call("append_record", commit, record_type=kind)

    async def _checkpoint(self, fx, sid, turn, queues):
        def commit():
            written = self._apply_writes(sid, turn)
            if self._aborting(sid, turn):
                return False
            items = self._pending(sid, turn, queues)
            if items:
                self.store.append_batch(
                    sid,
                    [
                        part
                        for item in items
                        for part in (
                            ("message", item["data"]["message"]),
                            ("queue_consumed", {"id": item["data"]["id"]}),
                        )
                    ],
                    turn,
                )
            return bool(items) or written

        return await fx.call("checkpoint", commit)

    async def _tools(self, fx, sid, turn, assistant, config, selected=None):
        calls = assistant["data"].get("tool_calls", [])
        # Opt-in concurrency only; manual drive preserves deterministic gates.
        if selected is None and not fx.manual:
            batch = []
            for index, call in enumerate(calls):
                tool = self.tools.get(call["function"]["name"])
                if tool and tool.parallel and tool.risk == "read":
                    batch.append(index)
                else:
                    if batch:
                        async with asyncio.TaskGroup() as group:
                            for item in batch:
                                group.create_task(
                                    self._tools(fx, sid, turn, assistant, config, item)
                                )
                        batch = []
                    await self._tools(fx, sid, turn, assistant, config, index)
            if batch:
                async with asyncio.TaskGroup() as group:
                    for item in batch:
                        group.create_task(
                            self._tools(fx, sid, turn, assistant, config, item)
                        )
            return
        for index, call in enumerate(calls):
            if selected is not None and selected != index:
                continue
            events = self.store.operation_events(sid, turn)
            if any(
                e["kind"] == "message"
                and e["seq"] > assistant["seq"]
                and e["data"].get("tool_call_id") == call["id"]
                for e in events
            ):
                continue
            intent = next(
                (
                    e
                    for e in events
                    if e["kind"] == "tool_intent"
                    and e["data"]["assistant_seq"] == assistant["seq"]
                    and e["data"]["index"] == index
                ),
                None,
            )
            name = call["function"]["name"]
            tool = self.tools.get(name)
            result = {"role": "tool", "tool_call_id": call["id"]}
            page_in = None
            try:
                if self._aborting(sid, turn):
                    raise asyncio.CancelledError
                response = next(
                    (
                        e
                        for e in events
                        if e["kind"] == "response"
                        and e["seq"] < assistant["seq"]
                        and e["data"].get("message") == assistant["data"]
                    ),
                    None,
                )
                if response and response["data"]["finish_reason"] == "length":
                    raise ValueError("Truncated tool batch")
                if intent and not (
                    intent["data"]["replay"] == "safe"
                    and (name == "context_read" or (tool and tool.replay == "safe"))
                ):
                    result["content"] = canonical(
                        {
                            "error": "Interrupted",
                            "message": "Execution outcome unknown; not replayed",
                        }
                    )
                else:
                    args = (
                        intent["data"]["args"]
                        if intent
                        else json.loads(call["function"]["arguments"])
                    )
                    if not isinstance(args, dict):
                        raise ValueError("Tool arguments must be an object")
                    if not intent:
                        decision = await fx.call(
                            "hook",
                            lambda: self.hooks.run(
                                "before_tool",
                                {"session": sid, "tool": name, "args": args},
                            ),
                            hook="before_tool",
                        )
                        if decision.get("block"):
                            raise PermissionError("Tool blocked by hook")
                        args = decision["args"]
                    if name != "context_read":
                        if tool is None:
                            raise KeyError(name)
                        if not intent:
                            await fx.call(
                                "authorize_tool",
                                lambda: self._authorize(
                                    sid, turn, tool, call, args, config
                                ),
                            )
                    if not intent:
                        await self._write(fx, sid, "tool_start", call, turn)
                        intent = await self._write(
                            fx,
                            sid,
                            "tool_intent",
                            {
                                "assistant_seq": assistant["seq"],
                                "index": index,
                                "id": call["id"],
                                "name": name,
                                "args": args,
                                "result_id": uuid4().hex,
                                "replay": "safe"
                                if name == "context_read"
                                else tool.replay,
                            },
                            turn,
                        )

                    async def execute():
                        if name == "context_read":
                            self.store.get(sid, args["ref"])
                            return None
                        context = self.tool_contexts.setdefault(
                            sid, ToolContext(Path(config.workspace))
                        )
                        execution = (
                            tool.run(args, context)
                            if tool.workspace_aware
                            else tool.run(args)
                        )
                        return await asyncio.wait_for(execution, 130)

                    value = await fx.call("execute_tool", execute, tool=name)
                    if name == "context_read":
                        duplicate = any(
                            e["kind"] == "page_in"
                            and e["data"]["source_ref"] == args["ref"]
                            for e in events
                        )
                        if duplicate:
                            result["content"] = canonical(
                                {"already_loaded": args["ref"]}
                            )
                        else:
                            result.update(page_ref=args["ref"], content="")
                        page_in = {"source_ref": args["ref"], "duplicate": duplicate}
                    else:
                        result["content"] = canonical(value)
            except (HarnessClosed, HarnessFault):
                raise
            except Exception as exc:
                result["content"] = canonical(
                    {
                        "error": type(exc).__name__,
                        "message": "Tool failed; check its arguments or availability.",
                    }
                )
            try:
                patched = await fx.call(
                    "hook",
                    lambda: self.hooks.run(
                        "after_tool", {"session": sid, "tool": name, "result": result}
                    ),
                    hook="after_tool",
                )
                result = patched["result"]
                if (
                    result.get("role") != "tool"
                    or result.get("tool_call_id") != call["id"]
                ):
                    raise ValueError("Hook changed tool identity")
            except (HarnessClosed, HarnessFault):
                raise
            except Exception:
                result = {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": canonical({"error": "Tool finalization failed"}),
                }
            records = [("message", result)]
            if page_in is not None and ("page_ref" in result or page_in["duplicate"]):
                records.insert(0, ("page_in", page_in))
            await fx.call(
                "commit_tool_result",
                lambda: self.store.append_batch(sid, records, turn),
            )

    async def _durable_run(self, sid, turn, fx):
        config = ContextConfig(
            **self.store.open_operation(sid)["data"].get(
                "config", self.store.session(sid)["config"]
            )
        )
        provider = self.provider
        try:
            op = self.store.open_operation(sid)
            if op["data"].get("kind") == "compaction":
                from .compaction import run_compaction

                return await run_compaction(self, sid, op, fx)
            while True:
                if self._aborting(sid, turn):
                    raise asyncio.CancelledError
                events = self.store.operation_events(sid, turn)
                failure = max(
                    (e["seq"] for e in events if e["kind"] == "error"), default=0
                )
                conversation = max(
                    (e["seq"] for e in events if e["kind"] == "queue_consumed"),
                    default=0,
                )
                if failure > conversation:
                    if await self._checkpoint(fx, sid, turn, {"steer", "follow_up"}):
                        continue
                    if await fx.call(
                        "finish_failed", lambda: self._try_finish(sid, turn, "failed")
                    ):
                        return None
                    continue
                pending = next(
                    (e for e in reversed(events) if e["kind"] == "message"), None
                )
                if pending and pending["data"].get("_deferred"):
                    handle = pending["data"]["_deferred"]
                    try:
                        completion = await fx.call(
                            "fetch_deferred", lambda: provider.fetch_deferred(handle)
                        )
                    except (HarnessClosed, HarnessFault):
                        raise
                    except Exception as exc:
                        raise ProviderError(
                            "Deferred result could not be retrieved"
                        ) from exc
                    if completion.get("usage") is not None:
                        await self._write(
                            fx,
                            sid,
                            "usage",
                            {
                                "cause": "deferred_fetch",
                                "usage": usage_metrics(completion["usage"]),
                            },
                            turn,
                        )
                    if completion["finish_reason"] == "deferred":
                        if completion.get("deferred") != handle:
                            raise ProviderError(
                                "Deferred provider changed the persisted handle"
                            )
                        return {"status": "suspended", "deferred": handle}
                    if completion["finish_reason"] == "error":
                        raise ProviderError(
                            "Deferred provider returned a terminal failure"
                        )
                    await fx.call(
                        "commit_deferred",
                        lambda: self.store.append_batch(
                            sid,
                            [
                                (
                                    "response",
                                    {
                                        "finish_reason": completion["finish_reason"],
                                        "message": completion["message"],
                                        "deferred_fetch": True,
                                    },
                                ),
                                ("message", completion["message"]),
                            ],
                            turn,
                        ),
                    )
                    continue
                messages = [e for e in events if e["kind"] == "message"]
                last = messages[-1]
                assistant = next(
                    (e for e in reversed(messages) if e["data"]["role"] == "assistant"),
                    None,
                )
                if assistant and assistant["data"].get("tool_calls"):
                    await self._tools(fx, sid, turn, assistant, config)
                last_response_seq = max(
                    (e["seq"] for e in events if e["kind"] == "response"), default=0
                )
                unfinished_attempt = any(
                    e["kind"] == "step_attempt" and e["seq"] > last_response_seq
                    for e in events
                )
                consumed = (
                    False
                    if unfinished_attempt
                    else await self._checkpoint(fx, sid, turn, {"steer"})
                )
                if (
                    not consumed
                    and last["data"]["role"] == "assistant"
                    and not last["data"].get("tool_calls")
                ):
                    if await self._checkpoint(fx, sid, turn, {"follow_up"}):
                        continue

                    def finish():
                        if self._pending(
                            sid, turn, {"steer", "follow_up"}
                        ) or self._aborting(sid, turn):
                            return False
                        response = next(
                            (e for e in reversed(events) if e["kind"] == "response"),
                            None,
                        )
                        reason = (
                            response["data"]["finish_reason"] if response else "stop"
                        )
                        self._finish(
                            sid, turn, "completed" if reason == "stop" else reason
                        )
                        return True

                    if await fx.call("try_finish_run", finish):
                        return last["data"]
                    continue
                events = self.store.operation_events(sid, turn)
                responses = [e for e in events if e["kind"] == "response"]
                if len(responses) >= op["data"].get("max_steps", self.max_steps):
                    raise ProviderError("Maximum model steps reached")
                last_response = responses[-1]["seq"] if responses else 0
                attempts = [
                    e
                    for e in events
                    if e["kind"] == "step_attempt" and e["seq"] > last_response
                ]
                if (
                    len(attempts)
                    >= self.store.open_operation(sid)["data"]["max_attempts"]
                ):
                    raise ProviderError("Durable model attempt limit reached")
                try:
                    snapshot = self.compiler.compile(sid, provider.model, self.schemas)
                except BudgetExceeded:
                    if not await fx.call(
                        "transition", lambda: self.compiler.transition(sid, force=True)
                    ):
                        raise
                    snapshot = self.compiler.compile(sid, provider.model, self.schemas)
                if hasattr(provider, "prepare_payload"):
                    snapshot["payload"] = provider.prepare_payload(snapshot["payload"])
                snapshot["provider_binding"] = getattr(provider, "binding", "demo")
                request_options = await fx.call(
                    "hook",
                    lambda: self.hooks.run(
                        "before_request", {"session": sid, "temperature": None}
                    ),
                    hook="before_request",
                )
                if request_options.get("temperature") is not None:
                    temperature = request_options["temperature"]
                    if (
                        not isinstance(temperature, (int, float))
                        or not 0 <= temperature <= 2
                    ):
                        raise ValueError("Invalid hook temperature")
                    snapshot["payload"]["temperature"] = temperature
                # Provider adapters and hooks may add options after compilation.
                payload = snapshot["payload"]
                snapshot["budget_units"] = (
                    len(tokens(canonical(payload), config.tokenizer))
                    if config.tokenizer
                    else units(payload)
                ) + 16 * len(payload["messages"])
                if snapshot["budget_units"] > snapshot["budget_limit"]:
                    raise BudgetExceeded(
                        "Final provider payload exceeds the request budget"
                    )
                await self._write(
                    fx,
                    sid,
                    "step_attempt",
                    {"attempt": len(attempts) + 1, "result_id": uuid4().hex},
                    turn,
                )
                request = await self._write(fx, sid, "request", snapshot, turn)
                started = perf_counter()

                async def stream():
                    completion = None
                    async for event in provider.stream(snapshot["payload"]):
                        if event["kind"] == "completion":
                            completion = event
                        else:
                            await self._write(
                                fx,
                                sid,
                                "delta",
                                {**event, "request_seq": request["seq"]},
                                turn,
                            )
                    if completion is None:
                        raise ProviderError("Provider did not complete")
                    return completion

                try:
                    completion = await fx.call("stream_assistant", stream)
                except (httpx.TransportError, ProviderError) as exc:
                    await self._write(
                        fx,
                        sid,
                        "request_error",
                        {"request_seq": request["seq"], "error": type(exc).__name__},
                        turn,
                    )
                    if isinstance(exc, ProviderError) and exc.overflow:
                        await self._overflow(fx, sid, turn)
                        continue
                    if isinstance(exc, httpx.TransportError) or exc.retryable:
                        await fx.call(
                            "retry_backoff",
                            lambda: asyncio.sleep(min(0.1 * 2 ** len(attempts), 2)),
                        )
                        continue
                    raise
                await self._write(
                    fx,
                    sid,
                    "usage",
                    {
                        "request_seq": request["seq"],
                        "usage": usage_metrics(completion.get("usage")),
                    },
                    turn,
                )
                transformed = await fx.call(
                    "hook",
                    lambda: self.hooks.run(
                        "after_response", {"session": sid, "completion": completion}
                    ),
                    hook="after_response",
                )
                completion = transformed["completion"]
                used_output = (completion.get("usage") or {}).get("completion_tokens")
                if (
                    completion["finish_reason"] == "length"
                    and used_output is not None
                    and used_output < config.output_reserve
                ):
                    await self._overflow(fx, sid, turn)
                    continue
                message = completion["message"]
                if completion["finish_reason"] == "deferred":
                    if not hasattr(provider, "fetch_deferred") or not completion.get(
                        "deferred"
                    ):
                        raise ProviderError(
                            "Deferred provider must supply a handle and fetch capability"
                        )
                    message = {**message, "_deferred": completion["deferred"]}
                ids = [c["id"] for c in message.get("tool_calls", [])]
                if len(set(ids)) != len(ids):
                    raise ProviderError("Duplicate tool call IDs")
                # Response and context message close together, avoiding duplicate effects on resume.
                await fx.call(
                    "commit_response",
                    lambda: self.store.append_batch(
                        sid,
                        [
                            (
                                "response",
                                {
                                    "request_seq": request["seq"],
                                    "latency_ms": round(
                                        (perf_counter() - started) * 1000
                                    ),
                                    "usage": usage_metrics(completion.get("usage")),
                                    "finish_reason": completion["finish_reason"],
                                    "message": message,
                                },
                            ),
                            ("message", message),
                        ],
                        turn,
                    ),
                )
                if completion["finish_reason"] == "deferred":
                    return {"status": "suspended", "deferred": completion["deferred"]}
                if completion["finish_reason"] not in {
                    "stop",
                    "tool_calls",
                } and not message.get("tool_calls"):
                    if await fx.call(
                        "finish_operation",
                        lambda: self._try_finish(
                            sid, turn, completion["finish_reason"]
                        ),
                    ):
                        return message
        except (HarnessClosed, HarnessFault):
            raise
        except sqlite3.Error as exc:
            self.fault = HarnessFault("Durable storage failure; reopen the Harness")
            raise self.fault from exc
        except asyncio.CancelledError:
            if not self.closed and not self.fault:
                self._finish(sid, turn, "cancelled")
        except Exception as exc:
            await self._write(
                fx,
                sid,
                "error",
                {
                    "error": type(exc).__name__,
                    "message": str(exc)
                    if isinstance(exc, (BudgetExceeded, ProviderError))
                    else "Run failed; inspect trace.",
                },
                turn,
            )
            if op["data"].get("kind") != "compaction" and self._pending(
                sid, turn, {"steer", "follow_up"}
            ):
                await self._checkpoint(fx, sid, turn, {"steer", "follow_up"})
                return await self._durable_run(sid, turn, fx)
            if not await fx.call(
                "finish_failed", lambda: self._try_finish(sid, turn, "failed")
            ):
                await self._checkpoint(fx, sid, turn, {"steer", "follow_up"})
                return await self._durable_run(sid, turn, fx)
        finally:
            self.running.pop(sid, None)
            fx.changed.set()
