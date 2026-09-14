# MAGI Harness 架构与进展

更新：2026-09-14。本文描述实际 Python 实现；项目进度指 **MAGI Harness**，不代表整个 MAGI Memo 仓库。tree/lanes 暂不纳入当前交付目标。

本轮交互增量：Web 运行中支持 steer/follow_up/next_run 追加、待处理队列与取消，以及显式压缩入口；暂停追加不会自动 resume。只读工具可显式设置 `parallel=True`，默认 read/glob/grep/calculate 启用，写入、shell、context_read 仍串行。并发批次之间保留顺序屏障，manual drive 仍串行便于确定性测试。工具并发与安全重放是独立配置。

新会话默认提示词加强了先读后判断、实际执行和结果验证要求；既有会话配置不自动替换。本轮未打开浏览器、未调用真实模型。自动语义回读和请求快照物理去重仍未实现。

## 1. 一句话定位

一个本地、单线会话的可恢复 Agent 运行时：**Harness 决定如何执行，Context Compiler 决定模型看什么，Store 保存发生过什么，Memo 提供长期记忆检索。**

不是 Pi v2 的完整移植，也不是 MAGI Memo 的新查询模式。

## 2. 分层

```text
Web / CLI / Python 嵌入
           │
         Harness ─── Hooks / Watch
           │
     DurableRuntime ─── Effects（自动执行 / 手动测试门）
       │       │
       │       └── Provider / Tools ─── 文件工作区、Memo.search
       │
  ContextCompiler
       │
      Store：SQLite journal + exact sources + open-operation projection
```

| 层 | 模块 | 职责与边界 |
|---|---|---|
| 宿主 | `web.py`、`__main__.py` | 启动、设置、会话 API、对话与 Trace；Web 为静态 JS，无前端构建 |
| 执行入口 | `runtime.py` | 创建会话、接受输入、工具授权、Turn 收尾、恢复入口 |
| 可恢复循环 | `durable.py`、`reducer.py` | attempt、队列、取消、恢复与日志前缀校验；reducer 尚不是唯一状态机 |
| 执行与观察 | `effects.py`、`hooks.py` | 副作用门、4 个 hook 点、隔离失败的被动订阅 |
| 上下文 | `context.py`、`compaction.py`、`tokenizer.py` | 四区投影、预算、Stage 迁移、显式语义 rebase |
| 持久化 | `store.py` | 有序事件、内容寻址原文、事务与恢复索引；目前只有 SQLite |
| 外部能力 | `provider.py`、`tools.py`、`memo.py` | 模型流、工具定义与参数基础校验、Memo 直连适配 |
| 评估 | `arena.py` | 四策略机制探针、逐请求 trace、质量与预算门禁 |

## 3. 数据模型

- **Workspace**：存储隔离标识；配置中的文件工作区路径另外约束文件工具的访问范围。
- **Session**：一条线性对话及其配置。没有 parent/branch/lane，整个 session 的有序消息是上下文候选。
- **Operation**：一次 run 或 compaction；每个 session 最多一个未完成 operation。
- **Turn**：一次正常 run 的对话周期，可含多次模型调用和工具执行；不是严格照搬 Pi 的 Turn 定义。
- **Event**：带 `seq/kind/turn/ref/created` 的追加日志。消息、请求快照、队列、usage、Stage 和执行控制记录共用事件表。
- **Source**：不可变 JSON，引用为 `ctx://v1/<scope>/<hash>`；按 workspace/session 隔离，读取校验 hash。
- **Stage**：上下文投影的版本；只改变模型可见表示，不删除原始历史。

SQLite 的 `sessions` 保存会话元数据，`sources` 保存内容，`events` 保存顺序，`operations` 保存当前未完成操作的索引。相关 event/source 与 operation 索引通过事务提交。`seq` 是数据库级递增值，允许间隔，不是树上的父子关系。

## 4. 一次执行如何流动

```text
输入 + operation_started 原子落盘
  → checkpoint 消费队列 / 应用 deferred writes
  → 编译上下文、检查最终请求预算
  → step_attempt / request 落盘
  → 模型流（delta 落盘）→ usage → response + message 原子落盘
  → 若有工具：校验 / hook / 授权 → intent 落盘 → 执行 → result 落盘
  → 下一次模型调用，或检查待处理输入后闭合 operation
```

文件写入受权限模式及 read-before-edit 限制；bash 需要批准。工作区路径检查不是 OS 沙箱，批准的 shell 命令不应被视为安全隔离的任意代码执行环境。

## 5. 四区上下文

| 区域 | 内容 | 生命周期 |
|---|---|---|
| Stable | 系统指令；工具 schema 确定排序 | 请求前缀的稳定部分 |
| Stubs | 较早 Turn 的导航摘录和原文引用 | 默认不是语义摘要 |
| Cold | 已闭合 Turn 的压缩表示，重工具结果保留引用 | 下次批量迁移进入 Stubs |
| Hot | 当前 Turn 与最近 k 个完整 Turn | 保留连续工作集，不拆开当前工具调用 |

请求顺序固定为 Stable → Stubs → Cold → Hot。每 n 个新闭合 Turn 批量迁移；`context_read` 临时恢复原文，同 Turn 去重，page-in 与工具结果一起提交。

默认预算是 UTF-8 bytes 加 framing 的代理值；可选 tokenizer 也是序列化估算，不等于 provider 实际计费。请求保存实际 payload，前缀复用估算不冒充服务端缓存命中。

显式 `compact()` 对可退休历史调用模型生成语义摘要，保留原文 archive root，并原子提交新 Stage。只支持 Four-Zone，单次摘要请求受预算限制；不是无限历史自动分层压缩。

## 6. Durable 的保证

- **恢复不自动执行**：新日志打开后返回 suspended；显式 resume 才继续。旧版无 operation 记录的未闭合 Turn 单独按 interrupted 收尾。
- **close ≠ abort**：close 保留未完成 operation；abort 先保存取消意图，再取消任务。
- **工具不盲重放**：已保存 intent、结果未知时，必须“历史声明 safe 且当前声明 safe”才重放；其他情况补未知结果。没有外部副作用 exactly-once 保证。
- **队列有明确语义**：steer 在 checkpoint 消费；follow_up 在收尾边界消费；next_run 留给下一次 run。独立 deferred writes 在 checkpoint 应用，取消时也保留。
- **重试有持久化上限**：崩溃不能重置 attempt cap；终止原因在恢复后保留。
- **可控测试**：manual drive 可以在副作用门前停止并重开数据库，检查 crash prefix；Watch 不参与执行决策。

一个服务进程持有数据库文件锁；不同 session 可异步运行，同一 session 不并行执行。直接调用 Store 绕过部分 Harness 防护，宿主必须遵守 single-writer 约定。

## 7. 与 Memo 的边界

Harness 保存短期 exact context、执行日志与四区状态；Memo 保存 Episode/Atom、语义索引与长期记忆。`memory_search` 调用已打开的 `MagiHandle.search`，读取不触发长期记忆写入。

当前 `contexts/harness.db` 是适配约定，不是已经接入 MagiRuntime 的 backend。共享生命周期、显式 promote、统一导出与 GC 尚未实现。详见 [Memo 边界](memo-context-contract.md)。

## 8. Pi v2 到底完成多少

**按完整设计广度粗估 40–50%；仅看单线 durable 执行子集约 65–75%。** 这是工程判断，不是通过条款数、代码行数或剩余工时比例；“有类似能力”不代表通过 Pi 的协议一致性测试。

| Pi v2 能力组 | 当前程度 |
|---|---|
| 输入 admission、operation journal、单 writer | 单线版本已实现 |
| close/abort、checkpoint、三类队列、安全工具恢复、attempt cap | 核心路径已实现并有回归；不等于完整竞态矩阵 |
| reducer、provisioned IDs、统一写失败 fault | 部分：reducer 主要做校验，ID 闭合和 fault 覆盖未完全统一 |
| manual drive、hooks、snapshot/watch | 部分：执行门可用，hook/event catalog 明显少于 Pi |
| compaction、overflow、deferred provider | 部分：显式有界 rebase；deferred 为自定义 provider 协议，非原生后台任务适配 |
| SessionTree、lanes、导航、fork/subagents | 未实现，本轮暂缓 |
| backend protocol、Memory/JSONL/SQLite parity、格式迁移导入导出 | 未实现；仅有自有 SQLite 实现 |
| typed telemetry、统一统计投影、完整 conformance 测试 | 未完成；已有 trace、usage 记录和局部回归 |

因此更准确的名称是“**吸收 Pi v2 durable 原则的单线 Harness**”，不是“Pi v2 已基本移植完”。

## 9. MAGI Harness 项目进展

若目标是“本地可用的单线 Agent + 可观测四区上下文 + 基础评估”，粗估 **70–80%**；若把完整 Pi v2 和生产级 Memo 集成都算进验收，则不能沿用这个比例。

| 工作流 | 进展 | 主要剩余 |
|---|---|---|
| 对话、工具、Web/CLI、兼容模型接口 | 已可用 | 真实模型联调、浏览器验收与故障体验打磨 |
| Four-Zone、exact sources、page-in、请求 trace | 核心已实现 | 长会话性能、投影元数据成本、自动分层压缩 |
| 单线 durable | 核心已实现，仍需加固 | 统一 reducer/fault、ID 约束、更多竞态回归 |
| 基础 Arena | 已实现 | 在线多次试验、公平语义摘要 baseline、真实 cache/cost |
| Memo 集成 | 读取适配已实现 | 生命周期、显式长期记忆晋升、backend 协议 |
| 发布与运维 | 本地测试/构建可用 | 会话备份恢复、迁移验收、运行手册 |

当前复验：**64 项 Python 测试、31 项 jsdom 测试、Ruff 和 JS 语法检查通过**。它们不代表真实浏览器或在线模型验证；真实 Provider 联调仍是拆仓后的首要验收项。

Arena 上次 16 次运行的机制 gate 通过；Full History/Four-Zone 各通过 4 个场景，两个有损 baseline 各通过 1 个。Four-Zone 在这些短样本中更贵，尚无真实费用节省结论。报告见 [Context Arena](../artifacts/context-arena/report.md)。该报告生成于最近两处校验改动之前，不是本次重跑。

会话备份/恢复仅提出方案，代码尚未实现；不能计入已完成。本文按代码盘点，不是 Linear 工单状态刷新。下一轮应先补可靠性与评估闭环，再决定是否扩展树结构。
