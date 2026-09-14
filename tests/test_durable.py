"""Crash prefixes and competing checkpoint inputs, with no network effects."""

import asyncio

import pytest

from mgh import Harness, Store
from mgh.tools import Tool, string_parameter
from test_harness import Scripted, answer, call


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "boundary",
    [
        "checkpoint",
        "append_record",
        "stream_assistant",
        "commit_response",
        "try_finish_run",
    ],
)
async def test_close_and_resume_prefix(tmp_path, boundary):
    store = Store(tmp_path / "journal.db")
    provider = Scripted([answer()])
    h = Harness(store, provider, drive="manual")
    sid = h.create()
    h.start(sid, "durable input")
    while (await h.peek_action(sid))["kind"] != boundary:
        await h.execute_action(sid)
    before = store.events(sid)
    await asyncio.sleep(0)
    assert store.events(sid) == before
    await h.close()
    store.close()
    store = Store(tmp_path / "journal.db")
    resumed = Harness(store, Scripted([answer()]))
    snapshot = store.events(sid)
    assert resumed.recover()[0]["session"] == sid
    assert store.events(sid) == snapshot
    await resumed.resume(sid)
    assert store.open_operation(sid) is None
    assert (
        len(
            [
                e
                for e in store.events(sid)
                if e["kind"] == "message" and e["data"]["role"] == "user"
            ]
        )
        == 1
    )
    store.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "persisted,current,executions",
    [("safe", "safe", 1), ("safe", "never", 0), ("never", "safe", 0)],
)
async def test_tool_crash_replay_requires_both_declarations(
    tmp_path, persisted, current, executions
):
    store = Store(tmp_path / "journal.db")
    calls = []

    async def tool(args):
        calls.append(args)
        return "ok"

    h = Harness(
        store,
        Scripted([call("probe", {"x": "v"}), answer()]),
        [Tool("probe", "probe", string_parameter("x"), tool, replay=persisted)],
        drive="manual",
    )
    sid = h.create()
    h.start(sid, "use tool")
    while (await h.peek_action(sid))["kind"] != "execute_tool":
        await h.execute_action(sid)
    await h.close()
    resumed = Harness(
        store,
        Scripted([answer()]),
        [Tool("probe", "probe", string_parameter("x"), tool, replay=current)],
    )
    await resumed.resume(sid)
    assert len(calls) == executions
    assert (
        len(
            [
                e
                for e in store.events(sid)
                if e["kind"] == "message" and e["data"].get("tool_call_id")
            ]
        )
        == 1
    )
    store.close()


@pytest.mark.asyncio
async def test_durable_attempt_cap_survives_restarts(tmp_path):
    store = Store(tmp_path / "journal.db")
    h = Harness(store, Scripted([]), drive="manual", max_attempts=2)
    sid = h.create()
    h.start(sid, "go")
    for _ in range(2):
        while (await h.peek_action(sid))["kind"] != "stream_assistant":
            await h.execute_action(sid)
        await h.close()
        h = Harness(store, Scripted([]), drive="manual", max_attempts=100)
        h.resume(sid)
    await h.run_to_completion(sid)
    assert store.open_operation(sid) is None
    assert len([e for e in store.events(sid) if e["kind"] == "step_attempt"]) == 2
    assert store.events(sid)[-1]["data"]["status"] == "failed"
    store.close()


@pytest.mark.asyncio
async def test_steer_finish_and_next_run_order(tmp_path):
    store = Store(tmp_path / "journal.db")
    h = Harness(store, Scripted([answer(), answer(), answer()]), drive="manual")
    sid = h.create()
    h.start(sid, "first")
    while (await h.peek_action(sid))["kind"] != "try_finish_run":
        await h.execute_action(sid)
    h.enqueue(sid, "steering")
    h.enqueue(sid, "next", "next_run")
    await h.run_to_completion(sid)
    with pytest.raises(RuntimeError, match="No active"):
        h.enqueue(sid, "too late")
    h.start(sid, "second")
    await h.run_to_completion(sid)
    users = [
        e["data"]["content"]
        for e in store.events(sid)
        if e["kind"] == "message" and e["data"]["role"] == "user"
    ]
    assert users == ["first", "steering", "next", "second"]
    store.close()
