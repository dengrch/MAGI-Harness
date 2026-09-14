import pytest

from mgh import ContextConfig, Harness, Store
from test_harness import Scripted, answer


@pytest.mark.asyncio
async def test_compaction_uses_edits_and_rejects_conversational_writes(tmp_path):
    from mgh.compaction import preparation

    store = Store(tmp_path / "edits.db")
    h = Harness(store, Scripted([answer(), answer()]))
    sid = h.create(ContextConfig(keep_hot_turns=1))
    await h.run(sid, "obsolete constraint")
    await h.run(sid, "current work")
    original = next(e for e in store.events(sid) if e["kind"] == "message")
    edit = store.append(
        sid,
        "message_edit",
        {"target_seq": original["seq"], "content": "corrected constraint"},
        original["turn"],
    )
    prep = preparation(store, sid)
    assert "corrected constraint" in prep["body"]
    assert "obsolete constraint" not in prep["body"]
    assert edit["ref"] in prep["source_refs"]
    h.drive = "manual"
    h.compact(sid)
    with pytest.raises(RuntimeError, match="compaction"):
        h.append_message(sid, "must not be lost")
    with pytest.raises(RuntimeError, match="compaction"):
        h.enqueue(sid, "must not be lost")
    h.enqueue(sid, "next", "next_run")
    await h.close()
    store.close()


@pytest.mark.asyncio
async def test_failed_deferred_fetch_is_not_retried_after_error_commit(tmp_path):
    class Deferred:
        model = "deferred-test"
        fetches = 0

        async def stream(self, payload):
            yield {
                "kind": "completion",
                "message": answer(""),
                "finish_reason": "deferred",
                "deferred": {"id": "job"},
            }

        async def fetch_deferred(self, handle):
            self.fetches += 1
            raise RuntimeError("failed")

    store = Store(tmp_path / "deferred-error.db")
    provider = Deferred()
    h = Harness(store, provider)
    sid = h.create()
    await h.run(sid, "go")
    h.drive = "manual"
    h.resume(sid)
    while (await h.peek_action(sid))["kind"] != "finish_failed":
        await h.execute_action(sid)
    await h.close()
    h = Harness(store, provider)
    await h.resume(sid)
    assert provider.fetches == 1
    assert not store.open_operation(sid)
    store.close()


@pytest.mark.asyncio
async def test_semantic_rebase_keeps_archive_and_survives_commit_crash(tmp_path):
    store = Store(tmp_path / "journal.db")
    h = Harness(store, Scripted([answer(), answer()]))
    sid = h.create(ContextConfig(keep_hot_turns=1))
    await h.run(sid, "Never delete the archive")
    await h.run(sid, "Current work")
    h.provider = Scripted([answer("Constraint: never delete the archive")])
    h.drive = "manual"
    h.compact(sid)
    while (await h.peek_action(sid))["kind"] != "commit_compaction":
        await h.execute_action(sid)
    await h.close()
    h = Harness(store, Scripted([answer("Constraint: never delete the archive")]))
    await h.resume(sid)
    snapshot = h.compiler.compile(sid, h.provider.model, [])
    assert len(snapshot["zones"]["stubs"]) == 1
    archive_ref = snapshot["zones"]["stubs"][0]["source_refs"][0]
    archive = store.get(sid, archive_ref)
    assert any(
        store.get(sid, ref).get("content") == "Never delete the archive"
        for ref in archive["source_refs"]
    )
    assert store.open_operation(sid) is None
    store.close()


@pytest.mark.asyncio
async def test_deferred_result_pending_ready_and_no_replacement(tmp_path):
    class Deferred:
        model = "deferred-test"
        calls = 0
        fetches = 0

        async def stream(self, payload):
            self.calls += 1
            yield {
                "kind": "completion",
                "message": answer(""),
                "finish_reason": "deferred",
                "deferred": {"id": "job1"},
            }

        async def fetch_deferred(self, handle):
            self.fetches += 1
            if self.fetches == 1:
                return {
                    "message": answer(""),
                    "finish_reason": "deferred",
                    "deferred": handle,
                }
            return {"message": answer("ready"), "finish_reason": "stop"}

    store = Store(tmp_path / "journal.db")
    p = Deferred()
    h = Harness(store, p)
    sid = h.create()
    assert (await h.run(sid, "run"))["status"] == "suspended"
    assert (await h.resume(sid))["status"] == "suspended"
    assert (await h.resume(sid))["content"] == "ready"
    assert p.calls == 1 and p.fetches == 2
    assert not store.open_operation(sid)
    store.close()
