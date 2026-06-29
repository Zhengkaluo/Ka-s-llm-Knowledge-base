# Vault Ingest — 原始材料加工与 LLM 友好副本

## 能力说明

本 tool 负责处理 `_vault/` 内的原始材料，将 PDF / EPUB / MOBI 等书籍资源加工成 LLM 更容易读取的 Markdown 副本，并生成质量报告。

核心定位：**原始材料层处理，而不是知识笔记层处理**。

也就是说，本 tool 只处理 `_vault/` 内的材料和派生文件，不自动修改 `topics/` 下的正式笔记。

## 触发条件

以下情况时使用此能力：

- 用户希望让 LLM 更方便读取 `_vault/books/` 里的电子书
- 用户希望批量检查 PDF 是文字版还是扫描版
- 用户希望将 PDF / EPUB 转成 Markdown 供后续检索、讨论或笔记整理使用
- 用户希望知道某本书的转换质量、OCR 风险或是否适合给 LLM 阅读
- 用户要求“加工 vault 里的书”“生成 LLM 可读版本”“给 PDF 做体检”“把书转 Markdown”

## 处理边界

### 可以新增或更新

```text
_vault/extracted/books/
```

用于保存从 `_vault/books/` 派生出的长期副本：

```text
_vault/extracted/books/{book-slug}.md
_vault/extracted/books/{book-slug}.meta.json
_vault/extracted/books/{book-slug}.report.md
```

### 可以读取

```text
_vault/books/
_vault/_index.md
tools/pdf-ocr.md
tools/epub-reader.md
```

### 不自动修改

```text
topics/
topics/*/_overview.md
topics/*/_discussions.md
topics/*/note-*.md
```

如果用户后续希望把阅读结果整理成正式笔记，必须另走知识库笔记录入流程，先预览，再等待确认。

### 原件保护

- 不覆盖 `_vault/books/` 中的原始文件
- 不删除原始文件
- 不移动原始文件
- 不自动重命名原始文件
- 派生文件可重新生成，但需要在报告中保留来源路径和生成时间

## 推荐目录结构

```text
_vault/
├── books/
│   └── xxx.pdf
├── extracted/
│   └── books/
│       ├── xxx.md
│       ├── xxx.meta.json
│       └── xxx.report.md
└── _index.md
```

## 工具分工

| Tool | 负责内容 |
|------|----------|
| `book-finder.md` | 找书、下载、存入 `_vault/books/`、维护 `_vault/_index.md` |
| `pdf-ocr.md` | 判断 PDF 类型、说明 OCR 处理方式 |
| `epub-reader.md` | 临时读取 EPUB/PDF、临时搜索原文 |
| `vault-ingest.md` | 长期加工 `_vault` 材料，生成 Markdown、meta 和质量报告 |

## 脚本位置

```text
tools/scripts/vault-ingest/
└── vault_ingest.py
```

当前已实现第一阶段的 `inventory`、`inspect`、`inspect-all`，第二阶段的单文件 `extract`，以及安全批量 `extract-all`。脚本不会修改 `_vault/books/` 原件，不写入 `topics/`；提取命令只会在 `_vault/extracted/books/` 生成派生文件。

## 命令规划

第一阶段已实现体检，不做大规模转换：

```bash
# 查看 _vault/books/ 中现有书籍格式分布
python tools/scripts/vault-ingest/vault_ingest.py inventory

# 体检单个文件
python tools/scripts/vault-ingest/vault_ingest.py inspect "_vault/books/xxx.pdf"

# 批量体检 _vault/books/
python tools/scripts/vault-ingest/vault_ingest.py inspect-all
```

第二阶段已实现单文件提取：

```bash
# 将单本文字层 PDF 或 EPUB 提取为 Markdown，并生成 meta/report
python tools/scripts/vault-ingest/vault_ingest.py extract "_vault/books/xxx.pdf"
python tools/scripts/vault-ingest/vault_ingest.py extract "_vault/books/xxx.epub"
```

第二阶段也已实现安全批量提取：

```bash
# 只预演，不写入文件
python tools/scripts/vault-ingest/vault_ingest.py extract-all --dry-run

# 批量提取 PDF/EPUB，默认跳过已经存在的派生文件
python tools/scripts/vault-ingest/vault_ingest.py extract-all

# 只处理 EPUB
python tools/scripts/vault-ingest/vault_ingest.py extract-all --formats epub

# 覆盖已有派生文件
python tools/scripts/vault-ingest/vault_ingest.py extract-all --overwrite
```

第三阶段按需增加 OCR：

```bash
# 仅对用户明确指定的扫描版 PDF 做 OCR
python tools/scripts/vault-ingest/vault_ingest.py ocr "_vault/books/xxx.pdf"
```

## 格式处理策略

### EPUB

优先使用 `markitdown` 转换为 Markdown。

特点：

- 通常比 PDF 更适合 LLM 读取
- 没有固定页码
- 章节结构通常能保留
- 图片、脚注、尾注可能丢失或位置变化

输出质量报告中应标注：

```text
format: epub
page_anchor: unavailable
structure: chapter-based
```

### 文字版 PDF

优先使用 `pdfplumber` 或 `pypdf` 提取文字；也可以使用 `markitdown` 快速转换。

处理要求：

- 保留 PDF 页码锚点
- 每页内容单独分段
- 记录空页、短页、疑似乱码页
- 重要引用必须能回看原 PDF 页码

推荐 Markdown 格式：

```markdown
# 书名

<!-- source: ../books/xxx.pdf -->
<!-- extraction_type: text_layer_pdf -->
<!-- generated: YYYY-MM-DD -->

## Page 1

正文……

## Page 2

正文……
```

### 扫描版 PDF

第一阶段只检测，不默认 OCR。

如果检测为扫描版：

- 生成 `.report.md`
- 标记 `needs_ocr: true`
- 不生成正文 Markdown，或只生成空壳说明
- 提醒用户 OCR 需要额外确认

原因：

- OCR 慢
- 中文 OCR 依赖较重
- 识别结果可能错误较多
- 扫描质量差时不适合直接给 LLM 使用

### MOBI

第一阶段暂不直接处理。

如果遇到 `.mobi`：

- 在 inventory 中统计
- 在 inspect 中标记 `unsupported_needs_conversion`
- 建议后续通过 Calibre `ebook-convert` 先转 EPUB，再进入 EPUB 流程

## 质量指标

每次 inspect / extract 应尽量生成以下指标：

| 指标 | 含义 |
|------|------|
| `format` | pdf / epub / mobi |
| `pages` | PDF 页数，EPUB/MOBI 可为空 |
| `pdf_type` | text_layer / scanned / mixed / unknown |
| `text_coverage` | 有可提取文字的页比例 |
| `average_chars_per_page` | 平均每页字符数 |
| `empty_pages` | 空页或近似空页列表 |
| `short_pages` | 文本过短的页列表 |
| `garbled_ratio` | 乱码字符比例 |
| `suspect_pages` | 疑似问题页列表 |
| `status` | pass / pass_with_warnings / needs_ocr / failed |

## 质量等级

### A：可直接给 LLM 读

- 文字层稳定
- 文字覆盖率高
- 乱码率很低
- 页码连续
- 抽样对照基本无误

### B：可读，但引用需回看原页

- 正文基本完整
- 有页眉页脚、断行、脚注混乱等问题
- 可用于整体阅读和讨论
- 不应直接作为精确引文依据

### C：只能粗读

- OCR 或提取质量一般
- 存在较多错字、断裂段落、注释串行
- 适合概览，不适合精确引用

### D：不建议给 LLM 读

- 大量空页
- OCR 严重错误
- 页序错乱
- 双栏串行严重
- 文字覆盖率很低

## meta.json 建议格式

```json
{
  "source": "_vault/books/xxx.pdf",
  "output": "_vault/extracted/books/xxx.md",
  "format": "pdf",
  "pdf_type": "text_layer",
  "pages": 180,
  "text_coverage": 0.94,
  "average_chars_per_page": 720,
  "garbled_ratio": 0.003,
  "empty_pages": [1, 2],
  "short_pages": [3],
  "suspect_pages": [57, 103],
  "quality_grade": "B",
  "status": "pass_with_warnings",
  "generated_at": "YYYY-MM-DD"
}
```

## report.md 建议格式

```markdown
# 提取质量报告：书名

- 原文件：`_vault/books/xxx.pdf`
- 输出文件：`_vault/extracted/books/xxx.md`
- 文件格式：PDF
- PDF 类型：文字层 PDF
- 页数：180
- 文字覆盖率：94%
- 平均每页字符数：720
- 乱码率：0.3%
- 质量等级：B
- 状态：pass_with_warnings

## 疑似问题

- 空页：1, 2
- 短页：3
- 疑似问题页：57, 103

## 建议

可用于 LLM 阅读和检索；如需精确引用，必须回看原 PDF 页码。
```

## 正确性校验原则

Markdown 是 LLM 友好阅读副本，不是权威原文。

必须遵守：

1. 原始 PDF / EPUB 始终保留在 `_vault/books/`
2. Markdown 中保留来源路径和页码或章节锚点
3. 质量报告中列出问题页和风险等级
4. 精确引用、术语判断、页码引用必须回看原始材料
5. OCR 结果默认低于文字层提取结果，需要更严格抽样

## 抽样校验建议

对每本转换后的书，至少抽样检查：

- 前言/目录附近 1-2 页
- 正文开头 1-2 页
- 中间随机 3-5 页
- 注释、参考文献或索引附近 1-2 页
- 质量报告标记的 suspect pages

检查重点：

- 段落是否完整
- 页码是否对应
- 是否漏掉脚注
- 多栏文本是否串行
- 人名、地名、术语、外文是否误识别
- 破折号、引号、括号等标点是否异常

## 注意事项

- 所有写入仍受 `SOUL.md` 权限规则约束
- 新增工具文件、脚本文件或 `_vault/extracted/` 目录前，应向用户说明范围并获得确认
- 不自动把转换结果写入 `topics/`
- 不把 Markdown 副本当成最终笔记
- 不删除临时文件以外的任何材料
- 不把 OCR 结果当成可信原文
