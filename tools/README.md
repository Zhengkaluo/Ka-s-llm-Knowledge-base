# Tools — 通用能力扩展

本目录存放**通用的 AI 能力指令文件**。每个 `.md` 文件定义一个具体能力，任何 AI agent 读取后即可获得该能力。

## 使用方式

1. AI agent 读取 `SOUL.md` 时会知道 `tools/` 目录的存在
2. 根据当前任务需要，agent 读取对应的 tool 文件
3. 按照 tool 文件中定义的工作流执行

## 设计原则

- **独立性**：每个 tool 文件是自包含的，不依赖特定 AI 工具链
- **插拔性**：需要什么能力就读什么文件，不需要的不加载
- **遵守 SOUL.md**：所有 tool 的执行仍受 SOUL.md 权限规则约束

## 当前 Tools

| 文件 | 能力 | 说明 | 依赖 |
|------|------|------|------|
| `book-finder.md` | 书籍查找与存档 | 搜索书籍信息，自动通过 Z-Library/Anna's Archive 搜索下载电子版并存入 _vault | Python3, requests, `scripts/zlib-download/` |
| `zhihu-downloader.md` | 网络文章下载与归档 | 下载知乎/微信公众号/CSDN/掘金文章为 Markdown，自动归档到 topics/ | Python3, requests, bs4, markdownify, flask, `scripts/zhihu-download/` |
| `pdf-ocr.md` | PDF 读取与文字提取 | 判断 PDF 类型（文字版/扫描版），文字版直接提取，扫描版需安装 Tesseract OCR | Python3, pypdf, Tesseract (可选), pdf2image (可选), pytesseract (可选) |
| `epub-reader.md` | 电子书读取与原文检索 | 将 epub/pdf 一步转换为 Markdown，再搜索原文段落；无需解压，无临时目录残留 | Python3, markitdown (`pip install markitdown`) |
| `vault-ingest.md` | 原始材料加工与 LLM 友好副本 | 只处理 `_vault/` 内材料，支持体检、单文件提取和安全批量提取，生成 Markdown、meta.json 与质量报告，不自动写入 topics/ | Python3, pypdf；EPUB 使用标准库解析 |

## 脚本目录

```
scripts/
├── zlib-download/        ← 书籍搜索下载脚本（Z-Library + Anna's Archive）
│   ├── book.py           ← 主脚本
│   ├── setup.sh          ← 环境安装
│   ├── Zlibrary.py       ← Z-Library API 封装
│   └── api_reference.md  ← API 参考
├── zhihu-download/       ← 网络文章下载脚本（知乎/微信公众号/CSDN/掘金）
│   ├── app.py            ← Flask Web 服务入口
│   ├── main_zhihu.py     ← 知乎解析器（⚠️ 有本地修改）
│   ├── main_csdn.py      ← CSDN 解析器（⚠️ 有本地修改）
│   ├── main_weixin.py    ← 微信公众号解析器（⚠️ 有本地修改）
│   ├── main_juejin.py    ← 掘金解析器（⚠️ 有本地修改）
│   ├── fix_md_images.py  ← 后处理：修复图片路径括号转义
│   ├── utils/util.py     ← 工具函数
│   └── tampermonkey.js   ← 油猴脚本（浏览器端）
└── vault-ingest/         ← 原始材料加工脚本（体检 + 提取已实现）
    └── vault_ingest.py   ← inventory / inspect / inspect-all / extract / extract-all
```

> **⚠️ 本地修改说明**：zhihu-download 的 4 个解析器文件名格式已从 `({date}){title}` 改为 `{date}_{title}`，避免括号导致 Markdown 图片引用失败。详见 `zhihu-downloader.md` 中的"已知问题与本地修改"章节。
