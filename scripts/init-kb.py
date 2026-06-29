#!/usr/bin/env python3
"""
init-kb — 初始化一个空的知识库骨架

用法:
    python scripts/init-kb.py [目标目录]

如果不指定目标目录，默认在当前目录初始化。
脚本会创建 topics/、_vault/、_changelog/ 等目录，
并生成空的 _vault/_index.md 与当月 changelog 文件。

它不会覆盖任何已存在的文件（安全：只新建缺失项）。
"""
import sys
import os
from datetime import date

# 需要确保存在的目录
DIRS = [
    "topics",
    "_vault",
    "_vault/books",
    "_vault/videos",
    "_vault/images",
    "_changelog",
    ".config",
]

VAULT_INDEX = """# 原始材料索引

> `_vault/` 用于存放原始材料（书籍/视频/截图等）。材料本体默认被 .gitignore 排除，
> 只有这张索引表纳入版本库。字段规范见 `_schema.md`。

| ID | 标题 | 类型 | 本地路径 | 外部链接 | 添加日期 | 备注 |
|----|------|------|----------|----------|----------|------|
"""


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    target = os.path.abspath(target)
    print(f"在以下目录初始化知识库骨架：\n  {target}\n")

    created = []
    for d in DIRS:
        path = os.path.join(target, d)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            created.append(d + "/")

    # _vault/_index.md
    index_path = os.path.join(target, "_vault", "_index.md")
    if not os.path.exists(index_path):
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(VAULT_INDEX)
        created.append("_vault/_index.md")

    # 当月 changelog
    month = date.today().strftime("%Y-%m")
    changelog_path = os.path.join(target, "_changelog", f"{month}.md")
    if not os.path.exists(changelog_path):
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(f"# {month} 操作日志\n\n")
        created.append(f"_changelog/{month}.md")

    if created:
        print("已创建：")
        for c in created:
            print(f"  + {c}")
    else:
        print("没有需要创建的项（骨架已存在）。")

    print(
        "\n完成。下一步：\n"
        "  1. 确认根目录已有 SOUL.md / SKILL.md / AGENTS.md / PLATFORMS.md / _schema.md\n"
        "  2. 让你的 AI 助手读取 SOUL.md，按首次交互协议自检\n"
        "  3. 开始录入第一条笔记\n"
        "（可选）删除 example/ 目录以移除示例内容。\n"
    )


if __name__ == "__main__":
    main()
