# _changelog/ — 知识库统一操作日志

> 跨平台、跨 Agent 的**结构化操作账本**。任何 AI agent（WorkBuddy / Claude Code /
> Cursor / Codex / CodeBuddy 等）在对知识库执行写操作后，必须在此追加一条记录。

## 这一层记什么

记录"**做了什么**"——增、删、改了哪个文件。它回答的问题是：

> 这个知识库被谁、在什么时候、对哪个文件、做了什么改动？

目的：让主人和所有 agent 在**同一个地方**看到全部操作历史，不必去翻各平台
私有的、格式各异的记忆。

## 两层记忆模型（重要）

知识库的记忆分为两层，职责严格分开：

| 层 | 记什么 | 维护者 | 是否共享 |
|----|--------|--------|----------|
| **`_changelog/`（本层）** | What：精简、结构化的操作账本（增/删/改了哪个文件） | **所有 agent** | ✅ 跨平台共享 |
| 各平台私有 memory | Why / How：叙事过程、思考、平台特定细节 | 各平台自己 | ❌ 互不干预 |

各平台的私有 memory 举例：

- WorkBuddy：`.workbuddy/memory/YYYY-MM-DD.md`（叙事工作日志）+ `MEMORY.md`（长期项目状态）
- Claude Code / Codex / 其他：各自的 memory 机制

### 互不干预原则

- 每个平台维护**自己**的私有 memory，可以详尽、可以是平台特定格式；
- **agent 不得读写、修改或清理其他平台的私有 memory**（在 Codex 里不碰 WorkBuddy 的记忆，反之亦然）；
- 跨平台唯一的共享渠道就是 `_changelog/`；
- 因此每个平台干完活，除了维护自己的私有 memory，**还有义务把工作内容的精简版同步进 `_changelog/`**。

> `_changelog/` 不替代各平台私有 memory，只补充一层统一、可检索、谁都能看的操作账本。

## 文件组织

- 按月一个文件：`_changelog/YYYY-MM.md`（如 `2026-06.md`）
- 月内按天用 `## YYYY-MM-DD` 分组，最新日期追加在文件**底部**
- **Append-only**：只追加新行，永不改写或删除已有条目（与 SOUL.md 红线一致）

## 条目格式

每条操作一行：

```
- `HH:MM` **[action]** (agent) `目标路径` — 一句话摘要
```

- 一次操作涉及多个文件 → 每个文件单独一行；同类批量操作可合并为一条并在摘要里说明数量
- `目标路径`：相对知识库根目录的路径；批量/目录级操作可写到目录
- 摘要：中文，一句话说清改动
- **时间戳可选**：无法确定时间时（如历史回填）省略，格式降为
  `- **[action]** (agent) \`目标路径\` — 摘要`

### action 枚举

| action | 含义 |
|--------|------|
| `add` | 新增文件 |
| `update` | 修改 / 追加已有文件（含 bug 修复） |
| `delete` | 删除文件（默认禁止，如确实发生必须如实记录） |
| `move` | 移动 / 重命名 |
| `discuss` | 讨论沉淀到 `_discussions.md` 或追加进笔记 |
| `config` | 配置 / 工具 / 协议文件（SOUL/SKILL/AGENTS/PLATFORMS 等）变更 |
| `other` | 其他 |

### agent 枚举

`workbuddy` / `claude-code` / `cursor` / `codex` / `codebuddy`（按实际平台填写）

## 何时写

- **任何**对知识库的写操作完成后**立即**追加（新增笔记、追加讨论、更新概览、
  存入 vault 材料、修改协议文件等）；
- 该日志追加是**已确认写操作的自动副作用**，本身**无需再次向用户确认**；
- 纯读取 / 查询 / 搜索 / 未产生文件写入的讨论**不记录**（那属于各平台私有叙事层）。

## 示例

```markdown
## 2026-06-24

- `15:40` **[config]** (claude-code) `_changelog/` — 新建统一操作日志系统
- `16:10` **[add]** (workbuddy) `topics/music-history/note-book-xxx.md` — 新增《XXX》书籍笔记
- `16:25` **[discuss]** (workbuddy) `topics/philosophy/_discussions.md` — 沉淀本雅明多 Agent 讨论
```

---

*本文件是 `_changelog/` 层的协议规范。实际操作记录按月存放在 `_changelog/YYYY-MM.md`，
并已通过 `.gitignore` 默认排除（属于你的个人操作历史，可按需自行纳入版本库）。*
