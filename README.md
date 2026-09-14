# MAGI Harness

A durable, observable Python agent runtime with four-zone context management and exact-source recovery.

MAGI Harness runs a single linear agent session across model calls and tool executions while preserving enough durable state to inspect, stop, and safely resume the work. It is available as a local Web application, a CLI, and an embeddable Python runtime.

## Four-zone context management

Long-running agents need more than a sliding window. A sliding window silently loses old constraints, while repeatedly summarizing the entire history can erase evidence and invalidate reusable prompt prefixes. MAGI Harness instead separates the model-visible context into four zones:

| Zone | Purpose | Representation |
| --- | --- | --- |
| **Stable** | Keep the request prefix predictable | System instructions and deterministically ordered tool schemas |
| **Stubs** | Make old history discoverable at low cost | Short navigational excerpts with exact source references |
| **Cold** | Preserve recently retired work without large tool payloads | Canonical turn text, tool arguments, provenance, and references to omitted bodies |
| **Hot** | Protect the active working set | The current turn and the most recent completed turns in full |

Requests are compiled in the fixed order **Stable → Stubs → Cold → Hot**. After a configurable number of completed turns, older Hot turns move to Cold and the previous Cold batch moves to Stubs. The newest completed turns remain protected in Hot, and an in-progress tool exchange is never split by a transition.

Every original message and tool result is stored independently from its compact projection as a content-addressed `ctx://` source. Stubs are explicitly marked as excerpts rather than summaries. When omitted evidence becomes relevant, the agent can call `context_read` to page the exact source back into the current turn. Moving history between zones therefore changes what the model sees, not what the system retains.

The compiler applies a request budget before each provider call. If a normal stage transition cannot fit the protected Hot tail, the run fails visibly instead of silently discarding history. An explicit semantic rebase can summarize retired history while retaining an archive root that still reaches the exact sources.

## Durable linear execution

Each session has one ordered execution line and at most one open operation. The durable design is built around these rules:

- **Durable admission:** the user input and `operation_started` record commit before execution begins.
- **Append-only journal:** requests, stream deltas, usage, responses, queue changes, context stages, tool intents, and tool results are ordered events in SQLite.
- **Single writer:** one process owns the database, and one task runs a given session at a time; different sessions may run asynchronously.
- **Explicit recovery:** restart discovers unfinished operations without executing them. The host must explicitly resume or abort.
- **Safe tool recovery:** a tool intent commits before the external effect. An unknown result is replayed only when both the stored policy and the currently registered tool declare the operation safe to replay.
- **Atomic boundaries:** a completed model response is committed with its assistant message; a tool result is committed with its page-in record; a semantic rebase commits its archive, stage, and operation completion together.
- **Bounded retries:** model attempts are persisted before the request, so a crash cannot reset the attempt limit.
- **Durable queues:** `steer` is consumed at the next checkpoint, `follow_up` at the end of the current answer, and `next_run` when the next operation starts.
- **Close is not abort:** closing the runtime preserves unfinished work for recovery; abort records cancellation intent before stopping execution.
- **Deterministic testing:** manual drive mode places every write, model call, tool execution, hook, and timer behind an explicit effect gate for crash-prefix tests.

The journal is the recovery source of truth. It does not provide exactly-once guarantees for arbitrary external side effects; unsafe or uncertain tool effects are surfaced instead of being blindly repeated.

## Included capabilities

- OpenAI-compatible Chat Completions streaming, including tool calls, reasoning content, and provider-reported usage
- Ollama and llama.cpp presets, plus an offline demonstration provider
- Workspace-scoped `read`, `glob`, `grep`, `write`, `edit`, `bash`, and `calculate` tools
- Read-before-edit enforcement, session permission modes, one-time approvals, and opt-in parallel read-only tools
- Request snapshots, source inspection, context-zone traces, cache metrics, and execution timelines
- Four context policies and a reproducible Context Arena for mechanism-level comparison
- Optional direct MAGI Memo search adapter for long-term Episode and Atom retrieval

## Quick start

MAGI Harness requires Python 3.11 or newer.

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -e .
./server
```

Open <http://127.0.0.1:34914>. The default provider is an offline demo and does not consume model credits. Independent checkouts store runtime data in `~/.magi-harness/`; use `--data-dir`, `--db`, or `MGH_DATA_DIR` to choose another location.

`./server` is the repository-local Web server entrypoint. It runs `python -m mgh` from the project virtual environment and forwards command-line options:

```bash
./server --port 8080
./server --data-dir /absolute/path/.magi-harness
MGH_DATA_DIR=/absolute/path/.magi-harness ./server
```

The equivalent installed entrypoint is `magi-harness`. To use the interactive terminal client instead of the Web UI, add `--cli`:

```bash
./server --cli
```

The service binds to loopback only. Provider credentials are stored with user-only permissions and are not returned by the settings API or written to traces.

To use a compatible provider:

```bash
export LLM_BINDING='openai'
export LLM_BINDING_HOST='https://provider.example/v1'
export LLM_BINDING_API_KEY='your-key'
export LLM_MODEL='your-model'
./server
```

## Python embedding

```python
from mgh import ContextConfig, Harness, Store
from mgh.provider import CompatibleProvider

store = Store('/absolute/path/context.db')
provider = CompatibleProvider('model-name', 'https://provider.example/v1', 'api-key')
harness = Harness(store, provider)

with store.writer():
    harness.recover()
    session = harness.create(ContextConfig())
    result = await harness.run(session, 'Inspect the workspace and summarize the constraints.')
    await harness.close()

store.close()
```

Custom tools are registered explicitly with `Tool(name, description, parameters, async_callable)`. A tool's replay declaration is a host promise, not an inference made by the Harness.

## Architecture

| Module | Responsibility |
| --- | --- |
| `runtime.py` | Public `Harness` API, admission, authorization, and turn lifecycle |
| `durable.py` / `reducer.py` | Recoverable model/tool loop, queues, retry and replay decisions, journal validation |
| `context.py` / `compaction.py` | Four-zone compilation, budgets, transitions, page-in, and semantic rebase |
| `store.py` | SQLite sessions, append-only events, immutable sources, and open-operation projection |
| `provider.py` / `tools.py` | Provider protocol and workspace tool boundary |
| `effects.py` / `hooks.py` | Deterministic effect gates, interception hooks, and passive observation |
| `web.py` / `__main__.py` | Local Web, CLI, settings, and process lifecycle |
| `arena.py` / `tokenizer.py` | Context-policy evaluation and optional token estimation |
| `memo.py` | Optional long-term memory search adapter |

More detailed contracts are documented in [Architecture](docs/architecture.md), [Durable coverage](docs/durable-coverage.md), and [Memo context boundary](docs/memo-context-contract.md).

## Verification

```bash
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
bun install --frozen-lockfile
bun test
bun run check
.venv/bin/python -m mgh.arena --output /tmp/magi-arena
```

The automated suite covers context projection, recovery prefixes, retry limits, queues, tool uncertainty, compaction, parallel read tools, HTTP behavior, and static UI interactions. It does not replace real-provider compatibility tests or browser-based visual validation.

## Current scope

MAGI Harness intentionally implements one linear conversation per session with one SQLite backend. Conversation trees, lanes, navigation transactions, multi-backend parity, distributed writers, and automatic promotion into long-term memory are outside the current implementation. The built-in shell tool is approval-gated but is not an operating-system sandbox.
