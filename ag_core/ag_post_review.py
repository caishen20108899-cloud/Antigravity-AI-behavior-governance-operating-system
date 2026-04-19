#!/usr/bin/env python3
"""
ag_post_review.py — 对话窗口物理审查闸门 v1.0

用途：大模型在对话中完成代码修改后，用 run_command 调用此脚本。
      输出结构化审查报告，无法伪造。

设计原则：
  - 复用现有 ag_core 组件（LearningsManager, git diff 分析）
  - 零外部依赖（仅 Python 标准库 + ag_core）
  - 对话窗口可通过 `python3 ag_core/ag_post_review.py <project_dir> [file1 file2 ...]` 调用
  - 输出人类可读的结构化审查报告

审查维度：
  1. 范围检测（git diff —— 改了多少？超标了吗？）
  2. 语法验证（Python: ast.parse / compile; Shell: bash -n）
  3. 已知陷阱匹配（_learnings.jsonl 历史经验回溯）
  4. 常见缺陷扫描（硬编码密码、调试日志遗留、危险操作等）
  5. 测试框架检测 + 建议运行的验证命令
"""

import os
import sys
import ast
import re
import json
import subprocess
import time
from datetime import datetime


# ============================================================
# 1. 范围检测 (Scope Check)
# ============================================================

def check_scope(project_dir, max_files=10, max_lines=300):
    """复用 SurgicalCheckMiddleware 的范围检测逻辑"""
    result = {"status": "SKIP", "detail": "", "files": 0, "lines": 0}

    try:
        proc = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            cwd=project_dir, capture_output=True, text=True, timeout=10
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            # 尝试 staged changes
            proc = subprocess.run(
                ["git", "diff", "--stat", "--cached"],
                cwd=project_dir, capture_output=True, text=True, timeout=10
            )

        output = proc.stdout.strip()
        if not output or "NOT_GIT" in output:
            result["detail"] = "非 git 仓库或无变更"
            return result

        lines = output.split('\n')
        summary = lines[-1] if lines else ""

        changed_files = 0
        insertions = 0
        deletions = 0

        m = re.search(r'(\d+) files? changed', summary)
        if m:
            changed_files = int(m.group(1))
        m = re.search(r'(\d+) insertions?\(\+\)', summary)
        if m:
            insertions = int(m.group(1))
        m = re.search(r'(\d+) deletions?\(-\)', summary)
        if m:
            deletions = int(m.group(1))

        total_lines = insertions + deletions
        result["files"] = changed_files
        result["lines"] = total_lines

        if changed_files > max_files:
            result["status"] = "ALERT"
            result["detail"] = f"🔴 手术刀违规！改了 {changed_files} 个文件，超过上限 {max_files}"
        elif total_lines > max_lines:
            result["status"] = "WARN"
            result["detail"] = f"🟡 改动 {total_lines} 行 (+{insertions}/-{deletions})，超过建议上限 {max_lines} 行"
        else:
            result["status"] = "PASS"
            result["detail"] = f"✅ 范围合规：{changed_files} 文件，{total_lines} 行 (+{insertions}/-{deletions})"

        # 附加变更文件列表
        result["changed_file_list"] = [l.strip().split("|")[0].strip() for l in lines[:-1] if "|" in l]

    except Exception as e:
        result["detail"] = f"范围检测异常: {e}"

    return result


# ============================================================
# 2. 语法验证 (Syntax Validation)
# ============================================================

def validate_syntax(file_path):
    """根据文件类型进行语法验证"""
    result = {"file": os.path.basename(file_path), "status": "SKIP", "detail": ""}

    if not os.path.exists(file_path):
        result["status"] = "ERROR"
        result["detail"] = "文件不存在"
        return result

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".py":
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            ast.parse(source, filename=file_path)
            compile(source, file_path, 'exec')
            result["status"] = "PASS"
            result["detail"] = "✅ Python 语法正确"
        except SyntaxError as e:
            result["status"] = "FAIL"
            result["detail"] = f"❌ Python 语法错误: 第 {e.lineno} 行 — {e.msg}"

    elif ext in (".sh", ".bash"):
        try:
            proc = subprocess.run(
                ["bash", "-n", file_path],
                capture_output=True, text=True, timeout=10
            )
            if proc.returncode == 0:
                result["status"] = "PASS"
                result["detail"] = "✅ Shell 语法正确 (bash -n)"
            else:
                result["status"] = "FAIL"
                result["detail"] = f"❌ Shell 语法错误:\n{proc.stderr.strip()}"
        except Exception as e:
            result["detail"] = f"Shell 语法检查异常: {e}"

    elif ext in (".bat", ".cmd"):
        # CMD 没有 -n 模式，做基本结构检查
        result = validate_bat_syntax(file_path)

    elif ext in (".json",):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            result["status"] = "PASS"
            result["detail"] = "✅ JSON 格式正确"
        except json.JSONDecodeError as e:
            result["status"] = "FAIL"
            result["detail"] = f"❌ JSON 格式错误: 第 {e.lineno} 行 — {e.msg}"

    else:
        result["detail"] = f"不支持 {ext} 类型的语法检查"

    return result


def validate_bat_syntax(file_path):
    """
    CMD/BAT 文件的已知陷阱检测。
    来源：跨平台脚本交付铁律 KI + 历史事故教训。
    """
    result = {"file": os.path.basename(file_path), "status": "PASS", "detail": "", "findings": []}
    findings = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        result["status"] = "ERROR"
        result["detail"] = f"读取失败: {e}"
        return result

    # 陷阱 1: %errorlevel% 在 if/for 括号块内不实时刷新
    in_block = False
    paren_depth = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip().upper()
        # 追踪括号深度
        paren_depth += stripped.count('(') - stripped.count(')')
        if paren_depth > 0 and '%ERRORLEVEL%' in line.upper():
            findings.append({
                "line": i,
                "severity": "P0",
                "category": "AUTO-FIX",
                "desc": f"第 {i} 行: %errorlevel% 在括号块内不会实时刷新。需用 enabledelayedexpansion + !errorlevel! 或拆分到括号外",
                "confidence": 10
            })

    # 陷阱 2: 缺少 @echo off
    if lines and '@ECHO OFF' not in lines[0].upper().strip():
        findings.append({
            "line": 1,
            "severity": "P2",
            "category": "INFO",
            "desc": "第 1 行: 缺少 @echo off，运行时会回显所有命令",
            "confidence": 8
        })

    # 陷阱 3: 使用了 set 赋值但等号两边有空格
    for i, line in enumerate(lines, 1):
        m = re.match(r'\s*set\s+"?(\w+)\s+=', line, re.IGNORECASE)
        if m:
            findings.append({
                "line": i,
                "severity": "P1",
                "category": "AUTO-FIX",
                "desc": f"第 {i} 行: set 赋值等号左边有空格，变量名会包含空格字符",
                "confidence": 10
            })

    # 陷阱 4: 死代码变量（set 了但从未被引用）
    defined_vars = {}
    for i, line in enumerate(lines, 1):
        m = re.match(r'\s*set\s+"?(\w+)=', line, re.IGNORECASE)
        if m:
            var_name = m.group(1).upper()
            defined_vars[var_name] = i

    for var_name, def_line in defined_vars.items():
        # 检查是否在其他地方被引用（%VAR% 或 !VAR!）
        ref_pattern = f'%{var_name}%|!{var_name}!'
        ref_found = False
        for i, line in enumerate(lines, 1):
            if i == def_line:
                continue  # 跳过定义行
            if re.search(ref_pattern, line, re.IGNORECASE):
                ref_found = True
                break
        if not ref_found:
            findings.append({
                "line": def_line,
                "severity": "P2",
                "category": "INFO",
                "desc": f"第 {def_line} 行: 变量 {var_name} 被定义但从未被引用（疑似死代码）",
                "confidence": 7
            })

    # 陷阱 5: 缺少 exit /b 或 exit 语句
    has_exit = any('EXIT' in line.upper() for line in lines)
    if not has_exit and len(lines) > 10:
        findings.append({
            "line": len(lines),
            "severity": "P2",
            "category": "INFO",
            "desc": "脚本末尾缺少 exit /b，从其他脚本调用时可能意外继续执行后续代码",
            "confidence": 6
        })

    # 陷阱 6: 编码问题检测（来自跨平台交付 KI）
    try:
        with open(file_path, 'rb') as f:
            raw = f.read(4)
            # 检测 BOM
            if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xef\xbb\xbf'):
                pass  # BOM 存在，OK
            # 检测是否有 \n 而非 \r\n
            with open(file_path, 'rb') as f2:
                full_raw = f2.read()
                if b'\n' in full_raw and b'\r\n' not in full_raw:
                    findings.append({
                        "line": 0,
                        "severity": "P1",
                        "category": "AUTO-FIX",
                        "desc": "文件使用 Unix 换行符 (LF)，Windows CMD 可能解析异常。应转为 CRLF",
                        "confidence": 9
                    })
    except Exception:
        pass

    if findings:
        result["status"] = "FAIL" if any(f["severity"] == "P0" for f in findings) else "WARN"
        result["findings"] = findings
        result["detail"] = f"发现 {len(findings)} 个问题"
    else:
        result["detail"] = "✅ BAT 文件基本检查通过"

    return result


# ============================================================
# 3. 已知陷阱匹配 (Learnings Recall)
# ============================================================

def recall_learnings(project_dir, files):
    """复用 LearningsManager 的关键词检索，回溯历史经验"""
    results = []
    learnings_path = os.path.join(project_dir, "_learnings.jsonl")

    if not os.path.exists(learnings_path):
        return results

    try:
        with open(learnings_path, 'r', encoding='utf-8') as f:
            entries = []
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        # 从文件名和扩展名生成搜索关键词
        keywords = set()
        for fp in files:
            basename = os.path.basename(fp).lower()
            name, ext = os.path.splitext(basename)
            keywords.add(name)
            keywords.add(ext.lstrip('.'))
            # 从文件名拆分关键词
            for part in re.split(r'[_\-.]', name):
                if len(part) > 2:
                    keywords.add(part)

        for entry in entries:
            search_text = f"{entry.get('key', '')} {entry.get('insight', '')}".lower()
            if any(kw in search_text for kw in keywords if kw):
                results.append(entry)

    except Exception:
        pass

    return results


# ============================================================
# 4. 常见缺陷扫描 (Common Defect Scan)
# ============================================================

DEFECT_PATTERNS = [
    {
        "pattern": r'(?:password|passwd|secret|api_key|token)\s*[=:]\s*["\'][^"\']{3,}["\']',
        "desc": "疑似硬编码敏感信息",
        "severity": "P0",
        "category": "ASK",
        "confidence": 8,
        "extensions": {".py", ".js", ".ts", ".go", ".java", ".sh", ".bat", ".yml", ".yaml", ".json"}
    },
    {
        "pattern": r'(?:console\.log|print\(|fmt\.Print|System\.out\.print)',
        "desc": "调试输出遗留",
        "severity": "P2",
        "category": "INFO",
        "confidence": 5,
        "extensions": {".py", ".js", ".ts", ".go", ".java"}
    },
    {
        "pattern": r'(?:rm\s+-rf\s+/|DROP\s+TABLE|TRUNCATE\s+TABLE|FLUSHALL)',
        "desc": "疑似危险的破坏性命令",
        "severity": "P0",
        "category": "ASK",
        "confidence": 9,
        "extensions": {".py", ".sh", ".bash", ".bat", ".sql", ".js"}
    },
    {
        "pattern": r'TODO|FIXME|HACK|XXX|TEMP|临时',
        "desc": "遗留的 TODO/FIXME 标记",
        "severity": "P3",
        "category": "INFO",
        "confidence": 6,
        "extensions": None  # 所有文件
    },
    {
        "pattern": r'except\s*:(?:\s*$|\s*#)',
        "desc": "Python 裸 except（吞掉所有异常，含 KeyboardInterrupt）",
        "severity": "P1",
        "category": "ASK",
        "confidence": 8,
        "extensions": {".py"}
    },
]


def scan_defects(file_path):
    """对单个文件进行常见缺陷扫描"""
    findings = []
    ext = os.path.splitext(file_path)[1].lower()

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception:
        return findings

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # 跳过注释行、字符串定义行（含正则模式定义）和 docstring
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        # 跳过明显的字典/列表常量定义行（如 DEFECT_PATTERNS 中的 pattern 字段）
        if stripped.startswith('"pattern"') or stripped.startswith("'pattern'"):
            continue

        for pattern_def in DEFECT_PATTERNS:
            # 跳过不适用的扩展名
            if pattern_def["extensions"] and ext not in pattern_def["extensions"]:
                continue

            if re.search(pattern_def["pattern"], line, re.IGNORECASE):
                findings.append({
                    "line": i,
                    "severity": pattern_def["severity"],
                    "category": pattern_def["category"],
                    "desc": f"第 {i} 行: {pattern_def['desc']}",
                    "snippet": stripped[:80],
                    "confidence": pattern_def["confidence"]
                })

    return findings


# ============================================================
# 5. 测试框架检测 (Test Framework Detection)
# ============================================================

def detect_test_command(project_dir):
    """复用 ValidationGateMiddleware 的测试框架检测逻辑"""
    detectors = {
        "package.json": {"check": '"test"', "cmd": "npm test"},
        "Gemfile": {"check": None, "cmd": "bundle exec rspec"},
        "pyproject.toml": {"check": None, "cmd": "python -m pytest -x -q"},
        "requirements.txt": {"check": None, "cmd": "python -m pytest -x -q"},
        "go.mod": {"check": None, "cmd": "go test ./..."},
        "Cargo.toml": {"check": None, "cmd": "cargo test"},
    }

    for config_file, detector in detectors.items():
        config_path = os.path.join(project_dir, config_file)
        if os.path.exists(config_path):
            if detector["check"]:
                try:
                    with open(config_path, 'r') as f:
                        if detector["check"] in f.read():
                            return detector["cmd"]
                except Exception:
                    pass
            else:
                return detector["cmd"]

    return None


# ============================================================
# 报告生成器 (Report Generator)
# ============================================================

def generate_report(project_dir, target_files):
    """生成结构化审查报告"""
    report = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    has_failures = False
    has_warnings = False

    report.append("=" * 60)
    report.append(f"  📋 AG POST-REVIEW 审查报告")
    report.append(f"  时间: {timestamp}")
    report.append(f"  项目: {os.path.basename(os.path.abspath(project_dir))}")
    report.append("=" * 60)

    # --- 第 1 节：范围检测 ---
    report.append("\n┌─── 1. 范围检测 (Scope Check) ──────────────────────┐")
    scope = check_scope(project_dir)
    report.append(f"  {scope['detail']}")
    if scope.get("changed_file_list"):
        for f in scope["changed_file_list"][:15]:
            report.append(f"    • {f}")
    if scope["status"] == "ALERT":
        has_failures = True
    elif scope["status"] == "WARN":
        has_warnings = True
    report.append("└────────────────────────────────────────────────────┘")

    # --- 第 2 节：语法验证 ---
    report.append("\n┌─── 2. 语法验证 (Syntax Check) ─────────────────────┐")
    if not target_files:
        report.append("  ⏭️ 无指定文件，跳过语法检查")
    else:
        for fp in target_files:
            abs_path = fp if os.path.isabs(fp) else os.path.join(project_dir, fp)
            syn = validate_syntax(abs_path)
            status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "ERROR": "💥"}.get(syn["status"], "⏭️")
            report.append(f"  {status_icon} {syn['file']}: {syn['detail']}")

            # BAT 文件有详细 findings
            if syn.get("findings"):
                for finding in syn["findings"]:
                    sev_icon = {"P0": "🔴", "P1": "🟡", "P2": "🔵"}.get(finding["severity"], "⚪")
                    report.append(f"    {sev_icon} [{finding['category']}] {finding['desc']}")

            if syn["status"] == "FAIL":
                has_failures = True
            elif syn["status"] == "WARN":
                has_warnings = True
    report.append("└────────────────────────────────────────────────────┘")

    # --- 第 3 节：已知陷阱回溯 ---
    report.append("\n┌─── 3. 历史经验回溯 (Learnings Recall) ─────────────┐")
    learnings = recall_learnings(project_dir, target_files)
    if learnings:
        report.append(f"  ⚠️ 命中 {len(learnings)} 条历史经验，请注意：")
        for entry in learnings[:5]:
            report.append(f"    📌 [{entry.get('type', '?')}] {entry.get('key', '?')}")
            report.append(f"       {entry.get('insight', '无详情')[:100]}")
    else:
        report.append("  ✅ 无匹配的历史陷阱记录")
    report.append("└────────────────────────────────────────────────────┘")

    # --- 第 4 节：缺陷扫描 ---
    report.append("\n┌─── 4. 常见缺陷扫描 (Defect Scan) ──────────────────┐")
    total_defects = 0
    has_p0_defect = False
    if not target_files:
        report.append("  ⏭️ 无指定文件，跳过缺陷扫描")
    else:
        for fp in target_files:
            abs_path = fp if os.path.isabs(fp) else os.path.join(project_dir, fp)
            defects = scan_defects(abs_path)
            if defects:
                total_defects += len(defects)
                report.append(f"  📍 {os.path.basename(fp)}:")
                for d in defects:
                    sev_icon = {"P0": "🔴", "P1": "🟡", "P2": "🔵", "P3": "⚪"}.get(d["severity"], "⚪")
                    report.append(f"    {sev_icon} [{d['category']}][{d['confidence']}/10] {d['desc']}")
                    if d["severity"] == "P0":
                        has_p0_defect = True

        if total_defects == 0:
            report.append("  ✅ 未发现常见缺陷模式")
        elif has_p0_defect:
            has_failures = True
    report.append("└────────────────────────────────────────────────────┘")

    # --- 第 5 节：验证命令建议 ---
    report.append("\n┌─── 5. 建议的验证命令 ──────────────────────────────┐")
    test_cmd = detect_test_command(project_dir)
    if test_cmd:
        report.append(f"  🔧 检测到测试框架，建议运行：")
        report.append(f"     $ {test_cmd}")
    else:
        report.append("  ℹ️ 未检测到测试框架")
    report.append("└────────────────────────────────────────────────────┘")

    # --- 总结 ---
    report.append("\n" + "=" * 60)
    if has_failures:
        report.append("  🔴 审查结论: FAIL — 存在严重问题，禁止交付！")
    elif has_warnings:
        report.append("  🟡 审查结论: WARN — 存在警告项，建议修复后交付")
    else:
        report.append("  ✅ 审查结论: PASS — 未发现高危问题")
    report.append("=" * 60)

    return "\n".join(report)


# ============================================================
# 入口
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("用法: python3 ag_post_review.py <project_dir> [file1] [file2] ...")
        print("")
        print("示例:")
        print("  python3 ag_core/ag_post_review.py . src/auth.py src/config.py")
        print("  python3 ag_core/ag_post_review.py /path/to/project Install.bat")
        sys.exit(1)

    project_dir = sys.argv[1]
    target_files = sys.argv[2:] if len(sys.argv) > 2 else []

    # 如果没有指定文件，自动从 git diff 获取变更文件
    if not target_files:
        try:
            proc = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=project_dir, capture_output=True, text=True, timeout=10
            )
            if proc.returncode == 0 and proc.stdout.strip():
                target_files = [f.strip() for f in proc.stdout.strip().split('\n') if f.strip()]
            else:
                # 尝试 staged
                proc = subprocess.run(
                    ["git", "diff", "--name-only", "--cached"],
                    cwd=project_dir, capture_output=True, text=True, timeout=10
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    target_files = [f.strip() for f in proc.stdout.strip().split('\n') if f.strip()]
        except Exception:
            pass

    report = generate_report(project_dir, target_files)
    print(report)

    # 返回退出码：有 FAIL 则非零
    if "FAIL" in report.split('\n')[-2]:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
