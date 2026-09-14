"""Local FastAPI host with a static UI; no frontend build step."""

import json
import os
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .context import ContextConfig
from .provider import FakeProvider, ProviderError
from .settings import (
    HarnessPreferences,
    PreferencesStore,
    ProviderSettings,
    SettingsStore,
)


class NewSession(BaseModel):
    policy: str | None = None
    window: int | None = Field(default=None, ge=4096, le=2000000)
    stage_turns: int | None = Field(default=None, ge=1, le=100)
    workspace: str = ""
    permission_mode: str = "ask"


class Prompt(BaseModel):
    text: str = Field(min_length=1, max_length=100000)
    attachments: list[dict] = Field(default_factory=list, max_length=12)


class PreferencesUpdate(BaseModel):
    language: str = "zh"
    theme: str = "system"
    base_prompt: str = Field(min_length=1, max_length=100000)
    instruction_file: str = "MAGI.md"
    context_policy: str = "four_zone"
    window: int = Field(default=32768, ge=4096, le=2000000)
    stage_turns: int = Field(default=3, ge=1, le=100)


class SessionUpdate(BaseModel):
    permission_mode: str


class MessageUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=100000)


class WorkspaceInstructions(BaseModel):
    workspace: str
    content: str = Field(max_length=500000)


class ProviderUpdate(BaseModel):
    binding: str
    model: str = ""
    host: str = ""
    api_key: str = ""
    timeout: float = Field(default=120, gt=0, le=3600)


def create_app(
    harness,
    settings_store: SettingsStore | None = None,
    preferences_store: PreferencesStore | None = None,
):
    @asynccontextmanager
    async def lifespan(app):
        with harness.store.writer():
            harness.recover()
            yield
            await harness.close()

    app = FastAPI(title="MAGI Harness", lifespan=lifespan)
    static = Path(__file__).parent / "static"
    default_workspace = str(Path.cwd().resolve())

    @app.middleware("http")
    async def local_origin(request: Request, call_next):
        origin = request.headers.get("origin")
        if (
            request.method not in {"GET", "HEAD"}
            and origin
            and origin != str(request.base_url).rstrip("/")
        ):
            from fastapi.responses import JSONResponse

            return JSONResponse(
                {"detail": "Cross-origin writes are disabled"}, status_code=403
            )
        try:
            return await call_next(request)
        except KeyError:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                {"detail": "Session or source not found"}, status_code=404
            )

    @app.get("/api/config")
    async def config():
        return dict(
            model=harness.provider.model,
            binding=getattr(harness.provider, "binding", "demo"),
            demo=harness.provider.model == "offline-demo",
            data_path=str(harness.store.path),
            version="0.1.0",
            default_workspace=default_workspace,
        )

    def preferences() -> HarnessPreferences:
        return preferences_store.load() if preferences_store else HarnessPreferences()

    def workspace_path(value: str) -> Path:
        path = Path(value or default_workspace).expanduser().resolve()
        if not path.exists() or not path.is_dir():
            raise ValueError("Workspace must be an existing directory")
        return path

    def instruction_text(workspace: Path) -> str:
        target = workspace / preferences().instruction_file
        if not target.exists():
            return ""
        if not target.is_file():
            raise ValueError("MAGI.md must be a file")
        return target.read_text(encoding="utf-8")

    @app.get("/api/settings/preferences")
    async def get_preferences():
        return asdict(preferences())

    @app.put("/api/settings/preferences")
    async def update_preferences(body: PreferencesUpdate):
        try:
            value = HarnessPreferences(**body.model_dump()).validated()
            return asdict(preferences_store.save(value) if preferences_store else value)
        except (ValueError, OSError) as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/api/workspace/instructions")
    async def get_workspace_instructions(workspace: str = ""):
        try:
            path = workspace_path(workspace)
            return {
                "workspace": str(path),
                "file": "MAGI.md",
                "content": instruction_text(path),
            }
        except (ValueError, OSError, UnicodeError) as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/api/workspaces")
    async def workspaces():
        paths = sorted(
            {
                session["config"].get("workspace", default_workspace)
                for session in harness.store.sessions()
            }
        )
        result = []
        for value in paths:
            try:
                path = workspace_path(value)
                result.append(
                    {
                        "path": str(path),
                        "name": path.name or str(path),
                        "instructions": instruction_text(path),
                    }
                )
            except (ValueError, OSError, UnicodeError):
                result.append(
                    {"path": value, "name": Path(value).name, "unavailable": True}
                )
        return result

    @app.put("/api/workspace/instructions")
    async def put_workspace_instructions(body: WorkspaceInstructions):
        try:
            path = workspace_path(body.workspace)
            target = path / "MAGI.md"
            temporary = path / ".MAGI.md.tmp"
            temporary.write_text(body.content, encoding="utf-8")
            os.replace(temporary, target)
            return {"workspace": str(path), "file": "MAGI.md", "saved": True}
        except (ValueError, OSError, UnicodeError) as exc:
            raise HTTPException(422, str(exc)) from exc

    def current_settings() -> ProviderSettings:
        if settings_store is not None:
            return settings_store.load()
        provider = harness.provider
        if isinstance(provider, FakeProvider):
            return ProviderSettings()
        return ProviderSettings(
            binding=getattr(provider, "binding", "openai"),
            model=provider.model,
            host=provider.base_url,
            api_key=provider.api_key,
            timeout=provider.timeout,
        )

    def proposed(body: ProviderUpdate) -> ProviderSettings:
        previous = current_settings()
        keep_key = body.binding in {previous.binding, "compatible"}
        return ProviderSettings(
            binding=body.binding,
            model=body.model,
            host=body.host,
            api_key=body.api_key or (previous.api_key if keep_key else ""),
            timeout=body.timeout,
        ).validated()

    @app.get("/api/settings/provider")
    async def get_provider_settings():
        return current_settings().public()

    @app.put("/api/settings/provider")
    async def update_provider_settings(body: ProviderUpdate):
        try:
            settings = proposed(body)
            if settings_store is not None:
                settings_store.save(settings)
            harness.provider = settings.provider()
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            raise HTTPException(422, str(exc)) from exc
        return settings.public()

    @app.post("/api/settings/provider/discover")
    async def discover_provider_models(body: ProviderUpdate):
        try:
            provider = proposed(body).provider()
            if not hasattr(provider, "list_models"):
                return {"models": [provider.model], "demo": True}
            return {"models": await provider.list_models(), "demo": False}
        except (ValueError, OSError) as exc:
            raise HTTPException(422, str(exc)) from exc
        except ProviderError as exc:
            raise HTTPException(502, str(exc)) from exc

    @app.get("/api/sessions")
    async def sessions():
        return harness.store.sessions()

    @app.post("/api/sessions", status_code=201)
    async def create(body: NewSession):
        try:
            workspace = workspace_path(body.workspace)
            prefs = preferences()
            instructions = instruction_text(workspace)
            system = prefs.base_prompt.strip()
            if instructions.strip():
                system += "\n\nWorkspace instructions (MAGI.md):\n" + instructions
            sid = harness.create(
                ContextConfig(
                    policy=body.policy or prefs.context_policy,
                    window=body.window or prefs.window,
                    stage_turns=body.stage_turns or prefs.stage_turns,
                    workspace=str(workspace),
                    permission_mode=body.permission_mode,
                    system=system,
                )
            )
        except (ValueError, OSError, UnicodeError) as exc:
            raise HTTPException(422, str(exc)) from exc
        return harness.store.session(sid)

    @app.get("/api/sessions/{sid}")
    async def session(sid: str, after: int = 0):
        return dict(
            session=harness.store.session(sid),
            events=harness.store.events(sid, after),
            running=sid in harness.running,
            operation=harness.store.open_operation(sid),
        )

    @app.patch("/api/sessions/{sid}")
    async def update_session(sid: str, body: SessionUpdate):
        if harness.store.open_operation(sid):
            raise HTTPException(
                409, "Cannot change configuration during an open operation"
            )
        try:
            config = ContextConfig(
                **{
                    **harness.store.session(sid)["config"],
                    "permission_mode": body.permission_mode,
                }
            )
            session = harness.store.update_config(
                sid, permission_mode=config.permission_mode
            )
            harness.store.append(
                sid,
                "session_config",
                {"permission_mode": config.permission_mode},
            )
            return session
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.patch("/api/sessions/{sid}/messages/{seq}")
    async def update_message(sid: str, seq: int, body: MessageUpdate):
        if harness.store.open_operation(sid):
            raise HTTPException(409, "Cannot edit messages during an open operation")
        target = next((e for e in harness.store.events(sid) if e["seq"] == seq), None)
        if (
            target is None
            or target["kind"] != "message"
            or target["data"].get("role") not in {"user", "assistant"}
            or target["data"].get("tool_calls")
        ):
            raise HTTPException(
                422, "Only user and assistant text messages can be edited"
            )
        return harness.store.append(
            sid,
            "message_edit",
            {"target_seq": seq, "content": body.content},
            target["turn"],
        )

    @app.post("/api/sessions/{sid}/messages", status_code=202)
    async def prompt(sid: str, body: Prompt):
        try:
            attachments = []
            total = 0
            for item in body.attachments:
                name = Path(str(item.get("name", ""))).name
                text = item.get("text")
                if not name or not isinstance(text, str):
                    raise ValueError("Only UTF-8 text attachments are supported")
                total += len(text.encode("utf-8"))
                attachments.append(
                    {
                        "name": name,
                        "type": str(item.get("type", "text/plain")),
                        "text": text,
                    }
                )
            if total > 2_000_000:
                raise ValueError("Attachments exceed the 2 MB limit")
            harness.start(sid, body.text, attachments)
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(409, str(exc)) from exc
        return {"accepted": True}

    @app.post("/api/sessions/{sid}/cancel")
    async def cancel(sid: str):
        harness.store.session(sid)
        await harness.cancel(sid)
        return {"cancelled": True}

    @app.post("/api/sessions/{sid}/resume", status_code=202)
    async def resume(sid: str):
        try:
            harness.resume(sid)
        except RuntimeError as exc:
            raise HTTPException(409, str(exc)) from exc
        return {"accepted": True}

    @app.post("/api/sessions/{sid}/compact", status_code=202)
    async def compact(sid: str):
        try:
            harness.compact(sid)
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(409, str(exc)) from exc
        return {"accepted": True}

    @app.post("/api/sessions/{sid}/queue/{queue}", status_code=202)
    async def enqueue(sid: str, queue: str, body: Prompt):
        try:
            return {"id": harness.enqueue(sid, body.text, queue)}
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.delete("/api/sessions/{sid}/queue/{ident}")
    async def cancel_queued(sid: str, ident: str):
        return {"outcome": harness.cancel_queued(sid, ident)}

    @app.post("/api/sessions/{sid}/approvals/{approval_id}")
    async def resolve_approval(sid: str, approval_id: str, allow: bool):
        try:
            harness.resolve_approval(sid, approval_id, allow)
        except KeyError as exc:
            raise HTTPException(404, "Approval is no longer pending") from exc
        return {"resolved": True, "allowed": allow}

    @app.get("/api/sessions/{sid}/source")
    async def source(sid: str, ref: str):
        return {"ref": ref, "value": harness.store.get(sid, ref)}

    @app.get("/")
    async def index():
        return FileResponse(static / "index.html")

    app.mount("/static", StaticFiles(directory=static), name="static")
    return app
