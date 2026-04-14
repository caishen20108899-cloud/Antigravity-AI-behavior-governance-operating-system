import os
import json
import time
from datetime import datetime, timedelta

def get_recent_learnings(base_dir):
    """提取过去 48 小时内的系统学习与技能新增情况"""
    now = time.time()
    cutoff = now - 48 * 3600
    
    learnings = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "new_skills": [],
        "updated_memories": []
    }
    
    # 扫描技能卡
    skills_dir = os.path.join(base_dir, "全局技能库_AG_Skills")
    trending_dir = os.path.join(skills_dir, "_trending_skills")
    
    seen_skills = set()
    
    for check_dir in [trending_dir, skills_dir]: # 先检查 trending
        if os.path.exists(check_dir):
            for f in os.listdir(check_dir):
                if f.endswith(".agskill.md"):
                    path = os.path.join(check_dir, f)
                    if os.path.getmtime(path) > cutoff:
                        # 从文件名推断特征
                        raw_name = f.replace('.agskill.md', '')
                        if '_' in raw_name:
                            name = raw_name.split('_', 1)[1].capitalize()
                        else:
                            name = raw_name.capitalize()
                            
                        if name in seen_skills:
                            continue
                        seen_skills.add(name)
                            
                        with open(path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            # 提取 📋 概要下的第一句话
                            desc = "新增技能特性"
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if "概要" in line or "Summary" in line:
                                    if i + 1 < len(lines) and lines[i+1].strip():
                                        desc = lines[i+1].strip()
                                        if len(desc) > 300: # 设一个较宽松的上限防爆版
                                            desc = desc[:300] + '...'
                                    break
                            learnings["new_skills"].append({"name": name, "desc": desc})

    # 扫描各项目 MEMORY.md
    for root, dirs, files in os.walk(base_dir):
        if any(x in root for x in ['.git', '.gemini', 'node_modules', 'venv', '全局技能库_AG_Skills']):
            continue
        if "MEMORY.md" in files:
            path = os.path.join(root, "MEMORY.md")
            if os.path.getmtime(path) > cutoff:
                project_name = os.path.basename(root)
                learnings["updated_memories"].append({
                    "project": project_name,
                    "desc": f"过去 48 小时内更新了 {project_name} 项目逻辑库"
                })

    return learnings

if __name__ == "__main__":
    base_dir = "/Users/qianxiangyunji/Antigravity"
    data = get_recent_learnings(base_dir)
    out_path = os.path.join(base_dir, "全局技能库_AG_Skills", "_learning_digest.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ AI 学习简报已生成: {out_path}")
