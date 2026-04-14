import os
import shutil
import hashlib
from .event_logger import log_event

CACHE_DIR = os.path.expanduser("~/.gemini/antigravity/.ag_repos")

class RepoCacheManager:
    """
    脱胎于 Multica repocache 的深层逻辑抽象。
    为庞大的前端/服务端架构创建极速上下文克隆，以实现无痛秒级追溯。
    """
    @staticmethod
    def _hash_path(path: str) -> str:
        return hashlib.md5(path.encode()).hexdigest()

    @staticmethod
    def create_snapshot(workspace_path: str, ignores=None):
        if not os.path.exists(workspace_path):
            log_event("@后勤保障", "MessageError", f"源矩阵 {workspace_path} 坍缩失效。")
            return None
            
        if ignores is None:
            ignores = ['.git', 'node_modules', 'target', 'venv', '__pycache__', '.idea', 'build']
            
        hashed_id = RepoCacheManager._hash_path(workspace_path)
        snapshot_path = os.path.join(CACHE_DIR, hashed_id)
        
        # 覆写热缓存
        if os.path.exists(snapshot_path):
            shutil.rmtree(snapshot_path)
            
        def ignore_func(d, files):
            return [f for f in files if f in ignores or f.startswith('.')]
            
        try:
            log_event("@后勤保障", "MessageThinking", f"正在对目标域 {workspace_path[-25:]} 施加克隆投影...")
            shutil.copytree(workspace_path, snapshot_path, ignore=ignore_func, symlinks=True)
            log_event("@后勤保障", "MessageToolResult", f"投影构建完毕: {snapshot_path}")
            return snapshot_path
        except Exception as e:
            log_event("@后勤保障", "MessageError", f"域投影遭遇屏障: {str(e)}")
            return None

    @staticmethod
    def wipe_all():
        if os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR)
            log_event("@后勤保障", "MessageStatus", "已清空全局全域缓存矩阵池。")
