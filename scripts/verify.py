"""
交叉验证脚本 — 调用多模型验证课后题答案
用法: python verify.py <tex文件路径> [--problem 2.10] [--all]
选项: --problem 验证指定题目, --all 验证全部
"""
import sys
import os
import json
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f'❌ 配置文件不存在: {CONFIG_PATH}')
        print('请创建config.json，格式见config.example.json')
        sys.exit(1)
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def call_api(base_url, api_key, model, prompt):
    """通用API调用"""
    import requests
    try:
        resp = requests.post(
            f'{base_url}/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.1,
                'max_tokens': 4000,
            },
            timeout=60
        )
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f'❌ API调用失败: {e}'

def extract_problem(filepath, problem_num):
    """从tex文件中提取指定题目的内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到题目位置
    pattern = rf'\\subsection\*{{题 {re.escape(problem_num)}}}'
    match = re.search(pattern, content)
    if not match:
        return None

    start = match.start()
    # 找到下一个subsection或section
    next_sub = re.search(r'\\subsection\*\{题', content[start + 10:])
    next_sec = re.search(r'\\section\*\{第', content[start + 10:])

    ends = []
    if next_sub:
        ends.append(start + 10 + next_sub.start())
    if next_sec:
        ends.append(start + 10 + next_sec.start())

    end = min(ends) if ends else len(content)
    return content[start:end]

def build_verify_prompt(problem_num, problem_content):
    """构建验证提示词"""
    return f"""请验证以下课后题的解答是否正确。

仔细检查：
1. 物理概念和图像是否正确
2. 数学推导是否有误（符号、系数、积分、微分等）
3. 边界条件是否正确应用
4. 最终结果是否与教材或标准结果一致
5. 应试要点是否准确

对每道题给出判断：
- ✅ 正确
- ⚠️ 有小问题（指出并给出修正）
- ❌ 错误（指出错误原因并给出正确解答）

---

题目 {problem_num}：

{problem_content}

---

请逐项检查并给出结论。"""

def verify_problem(filepath, problem_num, config):
    """验证单个题目"""
    print(f'\n{"="*50}')
    print(f'验证题 {problem_num}')
    print(f'{"="*50}')

    # 提取题目内容
    content = extract_problem(filepath, problem_num)
    if not content:
        print(f'❌ 未找到题 {problem_num}')
        return

    prompt = build_verify_prompt(problem_num, content)

    # 调用各模型
    models = []

    if config.get('deepseek', {}).get('api_key'):
        models.append(('DeepSeek', config['deepseek']))

    if config.get('relay', {}).get('api_key'):
        models.append(('Relay(Claude)', config['relay']))

    if config.get('gpt', {}).get('api_key'):
        models.append(('GPT', config['gpt']))

    if not models:
        print('❌ 没有配置任何可用的API key')
        return

    results = {}
    for name, cfg in models:
        print(f'\n🔄 调用 {name}...')
        result = call_api(cfg['base_url'], cfg['api_key'], cfg['model'], prompt)
        results[name] = result
        print(f'\n--- {name} 结果 ---')
        print(result)


    return results

def generate_gemini_prompt(problem_num=None):
    """生成Gemini网页端验证指令（配合PDF使用）"""
    if problem_num:
        prompt = f"""请验证这份PDF中题 {problem_num} 的解答是否正确。

检查要点：
1. 物理概念是否正确
2. 数学推导是否有误（符号、系数、积分等）
3. 边界条件是否正确应用
4. 最终结果是否正确

请给出：✅正确 / ⚠️有小问题 / ❌错误，并说明原因。"""
    else:
        prompt = """请验证这份PDF中的课后题解答是否正确。

检查要点：
1. 物理概念是否正确
2. 数学推导是否有误（符号、系数、积分等）
3. 边界条件是否正确应用
4. 最终结果是否正确

对每道题给出：✅正确 / ⚠️有小问题 / ❌错误，并说明原因。"""

    return prompt

if __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 2:
        print('用法:')
        print('  python verify.py <tex文件> --problem 2.10              验证单题')
        print('  python verify.py <tex文件> --problem 2.10 --problem 2.11  验证多题')
        print('  python verify.py <tex文件> --all                       验证全部')
        print('  python verify.py <tex文件> --gemini 2.10               生成Gemini提示词')
        sys.exit(1)

    filepath = sys.argv[1]
    config = load_config()

    if '--problem' in sys.argv:
        # 支持多个 --problem 参数：--problem 2.10 --problem 2.11
        problems = []
        i = 0
        while i < len(sys.argv):
            if sys.argv[i] == '--problem' and i + 1 < len(sys.argv):
                problems.append(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        for p in problems:
            verify_problem(filepath, p, config)

    elif '--all' in sys.argv:
        # 提取所有题号
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        problems = re.findall(r'\\subsection\*\{题\s+([\d.]+\(?[a-z]?\)?)\}', content)
        print(f'共找到 {len(problems)} 道题')
        for p in problems:
            verify_problem(filepath, p, config)

    elif '--gemini' in sys.argv:
        idx = sys.argv.index('--gemini')
        problem_num = None
        if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith('--'):
            problem_num = sys.argv[idx + 1]
        prompt = generate_gemini_prompt(problem_num)
        print('\n📋 复制以下内容到 Gemini 网页端，然后上传PDF：\n')
        print(prompt)
