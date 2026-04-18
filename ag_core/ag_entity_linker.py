import re
import json
import os
import uuid
import time
from .ag_learnings_manager import LearningsManager
from .event_logger import log_event

class EntityLinker:
    """
    gstack 风格的 GBrain 实体抽屉 (Entity Networking Tracker).
    在各类智能体产出信息后静默启动，利用启发式/正则或轻模型抽取出有业务价值的实体，
    并挂载进 _learnings.jsonl 中构建全息隐蔽图谱。
    """
    def __init__(self, project_cwd):
        self.cwd = project_cwd
        self.learnings = LearningsManager(project_cwd)
        
    def extract_and_link(self, content_stream: str, source_module: str = "general"):
        """探测内容并建立图谱。为避免拖慢速度采用启发式或异步弱探测。"""
        new_links = []
        
        # 1. 简易探测 IP/集群主机地址 (Host/Cluster entities)
        ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', content_stream)
        
        # 2. 探测明显提到的人员/组织代号 (例如: @[A-Z]\w+ 或 姓名)
        people_or_roles = re.findall(r'@([A-Z][a-zA-Z0-9_]+)', content_stream)
        
        # 3. 探测 Git 项目仓库哈希或关键词
        repos = re.findall(r'github\.com/([a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+)', content_stream)
        
        # 建立图谱集合
        entities_found = {"Host": set(ips), "Role": set(people_or_roles), "Repo": set(repos)}
        
        # 沉淀入网
        added_count = 0
        for category, entities in entities_found.items():
            for e in entities:
                # 检查是否已经存在
                existing = self.learnings.search_learnings([category.lower(), e.lower()])
                if not any(r.get('key') == e for r in existing):
                    self.learnings.log_learning(
                        skill="GBrain-Linker",
                        learning_type="entity_link",
                        key=e,
                        insight=f"System implicitly discovered a new {category} entity related to [{source_module}]",
                        confidence=9,
                        files=[]
                    )
                    added_count += 1
                    
        if added_count > 0:
            log_event("@GBrain", "MessageStatus", f"🕸️ [Entity Net] 后台感知运转... 已将 {added_count} 个新鲜实体名固化入业务知识图谱以备未来跨域唤醒。")
            
        return added_count

if __name__ == "__main__":
    test_stream = "我们在 192.168.1.1 部署了新的 @DevOps 和 @Architect 环境，代码来自 github.com/garrytan/gstack 。"
    linker = EntityLinker(".")
    linker.extract_and_link(test_stream, "test_script")
