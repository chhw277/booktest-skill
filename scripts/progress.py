"""
进度统计脚本 — 统计各章完成情况
用法: python progress.py <tex文件路径> [--missing]
选项: --missing 只显示未完成的题号
"""
import sys
import re

# 各章总题数（韩奎《电动力学》）
TOTAL_PER_CHAPTER = {
    1: 20,
    2: 28,
    3: 17,
    4: 7,
    5: 26,
    6: 20,
    7: 12,
}

def get_progress(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到所有 \subsection*{题 X.X}
    pattern = r'\\subsection\*\{题 (\d+)\.(\d+)\}'
    matches = re.findall(pattern, content)

    by_chapter = {}
    for ch, num in matches:
        ch = int(ch)
        num = int(num)
        if ch not in by_chapter:
            by_chapter[ch] = set()
        by_chapter[ch].add(num)

    return by_chapter

def print_progress(filepath, missing_only=False):
    by_chapter = get_progress(filepath)

    chapter_names = {
        1: '数学基础知识',
        2: '静电场',
        3: '静磁场',
        4: '电磁场的普遍规律',
        5: '电磁波的传播和辐射',
        6: '狭义相对论',
        7: '带电粒子与电磁场的相互作用',
    }

    total_done = 0
    total_all = 0

    for ch in sorted(TOTAL_PER_CHAPTER.keys()):
        total = TOTAL_PER_CHAPTER[ch]
        done = by_chapter.get(ch, set())
        done_count = len(done)
        total_done += done_count
        total_all += total

        name = chapter_names.get(ch, f'第{ch}章')
        pct = done_count / total * 100 if total > 0 else 0

        if missing_only:
            if done_count < total:
                missing = sorted(set(range(1, total + 1)) - done)
                missing_str = ', '.join(f'{ch}.{n}' for n in missing)
                print(f'第{ch}章 {name}: 缺 {total - done_count}题 → {missing_str}')
        else:
            bar = '█' * done_count + '░' * (total - done_count)
            status = '✅' if done_count == total else ''
            print(f'第{ch}章 {name}: {done_count}/{total} [{bar}] {pct:.0f}% {status}')

    if not missing_only:
        print(f'\n总计: {total_done}/{total_all} ({total_done/total_all*100:.0f}%)')

if __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 2:
        print('用法: python progress.py <tex文件路径> [--missing]')
        sys.exit(1)

    filepath = sys.argv[1]
    missing_only = '--missing' in sys.argv
    print_progress(filepath, missing_only)
