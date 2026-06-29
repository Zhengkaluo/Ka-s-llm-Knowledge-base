# PLATFORMS.md — 跨平台运行说明

## 1. 文件用途

本文件说明本知识库框架如何在不同 AI 平台 / Agent 调用器中运行，包括 WorkBuddy、Cursor、CodeBuddy、Codex、Claude Code、普通聊天模型等。

本文件只负责**平台适配**，不重复定义知识库工作流、角色设定或笔记格式。相关职责分工如下：

| 文件 | 负责内容 |
|---|---|
| `SOUL.md` | 行为契约、权限规则、首次交互协议、项目结构 |
| `SKILL.md` | 知识库完整工作流定义 |
| `AGENTS.md` | 多 Agent 讨论的角色池、主题映射与发言规范 |
| `_schema.md` | 笔记 frontmatter、命名约定、模板规范 |
| `PLATFORMS.md` | 不同平台如何执行上述协议、能力差异与降级策略 |

本文件回答的问题是：

> 换一个 AI 平台后，如何尽量按同一套知识库协议执行？

---

## 2. 核心原则

- **核心逻辑属于知识库，不属于任何单一平台。** 工作流、权限、角色、格式应沉淀在 Markdown 文件中。
- **平台能力只做增强，不做核心依赖。** WorkBuddy 的 Skill、记忆、自动化、连接器可以提高效率，但不应成为唯一运行方式。
- **优先使用通用文件协议。** 可迁移内容应尽量采用 Markdown、普通文件、明确提示词和可读规则。
- **不同平台是运行宿主，不是不同知识库。** WorkBuddy、Cursor、CodeBuddy、Codex、Claude Code、普通聊天模型都应尽量执行同一套核心协议。
- **能力不足时明确降级。** 平台缺少文件读写、记忆、自动化、subagent、连接器时，按本文件的降级策略执行。
- **不要假设平台记忆可靠。** 重要规则写入核心文件，重要结论写入知识库或 `.workbuddy/memory/`，不要只留在某个平台的隐性记忆中。

---

## 3. 兼容级别

### Level 1：纯文本协议模式

适用于：

- 普通 ChatGPT / Claude 网页版；
- 不能直接读写本地文件的平台；
- 临时没有知识库目录访问权限的场景。

可执行能力：

- 用户手动粘贴核心规则、相关笔记或讨论片段；
- 执行问答、总结、概念辨析；
- 执行多 Agent 角色模拟；
- 生成可复制的 Markdown 草稿。

限制：

- 不能自动扫描 `topics/`；
- 不能直接写入知识库；
- 不能自动更新 `_discussions.md`；
- 不能提交 Git；
- 不能依赖 WorkBuddy 记忆、自动化或连接器。

### Level 2：文件代理模式

适用于：

- WorkBuddy；
- Cursor；
- CodeBuddy；
- Codex；
- Claude Code；
- 其他可读取/修改项目文件的 AI Agent 工具。

可执行能力：

- 读取 `SOUL.md`、`SKILL.md`、`AGENTS.md`、`_schema.md`；
- 检索 `topics/` 下的主题、笔记和讨论记录；
- 生成上下文包；
- 执行知识库工作流 A/B/C/G/D/E；
- 写入前生成预览；
- 用户确认后写入 Markdown 文件；
- 在支持命令执行的平台上检查 Git diff、准备提交。

限制：

- 自动化、长期记忆、连接器、真 subagent 能力取决于具体平台；
- 各平台权限模型不同，必须额外确认写入、删除、移动等危险操作边界；
- 不应默认拥有 WorkBuddy 的 Skill、记忆或自动化能力。

### Level 3：平台增强模式

适用于：

- WorkBuddy 自动化；
- 平台原生 Skill / Expert / Connector；
- 支持 subagent / task 编排的平台；
- 带长期记忆和任务调度能力的平台。

可执行能力：

- 每日知识库讨论自动化；
- 外部搜索、连接器和平台集成；
- 更强的任务编排；
- 可能支持真多 Agent 并行；
- 可将任务结果写入项目记忆或知识库。

限制：

- 平台依赖强；
- 换平台时需要重新配置；
- 不能把平台增强能力写成核心工作流的硬前提；
- 自动化任务逻辑应能用手动方式复现。

---

## 4. 平台能力矩阵

| 能力 | WorkBuddy | Cursor | CodeBuddy | Codex | Claude Code | 普通聊天模型 |
|---|---|---|---|---|---|---|
| 读取本地文件 | 强 | 强 | 强 | 强 | 强 | 无 |
| 修改本地文件 | 强 | 强 | 强 | 强 | 强 | 无 |
| 遵守项目 Markdown 协议 | 强 | 强 | 强 | 强 | 强 | 需手动粘贴 |
| 查询 `topics/` | 强 | 强 | 强 | 强 | 强 | 无 |
| 多 Agent 角色模拟 | 强 | 强 | 强 | 强 | 强 | 可行 |
| 真 Subagent / Expert | 中-强 | 视版本 | 视平台 | 中-强，视当前环境 | 强（原生 subagent + Workflow 编排） | 无 |
| 自动化任务 | 强 | 弱 | 视平台 | 视环境 | 弱 | 无 |
| 长期记忆 | 强 | 弱/无 | 视平台 | 弱/无 | 弱/无 | 平台内置但不可控 |
| 外部连接器 | 强 | 弱 | 视平台 | 视环境 | 弱 | 无 |
| Git 操作 | 可执行 | 可执行 | 可执行 | 可执行 | 可执行 | 无 |
| 推荐角色 | 主运行环境 | 文件维护/重构 | 项目代理执行 | 项目代理执行 / 多 Agent 检索与整合 | 项目代理执行 / 多 Agent 编排与整合 | 讨论草稿 |

说明：平台能力变化较快，本矩阵只作为运行预期，不作为永久能力声明。

---

## 5. 各平台启动方式

### WorkBuddy

推荐级别：Level 3。

适合：

- 完整知识库管理；
- 多 Agent 讨论；
- 讨论沉淀；
- 每日自动化；
- 本地文件读写；
- 与 Skill、记忆、连接器结合。

执行方式：

- 可通过全局 `knowledge-base` Skill 触发；
- 全局 Skill 只作为薄入口；
- 实际执行时读取当前 workspace 根目录的 `SOUL.md`、`_schema.md`、`SKILL.md`；
- 如涉及多 Agent 讨论，额外读取 `AGENTS.md`；
- 如涉及跨平台问题，读取 `PLATFORMS.md`。

注意：

- WorkBuddy 的记忆、自动化、连接器属于增强能力；
- 重要规则仍应写入项目 Markdown 文件；
- 写入知识库前必须遵守 `SOUL.md` 的预览和确认规则。

### Cursor

推荐级别：Level 2。

适合：

- 编辑和重构 Markdown 文件；
- 修改 `SKILL.md`、`AGENTS.md`、`PLATFORMS.md` 等方法论文档；
- 批量调整格式；
- 前端 / Android App 代码修改。

执行方式：

- 明确要求 Cursor 先读取 `SOUL.md`、`_schema.md`、`SKILL.md`；
- 多 Agent 讨论时额外读取 `AGENTS.md`；
- 任何写入前先展示修改方案或 diff；
- 用户确认后再修改。

注意：

- 不应假设 Cursor 有 WorkBuddy 记忆；
- 不应依赖 WorkBuddy 自动化；
- Cursor 更适合作为文件维护和工程修改环境，而不是唯一讨论宿主。

### CodeBuddy

推荐级别：Level 2。

适合：

- 项目级文件操作；
- 命令行检查；
- Git diff 审查；
- 结构化文档维护；
- 执行需要读写项目文件的知识库工作流。

执行方式：

- 进入知识库根目录后，先读取 `SOUL.md`、`_schema.md`、`SKILL.md`；
- 多 Agent 讨论时读取 `AGENTS.md`；
- 按 `SOUL.md` 权限规则执行预览、确认、写入；
- 如果平台支持任务列表或子 Agent，可作为增强能力使用，但不作为硬前提。

注意：

- 不同 CodeBuddy 环境的工具、权限和记忆能力可能不同；
- 以项目 Markdown 协议为准，不以平台默认行为为准。

### Codex

推荐级别：Level 2+。

适合：

- 全库检索、主题梳理和跨笔记综合；
- 按 `SOUL.md` / `SKILL.md` / `_schema.md` 执行知识库写入预览；
- 维护 `PLATFORMS.md`、`AGENTS.md`、`SKILL.md` 等协议文件；
- 修改和验证 `tools/scripts/` 等工程部分；
- 在支持 subagent 的 Codex 环境中，执行真 subagent 多 Agent 讨论。

执行方式：

- 进入知识库根目录后，先读取 `SOUL.md`、`_schema.md`、`SKILL.md`；
- 多 Agent 讨论时额外读取 `AGENTS.md`；
- 如涉及平台适配或迁移问题，读取 `PLATFORMS.md`；
- 写入前必须展示预览或 diff，等待用户确认；
- 如使用 subagent，主 Codex 负责任务拆分、结果收集、最终综合与写入预览。

注意：

- Codex subagent 没有 WorkBuddy Team Mode 那种显式 Team 容器；
- subagent 之间默认不互相共享结果，信息应由主 Codex 汇总；
- 讨论型 subagent 默认只读知识库，不直接写入；
- 代码修改型 subagent 必须分配清晰的文件范围，避免并行冲突；
- 不应把 Codex subagent 当作 WorkBuddy 自动化、长期记忆或连接器的替代品。

### Claude Code

推荐级别：Level 2+。

适合：

- 命令行式项目操作；
- 文件检索、批量修改、Git 差异检查；
- 按规则维护知识库核心文档；
- 代码和文档混合任务。

执行方式：

- 明确要求 Claude Code 遵守根目录 `SOUL.md`；
- 读取 `SKILL.md` 获取工作流；
- 涉及多 Agent 讨论时读取 `AGENTS.md`；
- 对写入操作必须先展示预览或 diff。

注意：

- 不默认具备 WorkBuddy 自动化和记忆；
- subagent 能力视运行环境而定；
- 如不能保证写入安全，降级为只生成补丁或草稿。

### 普通聊天模型

推荐级别：Level 1。

适合：

- 讨论草稿；
- 多 Agent 角色模拟；
- 观点整理；
- 笔记预览草稿；
- 临时问题分析。

执行方式：

- 用户手动提供必要上下文；
- 明确告诉模型不要假设能访问本地文件；
- 输出 Markdown 草稿，由用户手动复制到知识库。

限制：

- 不能自动扫描知识库；
- 不能写入文件；
- 不能提交 Git；
- 不能依赖项目记忆或自动化。

---

## 6. 降级策略

当平台能力不足时，按以下方式降级。

### 无法读取文件

要求用户手动提供：

- 相关 topic 的 `_overview.md`；
- 相关 `note-*.md` 片段；
- 相关 `_discussions.md` 片段；
- 如涉及多 Agent，提供 `AGENTS.md` 中相关角色定义。

输出时必须说明：当前分析基于用户提供片段，不能代表全库检索结果。

### 无法写入文件

只生成 Markdown 预览或补丁建议，由用户手动写入。

不得声称已经完成写入。

### 无法运行多 Agent

使用单模型角色模拟：同一模型按 `AGENTS.md` 中的角色顺序依次发言。

仍需遵守：

- 每次 3-5 个 Agent；
- 必含方法论审稿人；
- 必含主持人；
- 解释型 Agent 说明依据、边界和不确定性。

### 无法检索全库

要求用户提供候选 topic，或只基于当前提供材料讨论。

输出时标记：

```text
未完成全库检索，结论仅基于当前上下文。
```

### 无法提交 Git

输出建议提交范围和 commit message，由用户手动提交。

### 无法访问外部搜索或连接器

只基于本地知识库和用户提供材料分析。

涉及现实事件、新闻、网络热词时，必须提醒：外部材料未核实或未更新。

---

## 7. 维护规则

- 如果新增或修改核心工作流，优先更新 `SKILL.md`，再视情况更新本文件。
- 如果新增 Agent、角色发言格式或主题映射，优先更新 `AGENTS.md`，再视情况更新本文件。
- 如果新增平台或平台能力发生变化，只在本文件中增加或调整平台适配说明。
- 不要把完整工作流复制到本文件。
- 不要把平台私有能力写成通用要求。
- 不要把临时平台表现写成长期事实，除非已经多次验证。
- 本文件应保持轻量，目标是说明跨平台运行边界，而不是成为平台使用手册。

---

## 8. 多 Agent 跨平台策略

多 Agent 讨论不是某个平台的专属功能，而是由 `SKILL.md` 工作流 G 与 `AGENTS.md` 共同定义的知识库协议。

### 角色模拟模式

适用于所有平台。

同一模型依次扮演多个 Agent，按 `AGENTS.md` 的角色定义和 7 段式格式发言。

### 分阶段调用模式

适用于可读取文件的平台。

执行顺序：

1. 读取 `AGENTS.md`；
2. 判断话题类型；
3. 选择 3-5 个 Agent；
4. 读取对应 topic 的 `_overview.md`、相关笔记和 `_discussions.md`；
5. 生成讨论上下文包；
6. 各 Agent 发言；
7. 方法论审稿人检查；
8. 主持人综合；
9. 如需沉淀，知识库管理员给出归档建议。

### 真 Subagent 模式

适用于支持独立 subagent / expert / skill 的平台。

可将 `AGENTS.md` 中的角色映射为独立 subagent，但必须遵守同一套发言格式、主题读取规则和沉淀规则。

### 不变规则

无论平台如何实现，多 Agent 讨论都必须遵守：

- 每次选择 3-5 个 Agent；
- 至少 2 个解释型 Agent；
- 必含方法论审稿人；
- 必含主持人；
- 解释型 Agent 发言前读取或参考对应主题；
- 在「我依赖的依据」中列出「知识库关联」；
- 找不到直接关联时明确说明；
- 写入知识库前展示预览并等待用户确认。

---

## 9. 文件读写与权限差异

无论平台是否允许直接写文件，都必须遵守 `SOUL.md` 的权限规则。

### 可自由执行

- 读取文件；
- 列出主题；
- 搜索知识库；
- 总结、对比、分析知识库内容。

### 必须先预览并确认

- 新增笔记；
- 追加 `_discussions.md`；
- 更新 `_overview.md`；
- 新建主题；
- 修改 `SKILL.md`、`AGENTS.md`、`PLATFORMS.md` 等规则文件。

### 禁止或高风险操作

- 删除文件；
- 覆盖已有笔记；
- 修改已有笔记正文；
- 移动或重命名文件；
- 绕过用户确认直接提交。

如果目标平台没有可靠的预览/确认机制，则降级为只生成草稿或补丁，由用户手动写入。

---

## 10. 记忆、自动化与连接器的迁移边界

以下能力属于平台依赖层，不应成为核心工作流的唯一依据：

- WorkBuddy 记忆；
- WorkBuddy 自动化；
- WorkBuddy Skill 触发；
- 专家 / Expert；
- 连接器；
- 平台任务列表；
- 平台内置长期记忆；
- 平台原生 subagent。

迁移原则：

- 重要规则写入 Markdown 核心文件；
- 重要项目状态写入 `.workbuddy/memory/` 或知识库笔记；
- 自动化任务可以依赖平台，但任务逻辑应能手动复现；
- 连接器结果如需长期保存，应沉淀为普通 Markdown；
- 平台记忆可以辅助执行，但不能替代 `SOUL.md`、`SKILL.md`、`AGENTS.md`、`_schema.md`。

当迁移到其他平台时，优先迁移：

- Markdown 核心文件；
- `topics/` 内容；
- `_vault/_index.md`；
- 可复用脚本和工具说明。

不强求迁移：

- WorkBuddy 自动化配置；
- WorkBuddy 私有记忆；
- 已连接平台的连接器授权；
- 平台原生专家配置。

---

## 11. WorkBuddy Team Mode 多 Agent 讨论启动指南

本节说明在 WorkBuddy 中如何用 **Team Mode** 真正 spawn 独立 subagent 来执行知识库多 Agent 讨论，而不是单模型角色模拟。

### 适用场景

满足以下任一条件时，可以考虑使用 Team Mode：

- 话题较复杂，各角色的知识库检索量大；
- 需要让角色真正独立读取对应 topic，而不依赖主 Agent 共享上下文；

Team Mode **不适合**：简单快速的讨论，或只是想快速看一个多视角草稿时，直接用角色模拟模式（Level 1）更省时。

---

### Agent 工具的两种调用方式

WorkBuddy 的 Agent 工具有两种模式，分工不同：

| 调用方式 | 行为 | 适用场景 |
|---|---|---|
| **不带 `name`（同步 subagent）** | 同步阻塞，等 subagent 完成后返回结果 | 轻量只读操作：读取 topic、检索笔记、搜索知识库 |
| **带 `name`（异步 Team Member）** | 异步后台运行，通过 SendMessage 通信 | 真正的多 Agent 发言：每个角色独立上下文、独立知识库读取 |

核心原则：**读文件用同步 subagent；让角色真正独立发言用异步 Team Member**。

---

### 完整启动流程

#### 第一步：主 Agent 执行 G1-G2（单独进行，无需 Team）

主 Agent 先完成：
- 确认话题主题句与核心问题；
- 用同步 subagent 或直接检索相关 topic，形成上下文包；
- 列出 Agent 阵容（角色 + 每个角色要读取的 topic）。

#### 第二步：创建 Team

```
TeamCreate(team_name="knowledge-discussion-[话题缩写]")
```

例如：`knowledge-discussion-benjamin` / `knowledge-discussion-lu-zhishen`

#### 第三步：并行 spawn 解释型 Agent

对每个解释型角色同时 spawn（可并行）：

```
Agent(
  name="[角色英文名]",
  prompt="[见下方模板]",
  run_in_background=True,
  max_turns=15
)
```

**解释型 Agent spawn prompt 模板**：

```markdown
你是本次知识库多 Agent 讨论中的「[角色中文名]」。

## 本次讨论任务

话题：[主题句]
核心问题：[本次最关键要追问的问题]

## 你的角色职责

适用场景：[从 AGENTS.md 第 8 节复制该角色的适用场景]
核心任务：[从 AGENTS.md 第 8 节复制核心任务]
常问问题：[从 AGENTS.md 第 8 节复制常问问题]
禁止倾向：[从 AGENTS.md 第 8 节复制禁止倾向]

## 必须先读取的知识库文件

发言前，先读取以下文件（文件不存在时在依据中标注「未找到」）：
- 主 topic：`topics/[对应主题]/_overview.md`
- 相关笔记：`topics/[对应主题]/note-*.md`（最相关的 1-2 篇）
- 历史讨论：`topics/[对应主题]/_discussions.md`（最近 2-3 段）

如有备用关联主题（参考 AGENTS.md 第 6 节），视情况补充读取。

## 发言格式（7 段式，三项硬约束不得省略）

### 1. 我看到的核心问题
### 2. 我的解释路径
### 3. 我依赖的依据

**知识库关联**：
- `topics/...md`：关联理由……（找不到时写「未找到直接关联笔记」）

**本轮材料 / 外部材料**：……

**推测或不确定处**：……

### 4. 我能解释的部分
### 5. 我解释不了的部分
### 6. 我对其他视角的提醒或质疑
### 7. 如果写入知识库，我建议保守表述为

## 完成后

发言完毕后，立即用 SendMessage 向 main 回传完整发言内容。

## Turn 预算

本任务配置 `max_turns=15`。
优先完成发言，完成后立即 SendMessage 回传，不做额外探索。
```

**角色名称与 spawn name / 主 topic 对应表**（参考 `AGENTS.md` 第 6 节）：

| 角色中文名 | 建议 spawn name | 优先读取 topic |
|---|---|---|
| 文本细读者 | `close-reader` | `literary-theory` |
| 文学理论家 | `literary-theorist` | `literary-theory` |
| 社会学家 | `sociologist` | `sociology` |
| 认知心理学家 | `cog-psychologist` | `cognitive-psychology` |
| 哲学概念分析者 | `philosopher` | `philosophy` |
| 历史学家 | `historian` | `history`, `chinese-history` |
| 史学理论者 | `historiographer` | `history` |
| 人类学家 | `anthropologist` | `ethnicity-and-culture`, `food-and-culture` |
| 传播学家 | `communication-scholar` | `communication` |
| 音乐史研究者 | `music-historian` | `music-history` |

等待所有解释型 Agent 回传后，再进入下一步。

#### 第四步：spawn 方法论审稿人

收集所有解释型 Agent 的发言后，spawn 方法论审稿人：

```
Agent(
  name="methodologist",
  prompt="[见下方模板]",
  run_in_background=True,
  max_turns=15
)
```

**方法论审稿人 prompt 要点**：

```markdown
你是本次讨论的「方法论审稿人」。

以下是各解释型 Agent 的发言：

[粘贴所有解释型 Agent 的 SendMessage 回传内容]

你的任务（至少指出以下每项一个问题）：
1. 哪个判断证据不足？
2. 哪里存在概念混用或过度解释？
3. 哪里需要回到原文或材料核实？
4. 对每个可疑判断给出保守表述建议。

禁止只附和，禁止只给正面评价。

完成后 SendMessage 向 main 回传审稿意见。

## Turn 预算
max_turns=15。完成后立即回传。
```

#### 第五步：spawn 主持人

方法论审稿人回传后，spawn 主持人：

```
Agent(
  name="moderator",
  prompt="[见下方模板]",
  run_in_background=True,
  max_turns=15
)
```

**主持人 prompt 要点**：

```markdown
你是本次讨论的「主持人」。不新增观点，只做综合。

以下是本次讨论的所有发言：

[解释型 Agent 发言 + 方法论审稿人意见]

输出以下五项：
1. 各 Agent 的共同点
2. 主要分歧
3. 最有价值的解释路径
4. 目前最不稳的判断
5. 建议下一轮追问方向

完成后 SendMessage 向 main 回传综合结论。

## Turn 预算
max_turns=15。完成后立即回传。
```

#### 第六步：询问用户是否继续或沉淀

主持人回传后，主 Agent 向用户展示综合结论，询问：

- 单次总结（进入 G7 沉淀）；
- 多轮延展（只保留 2-3 个角色继续）；
- 回到原文材料检索。

#### 第七步：如需沉淀，spawn 知识库管理员

```
Agent(
  name="kb-manager",
  prompt="...",
  run_in_background=True,
  max_turns=10
)
```

知识库管理员输出 G7 沉淀建议（归入哪个 topic / 写入 `_discussions.md` / 发展为正式笔记 / 待验证标记），**展示预览后等待用户确认才写入**。

#### 第八步：清理 Team

```
TeamDelete(team_name="knowledge-discussion-[话题缩写]")
```

---

### 快速示例：本雅明讨论阵容

```markdown
## 阵容确认

团队名：knowledge-discussion-benjamin

spawn 三个解释型 Agent（并行）：
- literary-theorist（文学理论家）→ 读 literary-theory
- communication-scholar（传播学家）→ 读 communication
- cog-psychologist（认知心理学家）→ 读 cognitive-psychology

收到三个回传后，spawn：
- methodologist（方法论审稿人）→ 审查三个发言

收到审稿后，spawn：
- moderator（主持人）→ 综合五项输出

询问用户是否沉淀，如需沉淀：
- kb-manager（知识库管理员）→ G7 归档建议

完成后 TeamDelete。
```

---

### 注意事项

- **并行 spawn 时**：每个 member 的 prompt 必须注明「与其他角色并行，不修改任何文件」；
- **max_turns 不得低于 15**；讨论型角色通常 15 就够，话题需大量检索时可设 20；
- **顺序约束**：解释型 Agent 可并行；方法论审稿人必须等解释型回传后启动；主持人必须等审稿人回传后启动；
- **写入知识库前**：无论用哪种模式，必须展示预览，等待用户确认，遵守 `SOUL.md` 权限规则；
- **Team Mode 不强制**：如果话题简单或希望快速讨论，直接用角色模拟模式（Level 1）更省时。

---

## 12. Codex Subagent 多 Agent 讨论启动指南

本节说明在 Codex 中如何用 subagent 执行知识库多 Agent 讨论。Codex 的 subagent 可以是真正独立运行的代理，但通常没有 WorkBuddy Team Mode 的显式 Team 容器，因此由主 Codex 负责调度、收集和综合。

### 适用场景

满足以下任一条件时，可以考虑使用 Codex subagent：

- 话题较复杂，需要多个角色分别读取不同 topic；
- 需要并行检索多个主题，减少主上下文压力；
- 希望方法论审稿人与解释型 Agent 相对独立；
- 需要让某个 subagent 专门做代码审查、材料检索或格式检查。

不适合：

- 简单快速讨论；
- 用户只想要一个轻量多视角草稿；
- 需要立即连续追问、频繁来回调整的短对话。

### Codex Subagent 的基本结构

```text
主 Codex
  ├─ subagent：解释型 Agent A
  ├─ subagent：解释型 Agent B
  ├─ subagent：解释型 Agent C
  └─ subagent：方法论审稿人 / 主持人（可选）

主 Codex 收集结果后：
  1. 综合各角色发言；
  2. 检查是否符合 `AGENTS.md`；
  3. 向用户展示结论；
  4. 如需沉淀，生成写入预览并等待确认。
```

### 推荐流程

1. 主 Codex 先执行 G1-G3：确认话题、读取上下文、选择阵容；
2. 并行启动 2-3 个解释型 subagent；
3. 每个解释型 subagent 只读取自己对应的 topic，并按 `AGENTS.md` 的 7 段式输出；
4. 主 Codex 收集解释型发言；
5. 可再启动方法论审稿人 subagent，专门检查证据、概念和边界；
6. 主 Codex 执行主持人综合，或启动主持人 subagent 后再由主 Codex 复核；
7. 如需沉淀，主 Codex 生成 `_discussions.md` 预览，等待用户确认后写入。

### Prompt 模板

```markdown
你是本次知识库多 Agent 讨论中的「[角色中文名]」。

本次话题：[主题句]
核心问题：[核心问题]

请先读取：
- `AGENTS.md` 中你的角色定义；
- `topics/[主 topic]/_overview.md`；
- `topics/[主 topic]/_discussions.md`；
- 最相关的 1-2 篇 `note-*.md`。

要求：
- 不修改任何文件；
- 不代表其他 Agent 发言；
- 严格按 `AGENTS.md` 的 7 段式输出；
- 在「我依赖的依据」中列出具体知识库路径；
- 找不到直接关联时，明确写「未找到直接关联笔记」；
- 标出推测、不确定处和解释边界。
```

### 注意事项

- Codex subagent 适合并行检索和独立分析，但最终沉淀权应保留在主 Codex；
- 写入知识库前必须展示预览并等待用户确认；
- 如果 subagent 用于代码修改，必须明确写入范围，并提醒不要回滚其他人的改动；
- 如果当前 Codex 环境没有 subagent 工具，则降级为角色模拟模式或分阶段调用模式；
- Codex subagent 是平台增强能力，不应成为知识库核心工作流的硬前提。

---

## 13. Claude Code 多 Agent 讨论启动指南

本节说明在 Claude Code 中如何执行知识库多 Agent 讨论。Claude Code 的 subagent 是真正独立运行、拥有独立上下文窗口的代理，没有 WorkBuddy Team Mode 的显式 Team 容器，由主 Claude 负责调度、收集和综合。它额外提供 Workflow 确定性编排能力，适合把固定讨论流程写成可复现脚本。

### 适用场景

满足以下任一条件时，可以考虑使用 Claude Code subagent：

- 话题较复杂，需要多个角色分别读取不同 topic；
- 各角色检索量大，希望独立上下文避免污染主对话窗口；
- 希望方法论审稿人与解释型 Agent 相对独立；
- 需要把「解释型 → 审稿 → 主持」的固定流程做成可复现编排。

不适合：

- 简单快速讨论；
- 用户只想要一个轻量多视角草稿；
- 需要频繁来回追问的短对话。

### 两种实现路径

| 路径 | 工具 | 行为 | 适用 |
|---|---|---|---|
| **即兴调度模式** | `Agent`（可并行 spawn） | 主 Claude 自行决定 spawn 哪些角色、何时收集 | 一次性讨论，结构与 Codex subagent 基本一致 |
| **确定性编排模式** | `Workflow`（JS 脚本） | 用脚本固定「并行解释型 → 审稿人 → 主持人」顺序 | 流程固定、希望可复现、角色数较多 |

核心原则：**读文件 / 独立分析用 `Agent` subagent；固定多阶段流程用 `Workflow`；命名 + `SendMessage` 用于需要持续往返的队友。**

### 即兴调度模式流程

1. 主 Claude 先执行 G1-G3：确认话题、读取上下文、选择 3-5 个角色阵容；
2. 在一条消息内并行 spawn 解释型 subagent（每个只读自己对应的 topic）；
3. 主 Claude 收集各解释型发言；
4. 再 spawn 方法论审稿人 subagent，专门检查证据、概念、边界；
5. 主 Claude 执行主持人综合（或 spawn 主持人后由主 Claude 复核）；
6. 如需沉淀，主 Claude 生成 `_discussions.md` 预览，等待用户确认后写入。

### 确定性编排模式（Workflow）

把固定流程写成脚本，顺序约束由代码保证，不依赖模型自觉。解释型角色之间无依赖用并行（`parallel`）；审稿人必须等全部解释型回传后启动（屏障）；主持人必须等审稿人之后。

下面是一段可直接套用的最小 Workflow 脚本示意（真实 JS，注意 `meta` 必须是纯字面量）：

```javascript
export const meta = {
  name: 'kb-multi-agent-discussion',
  description: '知识库多 Agent 讨论：并行解释型 → 方法论审稿人 → 主持人综合',
  phases: [
    { title: 'Explain', detail: '3-5 个解释型 Agent 并行发言' },
    { title: 'Review', detail: '方法论审稿人检查证据与边界' },
    { title: 'Moderate', detail: '主持人输出五项综合' },
  ],
}

// args 传入：{ topicSentence, coreQuestion, roles: [{ name, topic }] }
const { topicSentence, coreQuestion, roles } = args

// 阶段1：解释型 Agent 并行发言，各读自己对应的 topic
phase('Explain')
const speeches = (await parallel(roles.map(r => () =>
  agent(
    `你是本次知识库多 Agent 讨论中的「${r.name}」。
话题：${topicSentence}
核心问题：${coreQuestion}
先读取 AGENTS.md 中你的角色定义、topics/${r.topic}/_overview.md、
topics/${r.topic}/_discussions.md 及最相关的 1-2 篇 note-*.md。
不修改任何文件；严格按 AGENTS.md 的 7 段式输出；
在「我依赖的依据」中列出具体知识库路径；找不到关联时写「未找到直接关联笔记」。`,
    { label: `explain:${r.name}`, phase: 'Explain' }
  )
))).filter(Boolean)

// 阶段2：屏障——收齐全部发言后再 spawn 方法论审稿人
phase('Review')
const review = await agent(
  `你是本次讨论的「方法论审稿人」。以下是各解释型 Agent 的发言：\n\n${speeches.join('\n\n---\n\n')}\n\n` +
  `至少指出：哪条判断证据不足、哪里概念混用或过度解释、哪里需回原文核实，并给出保守表述建议。禁止只附和。`,
  { label: 'review:methodologist', phase: 'Review' }
)

// 阶段3：主持人综合，不新增观点
phase('Moderate')
const summary = await agent(
  `你是本次讨论的「主持人」，不新增观点，只做综合。以下是全部发言与审稿意见：\n\n` +
  `${speeches.join('\n\n---\n\n')}\n\n【审稿意见】\n${review}\n\n` +
  `输出五项：1 共同点 2 主要分歧 3 最有价值的解释路径 4 目前最不稳的判断 5 下一轮追问方向。`,
  { label: 'moderate', phase: 'Moderate' }
)

// 沉淀权保留在主 Claude：返回结果由主 Claude 生成 _discussions.md 预览，等用户确认
return { speeches, review, summary }
```

主 Claude 拿到 `return` 的结果后，再按 `SKILL.md` 工作流 G7 生成 `_discussions.md` 写入预览，等待用户确认——**Workflow 本身不写知识库**。

### 注意事项

- Claude Code subagent 拥有独立上下文，子 agent 的大量检索不进入主窗口，但**子 agent 之间默认不互相共享结果**，信息由主 Claude 汇总；
- **最终沉淀权必须保留在主 Claude**：写入知识库前展示预览、等待用户确认，子 agent / Workflow 默认只读，绝不下放写入操作（否则绕过 `SOUL.md` 的预览确认机制）；
- 代码修改型 subagent 必须分配清晰的文件范围，避免并行冲突；需要并行改文件时可用 worktree 隔离；
- Workflow 是平台增强能力，不应成为知识库核心工作流的硬前提；环境不支持时，降级为即兴调度模式，再不行降级为单模型角色模拟（Level 1）。
