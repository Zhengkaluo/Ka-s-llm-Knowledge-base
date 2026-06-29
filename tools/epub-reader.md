# epub-reader — 电子书读取与原文检索

## 能力说明

当需要读取书库（`_vault/books/`）中的 `.epub` 或 `.pdf` 文件，提取全文或搜索特定段落时，使用 `markitdown` 将文件一步转换为 Markdown，再进行文本搜索。

**适用场景**：
- 用户引用书中某段原文，需要找到上下文
- 需要定位某章节内容做笔记
- 需要了解书的目录结构

---

## 工具依赖

| 工具 | 安装命令 | 说明 |
|------|----------|------|
| markitdown | `pip install markitdown` | 核心转换工具，支持 epub/pdf/docx 等格式 |

安装一次后永久可用，无需重复安装。

---

## 标准工作流

### 第一步：转换为 Markdown

```powershell
# 路径相对知识库根目录；请按实际文件名替换，临时输出放到平台私有临时目录
# epub
python -m markitdown "_vault/books/书名(作者).epub" -o "_tmp/_epub_tmp.md"

# pdf（同样适用）
python -m markitdown "_vault/books/书名(作者).pdf" -o "_tmp/_epub_tmp.md"
```

### 第二步：搜索关键词

用 `search_content` 工具在生成的 md 文件中搜索，或用 `read_file` 读取片段。

搜索技巧：
- 用户引用的原文和书中实际文字可能有出入（记忆偏差、简繁差异、标点不同）
- 取引文中**最短、最独特**的 4～6 字片段作为搜索词
- 找不到时换备用词，不要反复搜同一段

### 第三步：用完立即删除临时文件（必须）

```powershell
Remove-Item -Force "_tmp/_epub_tmp.md"
```

**⚠️ 必须在每次操作结束后立即执行，否则临时文件会被 git 追踪，污染提交记录。**

---

## 注意事项

### epub 无固定页码
epub 内部没有和实体书对应的页码，用户说"第105页"只能用关键词定位，无法按页码直接跳转。

### PDF 有页码
PDF 文字版转换后会保留页码信息，可以用页码附近的关键词精确定位。

### 扫描版 PDF 无法提取
如果 markitdown 输出内容为空或乱码，说明是扫描版 PDF，需要改用 OCR 方案（参见 `pdf-ocr.md`）。

### 大文件转换时间
epub 通常几秒内完成；300 页以上的 PDF 可能需要 10～30 秒，正常现象。

---

## 常见问题

**Q: `python -m markitdown` 报错找不到命令**
先安装：`pip install markitdown`，安装后重试。

**Q: 输出 md 文件内容为空**
可能是扫描版 PDF 或加密 epub，改用 `pdf-ocr.md` 中的 OCR 流程处理。

**Q: 中文乱码**
markitdown 默认输出 UTF-8，在 Windows PowerShell 下读取 md 文件时若出现乱码，用 `read_file` 工具读取而非直接 `cat`。

---

## 与 pdf-ocr.md 的关系

| 场景 | 使用工具 |
|------|---------|
| epub 任意格式 | 本工具（markitdown） |
| 文字版 PDF | 本工具（markitdown） |
| 扫描版 PDF | `pdf-ocr.md`（Tesseract OCR） |
