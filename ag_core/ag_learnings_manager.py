import os
import json
import time

class LearningsManager:
    """
    gstack 风格的结构化沉淀系统 (v1.0)
    管理项目级 .learnings.jsonl 文件
    """
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.learnings_file = os.path.join(project_dir, "_learnings.jsonl")

    def log_learning(self, skill: str, learning_type: str, key: str, insight: str, confidence: int = 5, files: list = None):
        """
        沉淀一条经验。
        learning_type: pitfall, pattern, preference, operational
        """
        learning = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "skill": skill,
            "type": learning_type,
            "key": key,
            "insight": insight,
            "confidence": confidence,
            "source": "observed", # or user_stated, inferred
            "files": files or []
        }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.learnings_file), exist_ok=True)
        
        with open(self.learnings_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(learning, ensure_ascii=False) + "\n")
            
        return learning

    def search_learnings(self, keywords, min_confidence=5):
        """
        简单关键词搜索
        """
        if not os.path.exists(self.learnings_file):
            return []
            
        results = []
        with open(self.learnings_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("confidence", 0) < min_confidence:
                        continue
                        
                    # 匹配 keyword 到 key 或 insight
                    search_text = f"{entry.get('key', '')} {entry.get('insight', '')}".lower()
                    if any(k.lower() in search_text for k in keywords):
                        results.append(entry)
                except json.JSONDecodeError:
                    pass
                    
        return results

if __name__ == "__main__":
    # 测试代码
    manager = LearningsManager(".")
    manager.log_learning(
        skill="debug",
        learning_type="pitfall",
        key="test-framework-detection",
        insight="Python 项目如果用 requirements.txt 往往没有配置文件，需要尝试 fallback 到 pytest -x",
        confidence=8,
        files=["ag_core/middleware.py"]
    )
    res = manager.search_learnings(["pytest"])
    print(f"找到 {len(res)} 条经验")
