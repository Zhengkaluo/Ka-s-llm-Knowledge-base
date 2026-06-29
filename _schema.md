# _schema.md — 知识库格式规范

> 本文件定义所有笔记文件的格式规范、命名约定和元数据字段。所有新建文件必须遵循此规范。

## 命名约定

### 文件夹命名

- 使用**英文小写 + 短横线**：`evolutionary-psychology/`、`attention-management/`
- 中文名称放在 `_overview.md` 的 `title` 字段中
- 避免空格、特殊字符、中文路径（Git 跨平台兼容性）

### 文件命名

| 文件类型 | 命名格式 | 示例 |
|---------|---------|------|
| 主题总览 | `_overview.md` | `_overview.md` |
| 讨论记录 | `_discussions.md` | `_discussions.md` |
| 书籍笔记 | `note-book-{slug}.md` | `note-book-the-selfish-gene.md` |
| 播客笔记 | `note-podcast-{slug}.md` | `note-podcast-lex-fridman-ep42.md` |
| 网络内容笔记 | `note-web-{slug}.md` | `note-web-zhihu-consciousness.md` |
| 视频笔记 | `note-video-{slug}.md` | `note-video-3b1b-linear-algebra.md` |
| 文章笔记 | `note-article-{slug}.md` | `note-article-atlantic-ai-essay.md` |
| 通用笔记 | `note-{slug}.md` | `note-random-thought-20260325.md` |
| 散记/杂记 | `note-misc-{slug}.md` | `note-misc-philosophy.md`（source_type: other，多来源碎片合集） |

- `{slug}` 使用英文小写 + 短横线，简短有意义
- 以 `_` 开头的文件为元文件（`_overview.md`、`_discussions.md`、`_index.md`）

## 来源类型枚举

| source_type | 含义 | 说明 |
|-------------|------|------|
| `book` | 书籍 | 纸质书、电子书、有声书 |
| `podcast` | 播客 | 音频播客节目 |
| `web` | 网络内容 | 知乎、微博、Twitter、Reddit 等社交平台帖子 |
| `video` | 视频 | B站、YouTube、抖音等视频内容 |
| `article` | 文章 | 独立博客文章、新闻报道、学术论文 |
| `other` | 其他 | 不属于以上分类的内容 |

## Frontmatter 字段规范

### 通用必填字段（所有笔记）

```yaml
---
title: string          # 笔记标题（中文）
topic: string          # 所属主题的目录名（英文，如 evolutionary-psychology）
source_type: enum      # book | podcast | web | video | article | other
source_title: string   # 来源标题（如书名、播客名、帖子标题）
created: date          # YYYY-MM-DD 创建日期
updated: date          # YYYY-MM-DD 最后更新日期
tags: list             # 标签列表，如 [进化, 心理学, 利他行为]
---
```

### 通用可选字段

```yaml
source_author: string  # 作者/主播/UP主
source_url: string     # 原始链接（URL）
source_date: date      # 原始发布/出版日期
vault_ref: string      # _vault/_index.md 中对应的材料 ID（如 V001）
```

### 书籍扩展字段

```yaml
isbn: string           # ISBN 号
chapter: string        # 章节名或章节号
page_range: string     # 页码范围（如 "42-58"）
```

### 播客扩展字段

```yaml
episode: string        # 期数（如 "EP42"）
guest: string          # 嘉宾
timestamp: string      # 关键时间戳（如 "12:30-15:00"）
```

### 视频扩展字段

```yaml
platform: string       # 平台（B站/YouTube/抖音等）
duration: string       # 时长
timestamp: string      # 关键时间戳
```

### 网络内容扩展字段

```yaml
platform: string       # 平台（知乎/微博/Twitter/Reddit 等）
```

## 主题总览 `_overview.md` 格式

```yaml
---
title: string          # 主题中文名称
slug: string           # 主题英文目录名
created: date          # 主题创建日期
updated: date          # 最后更新日期
status: enum           # exploring | developing | mature
related_topics: list   # 关联主题的 slug 列表
tags: list             # 标签
---
```

### status 枚举

| 值 | 含义 |
|----|------|
| `exploring` | 刚开始接触，笔记较少 |
| `developing` | 持续学习中，有一定积累 |
| `mature` | 已有较深入的理解和体系 |

## 讨论记录 `_discussions.md` 格式

按日期倒序排列，每次讨论一个区块：

```markdown
## YYYY-MM-DD 讨论标题

**触发话题**：简述讨论是如何开始的

**讨论要点**：
- 要点 1
- 要点 2

**新理解**：
一段话总结这次讨论后的新认识

**待深入**：
- 还没弄明白的问题

**学习素材**：（可选，仅在讨论中 AI 应用户要求提供了结构化参考资料时才写）

### 素材标题（如：时间线/对比表/概念梳理等）

讨论中 AI 提供的表格、时间线、知识梳理、推荐阅读等，保留原始格式直接放入。

---
```

## `_vault/_index.md` 链接映射表格式

```markdown
# 原始材料索引

| ID | 标题 | 类型 | 本地路径 | 外部链接 | 添加日期 | 备注 |
|----|------|------|----------|----------|----------|------|
| V001 | ... | book/video/... | 相对路径 | URL 或 - | YYYY-MM-DD | ... |
```

- **ID**：`V` + 三位数字递增（V001, V002, ...）
- **本地路径**：相对于 `_vault/` 的路径（如 `books/the-selfish-gene.pdf`）
- **外部链接**：有则填 URL，无则填 `-`

## 编码与通用规则

- 所有文件使用 **UTF-8** 编码
- 笔记中引用原始材料使用**相对路径**（如 `../../_vault/books/xxx.pdf`）
- 标签使用**中文**，方便日后检索
- 日期统一使用 **YYYY-MM-DD** 格式

---

*本文件是知识库的数据格式规范，不得被 AI agent 修改。如需修改，请由用户手动编辑。*
