import asyncio
from typing import Callable, Coroutine, Any
from .event_logger import log_event
from .middleware import MiddlewareContext, MiddlewarePipeline, ContextHealthMiddleware, AutoMemoryMiddleware, SurgicalCheckMiddleware, ValidationGateMiddleware, DynamicSkillMiddleware

class AsyncGlobalDispatcher:
    """
    反重力并发调度神经元 V3.1 (已融合 Deer-Flow 洋葱拦截网)
    每一次工单执行不再是裸奔，而是必须穿透记忆、安全、和减负等中间防线。
    """
    def __init__(self, max_concurrent: int = 3):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.tasks = []
        
        # 挂载基础防线
        self.pipeline = MiddlewarePipeline([
            ContextHealthMiddleware(),
            DynamicSkillMiddleware(),
            AutoMemoryMiddleware(),
            SurgicalCheckMiddleware(),
            ValidationGateMiddleware()
        ])

    async def _worker(self, role: str, task_name: str, payload: dict, func: Callable[[], Coroutine[Any, Any, Any]]):
        async with self.semaphore:
            log_event(f"@{role}", "MessageStatus", f"⚡ 分配获取锁定 -> 挂载滤网进入交战圈: {task_name}")
            
            # 组装作战上下文
            ctx = MiddlewareContext(role=role, task_name=task_name, payload=payload)
            
            try:
                # 迫使执行体打穿整个 Pipeline 防线！
                result = await self.pipeline.execute(ctx, func)
                
                log_event(f"@{role}", "MessageToolResult", f"✅ 工单回执: {task_name} 经洋葱验证处理完毕。")
                return result
            except Exception as e:
                log_event(f"@{role}", "MessageError", f"❌ 贯穿防线时崩溃: {task_name} -> {str(e)}")
                raise

    def submit_task(self, role: str, task_name: str, func: Callable[[], Coroutine[Any, Any, Any]], payload: dict = None):
        if payload is None:
            payload = {}
        log_event("@系统阵列", "MessageLog", f"📥 调度器收容越狱工单: [{role}] {task_name}")
        task = asyncio.create_task(self._worker(role, task_name, payload, func))
        self.tasks.append(task)
        return task

    async def wait_all(self):
        log_event("@系统阵列", "MessageStatus", "⏳ 锁柜全闭，等待执行梯队归建...")
        await asyncio.gather(*self.tasks, return_exceptions=True)
        log_event("@系统阵列", "MessageStatus", "🎉 战术撤退，当前序列清空，释放洋葱防线。")
        self.tasks = []
