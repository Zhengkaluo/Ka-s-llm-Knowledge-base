"""
fix_md_images.py — 修复下载的 Markdown 文件中图片路径的括号转义问题

问题：Markdown 图片语法 ![]() 中，如果路径包含 ( 或 )，渲染器会误判闭合位置，导致图片加载失败。
方案：将图片路径中的 ( ) 进行 URL 编码（%28 %29）。

用法：
    python fix_md_images.py                    # 修复当前目录下所有 .md 文件
    python fix_md_images.py path/to/file.md    # 修复指定文件
    python fix_md_images.py path/to/dir/       # 修复指定目录下所有 .md 文件
"""

import os
import re
import sys
import glob


def fix_image_paths(content: str) -> str:
    """
    修复 Markdown 内容中图片引用路径的括号问题。
    将 ![alt](path/with(parens)/img.jpg) 中路径部分的 ( ) 编码为 %28 %29。
    """
    def encode_parens_in_path(match):
        alt = match.group(1)
        path = match.group(2)
        # 对路径中的括号进行 URL 编码
        fixed_path = path.replace('(', '%28').replace(')', '%29')
        return f'![{alt}]({fixed_path})'

    # 匹配 ![任意alt文本](路径) —— 贪婪匹配路径直到行末的 )
    # 使用更精确的正则：匹配到包含非空白字符的路径
    pattern = r'!\[([^\]]*)\]\((.+?)\)(\s|$)'
    
    def fix_match(match):
        alt = match.group(1)
        path = match.group(2)
        trailing = match.group(3)
        
        # 只处理本地路径（不以 http 开头的），且包含括号的
        if not path.startswith('http') and ('(' in path or ')' in path):
            fixed_path = path.replace('(', '%28').replace(')', '%29')
            return f'![{alt}]({fixed_path}){trailing}'
        return match.group(0)
    
    return re.sub(pattern, fix_match, content)


def process_file(filepath: str) -> bool:
    """处理单个文件，返回是否有修改。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    fixed = fix_image_paths(original)
    
    if fixed != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed)
        return True
    return False


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        files = glob.glob(os.path.join(target, '**', '*.md'), recursive=True)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)
    
    fixed_count = 0
    for f in files:
        if process_file(f):
            fixed_count += 1
            print(f"  FIXED: {f}")
        else:
            print(f"  OK:    {f}")
    
    print(f"\nDone. {fixed_count}/{len(files)} files fixed.")


if __name__ == '__main__':
    main()
