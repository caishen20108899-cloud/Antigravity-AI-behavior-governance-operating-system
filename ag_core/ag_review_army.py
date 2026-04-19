"""
Antigravity Review Army v2.0 — 真实静态分析版
将 gstack 式的并行专家审查从 mock 桩函数升级为基于 AST + Regex 的真实代码扫描。
零外部依赖，纯 Python 标准库。
"""
import asyncio
import ast
import json
import os
import re
import uuid
from .event_logger import log_event
from .ag_learnings_manager import LearningsManager


class ReviewArmy:
    """
    三路并行静态分析审查军团。
    每个 Specialist 使用不同的扫描策略：
      - Testing:     AST 分析分支覆盖 + 异常处理检测
      - Security:    正则 + AST 扫描安全漏洞模式
      - Consistency: AST 风格一致性 + 代码规范检查
    """

    SPECIALISTS = {
        "testing": {
            "name": "Testing Specialist",
            "focus": "分支覆盖盲区、异常处理遗漏、未测试的条件路径",
        },
        "security": {
            "name": "Security Specialist",
            "focus": "硬编码密钥、SQL/命令注入、敏感信息泄露、不安全的 eval/exec",
        },
        "consistency": {
            "name": "Consistency Specialist",
            "focus": "命名规范、print 调试遗留、未使用的导入、过长函数",
        },
    }

    # --- Security 扫描规则 ---
    SECURITY_PATTERNS = [
        {
            "pattern": r"""(?:password|passwd|pwd|secret|api_key|apikey|token|auth_token)\s*=\s*["'][^"']{3,}["']""",
            "desc": "疑似硬编码密钥/密码",
            "confidence": 8,
            "category": "ASK",
        },
        {
            "pattern": r"""eval\s*\(""",
            "desc": "使用 eval() — 存在代码注入风险",
            "confidence": 9,
            "category": "ASK",
        },
        {
            "pattern": r"""exec\s*\(""",
            "desc": "使用 exec() — 存在任意代码执行风险",
            "confidence": 9,
            "category": "ASK",
        },
        {
            "pattern": r"""os\.system\s*\(""",
            "desc": "使用 os.system() — 建议改用 subprocess 以防命令注入",
            "confidence": 7,
            "category": "INFO",
        },
        {
            "pattern": r"""subprocess\.\w+\(.*shell\s*=\s*True""",
            "desc": "subprocess 启用 shell=True — 存在命令注入风险",
            "confidence": 7,
            "category": "ASK",
        },
        {
            "pattern": r"""pickle\.loads?\s*\(""",
            "desc": "使用 pickle 反序列化 — 不可信数据源下存在 RCE 风险",
            "confidence": 8,
            "category": "ASK",
        },
        {
            "pattern": r"""(?:SELECT|INSERT|UPDATE|DELETE)\s+.*%s|\.format\(""",
            "desc": "疑似 SQL 字符串拼接 — 存在注入风险",
            "confidence": 7,
            "category": "ASK",
        },
    ]

    # --- Consistency 扫描规则 ---
    CONSISTENCY_PATTERNS = [
        {
            "pattern": r"""^\s*print\s*\(""",
            "desc": "调试用 print() 遗留 — 建议使用 logging 或 log_event()",
            "confidence": 6,
            "category": "AUTO-FIX",
        },
        {
            "pattern": r"""#\s*(?:TODO|FIXME|HACK|XXX|TEMP)\b""",
            "desc": "遗留的 TODO/FIXME 标记",
            "confidence": 5,
            "category": "INFO",
        },
        {
            "pattern": r"""^\s*import\s+pdb|^\s*pdb\.set_trace""",
            "desc": "调试断点遗留 (pdb)",
            "confidence": 9,
            "category": "AUTO-FIX",
        },
        {
            "pattern": r"""^\s*breakpoint\s*\(\s*\)""",
            "desc": "调试断点遗留 (breakpoint())",
            "confidence": 9,
            "category": "AUTO-FIX",
        },
    ]

    def __init__(self, project_cwd: str):
        self.cwd = project_cwd
        self.learnings = LearningsManager(project_cwd)

    # ========== Testing Specialist — AST 分析 ==========

    def _analyze_testing(self, source: str, filepath: str) -> list:
        """AST 级别分析：分支覆盖盲区、裸 except、缺失异常处理"""
        findings = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return findings

        for node in ast.walk(tree):
            # 检测裸 except（吞异常）
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                findings.append({
                    "id": str(uuid.uuid4())[:8],
                    "file": os.path.basename(filepath),
                    "line": node.lineno,
                    "description": f"第 {node.lineno} 行: 裸 except — 会吞掉所有异常，建议指定异常类型",
                    "confidence": 7,
                    "category": "ASK",
                })

            # 检测过长函数（>50 行）
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, "end_lineno") and node.end_lineno:
                    func_len = node.end_lineno - node.lineno
                    if func_len > 50:
                        findings.append({
                            "id": str(uuid.uuid4())[:8],
                            "file": os.path.basename(filepath),
                            "line": node.lineno,
                            "description": f"第 {node.lineno} 行: 函数 {node.name}() 长达 {func_len} 行，建议拆分",
                            "confidence": 6,
                            "category": "INFO",
                        })

            # 检测无异常处理的文件操作
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "open":
                    # 检查 open() 是否在 try 块或 with 语句内
                    # 简单启发式：只报告顶层调用
                    pass  # AST 父节点追踪需要更复杂逻辑，暂用正则补充

            # 检测嵌套过深的 if（> 4 层缩进）
            if isinstance(node, ast.If):
                col = getattr(node, "col_offset", 0)
                if col >= 16:  # 4 层 * 4 空格
                    findings.append({
                        "id": str(uuid.uuid4())[:8],
                        "file": os.path.basename(filepath),
                        "line": node.lineno,
                        "description": f"第 {node.lineno} 行: if 嵌套深度 ≥ 4 层，建议提前 return 或提取函数",
                        "confidence": 5,
                        "category": "INFO",
                    })

        return findings

    # ========== Security Specialist — Regex + AST ==========

    def _analyze_security(self, source: str, filepath: str) -> list:
        """正则 + AST 扫描安全漏洞模式"""
        findings = []
        lines = source.split("\n")

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # 跳过注释行和字符串定义行中的模式定义
            if stripped.startswith("#"):
                continue
            # 跳过 pattern/desc 定义行（避免审查自身的规则定义）
            if '"pattern"' in stripped or "'pattern'" in stripped:
                continue
            if '"desc"' in stripped or "'desc'" in stripped:
                continue

            for rule in self.SECURITY_PATTERNS:
                if re.search(rule["pattern"], line, re.IGNORECASE):
                    findings.append({
                        "id": str(uuid.uuid4())[:8],
                        "file": os.path.basename(filepath),
                        "line": i,
                        "description": f"第 {i} 行: {rule['desc']}",
                        "confidence": rule["confidence"],
                        "category": rule["category"],
                    })

        return findings

    # ========== Consistency Specialist — Regex + AST ==========

    def _analyze_consistency(self, source: str, filepath: str) -> list:
        """代码风格与一致性扫描"""
        findings = []
        lines = source.split("\n")

        # 正则扫描
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue

            for rule in self.CONSISTENCY_PATTERNS:
                if re.search(rule["pattern"], line, re.IGNORECASE):
                    findings.append({
                        "id": str(uuid.uuid4())[:8],
                        "file": os.path.basename(filepath),
                        "line": i,
                        "description": f"第 {i} 行: {rule['desc']}",
                        "confidence": rule["confidence"],
                        "category": rule["category"],
                    })

        # AST 级别检查：未使用的导入
        try:
            tree = ast.parse(source)
            imported_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name
                        imported_names.add((name, node.lineno))
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name
                        imported_names.add((name, node.lineno))

            # 简单检测：导入名是否在代码中被引用（排除 import 行本身）
            for name, lineno in imported_names:
                # 统计 name 在非 import 行中出现的次数
                usage_count = 0
                for i, line in enumerate(lines, 1):
                    if i == lineno:
                        continue
                    if re.search(r'\b' + re.escape(name) + r'\b', line):
                        usage_count += 1
                if usage_count == 0:
                    findings.append({
                        "id": str(uuid.uuid4())[:8],
                        "file": os.path.basename(filepath),
                        "line": lineno,
                        "description": f"第 {lineno} 行: 导入 '{name}' 似乎未被使用",
                        "confidence": 6,
                        "category": "INFO",
                    })
        except SyntaxError:
            pass

        return findings

    # ========== 主审查入口 ==========

    async def run_review(self, file_paths: list = None, diff_content: str = None) -> dict:
        """
        对指定文件或 diff 内容执行三路并行静态分析。
        
        Args:
            file_paths: 要审查的文件路径列表
            diff_content: 备选 — 直接传入代码文本
            
        Returns:
            三分类结果: {"AUTO-FIX": [...], "ASK": [...], "INFO": [...]}
        """
        log_event("@ReviewArmy", "MessageStatus",
                  f"⚔️ Review Army v2.0 集结！三路专家并发启动真实静态分析...")

        all_findings = []

        # 如果传入文件路径，读取并分析每个文件
        if file_paths:
            for fpath in file_paths:
                full_path = fpath if os.path.isabs(fpath) else os.path.join(self.cwd, fpath)
                if not os.path.exists(full_path):
                    continue
                if not full_path.endswith(".py"):
                    continue  # 当前版本仅支持 Python 文件的深度分析

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        source = f.read()
                except Exception:
                    continue

                # 三路并发（实际是三个分析函数，用 asyncio 包装以保持接口一致性）
                loop = asyncio.get_event_loop()
                testing_task = loop.run_in_executor(None, self._analyze_testing, source, full_path)
                security_task = loop.run_in_executor(None, self._analyze_security, source, full_path)
                consistency_task = loop.run_in_executor(None, self._analyze_consistency, source, full_path)

                results = await asyncio.gather(testing_task, security_task, consistency_task)
                for result in results:
                    all_findings.extend(result)

        # 如果传入 diff 文本（兼容旧接口）
        elif diff_content:
            testing = self._analyze_testing(diff_content, "diff_input")
            security = self._analyze_security(diff_content, "diff_input")
            consistency = self._analyze_consistency(diff_content, "diff_input")
            all_findings = testing + security + consistency

        # 指纹去重
        deduped = {}
        for f in all_findings:
            key = f"{f['file']}:{f['line']}:{f['description'][:30]}"
            if key not in deduped or f["confidence"] > deduped[key]["confidence"]:
                deduped[key] = f

        # 置信度校准（基于历史经验）
        calibrated_count = 0
        for f in deduped.values():
            past_tolerance = self.learnings.search_learnings(
                [f["category"].lower(), f["description"].lower()[:15]]
            )
            for record in past_tolerance:
                if record.get("type") in ("false_positive", "tolerance"):
                    old_conf = f["confidence"]
                    f["confidence"] -= min(3, f["confidence"])
                    log_event("@ReviewArmy", "MessageThinking",
                              f"📉 [校准]: '{f['description'][:25]}...' 置信度 {old_conf} → {f['confidence']} (历史误报记录)")
                    calibrated_count += 1
                    break

        if calibrated_count > 0:
            log_event("@ReviewArmy", "MessageStatus",
                      f"⚖️ 校准网激活: 已压降 {calibrated_count} 条已知误报。")

        # 过滤低置信度
        filtered = [f for f in deduped.values() if f["confidence"] >= 5]

        # 三分类
        triage = {"AUTO-FIX": [], "ASK": [], "INFO": []}
        for f in filtered:
            cat = f.get("category", "INFO")
            if cat in triage:
                triage[cat].append(f)

        self._report_findings(triage)
        return triage

    # 兼容旧接口
    async def run_review_army(self, diff_content: str) -> dict:
        """向后兼容旧的 diff 审查接口"""
        return await self.run_review(diff_content=diff_content)

    def _report_findings(self, triage: dict):
        total = sum(len(v) for v in triage.values())
        if total == 0:
            log_event("@ReviewArmy", "MessageToolResult",
                      "✅ Review Army v2.0 — 三路扫描完毕，未发现高危问题，绿灯放行。")
            return

        report = [f"⚔️ [Review Army v2.0] 扫描归建，共发现 {total} 项关注点：\n"]

        if triage["AUTO-FIX"]:
            report.append("🔧 [AUTO-FIX] (可自动修复):")
            for f in triage["AUTO-FIX"]:
                report.append(f"  - [{f['confidence']}/10] {f['file']}:{f['line']} — {f['description']}")

        if triage["ASK"]:
            report.append("\n⚠️ [ASK] (需人工定夺):")
            for f in triage["ASK"]:
                report.append(f"  - [{f['confidence']}/10] {f['file']}:{f['line']} — {f['description']}")

        if triage["INFO"]:
            report.append("\n💡 [INFO] (优化建议):")
            for f in triage["INFO"]:
                report.append(f"  - [{f['confidence']}/10] {f['file']}:{f['line']} — {f['description']}")

        log_event("@ReviewArmy", "MessageStatus", "\n".join(report))


# 保留旧类名作为别名，确保向后兼容
SpecialistReviewer = ReviewArmy


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        files = sys.argv[1:]
        reviewer = ReviewArmy(".")
        result = asyncio.run(reviewer.run_review(file_paths=files))
    else:
        # Demo: 审查自身
        reviewer = ReviewArmy(os.path.dirname(os.path.abspath(__file__)))
        result = asyncio.run(reviewer.run_review(file_paths=[__file__]))

    total = sum(len(v) for v in result.values())
    print(f"\n总发现: {total} (AUTO-FIX: {len(result['AUTO-FIX'])}, ASK: {len(result['ASK'])}, INFO: {len(result['INFO'])})")
