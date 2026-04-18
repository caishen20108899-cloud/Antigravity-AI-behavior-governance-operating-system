import asyncio
import json
import uuid
import re
from .event_logger import log_event
from .ag_learnings_manager import LearningsManager

class SpecialistReviewer:
    """
    gstack 风格的 Review Army (轻量化)
    定义并发专家角色及指纹去重机制
    """
    SPECIALISTS = {
        "testing": {
            "name": "Testing Specialist",
            "focus": "寻找未覆盖的边界测试、异常处理遗漏、Mock 数据失真",
        },
        "security": {
            "name": "Security Specialist",
            "focus": "寻找未授权访问、SQL/XSS/Command 注入、硬编码密钥、敏感信息泄露",
        },
        "consistency": {
            "name": "Consistency Specialist",
            "focus": "寻找命名污染、架构分层越权、未能复用已有工具函数",
        }
    }

    def __init__(self, project_cwd):
        self.cwd = project_cwd
        self.learnings = LearningsManager(project_cwd)

    async def _mock_llm_call(self, role, diff_content):
        """
        在无外部确切 LLM 接口前，为演示防线流程提供的桩函数。
        实际应用中，这里应替换为对大模型接口的 HTTP/SDK 并发调用。
        """
        await asyncio.sleep(1)  # Simulate network latency
        
        # 简单规则匹配模拟 LLM 发现
        findings = []
        if role == "security" and "password" in diff_content.lower():
            findings.append({
                "id": str(uuid.uuid4())[:8],
                "file": "mock_file.py",
                "line": "N/A",
                "description": "疑似硬编码密码或敏感词处理不当",
                "confidence": 8,
                "category": "ASK"
            })
            
        if role == "testing" and "if " in diff_content:
            findings.append({
                "id": str(uuid.uuid4())[:8],
                "file": "mock_file.py",
                "line": "N/A",
                "description": "新增的 if 分支未在当前上下文中看到测试支持",
                "confidence": 6,
                "category": "INFO"
            })
            
        if role == "consistency" and "print(" in diff_content:
            findings.append({
                "id": str(uuid.uuid4())[:8],
                "file": "mock_file.py",
                "line": "N/A",
                "description": "使用了 print() 代替统一的 log_event()",
                "confidence": 9,
                "category": "AUTO-FIX"
            })

        return findings

    async def run_review_army(self, diff_content: str):
        log_event("@ReviewArmy", "MessageStatus", f"⚔️ 触发专家评审团：将向 {len(self.SPECIALISTS)} 个子特工并发推送审查请求，等待回应...")
        
        tasks = []
        for role_key, role_info in self.SPECIALISTS.items():
            tasks.append(self._mock_llm_call(role_key, diff_content))
            
        results = await asyncio.gather(*tasks)
        
        # 展平全部 findings
        all_findings = [f for sublist in results for f in sublist]
        
        # 指纹去重 (简易版：按 description 相似度或精确匹配)
        deduped = {}
        for f in all_findings:
            key = f["description"]
            if key not in deduped or f["confidence"] > deduped[key]["confidence"]:
                deduped[key] = f
                
        # --- 置信度校准 (Confidence Calibration) ---
        calibrated_count = 0
        for f in deduped.values():
            # 获取关于此问题可能的宽容历史学习记录
            past_tolerance = self.learnings.search_learnings([f["category"].lower(), f["description"].lower()[:15]])
            for record in past_tolerance:
                if record.get("type") == "false_positive" or record.get("type") == "tolerance":
                    old_conf = f["confidence"]
                    # 发现宽容记录（如误报，或者用户倾向于忽略此类错误），则手动压低置信度
                    f["confidence"] -= min(3, f["confidence"])
                    log_event("@ReviewArmy", "MessageThinking", 
                             f"📉 [校准过滤]: 针对 '{f['description'][:20]}...' 侦测到历史宽容记录 (Id: {record.get('id', 'N/A')})。置信度自 {old_conf} 降纬至 {f['confidence']}。")
                    calibrated_count += 1
                    break
        
        if calibrated_count > 0:
            log_event("@ReviewArmy", "MessageStatus", f"⚖️ [校准网激活]: 已基于项目 _learnings 自动压降 {calibrated_count} 条已知误报的干扰报警。")
                
        # 过滤低置信度噪音 (confidence < 5)
        filtered = [f for f in deduped.values() if f["confidence"] >= 5]
        
        # 三分类存放
        triage = {"AUTO-FIX": [], "ASK": [], "INFO": []}
        for f in filtered:
            cat = f.get("category", "INFO")
            if cat in triage:
                triage[cat].append(f)
                
        self._report_findings(triage)
        return triage
        
    def _report_findings(self, triage):
        total = sum(len(v) for v in triage.values())
        if total == 0:
            log_event("@ReviewArmy", "MessageToolResult", "✅ 评审团未发现高危问题，绿灯放行。")
            return
            
        report = [f"⚔️ [Review Army] 评审团归建，共发现 {total} 项关注点：\n"]
        
        if triage["AUTO-FIX"]:
            report.append("🔧 [AUTO-FIX] (机械修改 - 将自动介入):")
            for f in triage["AUTO-FIX"]:
                report.append(f"  - [{f['confidence']}/10] {f['description']}")
                
        if triage["ASK"]:
            report.append("\n⚠️ [ASK] (风险判定 - 需指挥官定夺):")
            for f in triage["ASK"]:
                report.append(f"  - [{f['confidence']}/10] {f['description']}")
                
        if triage["INFO"]:
            report.append("\n💡 [INFO] (优化建议 - 暂存不强干预):")
            for f in triage["INFO"]:
                report.append(f"  - [{f['confidence']}/10] {f['description']}")
                
        log_event("@ReviewArmy", "MessageStatus", "\n".join(report))

if __name__ == "__main__":
    import sys
    diff_content = sys.argv[1] if len(sys.argv) > 1 else "def auth():\n    password = 'admin'\n    print('Logged in')\n    if True:\n        pass"
    reviewer = SpecialistReviewer(".")
    asyncio.run(reviewer.run_review_army(diff_content))
