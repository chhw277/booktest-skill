---
name: booktest
description: 教材课后题答案制作 — 读题、生成LaTeX、格式管理、编译PDF、交叉验证
allowed-tools: Bash(*), Read(*), Write(*), Edit(*), Glob(*), Grep(*), Agent(*), WebFetch(*), WebSearch(*)
---

# /booktest — 教材课后题答案制作

为教材课后题生成LaTeX格式的完整答案（题目→作答过程→应试要点），编译为PDF。

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

### 2. 每批做完汇报

批量做题时，每做完一批（建议3-5题）：
1. 报告已完成的题号和数量
2. 显示剩余未做题号
3. 问用户：继续做 / 先编译看看 / 先验证

```
我:   "已完成 2.10, 2.11, 2.13（3题）。
       剩余: 2.15, 2.17, 2.19, 2.21, 2.23, 2.24（6题）。
       继续做下一批？还是先编译看看效果？"
```

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
3. "上传到哪里？" — 默认自动归档到 `D:\教材\书名\` 下

**自动归档结构**：
```
D:\教材\书名\
├── 原书.pdf          ← 用户上传的整本PDF
├── 源文件\书名_答案.tex  ← 自动生成
├── 图片\             ← 如用户提供图片
├── OCR\              ← 如需OCR处理
└── build\            ← 编译中间产物
```

**上传后自动处理**：
- PDF → 存为 `原书.pdf`
- 图片 → 存到 `图片\` 目录
- docx → 转存或提取文字
- 章节PDF → 拆分到对应位置

**继续已有书籍**：
- 检测到memory中有记录 → 直接加载配置，不问上传
- 显示当前进度，问"从哪里继续？"

**做完一本开始下一本**：
- 当前书全部完成 → 提示"这本书做完了，要开始新书吗？"
- 用户确认后 → 进入新书启动引导

## 项目配置

根据memory文件 `hw_ed` 自动加载项目信息。核心路径：

- **通用脚本目录**: `D:\教材\通用脚本\`
- **项目目录**: `D:\教材\{书名}\`
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

## 工作流程

### 做新题

1. **读题**: 用 `get_ocr.py` 定位OCR文本，或读取用户提供的PDF/图片
   ```
   python D:/教材/通用脚本/get_ocr.py D:/教材/电动力学 2.10
   ```
   如需读图片：用 Read 工具直接读 page_XXX.png

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

对每个题号重复"做新题"流程，全部做完后统一编译。

### 格式检查

```
python D:/教材/通用脚本/check_format.py "D:/教材/电动力学/源文件/电动力学_答案.tex"
```

### 格式修复

```
python D:/教材/通用脚本/fix_format.py "D:/教材/电动力学/源文件/电动力学_答案.tex"
```

先 `--dry-run` 预览，确认后再执行。

### 编译PDF

```
python D:/教材/通用脚本/compile.py "D:/教材/电动力学/源文件/电动力学_答案.tex" --open
```

### 查看进度

```
python D:/教材/通用脚本/progress.py "D:/教材/电动力学/源文件/电动力学_答案.tex"
python D:/教材/通用脚本/progress.py "D:/教材/电动力学/源文件/电动力学_答案.tex" --missing
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

### API配置

配置文件：`D:\教材\通用脚本\config.json`

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
python D:/教材/通用脚本/verify.py <tex文件> --problem 2.10    验证单题
python D:/教材/通用脚本/verify.py <tex文件> --all            验证全部
python D:/教材/通用脚本/verify.py <tex文件> --gemini 2.10    生成Gemini提示词
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
python D:/教材/通用脚本/verify.py <tex文件> --gemini        全书检查指令
python D:/教材/通用脚本/verify.py <tex文件> --gemini 2.10   单题检查指令
```

如果错误，请给出正确解答。
```

## 注意事项

1. **不编造题目**: 必须从OCR/原书/用户输入获取题目，不凭记忆写题
2. **公式准确**: 推导过程要完整，不能跳步
3. **格式严格**: 三大标记、enumerate、itemize、vspace缺一不可
4. **先读后写**: 修改已有内容前必须先 Read 确认当前状态
5. **验证优先**: 批量做完后必须经过交叉验证才能交付
