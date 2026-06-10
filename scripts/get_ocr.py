"""
OCR题目读取脚本 — 根据题号定位并读取OCR文本或页面图片
用法: python get_ocr.py <书名目录> <题号>
示例: python get_ocr.py D:/教材/电动力学 2.10
"""
import sys
import os
import re

# 各章习题页码映射（韩奎《电动力学》）
CHAPTER_PAGES = {
    1: (31, 33),
    2: (76, 80),
    3: (114, 115),
    4: (128, 129),
    5: (186, 188),
    6: (218, 221),
    7: (248, 254),
}

def get_problem_info(book_dir, problem_num):
    """根据题号获取OCR文本和图片路径"""
    # 解析题号 X.Y
    match = re.match(r'(\d+)\.(\d+)', problem_num)
    if not match:
        print(f'❌ 题号格式错误: {problem_num}，应为 X.Y（如 2.10）')
        return None

    ch = int(match.group(1))
    num = int(match.group(2))

    # 获取该章的习题页码范围
    if ch not in CHAPTER_PAGES:
        print(f'❌ 章节 {ch} 超出范围（1-7）')
        return None

    start_page, end_page = CHAPTER_PAGES[ch]

    # 构建OCR目录和图片目录路径
    ocr_dir = os.path.join(book_dir, 'OCR')
    img_dir = os.path.join(book_dir, '图片')

    # 查找该章所有OCR文件
    ocr_files = []
    for page in range(start_page, end_page + 1):
        ocr_path = os.path.join(ocr_dir, f'page_{page:03d}.txt')
        img_path = os.path.join(img_dir, f'page_{page:03d}.png')
        if os.path.exists(ocr_path):
            with open(ocr_path, 'r', encoding='utf-8') as f:
                text = f.read()
            ocr_files.append({
                'page': page,
                'ocr_path': ocr_path,
                'img_path': img_path if os.path.exists(img_path) else None,
                'text': text,
            })

    if not ocr_files:
        print(f'❌ 未找到第{ch}章的OCR文件（page_{start_page:03d}-page_{end_page:03d}）')
        return None

    # 尝试在OCR文本中定位具体题目
    target = f'{ch}.{num}'
    target_patterns = [
        f'题{target}',
        f'题 {target}',
        f'{target}',
        f'{ch}.{num}',
    ]

    located = None
    for ocr in ocr_files:
        for pattern in target_patterns:
            if pattern in ocr['text']:
                located = ocr
                break
        if located:
            break

    # 输出结果
    print(f'📖 题 {ch}.{num}（第{ch}章）')
    print(f'   习题页范围: page_{start_page:03d} - page_{end_page:03d}')
    print(f'   共 {len(ocr_files)} 页OCR文本')

    if located:
        print(f'   📍 定位到: page_{located["page"]:03d}')
        print(f'   OCR路径: {located["ocr_path"]}')
        if located['img_path']:
            print(f'   图片路径: {located["img_path"]}')

        # 提取题目相关文本（从定位点开始截取）
        for pattern in target_patterns:
            idx = located['text'].find(pattern)
            if idx >= 0:
                # 截取从题目开始到下一个题目的内容
                excerpt = located['text'][idx:]
                # 找下一个题号
                next_problem = re.search(r'\n\d+\.\d+', excerpt[10:])
                if next_problem:
                    excerpt = excerpt[:10 + next_problem.start()]
                print(f'\n--- OCR文本片段 ---')
                print(excerpt[:2000].strip())
                print(f'--- 结束 ---')
                break
    else:
        print(f'   ⚠️ 未精确定位到题{target}，请手动查看以上页面的OCR文本。')

    return {
        'chapter': ch,
        'number': num,
        'pages': list(range(start_page, end_page + 1)),
        'ocr_dir': ocr_dir,
        'img_dir': img_dir,
        'located_page': located['page'] if located else None,
    }

if __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 3:
        print('用法: python get_ocr.py <书名目录> <题号>')
        print('示例: python get_ocr.py D:/教材/电动力学 2.10')
        sys.exit(1)

    book_dir = sys.argv[1]
    problem_num = sys.argv[2]
    get_problem_info(book_dir, problem_num)
