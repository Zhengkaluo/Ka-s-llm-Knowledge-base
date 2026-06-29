#!/usr/bin/env python3
"""Vault ingest utilities for the Markdown knowledge base framework.

This script works only on the raw-material layer. It reads files from
_vault/books and writes derived LLM-friendly files under
_vault/extracted/books. It never modifies source books and never writes to
topics.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
import zipfile
from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urldefrag
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
BOOKS_DIR = ROOT / "_vault" / "books"
EXTRACTED_BOOKS_DIR = ROOT / "_vault" / "extracted" / "books"
SUPPORTED_EXTS = {".pdf", ".epub", ".mobi"}
GARBLED_CHARS = {"\ufffd", "\u25a1", "\u25a0", "\u25fb", "\u25fc"}
BLOCK_TAGS = {
    "address", "article", "aside", "blockquote", "br", "dd", "div", "dl", "dt",
    "figcaption", "figure", "footer", "h1", "h2", "h3", "h4", "h5", "h6",
    "header", "hr", "li", "main", "nav", "ol", "p", "pre", "section", "table",
    "td", "th", "tr", "ul",
}
SKIP_TAGS = {"script", "style", "head", "noscript", "svg"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def output(data: dict[str, Any], code: int = 0) -> None:
    stream = sys.stdout if code == 0 else sys.stderr
    print(json.dumps(data, ensure_ascii=False, indent=2), file=stream)
    raise SystemExit(code)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def today() -> str:
    return datetime.now().date().isoformat()


def list_books() -> list[Path]:
    if not BOOKS_DIR.exists():
        return []
    files = []
    for path in BOOKS_DIR.iterdir():
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTS:
            files.append(path)
    return sorted(files, key=lambda p: p.name.lower())


def file_record(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": rel(path),
        "name": path.name,
        "format": path.suffix.lower().lstrip("."),
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / 1024 / 1024, 2),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
    }


def inventory(_: argparse.Namespace) -> None:
    files = list_books()
    formats = Counter(p.suffix.lower().lstrip(".") for p in files)
    output({
        "root": rel(ROOT),
        "books_dir": rel(BOOKS_DIR),
        "total": len(files),
        "formats": dict(sorted(formats.items())),
        "files": [file_record(p) for p in files],
    })


def load_pypdf():
    try:
        from pypdf import PdfReader  # type: ignore
        return PdfReader, None
    except Exception as exc:
        return None, f"pypdf unavailable: {type(exc).__name__}: {exc}"


def garbled_ratio(text: str) -> float:
    if not text:
        return 0.0
    bad = 0
    for ch in text:
        if ch in GARBLED_CHARS or (ord(ch) < 32 and ch not in "\n\r\t"):
            bad += 1
    return bad / max(len(text), 1)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def safe_output_stem(path: Path) -> str:
    stem = path.stem.strip()
    stem = re.sub(r"[\\/:*?\"<>|]+", "_", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem or "untitled"


def derived_paths(source: Path) -> dict[str, Path]:
    stem = safe_output_stem(source)
    return {
        "md": EXTRACTED_BOOKS_DIR / f"{stem}.md",
        "meta": EXTRACTED_BOOKS_DIR / f"{stem}.meta.json",
        "report": EXTRACTED_BOOKS_DIR / f"{stem}.report.md",
    }


def grade_pdf(text_coverage: float, avg_chars: float, ratio: float, pages: int) -> tuple[str, str]:
    if pages <= 0:
        return "D", "failed"
    if text_coverage < 0.1 and avg_chars < 40:
        return "D", "needs_ocr"
    if text_coverage < 0.45 or avg_chars < 120:
        return "C", "needs_ocr"
    if ratio > 0.03:
        return "C", "pass_with_warnings"
    if text_coverage >= 0.85 and avg_chars >= 400 and ratio <= 0.01:
        return "A", "pass"
    return "B", "pass_with_warnings"


def inspect_pdf(path: Path) -> dict[str, Any]:
    PdfReader, err = load_pypdf()
    base = file_record(path)
    base.update({"inspected_at": now_iso()})
    if PdfReader is None:
        base.update({
            "status": "failed",
            "quality_grade": "unknown",
            "error": err,
            "hint": "Install pypdf in the active Python environment to inspect PDFs.",
        })
        return base

    try:
        reader = PdfReader(str(path))
        pages = len(reader.pages)
        page_stats: list[dict[str, Any]] = []
        all_text_parts: list[str] = []
        for idx, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception as exc:
                text = ""
                page_error = f"{type(exc).__name__}: {exc}"
            else:
                page_error = None
            compact = normalize_space(text)
            char_count = len(compact)
            all_text_parts.append(compact)
            rec = {
                "page": idx,
                "chars": char_count,
                "garbled_ratio": round(garbled_ratio(compact), 5),
            }
            if page_error:
                rec["error"] = page_error
            page_stats.append(rec)
    except Exception as exc:
        base.update({
            "status": "failed",
            "quality_grade": "D",
            "error": f"{type(exc).__name__}: {exc}",
        })
        return base

    non_empty_pages = [s["page"] for s in page_stats if s["chars"] >= 40]
    empty_pages = [s["page"] for s in page_stats if s["chars"] < 10]
    short_pages = [s["page"] for s in page_stats if 10 <= s["chars"] < 120]
    total_chars = sum(s["chars"] for s in page_stats)
    avg_chars = total_chars / pages if pages else 0
    combined = "\n".join(all_text_parts)
    g_ratio = garbled_ratio(combined)
    text_coverage = len(non_empty_pages) / pages if pages else 0
    suspect_pages = sorted(set(
        empty_pages[:]
        + short_pages[:]
        + [s["page"] for s in page_stats if s["garbled_ratio"] > 0.03]
    ))
    grade, status = grade_pdf(text_coverage, avg_chars, g_ratio, pages)
    if status == "needs_ocr":
        pdf_type = "scanned_or_bad_text_layer"
    elif text_coverage < 0.85:
        pdf_type = "mixed_or_partial_text_layer"
    else:
        pdf_type = "text_layer"

    sample_pages = []
    if pages:
        candidates = {1, pages, max(1, math.ceil(pages / 2))}
        candidates.update(suspect_pages[:5])
        sample_pages = sorted(p for p in candidates if 1 <= p <= pages)

    base.update({
        "status": status,
        "quality_grade": grade,
        "pdf_type": pdf_type,
        "pages": pages,
        "text_coverage": round(text_coverage, 4),
        "non_empty_pages": len(non_empty_pages),
        "average_chars_per_page": round(avg_chars, 2),
        "total_extracted_chars": total_chars,
        "garbled_ratio": round(g_ratio, 5),
        "empty_pages": empty_pages,
        "short_pages": short_pages,
        "suspect_pages": suspect_pages,
        "sample_pages_for_manual_check": sample_pages,
        "note": "Markdown extraction should preserve page anchors; precise quotes must be checked against original PDF pages.",
    })
    return base


def inspect_epub(path: Path) -> dict[str, Any]:
    data = file_record(path)
    data.update({
        "inspected_at": now_iso(),
        "status": "pass_with_warnings",
        "quality_grade": "B",
        "structure": "chapter_based",
        "page_anchor": "unavailable",
        "note": "EPUB is usually LLM-friendly after Markdown conversion, but it has no stable PDF-style page numbers.",
    })
    return data


def inspect_mobi(path: Path) -> dict[str, Any]:
    data = file_record(path)
    data.update({
        "inspected_at": now_iso(),
        "status": "unsupported_needs_conversion",
        "quality_grade": "unknown",
        "hint": "Convert MOBI to EPUB first, for example with Calibre ebook-convert, then run the EPUB workflow.",
    })
    return data


def resolve_input(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def inspect(args: argparse.Namespace) -> None:
    path = resolve_input(args.file)
    if not path.exists():
        output({"status": "failed", "error": f"File not found: {path}"}, 1)
    if not path.is_file():
        output({"status": "failed", "error": f"Not a file: {path}"}, 1)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        output(inspect_pdf(path))
    if suffix == ".epub":
        output(inspect_epub(path))
    if suffix == ".mobi":
        output(inspect_mobi(path))
    output({"status": "failed", "error": f"Unsupported format: {suffix}"}, 1)


def inspect_all(_: argparse.Namespace) -> None:
    files = list_books()
    results = []
    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            results.append(inspect_pdf(path))
        elif suffix == ".epub":
            results.append(inspect_epub(path))
        elif suffix == ".mobi":
            results.append(inspect_mobi(path))
    statuses = Counter(item.get("status", "unknown") for item in results)
    grades = Counter(item.get("quality_grade", "unknown") for item in results)
    pdf_types = Counter(item.get("pdf_type", "not_pdf") for item in results if item.get("format") == "pdf")
    output({
        "root": rel(ROOT),
        "books_dir": rel(BOOKS_DIR),
        "total": len(results),
        "statuses": dict(sorted(statuses.items())),
        "quality_grades": dict(sorted(grades.items())),
        "pdf_types": dict(sorted(pdf_types.items())),
        "results": results,
    })


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in SKIP_TAGS:
            self.skip_stack.append(tag)
            return
        if self.skip_stack:
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n\n")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.skip_stack:
            if self.skip_stack[-1] == tag:
                self.skip_stack.pop()
            return
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_stack:
            return
        if data:
            self.parts.append(data)

    def text(self) -> str:
        raw = "".join(self.parts)
        raw = html.unescape(raw)
        lines = []
        for line in raw.splitlines():
            compact = re.sub(r"[ \t]+", " ", line).strip()
            if compact:
                lines.append(compact)
            elif lines and lines[-1] != "":
                lines.append("")
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def child_text_by_local_name(root: ET.Element | None, local_name: str) -> str | None:
    if root is None:
        return None
    for child in root.iter():
        if strip_ns(child.tag) == local_name and child.text:
            return child.text.strip()
    return None


def join_epub_path(base: PurePosixPath, href: str) -> str:
    href = unquote(urldefrag(href)[0])
    combined = base / href
    parts: list[str] = []
    for part in combined.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def html_to_text(data: bytes) -> str:
    content = data.decode("utf-8", errors="ignore")
    parser = TextExtractor()
    parser.feed(content)
    return parser.text()


def parse_epub(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        if "META-INF/container.xml" not in names:
            raise ValueError("META-INF/container.xml not found")
        container = ET.fromstring(zf.read("META-INF/container.xml"))
        rootfile = None
        for elem in container.iter():
            if strip_ns(elem.tag) == "rootfile":
                rootfile = elem.attrib.get("full-path")
                break
        if not rootfile:
            raise ValueError("OPF rootfile not found in container.xml")
        opf_xml = ET.fromstring(zf.read(rootfile))
        opf_base = PurePosixPath(rootfile).parent

        metadata = None
        manifest = None
        spine = None
        for child in opf_xml:
            local = strip_ns(child.tag)
            if local == "metadata":
                metadata = child
            elif local == "manifest":
                manifest = child
            elif local == "spine":
                spine = child

        meta = {
            "title": child_text_by_local_name(metadata, "title") or path.stem,
            "creator": child_text_by_local_name(metadata, "creator"),
            "language": child_text_by_local_name(metadata, "language"),
            "publisher": child_text_by_local_name(metadata, "publisher"),
            "date": child_text_by_local_name(metadata, "date"),
        }

        manifest_items: dict[str, dict[str, str]] = {}
        if manifest is not None:
            for item in manifest:
                if strip_ns(item.tag) == "item":
                    item_id = item.attrib.get("id")
                    href = item.attrib.get("href")
                    if item_id and href:
                        manifest_items[item_id] = {
                            "href": join_epub_path(opf_base, href),
                            "media_type": item.attrib.get("media-type", ""),
                            "properties": item.attrib.get("properties", ""),
                        }

        reading_order: list[str] = []
        if spine is not None:
            for itemref in spine:
                if strip_ns(itemref.tag) == "itemref":
                    idref = itemref.attrib.get("idref")
                    item = manifest_items.get(idref or "")
                    if item and item["href"] in names:
                        reading_order.append(item["href"])
        if not reading_order:
            reading_order = sorted(
                n for n in names
                if n.lower().endswith((".html", ".xhtml", ".htm")) and "nav" not in n.lower()
            )

        chapters = []
        for idx, href in enumerate(reading_order, start=1):
            if href not in names:
                continue
            text = html_to_text(zf.read(href))
            if not text:
                continue
            first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
            title = first_line[:80] if first_line else PurePosixPath(href).name
            chapters.append({
                "index": idx,
                "href": href,
                "title": title,
                "text": text,
                "chars": len(normalize_space(text)),
            })
    return {"metadata": meta, "chapters": chapters, "opf_path": rootfile}


def make_pdf_markdown(source: Path, inspection: dict[str, Any]) -> tuple[str, int]:
    PdfReader, err = load_pypdf()
    if PdfReader is None:
        raise RuntimeError(err or "pypdf unavailable")
    reader = PdfReader(str(source))
    title = source.stem
    generated = today()
    parts = [
        f"# {title}",
        "",
        f"<!-- source: {rel(source)} -->",
        "<!-- extraction_type: text_layer_pdf -->",
        f"<!-- generated: {generated} -->",
        f"<!-- pages: {len(reader.pages)} -->",
        "",
    ]
    total_chars = 0
    for idx, page in enumerate(reader.pages, start=1):
        try:
            text = clean_text(page.extract_text() or "")
        except Exception as exc:
            text = f"[Extraction error on page {idx}: {type(exc).__name__}: {exc}]"
        total_chars += len(normalize_space(text))
        parts.extend([
            f"## Page {idx}",
            "",
            f"<!-- page: {idx} -->",
            "",
            text if text else "[No extractable text on this page]",
            "",
        ])
    return "\n".join(parts).rstrip() + "\n", total_chars


def make_epub_markdown(source: Path, parsed: dict[str, Any]) -> tuple[str, int]:
    metadata = parsed["metadata"]
    title = metadata.get("title") or source.stem
    generated = today()
    chapters = parsed["chapters"]
    parts = [
        f"# {title}",
        "",
        f"<!-- source: {rel(source)} -->",
        "<!-- extraction_type: epub_chapter_text -->",
        f"<!-- generated: {generated} -->",
        "<!-- page_anchor: unavailable -->",
        "",
    ]
    if metadata.get("creator"):
        parts.extend([f"Author: {metadata['creator']}", ""])
    total_chars = 0
    for chapter in chapters:
        total_chars += chapter["chars"]
        heading = chapter["title"] or chapter["href"]
        parts.extend([
            f"## Section {chapter['index']}: {heading}",
            "",
            f"<!-- href: {chapter['href']} -->",
            "",
            chapter["text"],
            "",
        ])
    return "\n".join(parts).rstrip() + "\n", total_chars


def report_markdown(meta: dict[str, Any]) -> str:
    source = meta.get("source", "")
    output_path = meta.get("output", "")
    title = Path(source).stem if source else "unknown"
    lines = [
        f"# 提取质量报告：{title}",
        "",
        f"- 原文件：`{source}`",
        f"- 输出文件：`{output_path}`",
        f"- 文件格式：{str(meta.get('format', '')).upper()}",
        f"- 提取类型：{meta.get('extraction_type', '-')}",
        f"- 质量等级：{meta.get('quality_grade', '-')}",
        f"- 状态：{meta.get('status', '-')}",
        f"- 生成时间：{meta.get('generated_at', '-')}",
    ]
    if meta.get("format") == "pdf":
        lines.extend([
            f"- PDF 类型：{meta.get('pdf_type', '-')}",
            f"- 页数：{meta.get('pages', '-')}",
            f"- 文字覆盖率：{meta.get('text_coverage', '-')}",
            f"- 平均每页字符数：{meta.get('average_chars_per_page', '-')}",
            f"- 乱码率：{meta.get('garbled_ratio', '-')}",
            "",
            "## 疑似问题",
            "",
            f"- 空页：{', '.join(map(str, meta.get('empty_pages', []))) or '无'}",
            f"- 短页：{', '.join(map(str, meta.get('short_pages', []))) or '无'}",
            f"- 疑似问题页：{', '.join(map(str, meta.get('suspect_pages', []))) or '无'}",
            f"- 建议抽检页：{', '.join(map(str, meta.get('sample_pages_for_manual_check', []))) or '无'}",
        ])
    elif meta.get("format") == "epub":
        lines.extend([
            f"- 章节数：{meta.get('chapters', '-')}",
            f"- EPUB 标题：{meta.get('title', '-')}",
            f"- 作者：{meta.get('creator', '-')}",
            f"- 语言：{meta.get('language', '-')}",
            "",
            "## 疑似问题",
            "",
            "- EPUB 没有稳定页码，精确页码引用需回到其他版本或原始材料确认。",
            "- 图片、脚注、尾注可能在转换中丢失或位置变化。",
        ])
    lines.extend([
        "",
        "## 建议",
        "",
        "Markdown 是 LLM 友好阅读副本，不是权威原文。精确引用、页码和术语判断必须回看原始材料。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_extraction_files(source: Path, markdown: str, meta: dict[str, Any]) -> dict[str, str]:
    paths = derived_paths(source)
    EXTRACTED_BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    paths["md"].write_text(markdown, encoding="utf-8", newline="\n")
    paths["meta"].write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    paths["report"].write_text(report_markdown(meta), encoding="utf-8", newline="\n")
    return {key: rel(value) for key, value in paths.items()}


def extract_pdf(path: Path) -> dict[str, Any]:
    inspection = inspect_pdf(path)
    if inspection.get("status") == "needs_ocr":
        return {
            "status": "skipped_needs_ocr",
            "source": rel(path),
            "format": "pdf",
            "quality_grade": inspection.get("quality_grade"),
            "pdf_type": inspection.get("pdf_type"),
            "pages": inspection.get("pages"),
            "text_coverage": inspection.get("text_coverage"),
            "sample_pages_for_manual_check": inspection.get("sample_pages_for_manual_check", []),
            "hint": "This PDF has no usable text layer. Run OCR only after explicit confirmation.",
        }
    if inspection.get("status") == "failed":
        return {
            "status": "failed",
            "source": rel(path),
            "error": inspection.get("error"),
            "hint": inspection.get("hint"),
        }
    markdown, total_chars = make_pdf_markdown(path, inspection)
    paths = derived_paths(path)
    generated_at = now_iso()
    meta = {
        "source": rel(path),
        "output": rel(paths["md"]),
        "meta": rel(paths["meta"]),
        "report": rel(paths["report"]),
        "format": "pdf",
        "extraction_type": "text_layer_pdf",
        "generated_at": generated_at,
        "extracted_chars": total_chars,
        **{k: v for k, v in inspection.items() if k not in {"path", "name", "format"}},
    }
    written = write_extraction_files(path, markdown, meta)
    return {"status": "extracted", "source": rel(path), "outputs": written, "meta": meta}


def extract_epub(path: Path) -> dict[str, Any]:
    try:
        parsed = parse_epub(path)
    except Exception as exc:
        data = inspect_epub(path)
        data.update({"extraction_status": "failed", "error": f"{type(exc).__name__}: {exc}"})
        return data
    markdown, total_chars = make_epub_markdown(path, parsed)
    paths = derived_paths(path)
    metadata = parsed["metadata"]
    generated_at = now_iso()
    meta = {
        "source": rel(path),
        "output": rel(paths["md"]),
        "meta": rel(paths["meta"]),
        "report": rel(paths["report"]),
        "format": "epub",
        "extraction_type": "epub_chapter_text",
        "generated_at": generated_at,
        "status": "pass_with_warnings",
        "quality_grade": "B",
        "page_anchor": "unavailable",
        "opf_path": parsed.get("opf_path"),
        "title": metadata.get("title"),
        "creator": metadata.get("creator"),
        "language": metadata.get("language"),
        "publisher": metadata.get("publisher"),
        "date": metadata.get("date"),
        "chapters": len(parsed["chapters"]),
        "extracted_chars": total_chars,
        "note": "EPUB-derived Markdown has chapter anchors but no stable page numbers.",
    }
    written = write_extraction_files(path, markdown, meta)
    return {"status": "extracted", "source": rel(path), "outputs": written, "meta": meta}


def extract(args: argparse.Namespace) -> None:
    path = resolve_input(args.file)
    if not path.exists():
        output({"status": "failed", "error": f"File not found: {path}"}, 1)
    if not path.is_file():
        output({"status": "failed", "error": f"Not a file: {path}"}, 1)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        result = extract_pdf(path)
    elif suffix == ".epub":
        result = extract_epub(path)
    elif suffix == ".mobi":
        result = inspect_mobi(path)
        result["extraction_status"] = "skipped_unsupported"
    else:
        output({"status": "failed", "error": f"Unsupported format: {suffix}"}, 1)
    code = 0 if result.get("status") == "extracted" else 1
    output(result, code)


def parse_formats(text: str) -> set[str]:
    values = {part.strip().lower().lstrip(".") for part in text.split(",") if part.strip()}
    allowed = {"pdf", "epub", "mobi"}
    unknown = values - allowed
    if unknown:
        raise ValueError(f"Unsupported formats: {', '.join(sorted(unknown))}")
    return values or {"pdf", "epub"}


def outputs_exist(source: Path) -> bool:
    paths = derived_paths(source)
    return all(path.exists() for path in paths.values())


def dry_run_plan(path: Path, selected_formats: set[str], overwrite: bool) -> dict[str, Any]:
    suffix = path.suffix.lower().lstrip(".")
    base = {"source": rel(path), "format": suffix}
    if suffix not in selected_formats:
        return {**base, "status": "skipped_format"}
    existing = outputs_exist(path)
    if existing and not overwrite:
        return {**base, "status": "skipped_existing", "outputs": {k: rel(v) for k, v in derived_paths(path).items()}}
    if suffix == "mobi":
        return {**base, "status": "skipped_unsupported", "hint": "Convert MOBI to EPUB first."}
    if suffix == "epub":
        return {**base, "status": "would_extract", "outputs": {k: rel(v) for k, v in derived_paths(path).items()}}
    if suffix == "pdf":
        inspection = inspect_pdf(path)
        if inspection.get("status") == "needs_ocr":
            return {
                **base,
                "status": "would_skip_needs_ocr",
                "quality_grade": inspection.get("quality_grade"),
                "pdf_type": inspection.get("pdf_type"),
                "pages": inspection.get("pages"),
                "text_coverage": inspection.get("text_coverage"),
            }
        if inspection.get("status") == "failed":
            return {**base, "status": "would_fail", "error": inspection.get("error")}
        return {
            **base,
            "status": "would_extract",
            "quality_grade": inspection.get("quality_grade"),
            "pdf_type": inspection.get("pdf_type"),
            "pages": inspection.get("pages"),
            "outputs": {k: rel(v) for k, v in derived_paths(path).items()},
        }
    return {**base, "status": "skipped_unsupported"}


def extract_all(args: argparse.Namespace) -> None:
    try:
        selected_formats = parse_formats(args.formats)
    except ValueError as exc:
        output({"status": "failed", "error": str(exc)}, 1)

    results = []
    for path in list_books():
        suffix = path.suffix.lower().lstrip(".")
        if args.dry_run:
            results.append(dry_run_plan(path, selected_formats, args.overwrite))
            continue
        base = {"source": rel(path), "format": suffix}
        if suffix not in selected_formats:
            results.append({**base, "status": "skipped_format"})
            continue
        if outputs_exist(path) and not args.overwrite:
            results.append({**base, "status": "skipped_existing", "outputs": {k: rel(v) for k, v in derived_paths(path).items()}})
            continue
        if suffix == "pdf":
            results.append(extract_pdf(path))
        elif suffix == "epub":
            results.append(extract_epub(path))
        elif suffix == "mobi":
            results.append({**base, "status": "skipped_unsupported", "hint": "Convert MOBI to EPUB first."})
        else:
            results.append({**base, "status": "skipped_unsupported"})

    counts = Counter(item.get("status", "unknown") for item in results)
    output({
        "status": "dry_run" if args.dry_run else "completed",
        "dry_run": args.dry_run,
        "formats": sorted(selected_formats),
        "overwrite": args.overwrite,
        "total": len(results),
        "counts": dict(sorted(counts.items())),
        "results": results,
    })


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect and prepare _vault book materials for LLM-friendly extraction.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_inventory = sub.add_parser("inventory", help="List book files and format distribution under _vault/books")
    p_inventory.set_defaults(func=inventory)

    p_inspect = sub.add_parser("inspect", help="Inspect one book file")
    p_inspect.add_argument("file", help="Path to a file under _vault/books")
    p_inspect.set_defaults(func=inspect)

    p_inspect_all = sub.add_parser("inspect-all", help="Inspect all supported book files under _vault/books")
    p_inspect_all.set_defaults(func=inspect_all)

    p_extract = sub.add_parser("extract", help="Extract one text-layer PDF or EPUB into _vault/extracted/books")
    p_extract.add_argument("file", help="Path to a PDF or EPUB under _vault/books")
    p_extract.set_defaults(func=extract)

    p_extract_all = sub.add_parser("extract-all", help="Batch extract supported files into _vault/extracted/books")
    p_extract_all.add_argument("--dry-run", action="store_true", help="Only show what would happen; do not write files")
    p_extract_all.add_argument("--formats", default="pdf,epub", help="Comma-separated formats to process: pdf,epub,mobi")
    p_extract_all.add_argument("--overwrite", action="store_true", help="Overwrite existing derived md/meta/report files")
    p_extract_all.set_defaults(func=extract_all)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
