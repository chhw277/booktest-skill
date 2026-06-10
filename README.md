# booktest-skill

> Claude Code skill：教材课后题答案制作 — 读题、生成LaTeX、格式管理、编译PDF、交叉验证

## 这是什么

一个 Claude Code 自定义 skill，用于自动化制作教材课后题的 LaTeX 答案文档。支持从 OCR/图片/PDF 读取题目，自动生成包含「题目 → 作答过程 → 应试要点」三段式格式的 LaTeX 答案，编译为 PDF，并通过多模型交叉验证确保答案正确性。

## 功能一览

| 功能 | 说明 | 命令示例 |
|------|------|---------|
| 做新题 | 读取OCR/图片，生成LaTeX答案写入tex文件 | `/booktest 做2.10` |
| 批量做题 | 连续做多道题，每批汇报进度 | `/booktest 做第2章剩余` |
| 格式检查 | 扫描tex文件，报告所有格式问题 | `/booktest 检查格式` |
| 格式修复 | 自动修复格式问题（缺空行、缺enumerate等） | `/booktest 修复格式` |
| 编译PDF | 运行pdflatex，清理中间产物到build/ | `/booktest 编译` |
| 进度查看 | 显示各章完成情况，列出未做题号 | `/booktest 进度` |
| 修改题目 | 定位已有题目，修正答案 | `/booktest 修改2.10` |
| 补充应试要点 | 根据题目内容生成应试要点 | `/booktest 补充应试要点` |
| 交叉验证 | 多模型对比验证答案正确性 | `/booktest 验证` |

## 输出格式

每道题严格遵循三段式格式：

```latex
\subsection*{题 X.Y}

\textbf{【题目】}

题目原文...

\textbf{【作答过程】}

\begin{enumerate}
    \item \textbf{步骤标题}    推导过程...
    \item \textbf{步骤标题}    ...
\end{enumerate}

\textbf{【应试要点】}

\begin{itemize}
    \item \textbf{考查知识点}：xxx
    \item \textbf{关键}：xxx
    \item \textbf{易错点}：xxx
\end{itemize}

\vspace{1cm}
```

## 安装

### 1. 安装 skill

```bash
mkdir -p ~/.claude/skills/booktest
cp SKILL.md ~/.claude/skills/booktest/SKILL.md
```

### 2. 安装脚本

```bash
mkdir -p "D:/教材/通用脚本"
cp scripts/*.py "D:/教材/通用脚本/"
```

### 3. 配置项目

在项目的 memory 文件中添加教材信息（skill会自动读取）：

```markdown
## 文件路径
- 根目录：D:\教材\书名\
- 原书PDF：D:\教材\书名\原书.pdf
- OCR文本：D:\教材\书名\OCR\page_XXX.txt
- tex源文件：D:\教材\书名\源文件\书名_答案.tex
```

## 目录结构

```
D:\教材\书名\
├── 原书.pdf              ← 原始扫描PDF
├── 答案.pdf              ← 编译输出
├── 源文件\
│   └── 书名_答案.tex     ← LaTeX源文件
├── 图片\                 ← 页面图片
├── OCR\                  ← OCR文本
└── build\                ← 编译中间产物
```

## 脚本说明

| 脚本 | 用途 | 用法 |
|------|------|------|
| `check_format.py` | 格式检查 | `python check_format.py <tex文件>` |
| `fix_format.py` | 格式修复 | `python fix_format.py <tex文件> [--dry-run]` |
| `compile.py` | 编译+清理 | `python compile.py <tex文件> [--open]` |
| `progress.py` | 进度统计 | `python progress.py <tex文件> [--missing]` |
| `get_ocr.py` | OCR读取 | `python get_ocr.py <书名目录> <题号>` |

## 引导流程

```
启动 /booktest
  │
  ├─ 已有书籍 → 加载配置 → 显示进度 → "从哪里继续？"
  │
  └─ 新书 → "你要做哪本书？" → "你有什么材料？" → 自动归档
       │
       ▼
     做题前：展示题目 → 确认后解题
     每批做完：汇报进度 → 继续/编译/验证
     验证出错：展示错误 → 确认后修改
       │
       ▼
     全部完成 → "要做新书吗？"
```

## 交叉验证

批量做完后进行多模型验证（DeepSeek API + Claude中转站 + GPT API + Gemini网页端）：

- ✅ 正确
- ⚠️ 有小问题（指出并给出修正）
- ❌ 错误（指出原因并给出正确解答）

发现错误先展示，用户确认后再修正。

## 依赖

- Python 3.12+
- MiKTeX（pdflatex）
- Claude Code

## License

MIT
