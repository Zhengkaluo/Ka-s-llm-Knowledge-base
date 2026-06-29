# 平台入口文件说明

> 本框架在根目录放了一组**平台入口文件**。它们是同一套协议面向不同 AI 工具的"门牌"——
> 内容刻意保持一致，都只做一件事：**把 AI 引导到核心协议 `SOUL.md`**，绝不重复定义规则。

## 为什么有这么多看起来很像的文件？

不同的 AI 编码/agent 工具会**自动加载各自约定的入口文件**（文件名各不相同）。
为了让你无论用哪个工具打开这个知识库，AI 都能第一时间读到正确的协议，我们为主流工具各放了一个入口。

## 入口文件清单

| 文件 | 对应平台 | 加载方式 |
|---|---|---|
| `CLAUDE.md` | Claude Code | 自动加载 |
| `AGENTS.md` | Codex / OpenAI Codex CLI（及通用 agent 约定） | 自动加载（文件顶部含入口引导，同时也是多 Agent 角色池文档） |
| `GEMINI.md` | Gemini CLI | 自动加载 |
| `WARP.md` | Warp | 自动加载 |
| `WORKBUDDY.md` | WorkBuddy | 项目入口 |
| `CODEBUDDY.md` | CodeBuddy | 项目入口 |
| `.cursorrules` | Cursor | 自动加载 |
| `.windsurfrules` | Windsurf | 自动加载 |
| `.github/copilot-instructions.md` | GitHub Copilot | 自动加载 |

## 真正的规则在哪里？

入口文件都是**薄引导**。真正的协议在这几个核心文件里，所有平台共用：

- `SOUL.md` — 行为契约（权限规则、交互协议、首次交互自检）
- `SKILL.md` — 完整工作流
- `AGENTS.md` — 多 Agent 讨论角色池与发言格式
- `PLATFORMS.md` — 跨平台能力矩阵与降级策略
- `_schema.md` — 笔记格式规范

## 维护提示

- 修改协议时，**只改核心文件**，入口文件通常不用动（它们只是指针）。
- 如果你只用一两个平台，可以删掉用不到的入口文件，不影响框架运行。
- 新增一个平台支持时，复制任意一个入口文件，改掉标题和"运行定位"段落即可。
