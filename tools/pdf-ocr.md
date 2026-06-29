# PDF-OCR — PDF 读取与文字提取

## 能力说明

当需要读取 PDF 文件并提取文字内容时，agent 需要先判断 PDF 的类型，然后选择合适的工具。

## PDF 类型判断

### 1. 文字版 PDF（可提取文字）
- PDF 内部包含可提取的文字层
- 可以直接用 `pypdf` / `PyPDF2` 等库提取

### 2. 扫描版 PDF（图片组成）
- PDF 的每一页都是扫描图片，没有文字层
- 必须使用 OCR（光学字符识别）工具将图片转为文字
- 常见于：古籍扫描、早期电子书、手动扫描文档

## 判断方法

```python
from PyPDF2 import PdfReader

reader = PdfReader('文件.pdf')
text = reader.pages[0].extract_text()

if text and len(text.strip()) > 100:
    # 文字版 PDF，可以直接提取
    print("这是文字版 PDF")
else:
    # 扫描版 PDF，需要 OCR
    print("这是扫描版 PDF，需要 OCR")
```

## 工具依赖

### 文字版 PDF
- **Python 库**：`pypdf` 或 `PyPDF2`
- **安装命令**：`pip install --user pypdf`

### 扫描版 PDF（需要 OCR）
- **系统工具**：Tesseract OCR
- **Python 库**：`pdf2image` + `pytesseract`
- **安装步骤**：
  1. **安装 Tesseract OCR 本体**
     - macOS：`brew install tesseract`
     - Linux：`sudo apt install tesseract-ocr`
     - Windows：从 [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) 下载安装包
  2. **安装 Python 库**
     ```bash
     pip install --user pdf2image pytesseract
     ```
  3. **安装语言包**（如需中文）
     - macOS：`brew install tesseract-lang`
     - Linux：`sudo apt install tesseract-ocr-chi-sim`

## 工作流

### 情况一：Agent 发现 PDF 无法提取文字

1. **判断 PDF 类型**（用上面的 Python 代码）
2. **如果是扫描版**：
   - 检查系统是否安装 Tesseract：`which tesseract`
   - 如果未安装：
     - **优先询问用户**是否允许安装 Tesseract OCR
     - 获取用户同意后，执行安装命令
     - 如果安装失败（网络问题/权限问题），告知用户并提供替代方案
3. **替代方案**：
   - 让用户将关键页面截图发来，agent 直接读取图片
   - 让用户手动在终端安装：`brew install tesseract`（macOS）

### 情况二：用户主动要求安装 OCR 能力

1. 检查当前系统环境（macOS / Linux / Windows）
2. 选择对应的安装方式
3. 如遇网络问题，提示用户：
   - 开启代理/加速器
   - 或使用国内镜像源（如中科大镜像）
4. 安装完成后验证：`tesseract --version`

## 常见问题

### Q: Tesseract 安装很慢怎么办？
- **原因**：Homebrew 需要下载很多依赖，且可能从国外源下载
- **解决**：
  - 使用国内镜像源：
    ```bash
    cd "$(brew --repo)" && git remote set-url origin https://mirrors.ustc.edu.cn/brew.git
    export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles
    ```
  - 或让用户在终端手动运行安装命令（不通过 agent 执行）

### Q: 安装中断后怎么办？
- **现象**：`Error: A brew install process has already locked...`
- **解决**：
  ```bash
  rm -f ~/Library/Caches/Homebrew/downloads/*.incomplete
  brew cleanup
  brew install tesseract
  ```

### Q: macOS 版本太老，Homebrew 不支持怎么办？
- **解决**：
  - 使用 MacPorts：`sudo port install tesseract`
  - 或让用户拍照/截图，agent 直接读取图片

## 代码示例

### 文字版 PDF 提取

```python
from PyPDF2 import PdfReader

reader = PdfReader('文件.pdf')
full_text = ''
for page in reader.pages:
    text = page.extract_text()
    if text:
        full_text += text + '\n'
print(full_text)
```

### 扫描版 PDF 提取（OCR）

```python
from pdf2image import convert_from_path
import pytesseract

# 将 PDF 转为图片列表
images = convert_from_path('文件.pdf')

# OCR 识别每一页
full_text = ''
for i, image in enumerate(images):
    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
    full_text += f'\n=== 第 {i+1} 页 ===\n{text}'
    
print(full_text)
```

## 注意事项

1. **先判断，再行动** —— 不要假设所有 PDF 都能直接提取文字
2. **OCR 准确率有限** —— 手写体、模糊扫描、特殊字体的识别效果较差
3. **大文件处理慢** —— 100+ 页的扫描 PDF OCR 可能需要几分钟
4. **优先替代方案** —— 如果用户只是需要看某几页，建议直接截图，比装 OCR 快

## 依赖汇总

| 类型 | 工具 | 安装命令 |
|------|------|----------|
| 文字版 PDF | pypdf | `pip install --user pypdf` |
| 扫描版 PDF | Tesseract | `brew install tesseract` (macOS) |
| 扫描版 PDF | pdf2image | `pip install --user pdf2image` |
| 扫描版 PDF | pytesseract | `pip install --user pytesseract` |
