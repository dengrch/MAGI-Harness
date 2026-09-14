import asyncio

import pytest

from mgh import Harness, Store
from mgh.tools import Tool, string_parameter
from test_harness import Scripted, answer, call


@pytest.mark.asyncio
async def test_opt_in_read_tools_overlap_and_close_pairs(tmp_path):
    entered = []
    both = asyncio.Event()

    async def probe(args):
        entered.append(args["x"])
        if len(entered) == 2:
            both.set()
        await asyncio.wait_for(both.wait(), 2)
        return args

    message = call("probe", {"x": "a"})
    second = call("probe", {"x": "b"})["tool_calls"][0]
    second["id"] = "second"
    message["tool_calls"].append(second)
    store = Store(tmp_path / "parallel.db")
    harness = Harness(
        store,
        Scripted([message, answer()]),
        [Tool("probe", "probe", string_parameter("x"), probe, parallel=True)],
    )
    sid = harness.create()
    await harness.run(sid, "go")
    assert both.is_set()
    results = [
        e["data"]
        for e in store.events(sid)
        if e["kind"] == "message" and e["data"].get("role") == "tool"
    ]
    assert len(results) == 2
    assert all("error" not in r["content"] for r in results)
    assert store.open_operation(sid) is None
    store.close()
