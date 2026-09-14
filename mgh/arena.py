"""Reproducible context-policy arena. Run: python -m mgh.arena --output PATH.

The scripted provider can inspect only the real provider payload. Ground truth
belongs exclusively to the scorer; source reads use the public context tool.
"""

import argparse
import asyncio
import json
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

from .context import ContextConfig
from .runtime import Harness
from .store import Store, canonical, digest
from .tools import Tool


POLICIES = ("full_history", "sliding_window", "traditional_compaction", "four_zone")


@dataclass(frozen=True)
class Case:
    name: str
    category: str
    turns: tuple[str, ...]
    expected: str
    document: str = ""


def fixtures():
    noise = tuple(
        f"Progress {i}: " + "routine unrelated information " * 16 for i in range(10)
    )
    return [
        Case(
            "early_constraint",
            "constraint_retention",
            ("FACT format=JSON_ONLY", *noise, "CHECK format"),
            "JSON_ONLY",
        ),
        Case(
            "hidden_evidence",
            "hidden_evidence_recovery",
            ("LOAD_DOCUMENT", *noise, "CHECK code"),
            "MAGI_7281",
            "archive material " * 400 + "\nFACT code=MAGI_7281",
        ),
        Case(
            "unresolved_task",
            "constraint_retention",
            ("FACT pending=REVIEW_AUTH", *noise, "CHECK pending"),
            "REVIEW_AUTH",
        ),
        Case(
            "recent_fact",
            "task_success",
            (*noise, "FACT target=NEO4J", "CHECK target"),
            "NEO4J",
        ),
    ]


class ProbeProvider:
    """Payload-only fact probe, not an LLM quality estimator."""

    model = "arena-scripted-v1"

    def __init__(self):
        self.reads = set()

    async def stream(self, payload):
        messages = payload["messages"]
        last = messages[-1]
        text = canonical(messages)
        checks = re.findall(r"CHECK ([a-z_]+)", text)
        message = {"role": "assistant", "content": "Recorded"}
        if last.get("content") == "LOAD_DOCUMENT":
            message = self.call("load_document", {})
        elif checks:
            key = checks[-1]
            matches = re.findall(r"FACT " + re.escape(key) + r"=([A-Z0-9_]+)", text)
            if matches:
                message["content"] = matches[-1]
            else:
                refs = list(
                    dict.fromkeys(re.findall(r"ctx://v1/[a-f0-9]+/[a-f0-9]{64}", text))
                )
                ref = next((ref for ref in refs if ref not in self.reads), None)
                if ref:
                    self.reads.add(ref)
                    message = self.call("context_read", {"ref": ref})
                else:
                    message["content"] = "UNKNOWN"
        yield {
            "kind": "completion",
            "message": message,
            "usage": None,
            "finish_reason": "tool_calls" if message.get("tool_calls") else "stop",
        }

    def call(self, name, args):
        return {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": f"probe-{len(self.reads)}",
                    "type": "function",
                    "function": {"name": name, "arguments": canonical(args)},
                }
            ],
        }


def score(case, events):
    responses = [e for e in events if e["kind"] == "response"]
    final = responses[-1]["data"]["message"].get("content", "") if responses else ""
    ends = [e for e in events if e["kind"] == "turn_end"]
    success = (
        bool(ends)
        and ends[-1]["data"]["status"] == "completed"
        and final == case.expected
    )
    pairs = True
    for e in events:
        if e["kind"] != "message":
            continue
        for call in e["data"].get("tool_calls", []):
            results = [
                r
                for r in events
                if r["kind"] == "message"
                and r["turn"] == e["turn"]
                and r["seq"] > e["seq"]
                and r["data"].get("tool_call_id") == call["id"]
            ]
            pairs &= len(results) == 1
    requests = [e["data"] for e in events if e["kind"] == "request"]
    page_ins = [e["data"] for e in events if e["kind"] == "page_in"]
    return {
        "success": success,
        "answer": final,
        "tool_pairing": pairs,
        "requests": len(requests),
        "resident_units_total": sum(r["budget_units"] for r in requests),
        "resident_units_peak": max((r["budget_units"] for r in requests), default=0),
        "budget_ok": all(r["budget_units"] <= r["budget_limit"] for r in requests),
        "common_prefix_bytes_total": sum(r["common_prefix_bytes"] for r in requests),
        "page_ins": len(page_ins),
        "duplicate_page_ins": sum(p["duplicate"] for p in page_ins),
        "transitions": sum(e["kind"] == "stage" for e in events),
        "provider_input_tokens": None,
        "provider_cache_read_tokens": None,
        "cost": None,
    }


async def run_arena(output: Path, *, window=100000, policies=POLICIES, cases=None):
    output.mkdir(parents=True, exist_ok=True)
    cases = cases or fixtures()
    results = []
    for case in cases:
        for policy in policies:
            with tempfile.TemporaryDirectory(prefix="mgh-arena-") as directory:
                store = Store(Path(directory) / "journal.db")

                async def document(args):
                    return {"document": case.document}

                h = Harness(
                    store,
                    ProbeProvider(),
                    [
                        Tool(
                            "load_document",
                            "Read fixture document",
                            {"type": "object", "properties": {}},
                            document,
                            replay="safe",
                        )
                    ],
                    max_steps=64,
                )
                config = ContextConfig(
                    policy=policy,
                    stage_turns=2,
                    keep_hot_turns=1,
                    window=window,
                    summary_chars=1500,
                )
                sid = h.create(config)
                started = perf_counter()
                for text in case.turns:
                    await h.run(sid, text)
                events = store.events(sid)
                result = {
                    "case": case.name,
                    "category": case.category,
                    "policy": policy,
                    "config": asdict(config),
                    "fixture_hash": digest(asdict(case)),
                    "elapsed_ms": round((perf_counter() - started) * 1000),
                    **score(case, events),
                }
                result["source_integrity"] = all(
                    store.get(sid, e["ref"]) == e["data"] for e in events
                )
                trace = f"{case.name}-{policy}.json"
                (output / trace).write_text(
                    json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                result["trace"] = trace
                results.append(result)
                store.close()
    gate = all(
        r["tool_pairing"] and r["budget_ok"] and r["source_integrity"] for r in results
    )
    gate &= all(
        r["success"] for r in results if r["policy"] in {"full_history", "four_zone"}
    )
    report = {
        "schema_version": 1,
        "source_hash": digest(
            {
                p.name: p.read_text(encoding="utf-8")
                for p in sorted(Path(__file__).parent.glob("*.py"))
            }
        ),
        "provider": "scripted",
        "seed": 0,
        "quality_claim": "mechanism probes only; not real-model quality",
        "summary_method": "tail_excerpt",
        "budget_method": "utf8_bytes_plus_framing_proxy",
        "gate": bool(gate),
        "results": results,
    }
    (output / "results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# Context Arena",
        "",
        "Provider: scripted; quality results are deterministic mechanism probes.",
        "Budget: UTF-8 proxy units. Traditional compaction uses a tail excerpt, not a semantic model summary.",
        "Provider tokens, cache and cost are unavailable. Runtime includes local journal I/O.",
        "",
        f"Gate: {'PASS' if gate else 'FAIL'}",
        "",
        "Gate requires exact sources, complete tool pairing, budget compliance and all Full History/Four-Zone probes passing.",
        "",
        "| Case | Policy | Pass | Total units | Peak | Reads | Transitions |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    lines += [
        f"| {r['case']} | {r['policy']} | {r['success']} | {r['resident_units_total']} | {r['resident_units_peak']} | {r['page_ins']} | {r['transitions']} |"
        for r in results
    ]
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--window", type=int, default=100000)
    args = parser.parse_args()
    report = asyncio.run(run_arena(args.output, window=args.window))
    print(
        f"Context Arena: {'PASS' if report['gate'] else 'FAIL'}; {len(report['results'])} runs; {args.output / 'report.md'}"
    )
    raise SystemExit(0 if report["gate"] else 1)


if __name__ == "__main__":
    main()
