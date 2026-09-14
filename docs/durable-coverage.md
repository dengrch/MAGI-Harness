# Durable implementation and acceptance boundary

This document describes the local Python implementation, not an assertion of Pi v2 parity.
The earlier parent-repository AgentHarness design informed the durability principles, but
this document and the tests define this package's actual acceptance boundary. The runtime
remains one linear conversation per session, one process writer, SQLite only. No production
credentials are required by tests.

## Implemented contracts

| Contract | Implementation | Regression evidence |
|---|---|---|
| Durable admission | Input and operation start commit together; unique open-operation projection per session | `test_durable.py` |
| Read-only restoration | Indexed open operation lookup, prefix validation, suspended inventory; explicit resume | `test_durable.py` |
| Close versus abort | Close preserves journal; abort marker precedes cancellation and closes tool pairs | `test_durable_edges.py` |
| Bounded attempts | Attempt appended before model effect; persisted cap survives restart | `test_durable.py` |
| Tool uncertainty | Intent before execution; persisted AND current replay policy must be safe | `test_durable.py` |
| Page-in commit | Source load record and tool result commit together | `test_durable_edges.py` |
| Queue checkpoints | steer, follow_up, next_run; durable consumption/cancellation; finish rechecks pending input | `test_durable.py` |
| Deferred writes | append_message records intent while running; applied at checkpoints and survives abort | `test_durable_edges.py` |
| Deferred provider results | Persist handle, fetch once per resume; pending stays suspended, no replacement request | `test_compaction.py` |
| Cost ordering | Provider usage journaled before response hooks/classification; unknown remains unknown | runtime + provider tests |
| Effect gates | Automatic/manual execution; peek has no effect; nested stream/delta actions | crash-prefix tests |
| Hooks/watch | Ordered before_tool, after_tool, before_request, after_response; passive buffered watch | `test_durable_edges.py` |
| Semantic rebase | Persist preparation; atomic summary/stage/finish; archive root retains exact sources | `test_compaction.py` |
| Request trace | Final payload budget checked after adapter/hook changes; prefix metrics are explicitly estimates | context tests + Arena |

## Embedding usage

```python
from mgh import Harness, Store

store = Store('/absolute/path/context.db')
with store.writer():
    harness = Harness(store, provider, tools=tools)
    suspended = harness.recover()  # New operations are not changed by this read.
    if suspended:
        await harness.resume(suspended[0]['session'])
    sid = harness.create()
    task = harness.start(sid, 'Begin work')
    harness.enqueue(sid, 'Additional constraint', queue='steer')
    harness.enqueue(sid, 'Then review the result', queue='follow_up')
    harness.enqueue(sid, 'Input for the next run', queue='next_run')
    await task
    await harness.close()
store.close()
```

`resume` requires the same model name and session configuration captured at admission.
Tool implementations remain the host's responsibility: `replay='safe'` is a promise
of replay safety, not an automatic inference from a tool's name or read-only label.
Uncertain writes are not retried automatically. No exactly-once external effects guarantee.

For deterministic fault injection, construct `Harness(..., drive='manual')`, call
`start`, then `peek_action` / `execute_action`, or `run_to_completion`. Close at a chosen
gate, reopen the same database and resume. `peek_action` does not release an effect.

`append_message` accepts a durable user fact during a normal run; it is distinct from
steering and survives abort. Compaction rejects conversational writes/steering; next_run
may still be queued. Web editing and configuration changes reject all open operations,
including suspended ones. Direct Store mutation bypasses the runtime contract.

Web exposes POST `/api/sessions/{sid}/resume`, `/compact`, `/cancel`, and
`/queue/{queue}`, plus DELETE `/queue/{id}`. Session responses include `operation`.
The chat displays a Resume action for a suspended operation. CLI has `/resume`,
`/abort`, `/compact`, `/quit`.

## Deliberate limitations / unfinished Pi v2 work

- No tree entries, branches/lanes, checkout/navigation operations, JSONL v3 import/export,
  backend protocol or parity suite. SQLite events are the authoritative linear journal.
- The reducer validates prefixes but is not yet the sole state-machine implementation;
  runtime checkpoint decisions also read event history. Large-session performance needs profiling.
- Read tools may opt into concurrent batches with `parallel=True`; writes and other
  tools form sequential barriers. Manual drive stays sequential. Replay safety is
  independent. There is no complete JSON Schema validator, terminate-tool protocol,
  or full Pi event/hook catalog.
- Sticky runtime faults cover gated writes and SQLite execution failures, not every direct
  Store mutation. Hosts must serialize writes and acquire `store.writer()`.
- Deferred provider behavior is tested with a custom provider; the shipped compatible
  Chat Completions adapter does not implement native background-job retrieval.
- Rebase is explicit, Four-Zone only, and summarizes the retired history in one bounded
  request. It is not incremental multi-level automatic compaction; very large preparation
  fails visibly. Automatic overflow recovery only attempts an existing stage migration.
- Default stubs and traditional_compaction are excerpts, not semantic summaries. Semantic
  rebase uses a real provider call; offline tests use a scripted summary.
- The Arena is a reproducible mechanism gate, not a benchmark of model intelligence or
  production cache behavior. Online repeated trials, pricing and confidence intervals remain.
- Memo is an adapter seam, not integration into MagiRuntime lifecycle or automatic Episode
  promotion. No changes were made to production Memo data or Linear issue state.

## Verification commands

Session acceptance (2026-09-14): 64 backend tests, 31 jsdom tests, Ruff and JavaScript
syntax checks pass. The wheel builds offline through `setuptools.build_meta` (the repo
venv has no pip). Context Arena completes 16 runs and its mechanism gate passes.
The two lossy baselines each pass only the recent-fact case; this does not fail the
gate by design. [Generated report](../artifacts/context-arena/report.md) and
[machine-readable results](../artifacts/context-arena/results.json) include all outcomes.

Run from an independent checkout:

```bash
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check .
npm install
npm test
npm run check
python -m mgh.arena --output /tmp/magi-arena
```

When developing inside the MAGI Memo parent repository, the existing environments can
be reused:

```bash
./scripts/test.sh sages/magi-harness/tests
.venv/bin/ruff check sages/magi-harness
NODE_PATH="$PWD/sages/dsh/node_modules" node --test sages/magi-harness/tests/ui.test.cjs
node --check sages/magi-harness/mgh/static/app.js
PYTHONPATH=sages/magi-harness .venv/bin/python -m mgh.arena --output /tmp/magi-arena
```

UI tests exercise jsdom, not real-browser visual layout. No live LLM/network test is
included in these acceptance results. See the generated Arena report for per-policy
quality/cost-proxy results rather than inferring savings from compression alone.
