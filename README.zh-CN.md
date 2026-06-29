# Markdown 知识库框架

> 一个 **AI-native** 的个人知识库框架：用纯 Markdown 文件，把"AI 该如何帮你采集、组织、讨论、沉淀知识"定义成**协议文件**，并且**跨 AI 工具可迁移**（WorkBuddy、Cursor、Claude Code、Codex、CodeBuddy，甚至普通聊天模型）。

[English](./README.md)

---

## 为什么做这个

大多数"AI + 笔记"方案一换工具就失效，而且很多人（合理地）担心 AI 乱改自己的笔记。这套框架同时解决这两点：

- **协议即代码**：AI 的行为契约写在 Markdown 文件里（`SOUL.md` / `SKILL.md` / `AGENTS.md` / `PLATFORMS.md` / `_schema.md`）。任何有能力的 AI 工具读了就知道怎么干，不依赖任何专有插件。
- **权限分级**：读取自由 · **写入前必须预览** · 删除/覆盖默认禁止。直击"AI 偷偷改了我的笔记"这一核心恐惧。
- **多 Agent 讨论协议**：13 个思考角色（文本细读者、社会学家、认知心理学家、方法论审稿人、主持人……），固定 7 段式发言格式 + 沉淀环节，把单个模型变成一个结构化的"讨论小组"。
- **生而跨平台**：为 5+ 种 AI 工具提供能力矩阵和降级策略，同一套协议到哪都能跑。

## 目录结构

```
.
├── SOUL.md          # 行为契约 —— 任何 AI 必须先读
├── SKILL.md         # 完整工作流（查询 / 录入 / 讨论 / 材料加工 …）
├── AGENTS.md        # 多 Agent 讨论的角色池与发言格式
├── PLATFORMS.md     # 同一套协议如何在不同 AI 工具上运行
├── _schema.md       # 笔记格式规范（frontmatter、命名约定）
├── _templates/      # 7 个笔记模板（书/播客/网页/视频/文章/通用 + 主题总览）
├── tools/           # 可选能力扩展（找书、OCR、材料加工 …）
├── _changelog/      # 跨平台共享的结构化操作日志协议
├── example/         # 一个完全虚构的示例主题，让你立刻看到效果
└── scripts/
    └── init-kb.py   # 一条命令初始化空知识库骨架
```

## 5 分钟上手

1. **获取框架**
   ```bash
   git clone <本仓库> my-knowledge-base
   cd my-knowledge-base
   ```
2. **初始化空骨架**
   ```bash
   python scripts/init-kb.py
   ```
3. **让你的 AI 接管**：用任意 AI 工具打开这个目录，对它说"读取 SOUL.md 并执行首次交互自检"。它会回显权限规则、格式规范、已加载的工作流和当前主题，然后等你的指令。
4. **录入第一条笔记**：粘贴一张截图或一段文字，说"存到知识库里"。AI 会自动推断来源类型、建议归入哪个主题，并在**写入前先给你看预览**。
5. **（可选）先看看 example/ 示例**，准备好后删掉 `example/` 目录，把它变成你自己的库。

## 适配你的 AI 工具

框架自带**主流 AI 编码/agent 工具的入口文件**，无论你用哪个工具打开这个目录，AI 都能第一时间读到正确的协议：

`CLAUDE.md` · `AGENTS.md`（Codex）· `GEMINI.md` · `WARP.md` · `WORKBUDDY.md` · `CODEBUDDY.md` · `.cursorrules`（Cursor）· `.windsurfrules`（Windsurf）· `.github/copilot-instructions.md`（Copilot）

这些都是薄指针，统一指向核心协议 `SOUL.md`。详见 [`PLATFORM-ENTRIES.md`](./PLATFORM-ENTRIES.md)。用不到的可以直接删，不影响运行。

## 一张表看懂核心

| 层 | 文件 | 回答什么问题 |
|---|---|---|
| 契约 | `SOUL.md` | AI 被允许做什么？ |
| 工作流 | `SKILL.md` | AI 怎么完成每项任务？ |
| 角色 | `AGENTS.md` | 多 Agent 讨论里谁来发言？ |
| 可迁移 | `PLATFORMS.md` | 换个 AI 工具怎么跑？ |
| 格式 | `_schema.md` | 一条合法笔记长什么样？ |

## 设计原则

- **核心逻辑属于知识库，不属于任何单一平台。**
- **平台能力只做增强，不做核心依赖。**
- **重要规则写进 Markdown**，不要只留在某个工具的隐性记忆里。
- **能力不足时明确降级**（见 `PLATFORMS.md`）。

## 隐私与安全

- 默认 `.gitignore` 已**排除你的内容层**（可选排除 `topics/`、排除 `_vault/` 材料、`.config/` 凭证、`_changelog/` 历史），避免误把私人笔记或密钥公开。
- 可选工具的凭证放在本地 `.env`（见 `.env.example`），永不入库。
- `SOUL.md` 的权限分级默认禁止删除与覆盖。

## 许可证

[MIT](./LICENSE) —— 随便用、随便改、可商用。署名欢迎但不强制。

---

*本框架抽取并泛化自一个个人 Markdown 知识库。`example/` 中的内容完全虚构，仅作演示。*
