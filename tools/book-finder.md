# Book Finder — 书籍查找与存档

## 触发条件

以下情况时使用此能力：
- 用户录入的笔记来自某本书，且 `_vault/_index.md` 中尚无该书条目
- 用户主动要求查找某本书的信息或电子版
- 新建书籍笔记时，需要补全书籍元数据

## 脚本位置

```
tools/scripts/zlib-download/
├── book.py            ← 主脚本（搜索+下载）
├── setup.sh           ← 环境安装脚本
├── Zlibrary.py        ← Z-Library API 封装
└── api_reference.md   ← API 参考文档
```

## 工作流

### 1. 搜索书籍信息

根据已知信息（书名、作者、ISBN 中的任意一项）搜索：

- 书名全称（中英文）
- 作者
- 出版社、出版日期
- ISBN
- 豆瓣链接
- 简介/目录概要

将搜索到的信息整理后展示给用户确认。

### 2. 询问电子版情况

向用户确认：

> "你有这本书的电子版吗？（PDF/EPUB/MOBI 等）"

**如果有** → 进入步骤 3a
**如果没有** → 进入步骤 3b

### 3a. 指导存入（用户已有电子版）

1. 建议文件命名：`{english-slug}.{ext}`（如 `the-selfish-gene.pdf`）
2. 告知存放路径：`_vault/books/`
3. 用户存入后，生成 `_vault/_index.md` 新行预览：

```
| V00X | 书名 | book | books/{filename} | 豆瓣链接 | YYYY-MM-DD | 作者名 |
```

4. 用户确认后追加到 `_vault/_index.md`
5. 更新相关笔记的 `vault_ref` 字段

### 3b. 自动搜索并下载（用户没有电子版）

#### Preflight 检查

首次使用前运行环境检查：

```bash
python3 tools/scripts/zlib-download/book.py preflight
```

如果 `ready: false`，引导用户：

| 问题 | 解决 |
|------|------|
| `requests` 缺失 | `pip3 install requests` |
| Z-Library 未配置 | 引导用户编辑 `.config/book-tools/.env`，填入 `ZLIB_EMAIL` 和 `ZLIB_PASSWORD` |
| Z-Library token 过期 | 删除 `.config/book-tools/config.json`，脚本会用 .env 中的凭证重新登录 |
| Anna's Archive 未配置 | 可选——需要在 Anna's Archive 捐赠获取 API key |

**重要**：不要在聊天中直接问用户要密码。告诉用户自己编辑 .env 文件。

#### Z-Library EAPI 网络/SSL 连通性问题

如果执行 Z-Library 搜索、详情或下载命令时，遇到以下网络层错误：

- `SSL`
- `SSLError`
- `CERTIFICATE_VERIFY_FAILED`
- `UNEXPECTED_EOF_WHILE_READING`
- `record layer failure`
- `ReadTimeout`
- `ConnectTimeout`
- Z-Library EAPI 域名无法访问

不要继续反复重试，也不要把它误判为“书籍不存在”。

此时直接向用户返回：

> 当前无法连接 Z-Library EAPI，可能是本地网络、代理、证书或 Z-Library 域名连通性问题。请先检查当前网络是否能正常访问 Z-Library，或切换网络 / 配置代理后再重试。

如果用户只是想确认 Z-Library 上是否有某本书，可以改用公开搜索页做只读查询；但不要在 EAPI 不通的情况下继续尝试下载。

#### 搜索

```bash
# 自动选择后端（先 Z-Library，搜不到再 Anna's Archive）
python3 tools/scripts/zlib-download/book.py search "书名" --limit 10

# 中文书籍
python3 tools/scripts/zlib-download/book.py search "书名" --source zlib --lang chinese --limit 5

# 指定格式
python3 tools/scripts/zlib-download/book.py search "书名" --source zlib --ext pdf --limit 5
```

将搜索结果以表格展示：

```
| # | 标题 | 作者 | 年份 | 格式 | 大小 |
|---|------|------|------|------|------|
| 1 | ... | ... | ... | pdf | 22 MB |
```

问用户："要下载哪一本？（输入编号）"

#### 下载

```bash
# Z-Library
python3 tools/scripts/zlib-download/book.py download --source zlib --id {id} --hash {hash} -o "_vault/books/"

# Anna's Archive
python3 tools/scripts/zlib-download/book.py download --source annas --hash {hash} --filename "{slug}.pdf" -o "_vault/books/"
```

注意：`-o` 路径使用知识库的 `_vault/books/` 目录，直接下载到位。

#### 下载完成后

1. 确认文件已存入 `_vault/books/`
2. 按命名规范重命名（如有必要）：`{english-slug}.{ext}`
3. 生成 `_vault/_index.md` 新行预览并追加
4. 更新相关笔记的 `vault_ref` 字段
5. 告知用户完成：

```
[书籍存档] 完成！
书名：{title}
作者：{author}
路径：_vault/books/{filename}
大小：{size}
索引 ID：V00X
```

### 3c. 降级方案（搜索无结果）

如果 Z-Library 和 Anna's Archive 都搜不到：

1. 提供购买/获取渠道链接：
   - 微信读书、Kindle、多看、得到
   - 京东、当当、Amazon
   - 公版书：Project Gutenberg、标准电子书
2. 在 `_vault/_index.md` 中先创建条目，本地路径填 `-`，外部链接填最佳获取渠道
3. 用户后续获取到电子版后可补充

## 注意事项

- 所有写入操作遵循 SOUL.md 的确认规则
- ID 分配：读取 `_vault/_index.md` 最后一行 ID，递增
- Z-Library 每日有下载限额（免费账号通常 10 本/天），下载前可用 `info` 命令查看书籍详情避免浪费额度
- 中文书搜索加 `--lang chinese` 效果更好
- 凭证存储在 `.config/book-tools/.env`（知识库根目录下），不要在聊天中传输密码
- 遇到 Z-Library EAPI 网络/SSL 连通性错误时，直接提示用户检查网络与 Z-Library 连接，不要把该错误解释为搜索无结果
