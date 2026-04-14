#!/usr/bin/env python3
"""
ag_indexer.py — Antigravity 代码图谱引擎 (Codebase Map Generator)
==================================================================
扫描目标项目目录，按语言解析关键符号（类/函数/导入），
输出 Markdown 格式的 `_codebase_map.md` 供 AI 在编码前 1 秒读懂全局结构。

用法:
    python3 ag_indexer.py /path/to/project
    python3 -m ag_core.ag_indexer /path/to/project

部署: Mac mini Cron 定时每 2 小时扫描各项目
"""

import ast
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime


# ─────────────────────────────── 配置 ───────────────────────────────

# 忽略的目录名（全局，不可覆盖）
IGNORE_DIRS = {
    '.git', '.svn', '.hg', 'node_modules', '__pycache__', '.idea',
    '.vscode', '.gradle', 'build', 'dist', 'target', 'venv', '.venv',
    'env', '.env', 'vendor', 'Pods', '.eggs', '*.egg-info',
    '.next', '.nuxt', 'coverage', '.tox', 'DerivedData',
    'AGENTS', '.gemini', '.agent',
}

# 忽略的文件名模式
IGNORE_FILES = {
    '.DS_Store', 'Thumbs.db', 'package-lock.json', 'yarn.lock',
    'pnpm-lock.yaml', 'Podfile.lock', 'go.sum',
}

# 语言→扩展名映射
LANG_EXTENSIONS = {
    'Python':     {'.py'},
    'Java':       {'.java'},
    'JavaScript': {'.js', '.jsx', '.mjs'},
    'TypeScript': {'.ts', '.tsx'},
    'Go':         {'.go'},
    'Kotlin':     {'.kt', '.kts'},
    'Swift':      {'.swift'},
    'Lua':        {'.lua'},
    'Shell':      {'.sh', '.bash'},
    'SQL':        {'.sql'},
    'Markdown':   {'.md'},
    'YAML':       {'.yaml', '.yml'},
    'JSON':       {'.json'},
    'HTML':       {'.html', '.htm'},
    'CSS':        {'.css', '.scss', '.less'},
    'Vue':        {'.vue'},
    'XML':        {'.xml'},
    'Rust':       {'.rs'},
    'C/C++':      {'.c', '.cpp', '.h', '.hpp'},
}

# 构建扩展名→语言的反向映射
EXT_TO_LANG = {}
for lang, exts in LANG_EXTENSIONS.items():
    for ext in exts:
        EXT_TO_LANG[ext] = lang

# 最大单文件行数（超过则跳过解析，防止卡死）
MAX_LINES_PER_FILE = 10000

# ────────────────────────── 符号提取器 ──────────────────────────


def _safe_read(filepath):
    """安全读取文件内容，自动跳过二进制"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return content
    except Exception:
        return None


def _count_lines(content):
    """统计行数"""
    return content.count('\n') + (1 if content and not content.endswith('\n') else 0)


# ── Python: 使用 ast 精确解析 ──

def extract_python(filepath, content):
    """Python: 使用 ast 模块精确提取类/函数/导入"""
    symbols = {'classes': [], 'functions': [], 'imports': []}
    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError:
        # ast 解析失败，降级到正则
        return extract_by_regex(content, 'Python')

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            symbols['classes'].append({
                'name': node.name,
                'line': node.lineno,
                'methods': methods[:8],  # 最多记录 8 个方法
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # 只记录模块顶层函数（类内方法已在上面记录）
            if hasattr(node, '_parent_class'):
                continue
            symbols['functions'].append({
                'name': node.name,
                'line': node.lineno,
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                symbols['imports'].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                symbols['imports'].append(node.module)

    # 过滤掉类方法，只保留真正的顶层函数
    class_method_names = set()
    for cls in symbols['classes']:
        class_method_names.update(cls['methods'])
    symbols['functions'] = [
        f for f in symbols['functions']
        if f['name'] not in class_method_names
    ]

    return symbols


# ── 通用正则提取器 ──

# 每种语言的正则模式
REGEX_PATTERNS = {
    'Java': {
        'classes':   re.compile(r'(?:public\s+|abstract\s+|final\s+)*(?:class|interface|enum)\s+(\w+)'),
        'functions': re.compile(r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\('),
        'imports':   re.compile(r'import\s+([\w.]+)'),
    },
    'JavaScript': {
        'classes':   re.compile(r'(?:export\s+)?class\s+(\w+)'),
        'functions': re.compile(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)'),
        'imports':   re.compile(r"(?:import|require)\s*\(?\s*['\"]([^'\"]+)['\"]"),
    },
    'TypeScript': {
        'classes':   re.compile(r'(?:export\s+)?(?:abstract\s+)?class\s+(\w+)'),
        'functions': re.compile(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)'),
        'imports':   re.compile(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]"),
    },
    'Go': {
        'classes':   re.compile(r'type\s+(\w+)\s+struct'),
        'functions': re.compile(r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\('),
        'imports':   re.compile(r'"([\w./]+)"'),
    },
    'Kotlin': {
        'classes':   re.compile(r'(?:data\s+|sealed\s+|open\s+|abstract\s+)?class\s+(\w+)'),
        'functions': re.compile(r'(?:suspend\s+)?fun\s+(\w+)'),
        'imports':   re.compile(r'import\s+([\w.]+)'),
    },
    'Swift': {
        'classes':   re.compile(r'(?:class|struct|enum|protocol)\s+(\w+)'),
        'functions': re.compile(r'func\s+(\w+)'),
        'imports':   re.compile(r'import\s+(\w+)'),
    },
    'Lua': {
        'classes':   None,
        'functions': re.compile(r'(?:local\s+)?function\s+(\w[\w.:]*)\s*\('),
        'imports':   re.compile(r'require\s*\(\s*["\']([^"\']+)["\']'),
    },
    'Rust': {
        'classes':   re.compile(r'(?:pub\s+)?(?:struct|enum|trait)\s+(\w+)'),
        'functions': re.compile(r'(?:pub\s+)?(?:async\s+)?fn\s+(\w+)'),
        'imports':   re.compile(r'use\s+([\w:]+)'),
    },
    'C/C++': {
        'classes':   re.compile(r'(?:class|struct)\s+(\w+)'),
        'functions': re.compile(r'(?:\w[\w*&\s]+)\s+(\w+)\s*\([^)]*\)\s*\{'),
        'imports':   re.compile(r'#include\s*[<"]([^>"]+)[>"]'),
    },
    'Vue': {
        'classes':   None,
        'functions': re.compile(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)|(\w+)\s*\([^)]*\)\s*\{'),
        'imports':   re.compile(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]"),
    },
}


def extract_by_regex(content, lang):
    """通用正则符号提取"""
    symbols = {'classes': [], 'functions': [], 'imports': []}
    patterns = REGEX_PATTERNS.get(lang)
    if not patterns:
        return symbols

    lines = content.split('\n')

    if patterns.get('classes'):
        for i, line in enumerate(lines, 1):
            for m in patterns['classes'].finditer(line):
                symbols['classes'].append({'name': m.group(1), 'line': i, 'methods': []})

    if patterns.get('functions'):
        for i, line in enumerate(lines, 1):
            for m in patterns['functions'].finditer(line):
                name = m.group(1) or (m.group(2) if m.lastindex >= 2 else None)
                if name and not name.startswith('_'):
                    symbols['functions'].append({'name': name, 'line': i})

    if patterns.get('imports'):
        for line in lines:
            for m in patterns['imports'].finditer(line):
                symbols['imports'].append(m.group(1))

    # 去重
    symbols['imports'] = list(dict.fromkeys(symbols['imports']))
    return symbols


# ────────────────────── 核心扫描引擎 ──────────────────────


def scan_project(project_path):
    """
    扫描整个项目目录，生成结构化索引数据。
    返回: {
        'project_path': str,
        'scan_time': str,
        'tree': {relative_dir: [filenames]},
        'stats': {'total_files': int, 'total_lines': int, 'by_lang': {lang: {'files': int, 'lines': int}}},
        'modules': [{'file': str, 'lang': str, 'lines': int, 'symbols': {...}}]
    }
    """
    project_path = os.path.abspath(project_path)
    if not os.path.isdir(project_path):
        print(f"❌ 错误: 目录不存在 — {project_path}")
        sys.exit(1)

    tree = defaultdict(list)
    stats = {'total_files': 0, 'total_lines': 0, 'by_lang': defaultdict(lambda: {'files': 0, 'lines': 0})}
    modules = []

    for root, dirs, files in os.walk(project_path):
        # 剪枝：忽略不需要扫描的目录
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]

        rel_dir = os.path.relpath(root, project_path)
        if rel_dir == '.':
            rel_dir = ''

        for fname in sorted(files):
            if fname in IGNORE_FILES or fname.startswith('.'):
                continue

            _, ext = os.path.splitext(fname)
            ext = ext.lower()
            lang = EXT_TO_LANG.get(ext)

            if not lang:
                continue

            filepath = os.path.join(root, fname)
            rel_file = os.path.relpath(filepath, project_path)

            tree[rel_dir].append(fname)

            content = _safe_read(filepath)
            if content is None:
                continue

            line_count = _count_lines(content)
            stats['total_files'] += 1
            stats['total_lines'] += line_count
            stats['by_lang'][lang]['files'] += 1
            stats['by_lang'][lang]['lines'] += line_count

            # 仅对代码型语言提取符号（跳过 Markdown/YAML/JSON/HTML/CSS/SQL）
            skip_parse_langs = {'Markdown', 'YAML', 'JSON', 'HTML', 'CSS', 'XML', 'SQL', 'Shell'}
            if lang in skip_parse_langs:
                continue

            if line_count > MAX_LINES_PER_FILE:
                modules.append({
                    'file': rel_file, 'lang': lang, 'lines': line_count,
                    'symbols': {'classes': [], 'functions': [], 'imports': []},
                    'note': '⚠️ 文件过大，已跳过深度解析'
                })
                continue

            # 提取符号
            if lang == 'Python':
                symbols = extract_python(filepath, content)
            else:
                symbols = extract_by_regex(content, lang)

            # 仅记录有实质符号的文件
            if symbols['classes'] or symbols['functions']:
                modules.append({
                    'file': rel_file,
                    'lang': lang,
                    'lines': line_count,
                    'symbols': symbols,
                })

    return {
        'project_path': project_path,
        'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'tree': dict(tree),
        'stats': {
            'total_files': stats['total_files'],
            'total_lines': stats['total_lines'],
            'by_lang': dict(stats['by_lang']),
        },
        'modules': sorted(modules, key=lambda m: m['file']),
    }


# ────────────────────── Markdown 渲染器 ──────────────────────


def render_markdown(index_data):
    """将索引数据渲染为 Markdown 格式的代码图谱"""
    lines = []
    project_name = os.path.basename(index_data['project_path'])
    stats = index_data['stats']

    # ── 头部 ──
    lines.append(f"# 📊 项目代码图谱: {project_name}")
    lines.append(f"> 自动生成 by `ag_indexer` | 更新时间: {index_data['scan_time']}")
    lines.append(f"> ⚠️ 此文件由机器自动生成，请勿手动编辑")
    lines.append("")

    # ── 概览 ──
    lines.append("## 概览")
    lines.append(f"- **总文件数**: {stats['total_files']}")
    lines.append(f"- **总代码行数**: {stats['total_lines']:,}")
    lines.append("")

    if stats['by_lang']:
        lines.append("| 语言 | 文件数 | 行数 |")
        lines.append("|------|--------|------|")
        for lang, info in sorted(stats['by_lang'].items(), key=lambda x: -x[1]['lines']):
            lines.append(f"| {lang} | {info['files']} | {info['lines']:,} |")
        lines.append("")

    # ── 目录结构树 ──
    lines.append("## 目录结构")
    lines.append("```")
    tree = index_data['tree']
    sorted_dirs = sorted(tree.keys())
    for d in sorted_dirs:
        prefix = f"{d}/" if d else f"{project_name}/"
        file_count = len(tree[d])
        lines.append(f"├── {prefix} ({file_count} 文件)")
    lines.append("```")
    lines.append("")

    # ── 核心模块索引 ──
    modules = index_data['modules']
    if modules:
        lines.append("## 核心模块索引")
        lines.append("")
        lines.append("| 文件 | 语言 | 行数 | 类 | 函数 | 关键依赖 |")
        lines.append("|------|------|------|----|------|----------|")
        for mod in modules:
            syms = mod['symbols']
            cls_names = ', '.join(c['name'] for c in syms.get('classes', [])[:3])
            func_names = ', '.join(f['name'] + '()' for f in syms.get('functions', [])[:4])
            key_symbols = cls_names
            if func_names:
                key_symbols = f"{cls_names}, {func_names}" if cls_names else func_names

            # 关键依赖：取前 4 个非标准库的导入
            imports = syms.get('imports', [])
            key_deps = ', '.join(imports[:4]) if imports else '-'

            note = mod.get('note', '')
            file_display = mod['file']
            lines.append(f"| {file_display} | {mod['lang']} | {mod['lines']} | {key_symbols} | {key_deps} | {note}")
        lines.append("")

        # ── 详细符号清单（仅列出有类的文件） ──
        has_classes = [m for m in modules if m['symbols'].get('classes')]
        if has_classes:
            lines.append("## 类结构详情")
            lines.append("")
            for mod in has_classes:
                lines.append(f"### `{mod['file']}`")
                for cls in mod['symbols']['classes']:
                    methods_str = ', '.join(f"`{m}()`" for m in cls.get('methods', []))
                    if methods_str:
                        lines.append(f"- **{cls['name']}** (L{cls['line']}): {methods_str}")
                    else:
                        lines.append(f"- **{cls['name']}** (L{cls['line']})")
                lines.append("")

    # ── 尾部 ──
    lines.append("---")
    lines.append(f"*由 ag_indexer V1.0 生成 | Antigravity V3.3*")

    return '\n'.join(lines)


# ────────────────────── 入口 ──────────────────────


def main():
    if len(sys.argv) < 2:
        print("用法: python3 ag_indexer.py <项目路径>")
        print("示例: python3 ag_indexer.py /Users/qianxiangyunji/Antigravity/ChiChatIM系统")
        sys.exit(1)

    project_path = sys.argv[1]
    print(f"🔍 正在扫描项目: {project_path}")

    start = time.time()
    index_data = scan_project(project_path)
    elapsed = time.time() - start

    # 渲染 Markdown
    markdown = render_markdown(index_data)

    # 写入 _codebase_map.md
    output_path = os.path.join(project_path, '_codebase_map.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✅ 代码图谱已生成: {output_path}")
    print(f"   文件数: {index_data['stats']['total_files']}, 代码行: {index_data['stats']['total_lines']:,}")
    print(f"   模块数: {len(index_data['modules'])}, 耗时: {elapsed:.2f}s")


if __name__ == '__main__':
    main()
