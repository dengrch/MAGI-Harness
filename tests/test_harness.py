import asyncio
import json
import stat
from pathlib import Path

import httpx
import pytest
import mgh.settings as settings_module

from mgh import ContextCompiler, ContextConfig, Harness, Store
from mgh.context import BudgetExceeded
from mgh.memo import memo_tools, workspace_store
from mgh.provider import (
    CompatibleProvider,
    FakeProvider,
    ProviderError,
    usage_metrics,
)
from mgh.settings import (
    PreferencesStore,
    ProviderSettings,
    SettingsStore,
    default_data_dir,
)
from mgh.store import canonical
from mgh.tools import Tool, ToolContext, basic_tools, string_parameter
from mgh.web import create_app


class Scripted:
    model = "scripted"

    def __init__(self, messages):
        self.messages = iter(messages)
        self.payloads = []

    async def stream(self, payload):
        self.payloads.append(payload)
        yield dict(
            kind="completion",
            message=next(self.messages),
            usage=None,
            finish_reason="stop",
        )


def answer(content="Done"):
    return dict(role="assistant", content=content)


def call(name="calculate", args=None):
    return dict(
        role="assistant",
        content="",
        tool_calls=[
            dict(
                id="c1",
                type="function",
                function=dict(
                    name=name, arguments=json.dumps(args or {"expression": "2+3"})
                ),
            )
        ],
    )


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "context.db")
    yield s
    s.close()


@pytest.mark.asyncio
async def test_each_model_call_compiles_and_persists_tool_result(store):
    p = Scripted([call(), answer()])
    h = Harness(store, p)
    sid = h.create()
    await h.run(sid, "Calculate")
    events = store.events(sid)
    requests = [e for e in events if e["kind"] == "request"]
    assert len(requests) == 2
    result = next(
        e for e in events if e["kind"] == "message" and e["data"]["role"] == "tool"
    )
    assert requests[0]["seq"] < result["seq"] < requests[1]["seq"]
    assert json.loads(p.payloads[1]["messages"][-1]["content"]) == {"result": 5}
    assert requests[1]["data"]["prefix_retained"] == 1
    assert store.events(sid)[-1]["data"]["status"] == "completed"


@pytest.mark.asyncio
async def test_stages_sources_and_determinism_survive_reopen(store):
    h = Harness(store, Scripted([answer(str(i)) for i in range(5)]))
    sid = h.create(ContextConfig(stage_turns=1, keep_hot_turns=0))
    for i in range(3):
        await h.run(sid, f"constraint-{i}")
    events = store.events(sid)
    request = [e for e in events if e["kind"] == "request"][-1]["data"]
    assert [len(request["zones"][z]) for z in ("stable", "stubs", "cold", "hot")] == [
        1,
        1,
        1,
        1,
    ]
    for blocks in request["zones"].values():
        for block in blocks:
            for ref in block["source_refs"]:
                assert store.get(sid, ref)
    before = h.compiler.compile(sid, h.provider.model, h.schemas)
    other = Store(store.path)
    try:
        after = ContextCompiler(other).compile(sid, h.provider.model, h.schemas)
        assert canonical(before) == canonical(after)
        assert other.events(sid) == events
    finally:
        other.close()


@pytest.mark.asyncio
async def test_full_history_never_transitions(store):
    h = Harness(store, Scripted([answer(), answer(), answer()]))
    sid = h.create(ContextConfig(policy="full_history", stage_turns=1))
    for _ in range(3):
        await h.run(sid, "hello")
    assert not any(e["kind"] == "stage" for e in store.events(sid))
    snapshot = h.compiler.compile(sid, h.provider.model, h.schemas)
    assert len(snapshot["payload"]["messages"]) == 7


@pytest.mark.asyncio
async def test_page_in_has_no_copied_body_in_journal_or_cold(store):
    sid = store.create(ContextConfig(stage_turns=1, keep_hot_turns=0).to_dict())
    ref = store.put(sid, {"text": "SECRET ORIGINAL EVIDENCE"})
    h = Harness(
        store,
        Scripted([call("context_read", {"ref": ref}), answer("Conclusion"), answer()]),
    )
    await h.run(sid, "Read evidence")
    result = next(
        e
        for e in store.events(sid)
        if e["kind"] == "message" and e["data"]["role"] == "tool"
    )
    assert result["data"]["content"] == ""
    assert result["data"]["page_ref"] == ref
    assert (
        "SECRET ORIGINAL EVIDENCE" in h.provider.payloads[1]["messages"][-1]["content"]
    )
    await h.run(sid, "continue")
    stage = next(e["data"] for e in store.events(sid) if e["kind"] == "stage")
    assert stage["cold"][0]["loaded_from"] == [ref]
    assert "SECRET ORIGINAL EVIDENCE" not in canonical(stage)
    assert store.get(sid, ref)["text"] == "SECRET ORIGINAL EVIDENCE"


@pytest.mark.asyncio
async def test_budget_failure_never_sends_or_deletes_input(store):
    p = Scripted([answer()])
    h = Harness(store, p)
    sid = h.create(ContextConfig(window=4096))
    text = "x" * 10000
    await h.run(sid, text)
    assert p.payloads == []
    assert store.events(sid)[-1]["data"]["status"] == "failed"
    assert any(
        e["kind"] == "message" and e["data"]["content"] == text
        for e in store.events(sid)
    )
    with pytest.raises(BudgetExceeded):
        h.compiler.compile(sid, "x", [])


def test_sources_scoped_and_hash_checked(store):
    a, b = store.create({}), store.create({})
    ref = store.put(a, {"unicode": "中文"})
    assert store.put(a, {"unicode": "中文"}) == ref
    assert store.get_many(a, [ref, ref]) == [{"unicode": "中文"}] * 2
    with pytest.raises(KeyError):
        store.get(b, ref)
    other = Store(store.path, workspace="other")
    with pytest.raises(KeyError):
        other.get(a, ref)
    other.close()
    store.db.execute("UPDATE sources SET body='{}' WHERE ref=?", (ref,))
    with pytest.raises(ValueError, match="integrity"):
        store.get(a, ref)


def test_event_corruption_is_not_silently_ignored(store):
    sid = store.create({})
    e = store.append(sid, "message", answer())
    store.db.execute("UPDATE sources SET body='{}' WHERE ref=?", (e["ref"],))
    with pytest.raises(ValueError):
        store.events(sid)


def test_process_writer_exclusion(store):
    other = Store(store.path)
    try:
        with store.writer():
            with pytest.raises(RuntimeError, match="Another"):
                with other.writer():
                    pass
    finally:
        other.close()


def test_recovery_closes_unknown_tool_without_execution(store):
    h = Harness(store, Scripted([]))
    sid = h.create()
    store.append(sid, "turn_start", {}, "turn")
    store.append(sid, "message", call(), "turn")
    h.recover()
    events = store.events(sid)
    assert events[-1]["data"]["status"] == "interrupted"
    assert any(
        "unknown" in e["data"].get("content", "")
        for e in events
        if e["kind"] == "message"
    )
    h.recover()
    assert store.events(sid) == events


@pytest.mark.asyncio
async def test_cancel_and_busy_preserve_pairing(store):
    entered = asyncio.Event()

    async def wait(args):
        entered.set()
        await asyncio.Event().wait()

    h = Harness(
        store,
        Scripted([call("wait", {"x": "x"})]),
        [Tool("wait", "wait", string_parameter("x"), wait)],
    )
    sid = h.create()
    task = h.start(sid, "go")
    await entered.wait()
    with pytest.raises(RuntimeError, match="running"):
        h.start(sid, "overlap")
    await h.cancel(sid)
    await task
    events = store.events(sid)
    assert events[-1]["data"]["status"] == "cancelled"
    assert any(
        e["kind"] == "message" and e["data"].get("tool_call_id") == "c1" for e in events
    )
    assert sid not in h.running


@pytest.mark.asyncio
async def test_cancel_before_task_starts_is_closed(store):
    h = Harness(store, Scripted([]))
    sid = h.create()
    h.start(sid, "go")
    await h.cancel(sid)
    assert store.events(sid)[-1]["data"]["status"] == "cancelled"
    assert sid not in h.running


@pytest.mark.asyncio
async def test_failed_tool_yields_result_then_model_continues(store):
    h = Harness(
        store, Scripted([call(args={"expression": "__import__('os')"}), answer()])
    )
    sid = h.create()
    await h.run(sid, "calculate")
    assert '"error"' in h.provider.payloads[1]["messages"][-1]["content"]
    assert store.events(sid)[-1]["data"]["status"] == "completed"


@pytest.mark.asyncio
async def test_http_session_trace_and_source(store):
    h = Harness(store, Scripted([answer("hello")]))
    transport = httpx.ASGITransport(app=create_app(h))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/")).status_code == 200
        sid = (await client.post("/api/sessions", json={})).json()["id"]
        assert (
            await client.post(f"/api/sessions/{sid}/messages", json={"text": "Hi"})
        ).status_code == 202
        if sid in h.running:
            await h.running[sid]
        data = (await client.get(f"/api/sessions/{sid}")).json()
        assert data["running"] is False
        assert any(e["kind"] == "request" for e in data["events"])
        ref = data["events"][0]["ref"]
        assert (
            await client.get(f"/api/sessions/{sid}/source", params={"ref": ref})
        ).status_code == 200
        assert (
            await client.post(
                "/api/sessions", headers={"Origin": "https://foreign.example"}, json={}
            )
        ).status_code == 403
        assert (await client.get("/api/sessions/missing")).status_code == 404
        assert (
            await client.post("/api/sessions", json={"policy": "bad"})
        ).status_code == 422


@pytest.mark.asyncio
async def test_direct_memo_handle_and_workspace_layout(tmp_path):
    class Handle:
        async def search(self, text, **kwargs):
            assert kwargs == {"only_need_context": True}
            return {"text": text}

    tool = memo_tools(Handle())[0]
    assert await tool.run({"query": "memory"}) == {"text": "memory"}
    s = workspace_store(tmp_path, "workspace-a")
    assert s.path == tmp_path / "contexts" / "harness.db"
    assert s.workspace == "workspace-a"
    s.close()


@pytest.mark.parametrize(
    "raw,read",
    [
        (None, None),
        ({"prompt_tokens_details": {"cached_tokens": 0}}, 0),
        ({"prompt_cache_hit_tokens": 30}, 30),
        ({"prompt_tokens": 100}, None),
    ],
)
def test_cache_unknown_is_distinct_from_zero(raw, read):
    assert usage_metrics(raw)["cache_read_tokens"] == read


@pytest.mark.asyncio
async def test_compatible_provider_stream_fragments_and_usage(monkeypatch):
    chunks = [
        {"choices": [{"delta": {"reasoning_content": "thinking"}}]},
        {
            "choices": [
                {
                    "delta": {
                        "tool_calls": [
                            {
                                "index": 0,
                                "id": "c1",
                                "function": {
                                    "name": "calculate",
                                    "arguments": '{"expression":',
                                },
                            }
                        ]
                    }
                }
            ]
        },
        {
            "choices": [
                {
                    "delta": {
                        "tool_calls": [
                            {"index": 0, "function": {"arguments": '"2+3"}'}}
                        ]
                    },
                    "finish_reason": "tool_calls",
                }
            ]
        },
        {
            "choices": [],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 4,
                "prompt_tokens_details": {"cached_tokens": 0},
            },
        },
    ]

    def handler(request):
        assert request.url.path == "/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer secret"
        return httpx.Response(
            200,
            text="\n\n".join("data: " + json.dumps(c) for c in chunks)
            + "\n\ndata: [DONE]\n",
        )

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kw: original(transport=httpx.MockTransport(handler), **kw),
    )
    p = CompatibleProvider("model", "https://provider.test/v1", "secret")
    out = [e async for e in p.stream({"model": "model", "messages": []})]
    assert out[0]["field"] == "reasoning_content"
    assert (
        out[-1]["message"]["tool_calls"][0]["function"]["arguments"]
        == '{"expression":"2+3"}'
    )
    assert out[-1]["usage"]["prompt_tokens"] == 10


@pytest.mark.asyncio
async def test_provider_settings_are_persisted_without_echoing_secret(store, tmp_path):
    settings = SettingsStore(tmp_path / "settings.json")
    h = Harness(store, FakeProvider())
    transport = httpx.ASGITransport(app=create_app(h, settings))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/settings/provider",
            json={
                "binding": "ollama",
                "model": "qwen3:8b",
                "host": "http://127.0.0.1:11434/v1/",
                "api_key": "local-secret",
                "timeout": 45,
            },
        )
        assert response.status_code == 200
        assert response.json()["has_api_key"] is True
        assert "api_key" not in response.json()
        assert h.provider.model == "qwen3:8b"
        assert h.provider.binding == "ollama"
        assert h.provider.base_url == "http://127.0.0.1:11434/v1"
        loaded = (await client.get("/api/settings/provider")).json()
        assert "api_key" not in loaded
    assert settings.load().api_key == "local-secret"
    assert stat.S_IMODE(settings.path.stat().st_mode) == 0o600


@pytest.mark.asyncio
async def test_workspace_tools_are_scoped_and_require_read_before_edit(tmp_path):
    workspace = tmp_path / "work"
    workspace.mkdir()
    target = workspace / "note.txt"
    target.write_text("old", encoding="utf-8")
    tools = {tool.name: tool for tool in basic_tools()}
    context = ToolContext(workspace)
    with pytest.raises(PermissionError, match="outside"):
        await tools["read"].run({"file_path": "../secret"}, context)
    with pytest.raises(PermissionError, match="Read"):
        await tools["edit"].run(
            {"file_path": "note.txt", "old_string": "old", "new_string": "new"},
            context,
        )
    read = await tools["read"].run({"file_path": "note.txt"}, context)
    assert "old" in read["content"]
    await tools["edit"].run(
        {"file_path": "note.txt", "old_string": "old", "new_string": "new"},
        context,
    )
    assert target.read_text(encoding="utf-8") == "new"


@pytest.mark.asyncio
async def test_mutating_tool_waits_for_durable_approval(store, tmp_path):
    workspace = tmp_path / "work"
    workspace.mkdir()
    h = Harness(
        store,
        Scripted(
            [call("write", {"file_path": "new.txt", "content": "hello"}), answer()]
        ),
    )
    sid = h.create(ContextConfig(workspace=str(workspace), permission_mode="ask"))
    task = h.start(sid, "create a file")
    for _ in range(100):
        required = [e for e in store.events(sid) if e["kind"] == "approval_required"]
        if required:
            break
        await asyncio.sleep(0.01)
    assert required
    assert not (workspace / "new.txt").exists()
    h.resolve_approval(sid, required[0]["data"]["approval_id"], True)
    await task
    assert (workspace / "new.txt").read_text(encoding="utf-8") == "hello"
    assert any(e["kind"] == "approval_resolved" for e in store.events(sid))


@pytest.mark.asyncio
async def test_preferences_magi_snapshot_and_attachment_are_persisted(store, tmp_path):
    workspace = tmp_path / "work"
    workspace.mkdir()
    (workspace / "MAGI.md").write_text("Always cite tests.", encoding="utf-8")
    preferences = PreferencesStore(tmp_path / "preferences.json")
    h = Harness(store, Scripted([answer("ok")]))
    transport = httpx.ASGITransport(app=create_app(h, None, preferences))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        saved = await client.put(
            "/api/settings/preferences",
            json={
                "theme": "dark",
                "base_prompt": "Base rule.",
                "instruction_file": "MAGI.md",
            },
        )
        assert saved.status_code == 200
        session = await client.post("/api/sessions", json={"workspace": str(workspace)})
        sid = session.json()["id"]
        system = session.json()["config"]["system"]
        assert "Base rule." in system and "Always cite tests." in system
        response = await client.post(
            f"/api/sessions/{sid}/messages",
            json={
                "text": "inspect",
                "attachments": [
                    {"name": "a.txt", "type": "text/plain", "text": "evidence"}
                ],
            },
        )
        assert response.status_code == 202
        if sid in h.running:
            await h.running[sid]
    attachment = next(e for e in store.events(sid) if e["kind"] == "attachment")
    assert attachment["data"]["text"] == "evidence"


@pytest.mark.asyncio
async def test_message_edit_is_durable_and_changes_future_context(store):
    h = Harness(store, Scripted([answer("first")]))
    sid = h.create()
    await h.run(sid, "original")
    user = next(
        e
        for e in store.events(sid)
        if e["kind"] == "message" and e["data"]["role"] == "user"
    )
    transport = httpx.ASGITransport(app=create_app(h))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch(
            f"/api/sessions/{sid}/messages/{user['seq']}",
            json={"content": "corrected"},
        )
        assert response.status_code == 200
    snapshot = h.compiler.compile(sid, "model", h.schemas)
    assert any(
        message.get("content") == "corrected"
        for message in snapshot["payload"]["messages"]
    )
    assert store.get(sid, user["ref"])["content"] == "original"


@pytest.mark.asyncio
async def test_provider_http_error_keeps_safe_diagnosis(monkeypatch):
    def handler(request):
        return httpx.Response(
            429,
            json={"error": {"message": "rate limit reached"}},
            request=request,
        )

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kw: original(transport=httpx.MockTransport(handler), **kw),
    )
    provider = CompatibleProvider("model", "https://provider.test/v1", "secret")
    with pytest.raises(ProviderError, match="HTTP 429: rate limit reached"):
        _ = [event async for event in provider.stream({"messages": []})]


@pytest.mark.asyncio
async def test_local_provider_model_discovery_sends_no_fake_auth(monkeypatch):
    def handler(request):
        assert request.url.path == "/v1/models"
        assert "authorization" not in request.headers
        return httpx.Response(200, json={"data": [{"id": "b"}, {"id": "a"}]})

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kw: original(transport=httpx.MockTransport(handler), **kw),
    )
    provider = ProviderSettings(
        binding="llamacpp",
        model="local",
        host="http://127.0.0.1:8080/v1",
    ).provider()
    assert await provider.list_models() == ["a", "b"]


def test_llamacpp_wire_payload_enables_prompt_cache():
    provider = ProviderSettings(
        binding="llamacpp",
        model="local",
        host="http://127.0.0.1:8080/v1",
    ).provider()
    payload = {"model": "local", "messages": []}
    assert provider.prepare_payload(payload) == {**payload, "cache_prompt": True}
    assert "cache_prompt" not in payload


def test_default_data_dir_is_user_scoped(monkeypatch, tmp_path):
    monkeypatch.delenv("MGH_DATA_DIR", raising=False)
    monkeypatch.setattr(
        settings_module, "__file__", str(tmp_path / "checkout/mgh/settings.py")
    )
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: Path("/user/home")))
    assert default_data_dir() == Path("/user/home/.magi-harness")


def test_default_data_dir_preserves_parent_repo_sessions(monkeypatch, tmp_path):
    monkeypatch.delenv("MGH_DATA_DIR", raising=False)
    package = tmp_path / "sages/magi-harness/mgh/settings.py"
    legacy = tmp_path / "sages/mgh-test"
    legacy.mkdir(parents=True)
    monkeypatch.setattr(settings_module, "__file__", str(package))
    assert default_data_dir() == legacy


def test_default_data_dir_honors_environment(monkeypatch, tmp_path):
    target = tmp_path / "runtime"
    monkeypatch.setenv("MGH_DATA_DIR", str(target))
    assert default_data_dir() == target.resolve()


@pytest.mark.asyncio
async def test_provider_truncated_stream_fails(monkeypatch):
    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kw: original(
            transport=httpx.MockTransport(
                lambda _: httpx.Response(
                    200,
                    text='data: {"choices": [{"delta": {"content":"partial"}}]}\n\n',
                )
            ),
            **kw,
        ),
    )
    p = CompatibleProvider("m", "https://provider.test/v1", "secret")
    with pytest.raises(ProviderError, match="finish reason"):
        _ = [e async for e in p.stream({})]


@pytest.mark.asyncio
async def test_offline_demo_tool_loop(store):
    h = Harness(store, FakeProvider())
    sid = h.create()
    result = await h.run(sid, "/calc (12+8)*3")
    assert "60" in result["content"]
    assert len([e for e in store.events(sid) if e["kind"] == "request"]) == 2


@pytest.mark.asyncio
async def test_repeated_page_in_is_deduplicated(store):
    sid = store.create(ContextConfig().to_dict())
    ref = store.put(sid, {"text": "unique evidence body"})
    second = call("context_read", {"ref": ref})
    second["tool_calls"][0]["id"] = "c2"
    h = Harness(store, Scripted([call("context_read", {"ref": ref}), second, answer()]))
    await h.run(sid, "read twice")
    reads = [e for e in store.events(sid) if e["kind"] == "page_in"]
    assert [e["data"]["duplicate"] for e in reads] == [False, True]
    assert canonical(h.provider.payloads[-1]).count("unique evidence body") == 1


@pytest.mark.asyncio
async def test_serialized_snapshot_keeps_explicit_zone_order(store):
    h = Harness(store, Scripted([answer()]))
    sid = h.create()
    await h.run(sid, "Hello")
    request = next(e["data"] for e in store.events(sid) if e["kind"] == "request")
    assert request["zone_order"] == ["stable", "stubs", "cold", "hot"]
    assert request["payload"]["messages"][0]["role"] == "system"


@pytest.mark.asyncio
async def test_large_tool_output_is_projected_but_source_is_exact(store):
    text = "evidence " * 2000

    async def big(args):
        return {"text": text}

    h = Harness(
        store,
        Scripted([call("big", {"x": "x"}), answer()]),
        [Tool("big", "large result", string_parameter("x"), big)],
    )
    sid = h.create()
    await h.run(sid, "Fetch")
    preview = json.loads(h.provider.payloads[1]["messages"][-1]["content"])
    assert preview["truncated"] is True
    original = store.get(sid, preview["source_ref"])
    assert json.loads(original["content"])["text"] == text


def test_admission_batch_rolls_back_sources_and_events(store):
    sid = store.create({})
    with pytest.raises(ValueError):
        store.append_batch(
            sid,
            [("turn_start", {"text": "hello"}), ("message", {"invalid": float("nan")})],
            "turn",
        )
    assert store.events(sid) == []
    assert store.db.execute("SELECT count(*) FROM sources").fetchone()[0] == 0


@pytest.mark.asyncio
async def test_stage_retains_recent_hot_without_counting_it_again(store):
    h = Harness(store, Scripted([answer() for _ in range(7)]))
    sid = h.create(ContextConfig(stage_turns=3, keep_hot_turns=1))
    for i in range(7):
        await h.run(sid, f"turn-{i}")
    events = store.events(sid)
    stages = [e for e in events if e["kind"] == "stage"]
    turns = [e["turn"] for e in events if e["kind"] == "turn_start"]
    assert len(stages) == 2
    turn_starts = [e for e in events if e["kind"] == "turn_start"]
    turn_ends = [e for e in events if e["kind"] == "turn_end"]
    assert turn_ends[2]["seq"] < stages[0]["seq"] < turn_starts[3]["seq"]
    assert turn_ends[5]["seq"] < stages[1]["seq"] < turn_starts[6]["seq"]
    assert stages[0]["data"]["retained_hot"] == [turns[2]]
    assert stages[0]["data"]["moved_to_cold"] == turns[:2]
    assert stages[1]["data"]["retained_hot"] == [turns[5]]
    assert stages[1]["data"]["moved_to_cold"] == turns[2:5]
    requests = [e for e in events if e["kind"] == "request"]
    assert [e["data"]["stage"] for e in requests] == [0, 0, 0, 1, 1, 1, 2]
    assert requests[4]["data"]["prefix_retained"] == 1
    hot = requests[3]["data"]["zones"]["hot"]
    assert hot[0]["message"]["content"] == "turn-2"
    assert len([e for e in events if e["kind"] == "canonical"]) == 7
    assert next(e["seq"] for e in events if e["kind"] == "canonical") < stages[0]["seq"]


@pytest.mark.asyncio
async def test_budget_transition_cannot_evict_protected_recent_turn(store):
    h = Harness(store, Scripted([answer()]))
    sid = h.create(ContextConfig(stage_turns=1, keep_hot_turns=1))
    await h.run(sid, "Keep this reasoning")
    assert not h.compiler.transition(sid, force=True)
    assert not any(e["kind"] == "stage" for e in store.events(sid))
