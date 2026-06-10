"""
格式检查脚本 — 扫描tex文件，报告所有格式问题
用法: python check_format.py <tex文件路径>
"""
import sys
import re

def check_format(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    issues = []
    current_section = ""
    current_problem = None
    problem_start = 0

    for i, line in enumerate(lines):
        s = line.strip()
        lineno = i + 1

        # Track section
        if s.startswith(r'\section*{') and '章' in s:
            current_section = s

        # Track problem start
        if s.startswith(r'\subsection*{题'):
            if current_problem:
                # Check previous problem's trailing vspace
                pass
            current_problem = s
            problem_start = lineno

        # Check 三大标记后是否空行
        if s.startswith(r'\textbf{【题目】}') or s.startswith(r'\textbf{【作答过程】}') or s.startswith(r'\textbf{【应试要点】}'):
            marker = s
            if i + 1 < len(lines) and lines[i + 1].strip() != '':
                issues.append({
                    'type': 'missing-blank-line',
                    'line': lineno,
                    'section': current_section,
                    'problem': current_problem,
                    'detail': f'{marker[:20]}... 后缺空行，下一行: {lines[i+1].strip()[:40]}'
                })

    # Re-scan by problem blocks
    problems = []
    current = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith(r'\subsection*{题'):
            if current:
                current['end'] = i
                problems.append(current)
            current = {
                'header': s,
                'line': i + 1,
                'section': '',
                'content_lines': [],
            }
        elif current is not None:
            current['content_lines'].append(i)
            if s.startswith(r'\section*{'):
                current['section'] = s

    if current:
        current['end'] = len(lines)
        problems.append(current)

    # Find section for each problem
    current_section = ""
    for i, line in enumerate(lines):
        if line.strip().startswith(r'\section*{') and '章' in line:
            current_section = line.strip()
        for p in problems:
            if p['line'] == i + 1:
                p['section'] = current_section

    for p in problems:
        content = ''.join(lines[p['line']:p['end']])
        header = p['header']

        # Check enumerate
        if r'\begin{enumerate}' not in content and '【作答过程】' in content:
            # Skip short concept answers
            answer_match = re.search(r'【作答过程】\s*\n(.*?)(\n\s*\\textbf|\n\s*\\vspace|\n\s*\\subsection|\Z)', content, re.DOTALL)
            if answer_match and len(answer_match.group(1).strip()) > 80:
                issues.append({
                    'type': 'missing-enumerate',
                    'line': p['line'],
                    'section': p['section'],
                    'problem': header,
                    'detail': '作答过程未包enumerate'
                })

        # Check 应试要点
        if '【应试要点】' not in content:
            issues.append({
                'type': 'missing-yingshi',
                'line': p['line'],
                'section': p['section'],
                'problem': header,
                'detail': '缺少【应试要点】'
            })

        # Check vspace{1cm}
        if r'\vspace{1cm}' not in content and r'\newpage' not in content:
            issues.append({
                'type': 'missing-vspace',
                'line': p['line'],
                'section': p['section'],
                'problem': header,
                'detail': '缺少\\vspace{1cm}'
            })

        # Check 待补充 placeholder
        if '待补充' in content:
            issues.append({
                'type': 'placeholder',
                'line': p['line'],
                'section': p['section'],
                'problem': header,
                'detail': '应试要点含"待补充"'
            })

        # Check $$ (should be \[ \])
        if '$$' in content:
            issues.append({
                'type': 'double-dollar',
                'line': p['line'],
                'section': p['section'],
                'problem': header,
                'detail': '使用了$$（应改\\[ \\])'
            })

    return issues

if __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 2:
        print('用法: python check_format.py <tex文件路径>')
        sys.exit(1)

    filepath = sys.argv[1]
    issues = check_format(filepath)

    if not issues:
        print('✅ 格式检查通过，无问题。')
    else:
        print(f'⚠️ 发现 {len(issues)} 个格式问题：\n')
        by_type = {}
        for iss in issues:
            t = iss['type']
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(iss)

        type_names = {
            'missing-blank-line': '缺空行',
            'missing-enumerate': '缺enumerate',
            'missing-yingshi': '缺应试要点',
            'missing-vspace': '缺vspace{1cm}',
            'placeholder': '待补充占位',
            'double-dollar': '使用$$',
        }

        for t, items in by_type.items():
            print(f'【{type_names.get(t, t)}】({len(items)}处)')
            for item in items[:5]:
                print(f'  L{item["line"]} {item["problem"]}: {item["detail"]}')
            if len(items) > 5:
                print(f'  ... 还有 {len(items)-5} 处')
            print()
