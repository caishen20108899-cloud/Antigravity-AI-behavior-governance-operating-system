import asyncio
import sys
import os
import json

# Ensure import paths
sys.path.append(os.path.dirname(__file__))

from ag_core.dispatcher import AsyncGlobalDispatcher
from ag_core.event_logger import log_event

async def mock_h5_init():
    await asyncio.sleep(2)
    log_event("@中央宣传部(Web)", "MessageThinking", "正在装载 Vite + Vue3 脚手架...")
    await asyncio.sleep(1)
    log_event("@中央宣传部(Web)", "MessageToolUse", "mkdir -p /ChiChatIM系统/clients/h5", tool_name="run_command")
    return "H5 初始化完毕"

async def mock_nginx_config():
    await asyncio.sleep(1)
    log_event("@国家安全部(Security)", "MessageThinking", "开始迁移 Lua 登录防护脚本...")
    await asyncio.sleep(2)
    log_event("@国家安全部(Security)", "MessageToolUse", "cp gateway/lua/*  /etc/nginx/conf.d/", tool_name="run_command")
    return "Lua 配置迁移完成"

async def mock_issue_sync():
    # 模拟在执行时写入 Kanban 能读到的文件
    task_file = "/Users/qianxiangyunji/.gemini/antigravity/brain/chichat_mock_task.md"
    os.makedirs(os.path.dirname(task_file), exist_ok=True)
    with open(task_file, "w") as f:
        f.write("# 临时作战指挥室\n")
        f.write("- [/] [Issue-301] | 指派: [@统领/国防部] | 正在执行 H5 初始化...\n")
        f.write("- [/] [Issue-201] | 指派: [@统领/国防部] | Nginx Lua 脚本桥接中...\n")
    
    await asyncio.sleep(1)
    log_event("@总司令", "MessageStatus", "已挂载工单到看板的 In-Progress 轨道！")
    return "更新看板成功"

async def end_issue_sync():
    task_file = "/Users/qianxiangyunji/.gemini/antigravity/brain/chichat_mock_task.md"
    with open(task_file, "w") as f:
        f.write("# 临时作战指挥室\n")
        f.write("- [x] [Issue-301] | 指派: [@统领/国防部] | H5 初始化完毕！\n")
        f.write("- [x] [Issue-201] | 指派: [@统领/国防部] | Nginx Lua 桥接完成！\n")
    log_event("@总司令", "MessageStatus", "防线穿越成功！看板工单已转为 Done 态。")


async def main():
    log_event("@系统阵列", "MessageStatus", "🚀 正在为您演示：独立多智能体如何打穿底层架构！")
    
    # 模拟先写入看板状态
    await mock_issue_sync()
    
    disp = AsyncGlobalDispatcher(max_concurrent=3)
    
    # Archon 校验规则：强要求命令成功
    payload_h5 = {"strict_mode": True, "validation_command": "echo 'Vue3 脚手架通过检测'", "cwd": "."}
    payload_nginx = {"strict_mode": True, "validation_command": "echo 'Lua 语法检测通过'", "cwd": "."}
    
    disp.submit_task("中央宣传部", "TASK-501_H5端构建", mock_h5_init, payload=payload_h5)
    disp.submit_task("国家安全部", "TASK-201_网关配置", mock_nginx_config, payload=payload_nginx)
    
    await disp.wait_all()
    await end_issue_sync()

if __name__ == "__main__":
    asyncio.run(main())
