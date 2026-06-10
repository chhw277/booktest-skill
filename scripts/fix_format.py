"""
格式修复脚本 — 自动修复tex文件中的格式问题
用法: python fix_format.py <tex文件路径> [--dry-run]
选项: --dry-run 只报告不修改
"""
import sys
import re

def fix_format(filepath, dry_run=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    fixes = []

    # 1. 三大标记后缺空行
    for marker in ['【题目】', '【作答过程】', '应试要点】']:
        pattern = rf'(\\textbf\{{{re.escape(marker)}\}})\n(?!\n)'
        count = len(re.findall(pattern, content))
        if count > 0:
            content = re.sub(pattern, r'\1\n\n', content)
            fixes.append(f'三大标记后补空行: {count}处')

    # 2. vspace{0.5cm} → vspace{1cm}
    count = content.count(r'\vspace{0.5cm}')
    if count > 0:
        content = content.replace(r'\vspace{0.5cm}', r'\vspace{1cm}')
        fixes.append(f'vspace 0.5cm→1cm: {count}处')

    # 3. $$ → \[ \] (独立公式)
    # 只处理独占一行的 $$
    pattern = r'^\$\$\s*\n(.*?)\n\$\$\s*$'
    count = len(re.findall(pattern, content, re.MULTILINE | re.DOTALL))
    if count > 0:
        content = re.sub(pattern, r'\\[\n\1\n\\]', content, flags=re.MULTILINE | re.DOTALL)
        fixes.append(f'$$→\\[ \\]: {count}处')

    # 4. 缺vspace{1cm}的题目（在subsection之后、下一个subsection之前）
    # 找到每个问题的结尾，如果下一行是subsection且没有vspace/newpage，补上
    lines = content.split('\n')
    new_lines = []
    i = 0
    vspace_fixes = 0
    while i < len(lines):
        new_lines.append(lines[i])
        # 如果当前行是 \subsection*{题 且前几行没有 \vspace{1cm} 或 \newpage
        if lines[i].strip().startswith(r'\subsection*{题') and i > 0:
            # 往回看，找到上一个非空行
            prev_nonblank = i - 1
            while prev_nonblank > 0 and lines[prev_nonblank].strip() == '':
                prev_nonblank -= 1
            if prev_nonblank >= 0:
                prev_line = lines[prev_nonblank].strip()
                if r'\vspace{1cm}' not in prev_line and r'\newpage' not in prev_line and r'\section*' not in prev_line:
                    # 在subsection前插入vspace
                    new_lines.insert(-1, '')
                    new_lines.insert(-1, r'\vspace{1cm}')
                    new_lines.insert(-1, '')
                    vspace_fixes += 1
        i += 1

    if vspace_fixes > 0:
        content = '\n'.join(new_lines)
        fixes.append(f'补vspace{{1cm}}: {vspace_fixes}处')

    # 5. 多余空行（超过3个连续空行压缩为2个）
    count = len(re.findall(r'\n{4,}', content))
    if count > 0:
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        fixes.append(f'清理多余空行: {count}处')

    if not fixes:
        print('✅ 无需修复，格式已正确。')
        return

    print(f'🔧 修复 {len(fixes)} 类问题：')
    for fix in fixes:
        print(f'  • {fix}')

    if dry_run:
        print('\n[dry-run模式] 未写入文件。')
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'\n✅ 已写入: {filepath}')

if __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 2:
        print('用法: python fix_format.py <tex文件路径> [--dry-run]')
        sys.exit(1)

    filepath = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    fix_format(filepath, dry_run)
