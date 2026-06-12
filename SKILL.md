---
name: booktest
description: |
  教材课后题答案制作 — 从PDF/图片/OCR读取题目，生成LaTeX三段式答案（题目→作答过程→应试要点），编译PDF，多模型交叉验证。
  触发词：做题、做课后题、课后题答案、编译、检查格式、修复格式、验证、进度、补充应试要点。
  不要用于：从零写论文/报告（用其他写作skill）、非LaTeX格式的作业、编程题自动评测。
allowed-tools: Bash(*), Read(*), Write(*), Edit(*), Glob(*), Grep(*), Agent(*), WebFetch(*), WebSearch(*)
---

# /booktest — 教材课后题答案制作

为教材课后题生成LaTeX格式的完整答案（题目→作答过程→应试要点），编译为PDF。支持从PDF、图片、OCR文本读取题目，通过DeepSeek/Claude/GPT多模型交叉验证确保答案正确。

## 触发方式

```
/booktest 做2.10          ← 做指定题目
/booktest 做第2章剩余      ← 批量做题
/booktest 检查格式         ← 格式检查
/booktest 修复格式         ← 格式修复
/booktest 编译            ← 编译PDF
/booktest 进度            ← 查看完成情况
/booktest 修改2.10        ← 修改已有题目
/booktest 补充应试要点     ← 补充待补充的应试要点
/booktest 验证            ← 交叉验证答案
```

## 引导规则

使用skill时必须遵循以下引导流程，不能直接执行：

### 1. 做题前确认题目

收到做题指令后，**先**：
1. 读取OCR或原书，获取题目内容
2. 向用户展示题目内容
3. 等用户确认"题目对了"再开始解题

```
用户: /booktest 做2.10
我:   读取OCR... 展示题目内容...
      "这是题2.10的内容，确认无误后我开始解题。"
用户: 对的 / 不对，题目是...
我:   开始解题
```

### 2. 每批做完自动验证

批量做题时，每做完一批（建议3-5题）：
1. **自动编译** — 生成PDF
2. **自动验证** — 调用 `verify.py` 用DeepSeek验证刚做的题目
3. **报告结果** — 展示验证通过/有问题的题目
4. 问用户：继续做下一批 / 修正问题 / 先看看效果

```
我:   "已完成 2.10, 2.11, 2.13（3题），正在编译和验证..."
      [自动编译]
      [自动验证: verify.py --problem 2.10 --problem 2.11 --problem 2.13]
      "验证结果：
       ✅ 题2.10 正确
       ✅ 题2.11 正确
       ❌ 题2.13 积分限错误，应为0到a
       剩余: 2.15, 2.17, 2.19, 2.21, 2.23, 2.24（6题）。
       修正2.13后继续？还是先跳过？"
```

**自动验证流程**：
1. 编译PDF：`python scripts/compile.py "tex文件"`
2. 验证刚做的题目：`python scripts/verify.py "tex文件" --problem X.Y --problem X.Z ...`
3. 验证用DeepSeek API（需先配置 `scripts/config.json`，见下方"配置说明"）
4. 发现错误 → 展示错误原因和正确解答 → 等用户确认修改

### 3. 验证后确认修改

交叉验证发现问题时：
1. 展示错误题目、错误原因、正确解答
2. 等用户确认"改"才修改tex文件
3. 不自动修改

```
我:   "验证结果：
       ❌ 题2.10: 积分限错误，应为0到a而非0到r
       正确解答: [展示]
       确认修改？"
用户: 改
我:   修改tex文件
```

### 不需要引导的场景

以下场景直接执行，不用问：
- `/booktest 检查格式` — 直接跑脚本报告结果
- `/booktest 修复格式` — 直接修复（先dry-run）
- `/booktest 编译` — 直接编译
- `/booktest 进度` — 直接显示
- 用户明确说"直接做"/"不用确认" — 跳过引导

### 4. 新书启动引导

**触发条件**（满足任一即为"新书"）：
- memory中没有这本书的记录
- 用户主动说"开始新书"/"换一本书"

**启动时必须询问**：
1. "你要做哪本书？" — 获取书名、作者、出版社
2. "你有什么材料？" — 原书PDF / 章节PDF / docx / 图片
3. "上传到哪里？" — 默认自动归档到 `项目目录/` 下

**自动归档结构**：
```
项目目录/
├── 原书.pdf          ← 用户上传的整本PDF
├── 源文件\书名_答案.tex  ← 自动生成
├── 图片\             ← 如用户提供图片
├── OCR\              ← 如需OCR处理
└── build\            ← 编译中间产物
```

**上传后自动处理**：
- PDF → 存为 `原书.pdf`，自动检测类型并提取题目
- 文字型PDF → pdfplumber直接提取文字到 `OCR\`
- 扫描型PDF → PaddleOCR提取文字 + 保存页面图片到 `图片\`，供视觉AI读取公式/电路图
- 图片 → 存到 `图片\` 目录，视觉AI直接读取
- docx → python-docx提取文字
- 章节PDF → 拆分到对应位置

**继续已有书籍**：
- 检测到memory中有记录 → 直接加载配置，不问上传
- 显示当前进度，问"从哪里继续？"

**做完一本开始下一本**：
- 当前书全部完成 → 提示"这本书做完了，要开始新书吗？"
- 用户确认后 → 进入新书启动引导

## 项目配置

首次使用时通过新书启动引导获取项目信息，之后根据memory自动加载。核心路径：

- **脚本目录**: `scripts/`（随skill安装）
- **项目目录**: 用户指定（如 `D:/教材/电动力学/`）
  - `原书.pdf` — 原始扫描PDF
  - `图片\page_XXX.png` — 页面图片
  - `OCR\page_XXX.txt` — OCR文本
  - `源文件\{书名}_答案.tex` — LaTeX源文件
  - `答案.pdf` — 编译输出
  - `build\` — 编译中间产物

## LaTeX格式规范

### 文件头
```latex
\documentclass[12pt]{article}
\usepackage[UTF8]{ctex}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{tikz}
\usepackage{geometry}
\geometry{a4paper, margin=2.5cm}

\title{书名课后题答案 \\ {\normalsize 作者 · 出版社}}
\author{}
\date{}

\begin{document}
\maketitle
\begin{center}
\textit{署名行}
\end{center}
\vspace{1cm}
```

### 章节结构
```latex
\newpage
\section*{第X章 章节名}
```

### 每题结构（严格遵守）
```latex
%===========================================
% 题X.Y
%===========================================
\subsection*{题 X.Y}

\textbf{【题目】}

题目原文（保留原书编号(1)(2)(3)）

\textbf{【作答过程】}

\begin{enumerate}
    \item \textbf{小标题}    正文和公式混排
    \item \textbf{小标题}    ...
\end{enumerate}

\textbf{【应试要点】}

\begin{itemize}
    \item \textbf{考查知识点}：xxx
    \item \textbf{关键}：xxx
    \item \textbf{易错点}：xxx
\end{itemize}

\vspace{1cm}
```

### 格式规则（不可违反）

1. `\textbf{【题目】}`、`\textbf{【作答过程】}`、`\textbf{【应试要点】}` 后**必须有空行**
2. 作答过程**必须**用 `\begin{enumerate}` 包裹（概念简答题除外）
3. 应试要点**必须**用 `\begin{itemize}` 包裹，**固定三条**
4. 每题最后**必须**有 `\vspace{1cm}`
5. 公式用 `\[ ... \]`（不用`$$`），行内用 `$...$`
6. 矢量用 `\mathbf{}` 或 `\hat{\mathbf{}}`
7. 最后一题后用 `\newpage` 分章
8. 中文用ctex默认字体（宋体/黑体），12pt

### 分组题目处理

原书中连续的小题（如5.5-5.7概念题）：
- 每题独立一个 `\subsection*{题 X.Y}`
- 各自完整包含三大标记
- 不要合并为一个subsection

## 题目提取

支持三种文档格式，自动选择提取方式：

### 文字型PDF（pdfplumber直接提取，100%准确）
```
python scripts/extract.py "文件.pdf" -d "项目目录" -v
```

### 扫描型PDF（自动检测 → PaddleOCR提文字 + 保存图片供视觉AI）
```
python scripts/extract.py "文件.pdf" -d "项目目录" -v
```
- 自动检测PDF类型：pdfplumber提取不到文字 → 切换扫描模式
- PaddleOCR提取文字内容
- 页面图片保存到 `书名/图片/` 目录，供视觉AI读取公式和电路图
- 手动指定类型：`--type text` 或 `--type scanned`

### Word文档（python-docx直接提取）
```
python scripts/extract.py "文件.docx" -d "项目目录" -v
```

### 图片（视觉AI直接读取）
```
python scripts/extract.py "图片.png" -d "项目目录" -v
```

### 提取流程
1. 运行 `extract.py`，自动检测格式并提取
2. 文字型PDF → 直接得到题目文字
3. 扫描型PDF → OCR文字 + 页面图片
4. **视觉AI辅助**：公式、电路图、示意图由我直接读图片确认
5. 提取结果保存到 `书名/OCR/` 目录（txt文件）

## 工作流程

### 做新题

1. **读题**: 用 `extract.py` 提取题目，或用 `get_ocr.py` 定位已有OCR文本
   ```
   python scripts/extract.py "作业.pdf" -d "项目目录" -v
   python scripts/get_ocr.py 项目目录 2.10
   ```
   扫描型PDF：用 Read 工具读 `图片/page_XXX.png` 确认公式和电路图

2. **理解**: 分析题目，确定解题方法

3. **生成LaTeX**: 按格式规范生成完整的三段式答案
   - 作答过程要有清晰的步骤编号
   - 公式推导要完整
   - 应试要点要针对该题特点

4. **写入tex**: 用 Edit 工具将答案插入到 tex 文件的正确位置
   - 找到该章的 `\section*` 或上一题的 `\vspace{1cm}` 之后
   - 保持题号顺序

5. **更新进度**: 修改memory文件中的进度记录

### 批量做题

对每个题号重复"做新题"流程。每做完一批（3-5题）：
1. 自动编译PDF
2. 自动调用 `verify.py` 验证刚做的题目（DeepSeek API）
3. 报告验证结果，发现错误立即指出
4. 问用户：继续下一批 / 修正问题

### 做完全章

全部题目做完后：
1. 全章编译
2. 全章验证：`python scripts/verify.py "tex文件" --all`
3. 汇总报告：✅正确 / ⚠️小问题 / ❌错误
4. 有错误的题目展示修正方案，等用户确认后修改

### 格式检查

```
python scripts/check_format.py "源文件/xxx_答案.tex"
```

### 格式修复

```
python scripts/fix_format.py "源文件/xxx_答案.tex"
```

先 `--dry-run` 预览，确认后再执行。

### 编译PDF

```
python scripts/compile.py "源文件/xxx_答案.tex" --open
```

### 查看进度

```
python scripts/progress.py "源文件/xxx_答案.tex"
python scripts/progress.py "源文件/xxx_答案.tex" --missing
```

### 修改已有题目

1. 定位到 tex 文件中该题的位置
2. 读取现有内容
3. 重新生成或修正答案
4. 用 Edit 替换
5. 触发验证流程

### 补充应试要点

1. 扫描tex中含"待补充"的题目
2. 根据题目和作答内容生成应试要点（考查知识点+关键+易错点）
3. 用 Edit 替换占位内容

## 交叉验证流程

批量做完后触发验证，确保答案正确。

### 验证方式

1. **DeepSeek API** — Python调用，自动验证
2. **中转站(Claude)** — Python调用，自动验证
3. **GPT API** — Python调用，自动验证
4. **Gemini网页端** — 生成提示词，用户手动粘贴验证

### 配置说明

1. 复制 `scripts/config.example.json` 为 `scripts/config.json`
2. 填入你的API key（至少配置DeepSeek，其他可选）
3. 确保 `pdflatex` 在系统PATH中（安装MiKTeX或TeX Live）

配置文件：`scripts/config.json`

```json
{
    "deepseek": {
        "api_key": "sk-xxx",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat"
    },
    "relay": {
        "api_key": "你的中转站key",
        "base_url": "中转站地址",
        "model": "模型名"
    },
    "gpt": {
        "api_key": "sk-xxx",
        "base_url": "https://api.openai.com",
        "model": "gpt-4o"
    }
}
```

### 验证命令

```
python scripts/verify.py <tex文件> --problem 2.10    验证单题
python scripts/verify.py <tex文件> --all            验证全部
python scripts/verify.py <tex文件> --gemini 2.10    生成Gemini提示词
```

### 验证内容

对每道题检查：
- 物理概念和图像是否正确
- 数学推导是否有误（符号、系数、积分等）
- 边界条件是否正确应用
- 最终结果是否与教材或标准结果一致

### 验证输出

对每道题给出判断：
- ✅ 正确
- ⚠️ 有小问题（指出并给出修正）
- ❌ 错误（指出错误原因并给出正确解答）

### 错误处理

发现错误时：
1. 先向用户展示错误原因和正确解答
2. 用户确认后再修正 tex 文件
3. 重新编译验证

### Gemini网页端验证

生成检查指令，复制到 Gemini 网页端后上传 PDF 答案文件：

```
python scripts/verify.py <tex文件> --gemini        全书检查指令
python scripts/verify.py <tex文件> --gemini 2.10   单题检查指令
```

如果错误，请给出正确解答。
```

## 通用脚本

存放在 `scripts/`：
- `extract.py` — 题目提取（PDF/Word/图片，自动检测PDF类型）
- `get_ocr.py` — 读取已有OCR题目
- `check_format.py` — 格式检查
- `fix_format.py` — 格式修复
- `compile.py` — 编译+清理中间产物到build/
- `progress.py` — 进度统计
- `verify.py` — 交叉验证（多模型对比）
- `config.json` — API配置

## 注意事项

1. **不编造题目**: 必须从OCR/原书/用户输入获取题目，不凭记忆写题
2. **公式准确**: 推导过程要完整，不能跳步
3. **格式严格**: 三大标记、enumerate、itemize、vspace缺一不可
4. **先读后写**: 修改已有内容前必须先 Read 确认当前状态
5. **验证优先**: 批量做完后必须经过交叉验证才能交付
