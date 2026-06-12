"""
编译脚本 — 编译tex文件，清理中间产物到build目录
用法: python compile.py <tex文件路径> [--open]
选项: --open 编译后自动打开PDF
"""
import sys
import os
import shutil
import subprocess

# LaTeX中间产物扩展名
AUX_EXTS = ['.aux', '.log', '.out', '.toc', '.nav', '.snm', '.vrb', '.fls', '.fdb_latexmk', '.synctex.gz']

def compile_tex(filepath, auto_open=False):
    tex_dir = os.path.dirname(os.path.abspath(filepath))
    tex_name = os.path.basename(filepath)
    tex_stem = os.path.splitext(tex_name)[0]

    # 创建build目录
    build_dir = os.path.join(tex_dir, 'build')
    os.makedirs(build_dir, exist_ok=True)

    # pdflatex：优先用PATH里的，找不到再提示安装
    pdflatex = shutil.which('pdflatex')
    if not pdflatex:
        print('❌ 找不到pdflatex，请确保已安装MiKTeX或TeX Live并添加到PATH。')
        print('   MiKTeX: https://miktex.org/download')
        print('   TeX Live: https://www.tug.org/texlive/')
        sys.exit(1)

    print(f'📄 编译: {tex_name}')

    # 运行pdflatex两遍（生成目录和引用）
    for run in range(2):
        print(f'  第{run+1}遍编译...')
        result = subprocess.run(
            [pdflatex, '-interaction=nonstopmode', tex_name],
            cwd=tex_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # 检查错误
        if result.returncode != 0:
            # 解析log文件找错误
            log_path = os.path.join(tex_dir, tex_stem + '.log')
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                    log = f.read()
                errors = [line for line in log.split('\n') if line.startswith('!')]
                if errors:
                    print(f'  ❌ 编译错误:')
                    for err in errors[:5]:
                        print(f'    {err}')
                    # 仍然清理中间产物
                    _cleanup(tex_dir, tex_stem, build_dir)
                    sys.exit(1)

    # 检查PDF是否生成
    pdf_path = os.path.join(tex_dir, tex_stem + '.pdf')
    if os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f'  ✅ 编译成功: {pdf_path} ({size_kb:.0f} KB)')
    else:
        print(f'  ❌ PDF未生成，请检查log。')
        _cleanup(tex_dir, tex_stem, build_dir)
        sys.exit(1)

    # 清理中间产物到build目录
    _cleanup(tex_dir, tex_stem, build_dir)

    # 自动打开PDF
    if auto_open:
        if sys.platform == 'win32':
            os.startfile(pdf_path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', pdf_path])
        else:
            subprocess.run(['xdg-open', pdf_path])
        print(f'  📖 已打开PDF')

def _cleanup(tex_dir, tex_stem, build_dir):
    """移动中间产物到build目录"""
    moved = 0
    for ext in AUX_EXTS:
        src = os.path.join(tex_dir, tex_stem + ext)
        if os.path.exists(src):
            dst = os.path.join(build_dir, tex_stem + ext)
            shutil.move(src, dst)
            moved += 1
    if moved > 0:
        print(f'  🧹 清理 {moved} 个中间产物到 build/')

if __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 2:
        print('用法: python compile.py <tex文件路径> [--open]')
        sys.exit(1)

    filepath = sys.argv[1]
    auto_open = '--open' in sys.argv
    compile_tex(filepath, auto_open)
