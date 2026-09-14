import pytest

from mgh.arena import Case, run_arena


@pytest.mark.asyncio
async def test_arena_gate_and_unknown_answer_fail(tmp_path):
    case = Case("known", "task_success", ("FACT target=VALUE", "CHECK target"), "VALUE")
    report = await run_arena(tmp_path / "known", cases=[case])
    assert report["gate"]
    assert len(report["results"]) == 4
    assert all(r["provider_input_tokens"] is None for r in report["results"])
    unknown = Case("unknown", "task_success", ("CHECK target",), "SECRET")
    report = await run_arena(tmp_path / "unknown", cases=[unknown])
    assert not report["gate"]
    assert all(r["answer"] == "UNKNOWN" for r in report["results"])
