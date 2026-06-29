# Zhihu Downloader — 网络文章下载与归档

## 触发条件

以下情况时使用此能力：
- 用户要求保存知乎文章/回答/专栏到知识库
- 用户要求下载微信公众号、CSDN、掘金的文章
- 用户提供了上述平台的 URL 并希望转为笔记

## 支持的平台

| 平台 | URL 示例 | 解析器 |
|------|---------|--------|
| 知乎文章 | `zhuanlan.zhihu.com/p/xxx` | ZhihuParser |
| 知乎回答 | `zhihu.com/question/xxx/answer/xxx` | ZhihuParser |
| 知乎专栏 | `zhihu.com/column/c_xxx` | ZhihuParser（批量，支持断点续传） |
| 知乎视频 | `zhihu.com/zvideo/xxx` | ZhihuParser |
| 微信公众号 | `mp.weixin.qq.com/s/xxx` | WeixinParser |
| CSDN | `blog.csdn.net/xxx` | CsdnParser |
| 掘金 | `juejin.cn/post/xxx` | JuejinParser |

## 脚本位置

```
tools/scripts/zhihu-download/
├── app.py              ← Flask Web 服务入口
├── main_zhihu.py       ← 知乎解析器（已修改：文件名去括号）
├── main_csdn.py        ← CSDN 解析器（已修改：文件名去括号）
├── main_weixin.py      ← 微信公众号解析器（已修改：文件名去括号）
├── main_juejin.py      ← 掘金解析器（已修改：文件名去括号）
├── fix_md_images.py    ← 后处理脚本：修复图片路径中的括号转义
├── utils/util.py       ← 工具函数
├── tampermonkey.js      ← 油猴脚本（浏览器端）
├── templates/           ← Web UI 模板
├── static/              ← 静态资源
└── requirements.txt     ← Python 依赖
```

## 使用方式

### 方式一：启动 Web 服务（交互式使用）

```bash
cd tools/scripts/zhihu-download
python app.py
```

启动后访问 `http://127.0.0.1:5000/`，在网页中：
1. 选择平台（zhihu / weixin / csdn / juejin）
2. 粘贴文章 URL
3. 填入 Cookies（知乎必填，其他平台可选）
4. 点击下载 → 得到 ZIP 包（含 .md + 图片）

### 方式二：Python 直接调用（AI agent 推荐）

```python
import os, sys
sys.path.insert(0, "tools/scripts/zhihu-download")

from main_zhihu import ZhihuParser
from main_csdn import CsdnParser
from main_weixin import WeixinParser
from main_juejin import JuejinParser

# 知乎（需要 cookies）
parser = ZhihuParser(cookies="你的知乎cookie", keep_logs=True)

# 切换到输出目录
os.makedirs("_tmp_download", exist_ok=True)
os.chdir("_tmp_download")

# 解析文章/回答/专栏
title = parser.judge_type("https://zhuanlan.zhihu.com/p/xxxxxxx")
# 返回值 title 就是生成的 .md 文件名（不含扩展名）

# 微信公众号（不需要 cookies）
parser = WeixinParser(keep_logs=True)
title = parser.judge_type("https://mp.weixin.qq.com/s/xxxxxxx")

# CSDN（不需要 cookies）
parser = CsdnParser(keep_logs=True)
title = parser.judge_type("https://blog.csdn.net/xxx/article/details/xxx")

# 掘金（不需要 cookies）
parser = JuejinParser(keep_logs=True)
title = parser.judge_type("https://juejin.cn/post/xxx")
```

## 工作流：下载文章并归档到知识库

### 1. 获取 Cookies（知乎专用，首次使用需要）

引导用户自行获取：

> 1. 打开 Chrome/Edge，登录知乎
> 2. F12 打开开发者工具 → Network 标签
> 3. 刷新页面，点击任意一个请求
> 4. 在 Headers 中找到 `Cookie` 字段，复制完整值
> 5. 粘贴给我即可

**注意**：Cookie 会过期，如果下载报错 "Cookies are required" 需要重新获取。

### 2. 下载并解析文章

使用 Python 脚本将文章下载为临时 Markdown（agent 执行）：

```bash
cd "tools/scripts/zhihu-download"
python -c "
import os
os.makedirs('_tmp', exist_ok=True)
old_cwd = os.getcwd()
os.chdir('_tmp')

from main_zhihu import ZhihuParser
parser = ZhihuParser(cookies='USER_COOKIE_HERE', keep_logs=True)
title = parser.judge_type('ARTICLE_URL_HERE')
print(f'DONE: {title}')

os.chdir(old_cwd)
"
```

下载完成后运行后处理脚本修复图片路径：

```bash
python fix_md_images.py _tmp/
```

### 3. 与用户商量归档位置（⚠️ 必须步骤，不可跳过）

**下载完成后，agent 必须：**

1. **阅读文章内容**，提取标题、作者、核心主题
2. **扫描 `topics/` 目录**，列出现有主题
3. **向用户提出建议**，格式如下：

   > 📄 文章：《{标题}》by {作者}
   > 📝 核心内容：{一句话概括}
   >
   > 建议归入主题：
   > - **首选**：`topics/{best-match}/` — {理由}
   > - 备选：`topics/{alternative}/` — {理由}
   > - 或者：新建主题 `topics/{new-slug}/`
   >
   > 你觉得放哪个好？

4. **等待用户确认**后才进行下一步。**绝不自行决定主题。**

### 4. 转换为知识库笔记格式

用户确认归档主题后：

1. **识别来源类型**：web（知乎/CSDN/掘金/微信公众号 → 都算 web 类型）
2. **读取 `_templates/note-web.md` 模板**
3. **填充 frontmatter**：
   - `title`: 文章标题
   - `source_type`: web
   - `source_title`: 平台名 + 文章标题
   - `source_url`: 原文链接
   - `author`: 作者名
   - `tags`: 根据内容推断
   - `created`: 当前日期
4. **正文处理**：
   - 去掉原始的 `# 标题` / `Author` / `Link` 头部
   - 保留正文内容
   - 图片路径调整为相对于笔记文件的路径
5. **展示完整笔记预览**，用户确认后写入 `topics/{confirmed-topic}/`

### 5. 图片处理

- 将下载的图片目录移动到笔记所在的 topic 目录下
- 更新 Markdown 中的图片引用路径（相对路径）
- 确保图片在 Markdown 预览中正常显示

### 6. 清理

归档完成后，删除 `tools/scripts/zhihu-download/_tmp/` 临时目录。

## Cookies 存储

如果用户同意持久化保存 Cookies：
- 存储位置：`.config/zhihu-tools/.env`
- 格式：`ZHIHU_COOKIES=xxx`
- **不要在聊天中直接展示完整 Cookie 值**

## 注意事项

- 所有写入操作遵循 SOUL.md 的确认规则
- 知乎专栏下载支持**断点续传**，中途中断后重新运行会跳过已下载的文章
- 知乎 Cookie 有效期有限，过期后需要重新获取
- 微信公众号、CSDN、掘金**不需要 Cookie**
- IDM 可能拦截下载，将 `127.0.0.1:5000` 加入排除列表
- 下载的 Markdown 已包含 LaTeX 数学公式支持

## ⚠️ 已知问题与本地修改

### 图片路径括号问题（2026-03-27 修复）

**问题**：原始仓库的文件命名格式为 `({date}){title}_{author}`，文件名中的括号 `()` 会导致 Markdown 图片语法 `![]()` 被渲染器误判闭合位置，**造成图片全部加载失败**。

**修复措施（双保险）**：

#### 1. 源码修改（治本）

已修改 4 个解析器的文件命名逻辑，去掉文件名中的括号：

| 文件 | 原始格式 | 修改后 |
|------|---------|--------|
| `main_zhihu.py` | `({date}){title}_{author}` | `{date}_{title}_{author}` |
| `main_csdn.py` | `({date}){title}_{author}` | `{date}_{title}_{author}` |
| `main_weixin.py` | `({date}){title}_{author}` | `{date}_{title}_{author}` |
| `main_juejin.py` | `({date}){title}_{author}` | `{date}_{title}_{author}` |

**注意**：这些是对上游仓库的本地修改。如果执行 `git pull` 更新，这些改动可能被覆盖，需要重新应用。

#### 2. 后处理脚本（兜底）

`fix_md_images.py` 会扫描 Markdown 文件中的图片引用，将路径中的 `(` `)` 编码为 `%28` `%29`。

```bash
# 修复指定目录下所有 .md 文件
python tools/scripts/zhihu-download/fix_md_images.py path/to/output/

# 修复单个文件
python tools/scripts/zhihu-download/fix_md_images.py path/to/file.md
```

**建议**：每次下载后都跑一遍 `fix_md_images.py` 作为兜底，即使源码已修改也不会有副作用。

### 对 Agent 的提醒

1. **下载完成后**，务必对输出的 .md 文件运行 `fix_md_images.py`
2. 如果发现图片仍然加载失败，检查文件名中是否包含 `(` `)` `[` `]` 等 Markdown 特殊字符
3. 如果上游仓库更新后图片又出问题，重新应用上述源码修改
