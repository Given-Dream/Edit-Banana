<p align="center">
  <img src="/static/banana.jpg" width="180" alt="Edit Banana Logo"/>
</p>

<h1 align="center">🍌 Edit Banana</h1>
<h3 align="center">将静态图像转换为可编辑 Draw.io 文件</h3>

<p align="center">
面向本地使用场景的图像转 Draw.io 工具。<br/>
基于 SAM3 分割与 OCR 流程，将流程图、结构图、示意图中的图形与文字拆分重建为可编辑的 Draw.io XML。
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/License-Apache_2.0-2F80ED?style=flat-square&logo=apache&logoColor=white" alt="License"/>
  <img src="https://img.shields.io/badge/GPU-CUDA%20Recommended-76B900?style=flat-square&logo=nvidia" alt="CUDA"/>
</p>

---

## 项目说明

这是基于原始 Edit-Banana 项目整理的本地可运行版本，重点做了以下调整：

- 适配本地单机运行
- 补齐 SAM3 安装路径与配置说明
- 改为轻量网页入口，不再依赖单独 `frontend` 工程
- 一次上传，自动同时生成
  - 带文字版本
  - 不带文字版本
  - 识别文字 TXT
- 输出结果直接保存在 `output/` 目录中

---

## 当前版本特性

### 1. 图像转 Draw.io
上传一张流程图、结构图、示意图图片，输出可编辑的 `.drawio.xml` 文件。

### 2. 同时生成两套结果
每次转换会在 `output/` 下生成一个结果文件夹，包含：

- 带文字版 Draw.io
- 不带文字版 Draw.io
- 识别文字 TXT

### 3. 本地网页入口
运行 `python server_pa.py` 后，直接访问：

```bash
http://127.0.0.1:8000
```

页面中点一次“开始转换”即可。

### 4. OCR 可启用
当前版本支持本地 Tesseract OCR。启用后可以识别图片中的文字，并写入最终结果与 TXT 文件。

### 5. 本地 API 文档
接口文档地址：

```bash
http://127.0.0.1:8000/docs
```

---

## 项目结构

```text
Edit-Banana/
├── config/                  # 配置文件
├── docs/                    # 说明文档
├── flowchart_text/          # 文本处理相关模块
├── input/                   # 运行时临时输入目录
├── models/                  # 模型权重与相关资源
├── modules/                 # 主流程模块
├── output/                  # 输出目录
├── prompts/                 # 提示词配置
├── sam3/                    # 仓库自带 sam3 相关目录
├── sam3_output/             # SAM3 中间结果
├── sam3_service/            # SAM3 服务代码
├── sam3_src/                # 单独克隆安装的官方 SAM3 源码
├── scripts/                 # 工具脚本
├── static/                  # 本地网页静态文件
│   ├── banana.jpg
│   ├── demo/
│   └── index.html
├── main.py                  # 主处理流程入口
├── server_pa.py             # FastAPI 服务入口
├── requirements.txt         # Python 依赖
└── README.md
```

---

## 环境要求

建议环境：

- Python 3.10 及以上
- Windows 10/11 或 Linux
- CUDA 可用显卡
- Git
- Conda 或 venv

---

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/Given-Dream/Edit-Banana.git
cd Edit-Banana
```

### 2. 创建环境

#### conda 方式
```bash
conda create -n edit-banana python=3.10 -y
conda activate edit-banana
```

#### venv 方式
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

### 3. 安装基础依赖

```bash
pip install -r requirements.txt
```

---

## SAM3 安装

当前版本不能只放权重文件，还需要单独安装官方 SAM3 Python 包。

### 1. 克隆官方 SAM3 源码
注意目录名不要叫 `sam3`，避免与项目目录冲突。

```bash
git clone https://github.com/facebookresearch/sam3.git sam3_src
```

### 2. 安装 SAM3
进入源码目录后安装：

```bash
cd sam3_src
pip install -e .
cd ..
```

### 3. 复制 BPE 文件
将官方仓库中的 BPE 文件复制到 `models/` 目录：

#### Windows PowerShell
```powershell
Copy-Item .\sam3_src\assets\bpe_simple_vocab_16e6.txt.gz .\models\bpe_simple_vocab_16e6.txt.gz
```

#### Git Bash
```bash
cp sam3_src/assets/bpe_simple_vocab_16e6.txt.gz models/bpe_simple_vocab_16e6.txt.gz
```

### 4. 放置模型权重
将 SAM3 权重文件放到：

```text
models/sam3_ms/sam3.pt
```

如果目录不存在，请先手动创建：

```bash
mkdir -p models/sam3_ms
```

### 5. 检查导入
安装成功后，可以执行：

```bash
python -c "from sam3.model_builder import build_sam3_image_model; print('OK')"
```

---

## OCR 安装

当前版本推荐使用 Tesseract。

### 1. 安装 Tesseract
Windows 可以安装到类似路径：

```text
D:\soft\Tesseract-OCR\tesseract.exe
```

### 2. 确认命令可用

```bash
tesseract --version
```

### 3. 安装 Python 包

```bash
pip install pytesseract
```

### 4. 中文识别
如果需要中文识别，请确认 Tesseract 安装中包含：

- `eng`
- `chi_sim`

可以执行检查：

```bash
tesseract --list-langs
```

---

## 配置文件

将示例配置复制为正式配置：

#### Windows PowerShell
```powershell
Copy-Item .\config\config.yaml.example .\config\config.yaml
```

#### Git Bash
```bash
cp config/config.yaml.example config/config.yaml
```

重点确认 `config/config.yaml` 中这两项路径正确：

```yaml
sam3:
  checkpoint_path: "models/sam3_ms/sam3.pt"
  bpe_path: "models/bpe_simple_vocab_16e6.txt.gz"
```

---

## 启动方式

### 1. 启动网页服务

```bash
python server_pa.py
```

启动成功后访问：

```bash
http://127.0.0.1:8000
```

### 2. 打开接口文档

```bash
http://127.0.0.1:8000/docs
```

---

## 使用方式

### 网页方式
1. 启动服务
2. 浏览器打开 `http://127.0.0.1:8000`
3. 选择一张图片
4. 点击“开始转换”
5. 等待处理完成
6. 在页面中查看输出目录

### 命令行方式
也可以直接运行主流程：

```bash
python main.py -i input/test.png
```

---

## 输出说明

每次上传后，程序会在 `output/` 下生成一个结果文件夹，目录名为：

```text
原文件名_时间戳
```

如果原文件名包含不适合直接作为路径的字符，程序会自动转成安全名称。

例如：

```text
output/
└── flowchart_20260320_213015/
    ├── flowchart_20260320_213015_with_text.drawio.xml
    ├── flowchart_20260320_213015_no_text.drawio.xml
    └── flowchart_20260320_213015_recognized_text.txt
```

文件说明：

- `*_with_text.drawio.xml`
  - 包含文字结果的可编辑 Draw.io 文件

- `*_no_text.drawio.xml`
  - 不包含文字结果的可编辑 Draw.io 文件

- `*_recognized_text.txt`
  - OCR 识别出的纯文本内容

---

## 当前网页行为

当前版本的网页是轻量本地页面，位于：

```text
static/index.html
```

它不是 React 工程，不需要再执行：

```bash
cd frontend
npm install
npm run dev
```

只要运行：

```bash
python server_pa.py
```

就可以直接访问网页入口。

---

## 常见问题

### 1. `/` 打开后只有 JSON，没有页面
说明 `static/index.html` 没有正确返回，重点检查：

- `static/index.html` 是否存在
- `server_pa.py` 是否导入了 `FileResponse`
- 根路由是否返回 `FileResponse(index_path)`

### 2. `No module named 'sam3.model_builder'`
说明官方 SAM3 包还没有正确安装。请重新执行：

```bash
cd sam3_src
pip install -e .
```

### 3. `No such file or directory: models\bpe_simple_vocab_16e6.txt.gz`
说明 BPE 文件没有复制到 `models/` 目录。

### 4. `tesseract is not installed or it's not in your PATH`
说明 Tesseract 尚未安装，或者系统环境变量没有生效。

### 5. 图片路径乱码导致 OpenCV 读图失败
当前版本已经对上传文件名做了安全处理。若仍报错，请尽量使用英文文件名测试。

---

## 建议加入 `.gitignore` 的内容

```gitignore
__pycache__/
*.pyc
*.pyo
*.pyd

.venv/
venv/
env/

.idea/
.vscode/
.DS_Store
Thumbs.db

input/
output/
sam3_output/
*.log

models/**/*.pt
models/**/*.pth
models/**/*.bin
models/**/*.ckpt
models/**/*.safetensors
models/**/*.gz
```

---

## 适用场景

- 流程图转 Draw.io
- 技术架构图重建
- 示意图元素拆分与重构
- 图形和文字分离后编辑
- 生成带文字版与不带文字版两套结果

---

## 后续可扩展方向

- 更稳的箭头连接恢复
- 更高质量的公式识别
- 批量图片处理
- PDF 直接转换
- 更完整的本地网页交互
- 导出为更多格式

---

## 致谢

本项目基于 Edit-Banana 进行本地整理与适配。  
感谢原项目与相关依赖库提供的基础能力，包括但不限于：

- SAM3
- OpenCV
- FastAPI
- Tesseract
- Draw.io 相关 XML 生成流程

---

## License

本项目沿用原项目许可证，请以仓库中的 `LICENSE` 文件为准.

