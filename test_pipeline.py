import asyncio
import sys
import os

# Ensure import paths
sys.path.append(os.path.dirname(__file__))

from ag_core.dispatcher import AsyncGlobalDispatcher
from ag_core.event_logger import log_event

async def mock_task_success():
    await asyncio.sleep(1)
    log_event("@发改委", "MessageToolUse", "覆盖了代理服务器主表数据", tool_name="replace_file_content")
    return "加速通道重建完毕"

async def mock_task_fail():
    await asyncio.sleep(2)
    log_event("@工信部", "MessageToolUse", "尝试修改核心协议代码，不小心留了个bug", tool_name="replace_file_content")
    return "代码已修改完成"

async def main():
    log_event("@总司令", "MessageStatus", "🚨 [战备演练] 正式触发 Archon Validation-Gate V3.2 拦截实验")
    
    disp = AsyncGlobalDispatcher(max_concurrent=2)
    
    # 模拟正常任务 (无强校验 / 或是能通过强校验)
    payload_ok = {
        "strict_mode": True,
        "validation_command": "echo 'Syntax OK!'",
        "cwd": "."
    }
    t1 = disp.submit_task("发改委", "【防守】BGP节点维护", mock_task_success, payload=payload_ok)
    
    # 模拟危险任务 (抛出一个注定退出的错误校验命令，模拟语法错误过不去)
    payload_bad = {
        "strict_mode": True,
        "validation_command": "ls /path/that/does/not/exist/archon_test",
        "cwd": "."
    }
    t2 = disp.submit_task("工信部", "【高危】IM核心层渗透 (注定拦截)", mock_task_fail, payload=payload_bad)
    
    await disp.wait_all()

if __name__ == "__main__":
    asyncio.run(main())
