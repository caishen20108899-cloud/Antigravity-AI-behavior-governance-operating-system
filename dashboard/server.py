import http.server
import socketserver
import json
import os
import glob
from pathlib import Path

PORT = 8899
BASE_DIR = Path(__file__).resolve().parent.parent

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

    def do_GET(self):
        if self.path == '/api/skills':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            skills = []
            import re
            for skill_file in BASE_DIR.glob('*.agskill.md'):
                if skill_file.stem == 'template.agskill':
                    continue
                desc = f"Antigravity 全局能力卡片: {skill_file.stem}"
                display_name = skill_file.name
                try:
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        content = f.read(1500)
                        name_match = re.search(r'name:\s*"([^"]*)"', content)
                        desc_match = re.search(r'description:\s*"([^"]*)"', content)
                        if name_match:
                            display_name = name_match.group(1)
                        if desc_match:
                            desc = desc_match.group(1)
                except Exception:
                    pass
                
                skills.append({
                    "id": skill_file.stem,
                    "name": display_name,
                    "description": desc,
                    "path": str(skill_file)
                })
            self.wfile.write(json.dumps(skills).encode('utf-8'))
            return
            
        elif self.path == '/api/agents':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            import time
            now = time.time()
            projects_dir = BASE_DIR.parent
            
            # 1. 精准收集正在作业的兵种名单
            active_roles = set()
            
            # 从指挥大盘中搜寻正在进行 (▶) 的工单被分派给了谁
            for task_file in projects_dir.glob('*/AGENTS/commander/task_board.md'):
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if '|' in line and 'TASK-' in line and ('▶' in line or '进行中' in line):
                                parts = [p.strip() for p in line.split('|')]
                                if len(parts) >= 4:
                                    assignee = parts[2].lower().replace('@', '').replace('_', '')
                                    active_roles.add(assignee)
                except Exception:
                    pass
            
            # 从神经元发报机抓取 10 分钟以内的活动印记
            events_file = Path(os.path.expanduser("~/.gemini/antigravity/events.jsonl"))
            if events_file.exists():
                try:
                    with open(events_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[-30:]
                        for line in lines:
                            if line.strip():
                                evt = json.loads(line)
                                if now - evt.get("timestamp", 0) < 600:
                                    agent_name = evt.get("agent", "").lower().replace('@', '').replace('_', '')
                                    active_roles.add(agent_name)
                except Exception:
                    pass

            # 2. 匹配并映射展示格式
            agents_map = {}
            role_map = {
                "commander": "总司令 (Commander)",
                "architect": "发改委 (Architect)",
                "backend_engine": "基建部 (Backend)",
                "backend": "基建部 (Backend)",
                "engineer": "基建部 (Backend)",
                "frontend": "宣发部 (Frontend)",
                "web_craft": "宣发部 (Frontend)",
                "android_craft": "装备部 (Mobile)",
                "ios_craft": "装备部 (Mobile)",
                "mobile": "装备部 (Mobile)",
                "security_shield": "国安部 (Security)",
                "security": "国安部 (Security)",
                "devops": "后勤部 (DevOps)",
                "qa": "后勤部 (DevOps)",
                "quality_gate": "后勤部 (DevOps)"
            }
            for agents_dir in projects_dir.glob('*/AGENTS'):
                if agents_dir.is_dir():
                    project_name = agents_dir.parent.name
                    for role_dir in agents_dir.iterdir():
                        if role_dir.is_dir() and (role_dir / 'role.md').exists():
                            cn_role = role_dir.name.replace('_', ' ').title()
                            key = role_dir.name.lower()
                            display_name = role_map.get(key, cn_role)
                            
                            stripped_key = key.replace('_', '')
                            is_active = False
                            for ar in active_roles:
                                if stripped_key in ar or ar in stripped_key:
                                    is_active = True
                                    break
                            
                            if display_name not in agents_map:
                                agents_map[display_name] = {
                                    "role": display_name,
                                    "project": project_name,
                                    "status": "🟢 攻坚作业中" if is_active else "💤 挂机驻防"
                                }
                            else:
                                existing = agents_map[display_name]
                                if existing.get('project') and project_name not in existing['project']:
                                    existing['project'] += f" / {project_name}"
            
            agents = list(agents_map.values())
            self.wfile.write(json.dumps(agents).encode('utf-8'))
            return
            
        elif self.path == '/api/issues':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            issues = []
            projects_dir = BASE_DIR.parent
            
            # 扫描标准 AGENTS 编制的指挥看板 (支持 Markdown 表格解析)
            for task_file in projects_dir.glob('*/AGENTS/commander/task_board.md'):
                project_name = task_file.parent.parent.parent.name
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if '|' in line and 'TASK-' in line:
                                parts = [p.strip() for p in line.split('|')]
                                if len(parts) >= 4:
                                    task_id_title = parts[1]
                                    assignee = parts[2]
                                    status_raw = parts[3]
                                    
                                    status_str = "[Pending]"
                                    if '✅' in status_raw or '完成' in status_raw: status_str = "[Done]"
                                    elif '▶' in status_raw or '进行中' in status_raw: status_str = "[In-Progress]"
                                    elif '⛔' in status_raw or '阻塞' in status_raw: status_str = "[Blocker]"
                                    elif '■' in status_raw or '等待' in status_raw: status_str = "[Pending]"
                                    
                                    issues.append({
                                        "project": project_name,
                                        "content": f"[Issue-{task_id_title.split(' ')[0]}] | 指派: [{assignee}] | 状态: {status_str} | {task_id_title}"
                                    })
                except Exception:
                    pass
                    
            # 兼容全局法则下的单人记忆预警点 _active_task.md
            for active_file in projects_dir.glob('*/_active_task.md'):
                project_name = active_file.parent.name
                try:
                    with open(active_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if '当前停留点' in line or '正在执行' in line:
                                issues.append({
                                    "project": project_name,
                                    "content": f"[Issue-Current] | 指派: [@系统] | 状态: [In-Progress] | {line.strip()}"
                                })
                            elif '⛔' in line or '阻塞' in line or 'Blocker' in line:
                                issues.append({
                                    "project": project_name,
                                    "content": f"[Issue-Blocker] | 指派: [@系统] | 状态: [Blocker] | {line.strip()}"
                                })
                except Exception:
                    pass

            # 实时捕获 AI 大脑层的隐秘任务表 (task.md)
            import time
            now = time.time()
            brain_dir = Path("/Users/qianxiangyunji/.gemini/antigravity/brain")
            if brain_dir.exists():
                for task_file in brain_dir.glob('*/task.md'):
                    try:
                        if task_file.exists() and now - os.stat(task_file).st_mtime < 172800:
                            with open(task_file, 'r', encoding='utf-8') as f:
                                for line in f:
                                    line = line.strip()
                                    if line.startswith('- [') and len(line) > 5:
                                        status_str = ""
                                        if line.startswith('- [ ]'): status_str = "[Pending]"
                                        elif line.startswith('- [/]'): status_str = "[In-Progress]"
                                        elif line.startswith('- [x]'): status_str = "[Done]"
                                        content = line[5:].strip()
                                        if status_str:
                                            issues.append({
                                                "project": f"AI核心阵列 ({task_file.parent.name[:6]})",
                                                "content": f"[Issue-SYS] | 指派: [@统领/国防部] | 状态: {status_str} | {content}"
                                            })
                    except Exception:
                        pass
                        
            self.wfile.write(json.dumps(issues).encode('utf-8'))
            return
            
        elif self.path == '/api/events':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            events = []
            events_file = Path(os.path.expanduser("~/.gemini/antigravity/events.jsonl"))
            if events_file.exists():
                try:
                    with open(events_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[-150:] # 取最近150条截获包
                        for line in lines:
                            if line.strip():
                                events.append(json.loads(line))
                except Exception:
                    pass
            self.wfile.write(json.dumps(events).encode('utf-8'))
            return

        elif self.path == '/api/digest':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            digest = {
                'date': '',
                'github': [],
                'hackernews': [],
                'awesome': [],
                'suggestion': '',
                'raw_exists': False,
            }

            digest_file = BASE_DIR / '_community_digest.md'
            if digest_file.exists():
                digest['raw_exists'] = True
                import time as _time2
                age_hours = (_time2.time() - os.stat(digest_file).st_mtime) / 3600
                digest['is_stale'] = age_hours > 24
                digest['age_hours'] = round(age_hours, 1)
                try:
                    with open(digest_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取日期
                    import re
                    date_match = re.search(r'简报\s*\((\d{4}-\d{2}-\d{2})\)', content)
                    if date_match:
                        digest['date'] = date_match.group(1)

                    # 解析 GitHub 板块
                    gh_section = re.search(r'## 🔥 GitHub.*?\n(.*?)(?=\n## )', content, re.DOTALL)
                    if gh_section:
                        for m in re.finditer(
                            r'\d+\.\s*\*\*\[([^\]]+)\]\(([^)]+)\)\*\*\s*⭐\s*([\d,]+)\s*(?:\[(\w+)\])?\s*\n\s*(.+)',
                            gh_section.group(1)
                        ):
                            digest['github'].append({
                                'name': m.group(1),
                                'url': m.group(2),
                                'stars': m.group(3),
                                'lang': m.group(4) or '',
                                'desc': m.group(5).strip(),
                            })

                    # 解析 HN 板块
                    hn_section = re.search(r'## 📰 Hacker News.*?\n(.*?)(?=\n## )', content, re.DOTALL)
                    if hn_section:
                        for m in re.finditer(
                            r'-\s*\[([^\]]+)\]\(([^)]+)\)\s*(?:△(\d+))?\s*(?:💬(\d+))?\s*(?:\(\[讨论\]\(([^)]+)\)\))?',
                            hn_section.group(1)
                        ):
                            digest['hackernews'].append({
                                'title': m.group(1),
                                'url': m.group(2),
                                'score': m.group(3) or '0',
                                'comments': m.group(4) or '0',
                                'hn_url': m.group(5) or '',
                            })

                    # 解析 Awesome 板块
                    aw_section = re.search(r'## 📚 Awesome.*?\n(.*?)(?=\n## )', content, re.DOTALL)
                    if aw_section:
                        for m in re.finditer(
                            r'-\s*\*\*([^*]+)\*\*\s*\(([^)]+)\):\s*(.+)',
                            aw_section.group(1)
                        ):
                            digest['awesome'].append({
                                'repo': m.group(1),
                                'date': m.group(2),
                                'message': m.group(3).strip(),
                            })

                    # 解析 Reddit 板块
                    reddit_section = re.search(r'## 🔴 Reddit.*?\n(.*?)(?=\n## )', content, re.DOTALL)
                    if reddit_section:
                        for m in re.finditer(
                            r'-\s*\[([^\]]+)\]\(([^)]+)\)\s*(?:△(\d+))?\s*(?:💬(\d+))?\s*(?:\[([^\]]*)\])?\s*(?:\(\[讨论\]\(([^)]+)\)\))?',
                            reddit_section.group(1)
                        ):
                            digest.setdefault('reddit', []).append({
                                'title': m.group(1),
                                'url': m.group(2),
                                'score': m.group(3) or '0',
                                'comments': m.group(4) or '0',
                                'flair': m.group(5) or '',
                                'reddit_url': m.group(6) or '',
                            })

                    # 解析 arXiv 板块
                    arxiv_section = re.search(r'## 📄 arXiv.*?\n(.*?)(?=\n## )', content, re.DOTALL)
                    if arxiv_section:
                        for m in re.finditer(
                            r'-\s*\*\*\[([^\]]+)\]\(([^)]+)\)\*\*\s*\(([^)]*)\)\s*\n\s*(.+)',
                            arxiv_section.group(1)
                        ):
                            digest.setdefault('arxiv', []).append({
                                'title': m.group(1),
                                'url': m.group(2),
                                'date': m.group(3),
                                'summary': m.group(4).strip(),
                            })

                    # 提取建议
                    sug_section = re.search(r'## 🎯 建议关注.*?\n>\s*(.+)', content)
                    if sug_section:
                        digest['suggestion'] = sug_section.group(1).strip()

                except Exception as e:
                    digest['error'] = str(e)

            self.wfile.write(json.dumps(digest, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/api/learning':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            import time as _time
            learning_file = BASE_DIR / '_learning_digest.json'
            data = {"date": "", "new_skills": [], "updated_memories": [], "is_stale": True}
            if learning_file.exists():
                try:
                    with open(learning_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    age_hours = (_time.time() - os.stat(learning_file).st_mtime) / 3600
                    data['is_stale'] = age_hours > 24
                    data['age_hours'] = round(age_hours, 1)
                except Exception:
                    pass
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
            
        else:
            # serve static files
            return super().do_GET()

if __name__ == '__main__':
    os.chdir(BASE_DIR / 'dashboard')
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("localhost", PORT), DashboardHandler) as httpd:
        print(f"🚀 Antigravity Dashboard Server running at http://localhost:{PORT}")
        httpd.serve_forever()
