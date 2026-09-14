import asyncio

import pytest

from mgh import Harness, Store
from mgh.reducer import reduce_operation
from mgh.tools import Tool, string_parameter
from test_harness import Scripted, answer, call


@pytest.mark.asyncio
async def test_input_accepted_at_failure_finish_is_not_lost(tmp_path):
    from mgh.provider import ProviderError

    class FailsOnce(Scripted):
        calls = 0

        async def stream(self, payload):
            self.calls += 1
            if self.calls == 1:
                raise ProviderError("failed")
            async for event in super().stream(payload):
                yield event

    store = Store(tmp_path / "finish-race.db")
    provider = FailsOnce([answer("recovered")])
    h = Harness(store, provider, drive="manual")
    sid = h.create()
    h.start(sid, "go")
    while (await h.peek_action(sid))["kind"] != "finish_failed":
        await h.execute_action(sid)
    ident = h.enqueue(sid, "new instruction", "follow_up")
    await h.run_to_completion(sid)
    assert any(
        e["kind"] == "queue_consumed" and e["data"]["id"] == ident
        for e in store.events(sid)
    )
    assert provider.calls == 2
    assert not store.open_operation(sid)
    store.close()


@pytest.mark.asyncio
async def test_web_rejects_mutating_suspended_configuration_and_messages(tmp_path):
    import httpx
    from mgh.web import create_app

    store = Store(tmp_path / "api.db")
    h = Harness(store, Scripted([]), drive="manual")
    sid = h.create()
    h.start(sid, "accepted")
    await h.peek_action(sid)
    await h.close()
    h = Harness(store, Scripted([answer()]))
    message = next(e for e in store.events(sid) if e["kind"] == "message")
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app(h)), base_url="http://test"
    ) as client:
        state = await client.get(f"/api/sessions/{sid}")
        assert state.json()["operation"]
        assert (
            await client.patch(
                f"/api/sessions/{sid}", json={"permission_mode": "read_only"}
            )
        ).status_code == 409
        assert (
            await client.patch(
                f"/api/sessions/{sid}/messages/{message['seq']}",
                json={"content": "changed"},
            )
        ).status_code == 409
        assert (await client.post(f"/api/sessions/{sid}/resume")).status_code == 202
        if task := h.running.get(sid):
            await task
        assert not store.open_operation(sid)
    store.close()


@pytest.mark.asyncio
async def test_page_in_commit_is_atomic_across_resume(tmp_path):
    store = Store(tmp_path / "page.db")
    h = Harness(store, Scripted([]), drive="manual")
    sid = h.create()
    ref = store.put(sid, {"evidence": "must remain available"})
    h.provider = Scripted([call("context_read", {"ref": ref})])
    h.start(sid, "read")
    while (await h.peek_action(sid))["kind"] != "commit_tool_result":
        await h.execute_action(sid)
    assert not any(e["kind"] == "page_in" for e in store.events(sid))
    await h.close()
    h = Harness(store, Scripted([answer()]))
    await h.resume(sid)
    pages = [e for e in store.events(sid) if e["kind"] == "page_in"]
    results = [
        e
        for e in store.events(sid)
        if e["kind"] == "message" and e["data"].get("page_ref")
    ]
    assert len(pages) == len(results) == 1
    assert not pages[0]["data"]["duplicate"]
    store.close()


@pytest.mark.asyncio
async def test_terminal_reason_survives_response_commit(tmp_path):
    class Limited(Scripted):
        async def stream(self, payload):
            yield {
                "kind": "completion",
                "message": answer("partial"),
                "finish_reason": "length",
            }

    store = Store(tmp_path / "limit.db")
    h = Harness(store, Limited([]), drive="manual")
    sid = h.create()
    h.start(sid, "go")
    while (await h.peek_action(sid))["kind"] != "finish_operation":
        await h.execute_action(sid)
    await h.close()
    h = Harness(store, Scripted([]))
    await h.resume(sid)
    end = next(e for e in store.events(sid) if e["kind"] == "turn_end")
    assert end["data"]["status"] == "length"
    store.close()


def test_reentrant_observers_preserve_commit_order(tmp_path):
    store = Store(tmp_path / "watch.db")
    sid = Harness(store, Scripted([])).create()
    seen = []

    def nested(session, event):
        if event["kind"] == "first":
            store.append(session, "nested", {})

    store.observers.extend([nested, lambda session, event: seen.append(event["kind"])])
    store.append_batch(sid, [("first", {}), ("second", {})])
    assert seen == ["first", "second", "nested"]
    store.close()


@pytest.mark.asyncio
async def test_deferred_writes_survive_abort_but_steering_does_not(tmp_path):
    store = Store(tmp_path / "journal.db")
    h = Harness(store, Scripted([]), drive="manual")
    sid = h.create()
    h.start(sid, "go")
    await h.peek_action(sid)
    h.enqueue(sid, "discard this")
    h.enqueue(sid, "later", "next_run")
    h.append_message(sid, "durable fact")
    await h.cancel(sid)
    users = [e["data"]["content"] for e in store.events(sid) if e["kind"] == "message"]
    assert "durable fact" in users
    assert "discard this" not in users and "later" not in users
    assert (
        h._pending(sid, None, {"next_run"})[0]["data"]["message"]["content"] == "later"
    )
    store.close()


@pytest.mark.asyncio
async def test_hook_failure_prevents_tool_effect_and_watch_is_passive(tmp_path):
    store = Store(tmp_path / "journal.db")
    executed = []

    async def tool(args):
        executed.append(args)

    h = Harness(
        store,
        Scripted([call("probe", {"x": "v"}), answer()]),
        [Tool("probe", "probe", string_parameter("x"), tool)],
    )
    sid = h.create()
    watch = h.watch(sid)
    received = []

    def broken(event):
        raise RuntimeError("hook failed")

    h.hooks.on("before_tool", broken)
    await h.run(sid, "go")
    assert not executed
    assert not any(e["kind"] == "tool_intent" for e in store.events(sid))
    watch.start(lambda event: received.append(event["seq"]))
    assert received == [e["seq"] for e in store.events(sid)]
    failing = h.watch(sid)
    failing.start(broken)
    h.record_usage(sid, {"input_tokens": 2})
    assert received[-1] == store.events(sid)[-1]["seq"]
    watch.unsubscribe()
    failing.unsubscribe()
    store.close()


def test_reducer_rejects_nonconsecutive_attempts(tmp_path):
    store = Store(tmp_path / "journal.db")
    h = Harness(store, Scripted([]))
    sid = h.create()
    store.append(
        sid, "operation_started", {"model": "scripted", "max_attempts": 3}, "t"
    )
    store.append(sid, "step_attempt", {"attempt": 2, "result_id": "x"}, "t")
    with pytest.raises(ValueError, match="Non-consecutive"):
        reduce_operation(store.operation_events(sid, "t"))
    with pytest.raises(ValueError):
        h.recover()
    store.close()


@pytest.mark.asyncio
async def test_truncated_tool_batch_never_executes(tmp_path):
    class Truncated(Scripted):
        async def stream(self, payload):
            value = next(self.messages)
            yield {
                "kind": "completion",
                "message": value,
                "finish_reason": "length" if value.get("tool_calls") else "stop",
            }

    store = Store(tmp_path / "journal.db")
    executed = []

    async def tool(args):
        executed.append(args)

    h = Harness(
        store,
        Truncated([call("probe", {"x": "v"}), answer()]),
        [Tool("probe", "probe", string_parameter("x"), tool)],
    )
    sid = h.create()
    await h.run(sid, "go")
    assert not executed
    assert not any(e["kind"] == "tool_intent" for e in store.events(sid))
    store.close()


@pytest.mark.asyncio
async def test_every_no_tool_action_prefix_reopens(tmp_path):
    # The loop terminates when a complete execution has fewer actions than the
    # requested prefix. Each earlier prefix closes at its exact manual gate.
    reached_complete = False
    for prefix in range(30):
        store = Store(tmp_path / f"prefix-{prefix}.db")
        h = Harness(store, Scripted([answer()]), drive="manual")
        sid = h.create()
        task = h.start(sid, "accepted once")
        for _ in range(prefix):
            if task.done() or await h.peek_action(sid) is None:
                break
            await h.execute_action(sid)
        if task.done():
            reached_complete = True
            store.close()
            break
        await h.close()
        h = Harness(store, Scripted([answer()]))
        await h.resume(sid)
        assert store.open_operation(sid) is None
        assert len([e for e in store.events(sid) if e["kind"] == "turn_end"]) == 1
        store.close()
        await asyncio.sleep(0)
    assert reached_complete
