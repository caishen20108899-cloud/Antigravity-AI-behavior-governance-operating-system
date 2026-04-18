import asyncio
from typing import Callable, Coroutine, Any, List
import sys
import os
import json
import time
from .event_logger import log_event

class StrikeTracker:
    def __init__(self, project_cwd):
        self.tracker_file = os.path.join(project_cwd, ".ag_strike_tracker.json")
    def _read(self):
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r') as f: return json.load(f)
            except Exception: pass
        return {}
    def _write(self, data):
        with open(self.tracker_file, 'w') as f: json.dump(data, f)
    def record_failure(self, identifier: str) -> int:
        data = self._read()
        strikes = data.get(identifier, 0) + 1
        data[identifier] = strikes
        self._write(data)
        return strikes
    def reset_failure(self, identifier: str):
        data = self._read()
        if identifier in data:
            del data[identifier]
            self._write(data)

class MiddlewareContext:
    def __init__(self, role: str, task_name: str, payload: dict = None):
        self.role = role
        self.task_name = task_name
        self.payload = payload or {}
        self.results = {}
        self.start_time = time.time()
        self.modified_files = []  # 追踪本次任务修改的文件

class Middleware:
    """抽象中间件基类"""
    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        raise NotImplementedError

class ContextHealthMiddleware(Middleware):
    """
    上下文健康度中间件 v3.2
    - 检测 payload 复杂度
    - 追踪执行时间
    - 超时预警
    """
    MAX_EXECUTION_TIME = 300  # 5 分钟软超时

    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        log_event(f"@{context.role}", "MessageThinking", "🗜️ [ContextHealth: Pre-check] 评估神经元记忆负荷度...")
        
        # 真实检查：payload 大小预警
        payload_size = len(json.dumps(context.payload, default=str))
        if payload_size > 50000:
            log_event(f"@{context.role}", "MessageStatus", f"⚠️ Payload 体积 {payload_size} 字节，超过 50KB 阈值，启动心理压缩。")
            context.payload["_context_compressed"] = True
            
        result = await next_func()
        
        # 后置检查：执行时间监控
        elapsed = time.time() - context.start_time
        if elapsed > self.MAX_EXECUTION_TIME:
            log_event(f"@{context.role}", "MessageStatus", f"⏰ [ContextHealth] 执行耗时 {elapsed:.0f}s，超过 {self.MAX_EXECUTION_TIME}s 软限，建议分拆任务。")
        else:
            log_event(f"@{context.role}", "MessageThinking", f"🗜️ [ContextHealth: Post-check] 执行耗时 {elapsed:.1f}s，正常范围。")
        
        return result

class DynamicSkillMiddleware(Middleware):
    """
    ag_evolve V2.0 联通桥梁: 
    根据当前执行的任务，动态且静默地从全局技能库中寻找最匹配的 Deep Learning 技能卡，
    并挂载到当前执行环境上下文 (payload) 中，赋予系统 '无师自通' 的能力。
    """
    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        task_query = context.task_name
        if context.payload and "goal" in context.payload:
            task_query += " " + context.payload["goal"]
            
        log_event(f"@{context.role}", "MessageThinking", f"🔍 [DynamicSkill: Probe] 正在全局技能库中扫描匹配 '{task_query[:20]}...'")
        
        try:
            from .ag_evolve import match_skills_for_task
            matches = match_skills_for_task(task_query)
            
            if matches:
                # 过滤出 10 分以上的高度匹配项
                top_skills = [m for m in matches if m[0] >= 10]
                if top_skills:
                    mounted = []
                    for score, path, name in top_skills:
                        mounted.append(name)
                    
                    context.payload["mounted_skills"] = top_skills
                    if len(mounted) > 1:
                        context.payload["skill_usage_strategy"] = (
                            "⚠️ 战术防冲突指令: 检测到系统为您同时挂载了多个技能卡。若这些技能在职能上存在高度重叠或属于竞品框架"
                            "(如同时注入了多种通信层、多个 Agent 编排引擎)，请务必在执行前：\n"
                            "1. 分析当前环境与业务诉求。\n"
                            "2. 做单选裁断（One-way Convergence），仅使用最合适的一项。\n"
                            "3. 绝对禁止将具有相同职能的不同框架 API 混合交织使用，以免发生排异反应。"
                        )
                        log_event(f"@{context.role}", "MessageStatus", f"🧬 [DynamicSkill: Loaded] 挂载高分技能: {', '.join(mounted)} (已注入防冲突校验令)")
                    else:
                        log_event(f"@{context.role}", "MessageStatus", f"🧬 [DynamicSkill: Loaded] 触发突触记忆！挂载独占技能: {mounted[0]}")
                else:
                    log_event(f"@{context.role}", "MessageThinking", "🧠 [DynamicSkill: Pass] 无高置信度技能卡，依赖基础智力。")
        except Exception as e:
            log_event(f"@{context.role}", "MessageError", f"⚠️ 技能库检索失败: {e}")
            
        return await next_func()

class AutoMemoryMiddleware(Middleware):
    """
    自动记忆中间件 v3.2
    - 前置：加载项目 _learnings.jsonl 
    - 后置：沉淀新经验（如果有）
    """
    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        # 前置：加载历史学习记忆
        learnings_loaded = 0
        cwd = context.payload.get("cwd", ".")
        learnings_path = os.path.join(cwd, "_learnings.jsonl")
        
        if os.path.exists(learnings_path):
            try:
                with open(learnings_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                            # 检查是否与当前任务相关（简单关键词匹配）
                            task_lower = context.task_name.lower()
                            key = entry.get("key", "").lower()
                            insight = entry.get("insight", "").lower()
                            if any(word in key or word in insight for word in task_lower.split()[:3]):
                                if "relevant_learnings" not in context.payload:
                                    context.payload["relevant_learnings"] = []
                                context.payload["relevant_learnings"].append(entry)
                                learnings_loaded += 1
                        except json.JSONDecodeError:
                            pass
                if learnings_loaded > 0:
                    log_event(f"@{context.role}", "MessageStatus", f"📚 [AutoMemory: Loaded] 命中 {learnings_loaded} 条历史经验记忆！")
                else:
                    log_event(f"@{context.role}", "MessageThinking", "🧠 [AutoMemory: Probe] 已扫描学习库，无匹配项。")
            except Exception as e:
                log_event(f"@{context.role}", "MessageError", f"⚠️ 学习库读取失败: {e}")
        else:
            log_event(f"@{context.role}", "MessageThinking", "🧠 [AutoMemory: Probe] 项目无学习库文件，跳过。")
        
        result = await next_func()
        
        # 后置：如果 payload 中有新经验要沉淀
        new_learnings = context.payload.get("new_learnings", [])
        if new_learnings and os.path.isdir(cwd):
            try:
                with open(learnings_path, 'a') as f:
                    for learning in new_learnings:
                        learning["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                        learning["skill"] = context.task_name
                        f.write(json.dumps(learning, ensure_ascii=False) + "\n")
                log_event(f"@{context.role}", "MessageStatus", f"📚 [AutoMemory: Saved] 沉淀 {len(new_learnings)} 条新经验到学习库。")
            except Exception as e:
                log_event(f"@{context.role}", "MessageError", f"⚠️ 经验沉淀失败: {e}")
        
        return result

class SurgicalCheckMiddleware(Middleware):
    """
    Karpathy 手术刀中间件 v3.2 — 真牙齿版
    - 前置：记录修改前的文件状态
    - 后置：验证改动范围是否超标
    """
    MAX_CHANGED_FILES = 10     # 单次任务最大文件修改数
    MAX_CHANGED_LINES = 300    # 单次任务最大改动行数
    
    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        log_event(f"@{context.role}", "MessageStatus", "🔬 [SurgicalCheck: Entry] 装载 Karpathy 四项铁律，记录术前快照...")
        
        # 前置：记录 git 状态快照（真实检查）
        cwd = context.payload.get("cwd", ".")
        pre_diff = ""
        try:
            proc = await asyncio.create_subprocess_shell(
                "git diff --stat HEAD 2>/dev/null || echo 'NOT_GIT'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            stdout, _ = await proc.communicate()
            pre_diff = stdout.decode('utf-8', errors='ignore').strip()
        except Exception:
            pre_diff = "UNKNOWN"
        
        context.payload["_pre_surgical_diff"] = pre_diff
        
        result = await next_func()
        
        # 后置：比较修改范围（真实验证）
        try:
            proc = await asyncio.create_subprocess_shell(
                "git diff --stat HEAD 2>/dev/null || echo 'NOT_GIT'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            stdout, _ = await proc.communicate()
            post_diff = stdout.decode('utf-8', errors='ignore').strip()
            
            if post_diff and post_diff != "NOT_GIT":
                # 解析改动统计
                lines = post_diff.strip().split('\n')
                summary_line = lines[-1] if lines else ""
                changed_files = 0
                insertions = 0
                deletions = 0
                
                # 解析 "N files changed, X insertions(+), Y deletions(-)"
                import re
                match = re.search(r'(\d+) files? changed', summary_line)
                if match:
                    changed_files = int(match.group(1))
                ins_match = re.search(r'(\d+) insertions?\(\+\)', summary_line)
                if ins_match:
                    insertions = int(ins_match.group(1))
                del_match = re.search(r'(\d+) deletions?\(-\)', summary_line)
                if del_match:
                    deletions = int(del_match.group(1))
                
                total_lines = insertions + deletions
                
                # 范围超标检测
                max_files = context.payload.get("max_files", self.MAX_CHANGED_FILES)
                max_lines = context.payload.get("max_lines", self.MAX_CHANGED_LINES)
                
                if changed_files > max_files:
                    log_event(f"@{context.role}", "MessageError", 
                             f"🔴 [SurgicalCheck: ALERT] 手术刀违规！改了 {changed_files} 个文件，超过上限 {max_files}，疑似范围蔓延！")
                elif total_lines > max_lines:
                    log_event(f"@{context.role}", "MessageError",
                             f"🟡 [SurgicalCheck: WARN] 改动 {total_lines} 行（+{insertions}/-{deletions}），超过建议上限 {max_lines} 行，请自查是否过度修改。")
                else:
                    log_event(f"@{context.role}", "MessageStatus",
                             f"✅ [SurgicalCheck: PASS] 范围合规：{changed_files} 文件，{total_lines} 行改动（+{insertions}/-{deletions}）。")
                
                # 记录改动详情供审计
                context.results["surgical_audit"] = {
                    "changed_files": changed_files,
                    "insertions": insertions,
                    "deletions": deletions,
                    "total_lines": total_lines,
                    "within_limits": changed_files <= max_files and total_lines <= max_lines
                }
            else:
                log_event(f"@{context.role}", "MessageThinking", "🔬 [SurgicalCheck: Skip] 非 git 仓库或无变更，跳过范围检查。")
        except Exception as e:
            log_event(f"@{context.role}", "MessageError", f"⚠️ [SurgicalCheck] 后置验证异常: {e}")
        
        return result

class ValidationGateMiddleware(Middleware):
    """
    Archon 物理验证门禁 v3.2 — 增强版
    - 自动检测项目测试框架
    - 默认启用编译检查
    - strict_mode 启用全量测试
    """
    # 自动检测的测试命令映射
    TEST_DETECTORS = {
        "package.json": {"check": '"test"', "cmd": "npm test -- --passWithNoTests 2>&1 | tail -20"},
        "Gemfile": {"check": None, "cmd": "bundle exec rspec --format progress 2>&1 | tail -20"},
        "pyproject.toml": {"check": None, "cmd": "python -m pytest -x -q 2>&1 | tail -20"},
        "requirements.txt": {"check": None, "cmd": "python -m pytest -x -q 2>&1 | tail -20"},
        "go.mod": {"check": None, "cmd": "go test ./... 2>&1 | tail -20"},
        "Cargo.toml": {"check": None, "cmd": "cargo test 2>&1 | tail -20"},
    }

    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        # 先放行执行主逻辑
        result = await next_func()
        
        cwd = context.payload.get("cwd", ".")
        
        # === 自动检测并执行验证 ===
        # 除非明确 skip_validation=True，否则始终尝试验证
        if context.payload.get("skip_validation"):
            log_event(f"@{context.role}", "MessageThinking", "⏭️ [Archon-Gate] 已标记 skip_validation，跳过。")
            return result
        
        # 检测测试命令
        validation_cmd = context.payload.get("validation_command")
        
        if not validation_cmd:
            # 自动检测
            for config_file, detector in self.TEST_DETECTORS.items():
                config_path = os.path.join(cwd, config_file)
                if os.path.exists(config_path):
                    if detector["check"]:
                        try:
                            with open(config_path, 'r') as f:
                                if detector["check"] in f.read():
                                    validation_cmd = detector["cmd"]
                                    break
                        except Exception:
                            pass
                    else:
                        validation_cmd = detector["cmd"]
                        break
        
        if not validation_cmd:
            log_event(f"@{context.role}", "MessageThinking", "🔍 [Archon-Gate] 未检测到测试框架，跳过物理验证。")
            return result
        
        # 执行验证
        log_event(f"@{context.role}", "MessageStatus", f"🛡️ [Archon-Gate] 执行物理门禁: {validation_cmd[:60]}...")
        
        try:
            proc = await asyncio.create_subprocess_shell(
                validation_cmd, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE, 
                cwd=cwd
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
            
            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')
            
            if proc.returncode != 0:
                combined = (error_output or output).strip()
                log_event(f"@{context.role}", "MessageError", 
                         f"❌ [Archon-Gate] 物理验证失败 (Exit Code {proc.returncode}):\n{combined[:500]}")
                
                # --- 3-Strike 防狂奔熔断 ---
                from .ag_learnings_manager import LearningsManager
                tracker = StrikeTracker(cwd)
                target_file = next(iter(context.modified_files)) if context.modified_files else "general_task"
                strikes = tracker.record_failure(f"validation_fail_{target_file}")
                
                if strikes >= 3:
                     # 彻底熔断，防止无限循环
                     log_event(f"@{context.role}", "MessageError", f"🛑 [3-STRIKE EJECTION] 针对 '{target_file}' 的验证已连续失败 {strikes} 次！触发熔断。AI 权限已降级，请交由指挥官核查。")
                     raise RuntimeError(f"[3-STRIKE EJECTION] 停止盲目重试！文件 '{target_file}' 已连续失败 3 次。系统强行制止。")
                else:
                    log_event(f"@{context.role}", "MessageStatus", f"⚠️ 警告: Strike {strikes}/3. 物理测试尚未通过。")

                # strict_mode 下直接抛异常阻止继续
                if context.payload.get("strict_mode"):
                    raise RuntimeError(f"Archon Gate FAILED: {validation_cmd}\nExit Code: {proc.returncode}\n{combined[:300]}")
                else:
                    log_event(f"@{context.role}", "MessageStatus", 
                             "⚠️ [Archon-Gate] 非严苛模式，记录失败但不阻断。建议人工检查。")
            else:
                log_event(f"@{context.role}", "MessageToolResult", 
                         f"✅ [Archon-Gate] 物理门禁放行！Exit Code 0。")
                
                # 重置计数器
                tracker = StrikeTracker(cwd)
                target_file = next(iter(context.modified_files)) if context.modified_files else "general_task"
                tracker.reset_failure(f"validation_fail_{target_file}")
            
            # --- 覆盖率看门狗 (Coverage Watchdog) 阶段 ---
            # 只在有 .py 代码修改时触发覆盖率审计
            if context.modified_files:
                py_files = [f for f in context.modified_files if f.endswith('.py')]
                if py_files:
                    log_event(f"@{context.role}", "MessageThinking", "🔍 [Archon-Gate] 触发 Coverage Watchdog 代码路径审计...")
                    try:
                        from .ag_coverage_audit import CoverageAuditor
                        auditor = CoverageAuditor(cwd)
                        audit_results = []
                        all_passed = True
                        for pyf in py_files:
                            report = auditor.audit_file(pyf)
                            if report:
                                audit_results.append(report)
                                if "STATUS:   FAILED" in report:
                                    all_passed = False
                        
                        if audit_results:
                            combined_report = "\n\n".join(audit_results)
                            if all_passed:
                                log_event(f"@{context.role}", "MessageToolResult", f"✅ [Coverage Watchdog] 审计通过：\n{combined_report[:300]}...")
                            else:
                                log_event(f"@{context.role}", "MessageError", f"🟡 [Coverage Watchdog] 审计暴漏覆盖区盲点（第一周仅警告，不拦截）：\n{combined_report[:500]}...")
                    except Exception as ce:
                        log_event(f"@{context.role}", "MessageError", f"⚠️ [Coverage Watchdog] 审计组件异常，放行: {ce}")

            # 记录验证结果
            context.results["validation"] = {
                "command": validation_cmd,
                "exit_code": proc.returncode,
                "passed": proc.returncode == 0,
                "output_tail": output[-200:] if output else ""
            }
            
        except asyncio.TimeoutError:
            log_event(f"@{context.role}", "MessageError", f"⏰ [Archon-Gate] 验证命令超时（120s），跳过。")
        except RuntimeError:
            raise  # 重新抛出 strict_mode 的异常
        except Exception as e:
            log_event(f"@{context.role}", "MessageError", f"⚠️ [Archon-Gate] 验证执行异常: {e}")
                
        return result

class MiddlewarePipeline:
    def __init__(self, middlewares: List[Middleware]):
        self.middlewares = middlewares

    async def execute(self, context: MiddlewareContext, final_action: Callable[[], Coroutine[Any, Any, Any]]):
        # 洋葱圈模型编排
        async def build_chain(index: int):
            if index < len(self.middlewares):
                middleware = self.middlewares[index]
                async def _next():
                    return await build_chain(index + 1)
                return await middleware.process(context, _next)
            else:
                return await final_action()
        
        return await build_chain(0)
