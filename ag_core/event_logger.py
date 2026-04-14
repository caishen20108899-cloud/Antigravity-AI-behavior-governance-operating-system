import os
import json
import time

EVENTS_FILE = os.path.expanduser("~/.gemini/antigravity/events.jsonl")

def log_event(agent_role: str, event_type: str, content: str, tool_name: str = None, metadata: dict = None):
    """
    统一智能体协议事件录入钩子 (Unified Agent Event Logger)
    event_type: 'MessageThinking', 'MessageToolUse', 'MessageToolResult', 'MessageStatus', 'MessageError'
    """
    os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)
    
    event = {
        "timestamp": time.time(),
        "agent": agent_role,
        "type": event_type,
        "content": content,
    }
    if tool_name:
        event["tool"] = tool_name
    if metadata:
        event["metadata"] = metadata
        
    try:
        with open(EVENTS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
            
        # 尺寸削峰 (日志旋转防胀死) 10MB
        if os.path.getsize(EVENTS_FILE) > 1024 * 1024 * 10:
            with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines[-200:])
    except Exception as e:
        print(f"Failed to log event: {e}")

if __name__ == "__main__":
    # 模拟写入一条系统自启动数据
    log_event("@系统中枢", "MessageStatus", "Antigravity Logger 模块已挂载并初始化成功。")
