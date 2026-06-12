# booktest-skill

> 把教材PDF变成经过交叉验证的LaTeX课后题答案集——从OCR到编译到验证全自动。

一个 Claude Code skill：教材课后题答案制作。支持从 PDF/图片/OCR 读取题目，自动生成「题目 → 作答过程 → 应试要点」三段式 LaTeX 答案，编译为 PDF，并通过 DeepSeek/Claude/GPT/Gemini 多模型交叉验证确保答案正确。

## 你什么时候需要它？

- 你有一本教材，想把课后题答案做成LaTeX文档
- 你手写LaTeX答案太慢，想要AI辅助生成+自动格式化
- 你做完题想自动验证答案是否正确（多模型对比）
- 你有扫描版PDF，想自动提取题目再做题

## 它会交付什么

- 完整的LaTeX答案文件（`.tex`），严格遵循三段式格式
- 编译好的PDF（`.pdf`），可直接打印或分享
- 多模型交叉验证报告（✅正确 / ⚠️小问题 / ❌错误）

## 快速开始

### 1. 安装 skill

```bash
npx skills add chhw277/booktest-skill -g
```

或手动安装：

```bash
git clone https://github.com/chhw277/booktest-skill.git
mkdir -p ~/.claude/skills/booktest
cp booktest-skill/SKILL.md ~/.claude/skills/booktest/
cp -r booktest-skill/scripts ~/.claude/skills/booktest/
```

### 2. 配置环境

```bash
# 确保 pdflatex 在 PATH 中（安装 MiKTeX 或 TeX Live）
pdflatex --version

# 配置 API key
cp ~/.claude/skills/booktest/scripts/config.example.json ~/.claude/skills/booktest/scripts/config.json
# 编辑 config.json，填入你的 DeepSeek API key
```

### 3. 开始使用

装完后对 Claude Code 说：

```
/booktest 做2.10
```

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

## 项目目录结构

```
教材书名/
├── 原书.pdf              ← 原始扫描PDF
├── 答案.pdf              ← 编译输出
├── 源文件/
│   └── 书名_答案.tex     ← LaTeX源文件
├── 图片/                 ← 页面图片（扫描型PDF）
├── OCR/                  ← OCR文本
└── build/                ← 编译中间产物
```

## 脚本说明

| 脚本 | 用途 | 用法 |
|------|------|------|
| `extract.py` | 题目提取（PDF/Word/图片） | `python extract.py "文件.pdf" -d "项目目录" -v` |
| `get_ocr.py` | 读取已有OCR题目 | `python get_ocr.py <项目目录> <题号>` |
| `check_format.py` | 格式检查 | `python check_format.py <tex文件>` |
| `fix_format.py` | 格式修复 | `python fix_format.py <tex文件> [--dry-run]` |
| `compile.py` | 编译+清理 | `python compile.py <tex文件> [--open]` |
| `progress.py` | 进度统计 | `python progress.py <tex文件> [--missing]` |
| `verify.py` | 交叉验证 | `python verify.py <tex文件> [--problem X.Y] [--all]` |

## 交叉验证

批量做完后自动进行多模型验证：

- **DeepSeek API** — 自动验证（需配置key）
- **Claude中转站** — 自动验证（需配置key）
- **GPT API** — 自动验证（需配置key）
- **Gemini网页端** — 生成提示词，手动粘贴验证

验证结果：✅ 正确 / ⚠️ 有小问题 / ❌ 错误。发现错误先展示，用户确认后再修正。

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
     每批做完：编译+验证 → 继续/修正
     验证出错：展示错误 → 确认后修改
       │
       ▼
     全部完成 → "要做新书吗？"
```

## 依赖

- Python 3.12+
- MiKTeX 或 TeX Live（pdflatex 需在 PATH 中）
- pdfplumber（文字型PDF提取）
- PaddleOCR（扫描型PDF提取，可选）
- 至少一个AI API key（DeepSeek推荐）

## License

MIT
