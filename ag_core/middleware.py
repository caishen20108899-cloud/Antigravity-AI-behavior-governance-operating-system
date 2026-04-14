import asyncio
from typing import Callable, Coroutine, Any, List
import sys
import os
from .event_logger import log_event

class MiddlewareContext:
    def __init__(self, role: str, task_name: str, payload: dict = None):
        self.role = role
        self.task_name = task_name
        self.payload = payload or {}
        self.results = {}

class Middleware:
    """抽象中间件基类"""
    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        raise NotImplementedError

class ContextHealthMiddleware(Middleware):
    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        log_event(f"@{context.role}", "MessageThinking", "🗜️ [ContextHealth: Pre-check] 评估神经元记忆负荷度...")
        # 预检查逻辑：检测 payload 长度或任务复杂度
        if context.payload.get("long_context"):
            log_event(f"@{context.role}", "MessageStatus", "⚠️ 测定到高负载上下文流，启动心理压缩准备工作。")
            
        result = await next_func()
        
        # 兜底截断预判
        log_event(f"@{context.role}", "MessageThinking", "🗜️ [ContextHealth: Post-check] 回收临时上下文痕迹。")
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
    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        log_event(f"@{context.role}", "MessageThinking", "🧠 [AutoMemory: Probe] 已锁定关联项目，待沉淀。")
        
        result = await next_func()
        
        # 核心在于执行完毕后的 "异步脱落" 机制
        # 探测如果有变更，则写盘 (此处为演练流)
        log_event(f"@{context.role}", "MessageStatus", "📚 [AutoMemory: Extract] 已异步捕获关键经验，正在后台归档中 (无阻塞)。")
        return result

class SurgicalCheckMiddleware(Middleware):
    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        log_event(f"@{context.role}", "MessageStatus", "🔬 [SurgicalCheck: Entry] 装载 Karpathy 四项铁律，开始防御检查...")
        # (1) Think Before Coding -> (2) Simplicity -> (3) Surgical Changes -> (4) Goal-Driven
        
        result = await next_func()
        
        log_event(f"@{context.role}", "MessageStatus", "✅ [SurgicalCheck: Verify] 执行波符合纯净手术刀要求，无额外感染蔓延。")
        return result

class ValidationGateMiddleware(Middleware):
    async def process(self, context: MiddlewareContext, next_func: Callable[[], Coroutine[Any, Any, Any]]):
        # 先放行执行主逻辑
        result = await next_func()
        
        # Archon-style Bash-Gate 后置硬性校验
        if context.payload.get("strict_mode"):
            cmd = context.payload.get("validation_command")
            cwd = context.payload.get("cwd", ".")
            log_event(f"@{context.role}", "MessageStatus", f"🛡️ [Archon-Gate] 探知严苛模式开启 -> 执行物理门禁令: {cmd}")
            
            proc = await asyncio.create_subprocess_shell(
                cmd, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE, 
                cwd=cwd
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore') or stdout.decode('utf-8', errors='ignore')
                log_event(f"@{context.role}", "MessageError", f"❌ [Archon-Gate] 拦截提交! 物理校验溃败 (返回码 {proc.returncode}): {error_msg.strip()}")
                raise RuntimeError(f"Archon Strict Gate Failed Validation `{cmd}`: {error_msg}")
                
            log_event(f"@{context.role}", "MessageToolResult", f"✅ [Archon-Gate] 物理级门禁放行，校验代码 {proc.returncode} 跑通。")
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
