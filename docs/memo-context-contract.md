# MAGI Harness / Memo 上下文存储边界

状态：2026-09-13，已形成 Harness-first 基线；Memo backend 与长期记忆晋升接口仍待实现。

## 当前决定

原始上下文持久化、Session journal、projection、page-in 和恢复语义属于 Harness。Harness 对自己实际发送给模型和交给工具的内容负有完整、可寻址、可审计的保存义务；它不能依赖一次可能失败、昂贵或带语义损失的长期记忆抽取，才能恢复正在运行的 Session。

Memo 继续负责 Episode / Atom、语义检索、图关系和长期反思。短期上下文只有经过显式 `promote` / episode commit / reflect 动作时才进入 Memo；普通消息、模型调用和 page-in 都不自动产生长期记忆。

物理存储可以演化：默认由 Harness 的 SQLite backend 完成，未来可以增加 Memo workspace backend，让数据库与 `.mgc` 放在同一 workspace、共享 lease/export/GC 生命周期。但 **Four-Zone 模型和 Context Compiler 始终由 Harness 所有**，不能下沉成 Memo 的 query mode。

读取 `src/interface/api.py` 后，当前 `MagiHandle` 提供 ingest / ingest_extracted / search / status / extension，但没有原始上下文 exact fetch、版本化 projection 或 append journal。把每轮上下文塞入 ingest 会混淆原文保存、语义抽取和查询生命周期，也引入不必要的 LLM/embedding 成本。

## 当前已实现

- `workspace_store(root, workspace_id)` 在 `contexts/harness.db` 保存 session / events / sources。
- `Store.put/get/get_many` 支持稳定 `ctx://v1/<scope>/<sha256>`、内容寻址、workspace + session 隔离、读取时 hash 校验。
- `Store.append/events` 保存有序原始事件；编译后的实际 provider payload 作为 request 事件保存。
- `memo_tools(handle)` 直接调用已存在的 `MagiHandle.search`；不经过 REST，不新增自动长期记忆写入。

这是实际可用的嵌入接口，但不是已经接入 MagiRuntime 的 Context backend。其数据库、关闭、迁移和 workspace 清理仍由宿主负责。

## Backend seam

Harness 后续应把当前 `Store` 收敛成窄的 backend protocol。调用面保持 Harness-owned；Memo 只需在未来提供可选实现：

```python
ref = await context_store.put(
    session_id, content, kind="tool_result", source_refs=[],
)
source = await context_store.fetch(ref)
sources = await context_store.fetch_many(refs)
seq = await context_store.append(
    session_id, event, expected_revision=revision,
)
await context_store.commit_projection(
    session_id, projection, expected_revision=revision,
)
```

| 能力 | 必须明确的语义 |
| --- | --- |
| put / fetch / fetch_many | immutable 内容、媒体类型、hash / version 校验；完整返回或显式失败 |
| session journal | 单 writer 或 revision CAS；输入 admission 原子提交；journal 不被摘要覆盖 |
| projection commit | 原始引用必须已持久化；stage 变更和 revision 原子提交 |
| provenance | source / loaded_from / derived_from / supersedes 分开；读取不是派生或写入 |
| workspace 生命周期 | 复用 Runtime lease；切换、drain、close、delete 时 Context store 同步参与 |
| 导出与备份 | 原始 sources + journal + projection 可整体导出、校验和恢复 |
| 留存与 GC | 被 journal、Stub、checkpoint 引用的原文不能回收；先设计引用根再引入删除 |

不建议把它包装成 `search(mode="ctx")`，也不建议初版创建新的四类 Core storage。精确 fetch、append journal 与版本化 projection 不是检索模式。

独立 checkout 与安装包的默认路径为 `~/.magi-harness/context.db`；仍处于 MAGI Memo 母仓且检测到既有 `sages/mgh-test/` 时继续沿用旧目录，避免现有会话不可见。可通过 `--data-dir`、`--db` 或 `MGH_DATA_DIR` 明确指定。Provider 设置保存在同目录的 `settings.json`，权限为当前用户读写。

## 尚待讨论和实现

1. **Memo backend 形态**：直接实现 Harness 的 backend protocol，还是在 `MagiHandle` 下暴露一层等价的低层 `context` surface。
2. **长期记忆晋升协议**：定义显式 promote/episode commit 的 payload、权限、幂等键和 provenance；不因每次 page-in 或模型调用自动抽取 Atom。
3. **原子 projection commit**：当前 SQLite 以事务追加 source + event；正式 backend 需要 revision CAS、snapshot root 和崩溃恢复测试。
4. **摘要质量**：当前 Stub 仅是可恢复摘录。后续需要独立 canonicalizer，明确约束、结论、副作用和未解决问题，并进行质量验证。
5. **留存与删除**：先定义 journal、Stub、checkpoint 和 Memo evidence 的引用根，再实现 GC 与 workspace 删除。

这些事项不阻塞当前 Harness 运行。正式跨 Session 授权、批量 page-in 预算及 Memory / Context Arena 在下一轮决策。
