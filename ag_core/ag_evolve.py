#!/usr/bin/env python3
"""
ag_evolve.py — Antigravity 社区自进化引擎 (Community Evolution Engine)
=====================================================================
每日自动从全球开发者社区抓取 AI/Agent 领域最新动态，
转化为可被 AI 直接消费的社区简报和趋势技能卡。

信息源:
    1. GitHub Trending (API)
    2. Hacker News Top Stories (API + 关键词过滤)
    3. Awesome 列表监控 (GitHub commits API)
    4. Reddit /r/MachineLearning (RSS)
    5. arXiv AI 每日论文 (API)
    6. MCP Server Registry (预留)

用法:
    python3 ag_evolve.py
    python3 ag_evolve.py --output /custom/path

部署: Mac mini Cron 每日 UTC 00:00 执行
依赖: 零外部依赖，仅用 Python 标准库
"""

import json
import os
import ssl
import sys
import time
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


# ─────────────────────────────── 配置 ───────────────────────────────

# 输出路径
SKILLS_DIR = os.path.expanduser(
    "~/Antigravity/全局技能库_AG_Skills"
)
DIGEST_FILE = os.path.join(SKILLS_DIR, "_community_digest.md")
TRENDING_DIR = os.path.join(SKILLS_DIR, "_trending_skills")

# AI/Agent 关键词过滤器（HN 标题匹配用）
AI_KEYWORDS = {
    'ai', 'agent', 'llm', 'gpt', 'claude', 'gemini', 'copilot',
    'langchain', 'openai', 'anthropic', 'rag', 'vector', 'embedding',
    'transformer', 'diffusion', 'stable diffusion', 'midjourney',
    'coding agent', 'code generation', 'code review',
    'mcp', 'model context protocol', 'tool use', 'function calling',
    'autonomous', 'agentic', 'multi-agent', 'swarm',
    'cursor', 'windsurf', 'devin', 'replit', 'bolt',
}

# GitHub Trending 语言过滤
TRENDING_LANGUAGES = ['python', 'typescript', 'go', 'rust', 'javascript']

# 请求超时（秒）
REQUEST_TIMEOUT = 15

# SSL 上下文（忽略证书验证，适应各种网络环境）
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# User-Agent
UA = "Antigravity-Evolve/1.0"


# ─────────────────────────── 网络工具 ───────────────────────────


def _fetch_json(url, headers=None):
    """安全的 JSON HTTP GET"""
    req_headers = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        req_headers.update(headers)

    req = Request(url, headers=req_headers)
    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT, context=SSL_CTX) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except (URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"  ⚠️ 网络请求失败: {url} — {e}")
        return None


def _fetch_text(url):
    """安全的纯文本 HTTP GET"""
    req = Request(url, headers={"User-Agent": UA})
    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT, context=SSL_CTX) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        print(f"  ⚠️ 网络请求失败: {url} — {e}")
        return None


def _translate_text(text):
    """使用 Google 免费翻译 API 将英文翻译为中文（无需 key）"""
    if not text or len(text) < 3:
        return text
    try:
        encoded = quote(text)
        url = (
            "https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded}"
        )
        req = Request(url, headers={"User-Agent": UA})
        with urlopen(req, timeout=8, context=SSL_CTX) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            # 返回格式: [[['翻译结果','原文',null,null,10]], ...]
            if data and data[0]:
                return ''.join(seg[0] for seg in data[0] if seg[0])
    except Exception:
        pass
    return text


def _translate_batch(texts, label=""):
    """批量翻译文本列表，带进度提示，失败静默降级为原文"""
    if not texts:
        return texts
    results = []
    translated = 0
    for t in texts:
        zh = _translate_text(t)
        results.append(zh)
        if zh != t:
            translated += 1
        time.sleep(0.15)  # 限速防封
    if label and translated > 0:
        print(f"  🌐 {label}: {translated}/{len(texts)} 条已翻译为中文")
    return results


# ────────────────────── 数据源采集器 ──────────────────────


def fetch_github_trending():
    """
    抓取 GitHub Trending 仓库（使用搜索 API 近似实现）。
    GitHub 没有官方 Trending API，使用 search/repositories 按最近 stars 排序。
    三级降级策略确保总能拿到数据。
    """
    print("📡 正在抓取 GitHub Trending...")
    results = []

    # 动态计算 7 天前日期
    from datetime import timedelta
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')

    # ── 第一优先：最近 7 天有更新的 AI/Agent 热门仓库 ──
    q1 = quote(f"ai agent pushed:>{week_ago} stars:>500")
    url1 = f"https://api.github.com/search/repositories?q={q1}&sort=stars&order=desc&per_page=10"
    data = _fetch_json(url1)

    # ── 降级1：按 topic 搜索 ──
    if not data or not data.get('items'):
        print("  ⚠️ 第一查询无结果，降级到 topic 搜索...")
        q2 = quote("topic:agent topic:llm language:python")
        url2 = f"https://api.github.com/search/repositories?q={q2}&sort=stars&order=desc&per_page=10"
        data = _fetch_json(url2)

    # ── 降级2：最宽泛的搜索 ──
    if not data or not data.get('items'):
        print("  ⚠️ 降级到宽泛搜索...")
        q3 = quote("topic:agent stars:>1000")
        url3 = f"https://api.github.com/search/repositories?q={q3}&sort=stars&order=desc&per_page=10"
        data = _fetch_json(url3)

    if data and data.get('items'):
        for repo in data['items'][:10]:
            results.append({
                'name': repo.get('full_name', ''),
                'description': (repo.get('description') or '无描述')[:100],
                'stars': repo.get('stargazers_count', 0),
                'url': repo.get('html_url', ''),
                'language': repo.get('language', ''),
                'topics': repo.get('topics', [])[:5],
            })
        print(f"  ✅ 获取到 {len(results)} 个热门仓库")

        # ── 翻译描述为中文 ──
        descs = [r['description'] for r in results]
        zh_descs = _translate_batch(descs, label="GitHub 描述")
        for i, r in enumerate(results):
            r['description'] = zh_descs[i]
    else:
        print("  ⚠️ GitHub Trending 数据获取失败（可能触发 API 限流）")

    return results


def fetch_hackernews():
    """
    抓取 Hacker News Top Stories，按 AI 关键词过滤。
    使用 HN 官方 Firebase API（无需认证）。
    """
    print("📡 正在抓取 Hacker News...")
    results = []

    # 获取前 100 个热门故事 ID
    top_ids = _fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not top_ids:
        print("  ⚠️ HN 数据获取失败")
        return results

    # 逐个获取详情，但限制并发（最多检查前 60 个）
    checked = 0
    for story_id in top_ids[:60]:
        if len(results) >= 8:
            break

        story = _fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
        if not story or story.get('type') != 'story':
            continue

        title = story.get('title', '').lower()
        # 关键词匹配
        if any(kw in title for kw in AI_KEYWORDS):
            results.append({
                'title': story.get('title', ''),
                'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                'score': story.get('score', 0),
                'comments': story.get('descendants', 0),
                'hn_url': f"https://news.ycombinator.com/item?id={story_id}",
            })

        checked += 1
        # 简易限速，避免被封
        if checked % 10 == 0:
            time.sleep(0.3)

    print(f"  ✅ 筛选出 {len(results)} 条 AI 相关新闻（检查了 {checked} 条）")

    # ── 翻译标题为中文 ──
    if results:
        titles = [r['title'] for r in results]
        zh_titles = _translate_batch(titles, label="HN 标题")
        for i, r in enumerate(results):
            r['title_zh'] = zh_titles[i]  # 保留原标题用于链接

    return results


def fetch_awesome_updates():
    """
    监控 awesome-agents 等仓库的最近 commits。
    使用 GitHub commits API。
    """
    print("📡 正在检查 Awesome 列表更新...")
    results = []

    awesome_repos = [
        "e2b-dev/awesome-ai-agents",
        "Jenqyang/awesome-ai-agents",
    ]

    for repo in awesome_repos:
        url = f"https://api.github.com/repos/{repo}/commits?per_page=3"
        data = _fetch_json(url)
        if data and isinstance(data, list):
            for commit in data[:3]:
                msg = commit.get('commit', {}).get('message', '')[:120]
                date = commit.get('commit', {}).get('committer', {}).get('date', '')[:10]
                if msg:
                    results.append({
                        'repo': repo,
                        'message': msg,
                        'date': date,
                        'url': commit.get('html_url', ''),
                    })

    print(f"  ✅ 获取到 {len(results)} 条 Awesome 列表更新")
    return results


def fetch_reddit_ml():
    """
    抓取 Reddit /r/MachineLearning 热门帖子。
    使用 Reddit JSON API（免认证）。
    """
    print("📡 正在抓取 Reddit /r/MachineLearning...")
    results = []

    url = "https://www.reddit.com/r/MachineLearning/hot.json?limit=15&t=day"
    data = _fetch_json(url, headers={"User-Agent": "Antigravity-Evolve/2.1"})

    if data and data.get('data', {}).get('children'):
        for post in data['data']['children']:
            d = post.get('data', {})
            title = d.get('title', '')
            score = d.get('score', 0)
            if score < 20:
                continue
            flair = d.get('link_flair_text', '')
            results.append({
                'title': title,
                'url': d.get('url', ''),
                'score': score,
                'comments': d.get('num_comments', 0),
                'flair': flair or 'Discussion',
                'reddit_url': f"https://reddit.com{d.get('permalink', '')}",
            })
        results = results[:8]
        print(f"  ✅ 筛选出 {len(results)} 条热门帖子")

        if results:
            titles = [r['title'] for r in results]
            zh_titles = _translate_batch(titles, label="Reddit 标题")
            for i, r in enumerate(results):
                r['title_zh'] = zh_titles[i]
    else:
        print("  ⚠️ Reddit 数据获取失败（可能需要代理）")

    return results


def fetch_arxiv_papers():
    """
    抓取 arXiv 最新 AI/ML 论文摘要。
    使用 arXiv Atom API（免认证）。
    """
    print("📡 正在抓取 arXiv AI 最新论文...")
    results = []

    # 搜索 AI Agent 相关论文，按最近提交排序
    query = quote("(cat:cs.AI OR cat:cs.CL OR cat:cs.LG) AND (agent OR LLM OR reasoning)")
    url = f"http://export.arxiv.org/api/query?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results=8"

    xml_text = _fetch_text(url)
    if xml_text:
        # 简易 XML 解析（避免引入 lxml 依赖）
        entries = re.findall(r'<entry>(.*?)</entry>', xml_text, re.DOTALL)
        for entry in entries[:8]:
            title_m = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            summary_m = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            id_m = re.search(r'<id>(.*?)</id>', entry)
            published_m = re.search(r'<published>(.*?)</published>', entry)

            if title_m:
                title = title_m.group(1).strip().replace('\n', ' ')
                summary = (summary_m.group(1).strip().replace('\n', ' ') if summary_m else '')[:200]
                arxiv_url = id_m.group(1).strip() if id_m else ''
                pub_date = published_m.group(1)[:10] if published_m else ''

                results.append({
                    'title': title,
                    'summary': summary,
                    'url': arxiv_url,
                    'date': pub_date,
                })

        print(f"  ✅ 获取到 {len(results)} 篇最新论文")

        if results:
            titles = [r['title'] for r in results]
            zh_titles = _translate_batch(titles, label="arXiv 标题")
            for i, r in enumerate(results):
                r['title_zh'] = zh_titles[i]

            summaries = [r['summary'] for r in results]
            zh_summaries = _translate_batch(summaries, label="arXiv 摘要")
            for i, r in enumerate(results):
                r['summary_zh'] = zh_summaries[i]
    else:
        print("  ⚠️ arXiv 数据获取失败")

    return results


# ──────────────── 深度仓库解析 (V2.0 核心) ────────────────


import base64
import re


def deep_analyze_repo(repo):
    """
    深度解析 GitHub 仓库：读取 README、目录结构、核心入口文件。
    仅对 Stars > 5000 的高价值仓库执行，避免浪费 API 配额。
    """
    owner_repo = repo['name']  # e.g. "langgenius/dify"
    print(f"  🔬 深度解析: {owner_repo}...")

    analysis = {
        'readme_text': '',
        'dir_tree': [],
        'core_code_snippet': '',
        'install_cmd': '',
        'usage_examples': [],
        'key_concepts': [],
        'quick_start': '',
    }

    # ── 1. 读取 README ──
    readme_data = _fetch_json(f"https://api.github.com/repos/{owner_repo}/readme")
    if readme_data and readme_data.get('content'):
        try:
            raw = base64.b64decode(readme_data['content']).decode('utf-8', errors='replace')
            # 截取前 4000 字符（节省 Token，保留核心信息）
            analysis['readme_text'] = raw[:4000]
        except Exception:
            pass

    readme = analysis['readme_text']

    # ── 2. 获取目录树 ──
    default_branch = 'main'
    repo_info = _fetch_json(f"https://api.github.com/repos/{owner_repo}")
    if repo_info:
        default_branch = repo_info.get('default_branch', 'main')

    tree_data = _fetch_json(
        f"https://api.github.com/repos/{owner_repo}/git/trees/{default_branch}?recursive=1"
    )
    if tree_data and tree_data.get('tree'):
        # 仅保留前两层目录和关键文件
        for item in tree_data['tree'][:200]:
            path = item.get('path', '')
            depth = path.count('/')
            if depth <= 1:
                analysis['dir_tree'].append(path)

    # ── 3. 从 README 提取安装命令 ──
    install_patterns = [
        r'(?:pip install [^\n`]+)',
        r'(?:npm install [^\n`]+)',
        r'(?:yarn add [^\n`]+)',
        r'(?:docker (?:run|pull|compose)[^\n`]+)',
        r'(?:brew install [^\n`]+)',
        r'(?:cargo install [^\n`]+)',
        r'(?:go install [^\n`]+)',
    ]
    for pattern in install_patterns:
        match = re.search(pattern, readme, re.IGNORECASE)
        if match:
            analysis['install_cmd'] = match.group(0).strip()
            break

    # ── 4. 从 README 提取代码示例 ──
    code_blocks = re.findall(r'```(?:python|typescript|javascript|bash|sh)?\n(.*?)```',
                             readme, re.DOTALL)
    for block in code_blocks[:3]:
        cleaned = block.strip()
        if len(cleaned) > 20 and len(cleaned) < 800:
            analysis['usage_examples'].append(cleaned)

    # ── 5. 从 README 提取 Quick Start 段落 ──
    qs_match = re.search(
        r'(?:##?\s*(?:Quick\s*Start|Getting\s*Started|Usage|快速开始|使用方法))\s*\n(.*?)(?=\n##|\Z)',
        readme, re.DOTALL | re.IGNORECASE
    )
    if qs_match:
        analysis['quick_start'] = qs_match.group(1).strip()[:1500]

    # ── 6. 提炼核心概念（从 README 标题结构提取） ──
    headings = re.findall(r'^##?\s+(.+)$', readme, re.MULTILINE)
    for h in headings[:10]:
        h_clean = h.strip().strip('#').strip()
        if h_clean and len(h_clean) > 2:
            analysis['key_concepts'].append(h_clean)

    # ── 7. 读取核心入口代码（可选，仅 API 配额充足时） ──
    lang = (repo.get('language') or '').lower()
    entry_files = {
        'python': ['src/main.py', 'main.py', 'app.py', 'cli.py', 'setup.py'],
        'typescript': ['src/index.ts', 'index.ts', 'src/main.ts'],
        'javascript': ['src/index.js', 'index.js', 'src/main.js'],
        'go': ['main.go', 'cmd/main.go'],
        'rust': ['src/main.rs', 'src/lib.rs'],
    }
    candidates = entry_files.get(lang, [])
    for candidate in candidates:
        if candidate in analysis['dir_tree']:
            file_data = _fetch_json(
                f"https://api.github.com/repos/{owner_repo}/contents/{candidate}"
            )
            if file_data and file_data.get('content'):
                try:
                    code_raw = base64.b64decode(file_data['content']).decode('utf-8', errors='replace')
                    analysis['core_code_snippet'] = code_raw[:1500]
                except Exception:
                    pass
            break  # 只读一个入口文件

    print(f"    ✅ README: {len(readme)}字 | 目录: {len(analysis['dir_tree'])}项 "
          f"| 示例: {len(analysis['usage_examples'])}段 | 安装: {'✅' if analysis['install_cmd'] else '❌'}")

    return analysis


def generate_deep_skill_card(repo, analysis):
    """
    根据深度解析结果生成实战级技能卡（对齐 template.agskill.md 格式）。
    这张卡可以被 AI 在任务中直接挂载和消费。
    """
    name = repo['name'].split('/')[-1]
    safe_name = name.replace(' ', '_').replace('.', '_').lower()
    date_str = datetime.now().strftime('%Y-%m-%d')
    desc_zh = repo.get('description_zh', repo.get('description', ''))
    lang = repo.get('language', '未知')
    stars = repo.get('stars', 0)
    topics = repo.get('topics', [])

    # 构建 trigger_conditions
    triggers = [name.lower()]
    triggers.extend([t for t in topics[:5] if t])
    triggers_str = ', '.join(f'"{t}"' for t in triggers[:6])

    # 构建安装段落
    install_section = ""
    if analysis['install_cmd']:
        install_section = f"""## ⚙️ 安装与部署 (Installation)

```bash
{analysis['install_cmd']}
```
"""

    # 构建核心概念
    concepts_section = ""
    if analysis['key_concepts']:
        concepts_list = '\n'.join(f"- {c}" for c in analysis['key_concepts'][:8])
        concepts_section = f"""## 📖 核心概念 (Key Concepts)

{concepts_list}
"""

    # 构建代码示例
    examples_section = ""
    if analysis['usage_examples']:
        examples_section = "## 💻 代码示例 (Code Examples)\n\n"
        for i, ex in enumerate(analysis['usage_examples'][:2], 1):
            examples_section += f"### 示例 {i}\n```\n{ex}\n```\n\n"

    # 构建 Quick Start 执行流
    procedure_section = ""
    if analysis['quick_start']:
        # 翻译 Quick Start 为中文
        qs_zh = _translate_text(analysis['quick_start'][:500])
        procedure_section = f"""## ⚙️ 标准执行流 (Procedure)

> 以下基于官方 Quick Start 提炼。

{qs_zh}
"""

    # 构建核心入口代码段
    core_code_section = ""
    if analysis['core_code_snippet']:
        snippet = analysis['core_code_snippet'][:800]
        core_code_section = f"""## 🧬 核心入口代码解读 (Core Entry Point)

```{lang.lower()}
{snippet}
```
"""

    # 构建目录结构概览
    tree_section = ""
    if analysis['dir_tree']:
        tree_items = '\n'.join(f"  {d}" for d in analysis['dir_tree'][:20])
        tree_section = f"""## 📁 项目结构概览

```
{tree_items}
```
"""

    content = f"""---
name: "{name} — 深度学习技能卡 (deep-learn-{safe_name})"
description: "{desc_zh}"
version: 2.0.0
author: "@社区自进化引擎 (深度学习)"
compatibility: "Antigravity v3.3"
metadata:
  antigravity:
    tags: [深度学习, {lang}, 实战技能]
    category: DeepLearned
    source: "{repo['url']}"
    stars: {stars}
    discovered: "{date_str}"
    depth: "deep"
    requires_tools: [run_command]
    trigger_conditions: [{triggers_str}]
---

# 🧠 深度学习技能卡: {name}

> 由 ag_evolve V2.0 深度解析引擎自动生成 | {date_str}
> 原始仓库: [{repo['name']}]({repo['url']}) | ⭐ {stars:,} | {lang}

## 📋 概要
{desc_zh}

## 🎯 挂载与触发 (When to Mount)

- 当任务涉及以下关键词时自动挂载: {', '.join(triggers[:6])}
- 当需要 {desc_zh[:50]} 的能力时

{install_section}{concepts_section}{procedure_section}{examples_section}{core_code_section}{tree_section}
## 🔗 与 Antigravity 集成点 (Integration Points)

> 此技能可在以下场景被 `match_skills_for_task()` 自动匹配并挂载:
> - 多智能体工作流中需要 {name} 能力时
> - 项目构建或技术选型评估时

## ⚠️ 注意
此技能卡由 ag_evolve V2.0 深度学习引擎自动生成。核心信息已从源码和文档中提炼，但可能需要人工审核具体参数后才能投入生产使用。
"""
    return safe_name, content


# ──────────────── 任务匹配引擎 (V2.0 核心) ────────────────


def match_skills_for_task(task_desc, skills_dir=None):
    """
    根据任务描述，自动匹配并返回应该挂载的技能卡列表。
    返回: [(匹配度分数, 技能卡路径, 技能名称), ...]
    """
    if skills_dir is None:
        skills_dir = SKILLS_DIR

    matches = []
    task_lower = task_desc.lower()

    # 扫描所有 .agskill.md 文件
    for root, dirs, files in os.walk(skills_dir):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if not f.endswith('.agskill.md'):
                continue

            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
            except Exception:
                continue

            score = 0
            skill_name = f.replace('.agskill.md', '')

            # 1. 从 YAML frontmatter 提取 trigger_conditions
            tc_match = re.search(r'trigger_conditions:\s*\[([^\]]+)\]', content)
            if tc_match:
                triggers = [t.strip().strip('"').strip("'").lower()
                            for t in tc_match.group(1).split(',')]
                for trigger in triggers:
                    if trigger in task_lower:
                        score += 10  # 精确触发词匹配，高权重

            # 2. 从 tags 中匹配
            tags_match = re.search(r'tags:\s*\[([^\]]+)\]', content)
            if tags_match:
                tags = [t.strip().lower() for t in tags_match.group(1).split(',')]
                for tag in tags:
                    if tag in task_lower:
                        score += 5

            # 3. 从 description 中匹配
            desc_match = re.search(r'description:\s*"([^"]*)"', content)
            if desc_match:
                desc_words = desc_match.group(1).lower().split()
                for word in desc_words:
                    if len(word) > 2 and word in task_lower:
                        score += 2

            # 4. 文件名关键词匹配
            name_parts = skill_name.replace('-', ' ').replace('_', ' ').lower().split()
            for part in name_parts:
                if len(part) > 2 and part in task_lower:
                    score += 3

            # 5. 深度学习卡加分（优先推荐实战级卡）
            if 'depth: "deep"' in content:
                score += 2

            if score > 0:
                matches.append((score, path, skill_name))

    # 按匹配度降序排列
    matches.sort(key=lambda x: x[0], reverse=True)
    return matches[:5]


# ──────────────────── 技能卡自动生成（浅层） ────────────────────


def generate_skill_card(repo):
    """根据 GitHub 仓库信息生成浅层 .agskill.md 技能卡（保持向后兼容）"""
    name = repo['name'].split('/')[-1]
    safe_name = name.replace(' ', '_').replace('.', '_').lower()
    date_str = datetime.now().strftime('%Y-%m-%d')

    desc_zh = repo.get('description_zh', repo['description'])
    content = f"""---
name: "{safe_name}"
description: "{desc_zh}"
version: 1.0.0
author: "@社区自进化引擎"
compatibility: "Antigravity v3.3"
metadata:
  antigravity:
    tags: [社区发现, {repo.get('language', 'unknown')}]
    category: CommunityDiscovery
    source: "{repo['url']}"
    stars: {repo.get('stars', 0)}
    discovered: "{date_str}"
---

# 🌐 社区发现: {name}

> 由 ag_evolve 自动发现并生成 | {date_str}
> 原始仓库: [{repo['name']}]({repo['url']})

## 📋 概要
{desc_zh}

## 🏷️ 标签
- 语言: {repo.get('language', '未知')}
- Stars: ⭐ {repo.get('stars', 0):,}
- 主题: {', '.join(repo.get('topics', []))}

## 🎯 潜在用途
> 请 AI 在下次相关任务时评估此工具是否可以集成到当前工作流中。

## ⚠️ 注意
此技能卡由自动化引擎生成，内容可能需要人工审核后才能投入使用。
"""
    return safe_name, content


# ────────────────────── 报告生成器 ──────────────────────


def generate_digest(github_data, hn_data, awesome_data, reddit_data=None, arxiv_data=None):
    """生成 Markdown 格式的每日社区简报"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    lines = []

    lines.append(f"# 🌐 社区情报简报 ({date_str})")
    lines.append(f"> 自动生成 by `ag_evolve` | Antigravity V3.3")
    lines.append(f"> ⚠️ 此文件每日自动更新，请勿手动编辑")
    lines.append("")

    # ── GitHub 热门 ──
    lines.append("## 🔥 GitHub 热门 (AI/Agent 领域)")
    lines.append("")
    if github_data:
        for i, repo in enumerate(github_data, 1):
            lang_badge = f"[{repo.get('language', '?')}]" if repo.get('language') else ""
            lines.append(
                f"{i}. **[{repo['name']}]({repo['url']})** "
                f"⭐ {repo['stars']:,} {lang_badge}"
            )
            lines.append(f"   {repo['description']}")
            if repo.get('topics'):
                lines.append(f"   `{'` `'.join(repo['topics'])}`")
            lines.append("")
    else:
        lines.append("*数据暂不可用（可能触发 GitHub API 限流）*")
        lines.append("")

    # ── Hacker News ──
    lines.append("## 📰 Hacker News 精选 (AI 相关)")
    lines.append("")
    if hn_data:
        for item in hn_data:
            display_title = item.get('title_zh') or item['title']
            score_badge = f"△{item['score']}" if item.get('score') else ""
            comment_badge = f"💬{item['comments']}" if item.get('comments') else ""
            lines.append(
                f"- [{display_title}]({item['url']}) "
                f"{score_badge} {comment_badge} "
                f"([讨论]({item['hn_url']}))"
            )
        lines.append("")
    else:
        lines.append("*今日无匹配的 AI 相关新闻*")
        lines.append("")

    # ── Awesome 列表 ──
    lines.append("## 📚 Awesome 列表动态")
    lines.append("")
    if awesome_data:
        for item in awesome_data:
            lines.append(f"- **{item['repo']}** ({item['date']}): {item['message']}")
    else:
        lines.append("*近期无更新*")
    lines.append("")

    # ── Reddit /r/MachineLearning ──
    lines.append("## 🔴 Reddit /r/MachineLearning (热门)")
    lines.append("")
    if reddit_data:
        for item in reddit_data:
            display_title = item.get('title_zh') or item['title']
            flair = f"[{item.get('flair', '')}]" if item.get('flair') else ""
            lines.append(
                f"- [{display_title}]({item['url']}) "
                f"△{item.get('score', 0)} 💬{item.get('comments', 0)} {flair} "
                f"([讨论]({item.get('reddit_url', '')}))"
            )
    else:
        lines.append("*数据暂不可用*")
    lines.append("")

    # ── arXiv 最新论文 ──
    lines.append("## 📄 arXiv 最新 AI 论文")
    lines.append("")
    if arxiv_data:
        for item in arxiv_data:
            display_title = item.get('title_zh') or item['title']
            summary = item.get('summary_zh') or item.get('summary', '')[:100]
            lines.append(f"- **[{display_title}]({item['url']})** ({item.get('date', '')})")
            lines.append(f"  {summary}")
            lines.append("")
    else:
        lines.append("*数据暂不可用*")
    lines.append("")

    # ── 建议学习 ──
    lines.append("## 🎯 建议关注")
    lines.append("")
    if github_data:
        # 挑选 stars 最高的仓库推荐
        top = max(github_data, key=lambda x: x.get('stars', 0))
        lines.append(
            f"> 发现 **[{top['name']}]({top['url']})** (⭐{top['stars']:,}) 值得深入研究，"
            f"可能对 Antigravity 工作流有帮助。"
        )
    else:
        lines.append("> 本次扫描未发现高优先级目标。等待下次扫描。")
    lines.append("")

    # ── 尾部 ──
    lines.append("---")
    lines.append(f"*由 ag_evolve V1.0 生成 | 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC*")

    return '\n'.join(lines)


# ────────────────────── 入口 ──────────────────────


def main():
    print("🧬 Antigravity 社区自进化引擎 V2.0 启动...")
    print(f"   输出目录: {SKILLS_DIR}")
    start = time.time()

    # 自定义输出路径
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            global DIGEST_FILE, TRENDING_DIR
            out_dir = sys.argv[idx + 1]
            DIGEST_FILE = os.path.join(out_dir, "_community_digest.md")
            TRENDING_DIR = os.path.join(out_dir, "_trending_skills")

    # 确保输出目录存在
    os.makedirs(TRENDING_DIR, exist_ok=True)

    # ── 阶段 1：采集数据（浅层侦察） ──
    print("\n═══ 阶段 1/4：浅层情报侦察 ═══")
    github_data = fetch_github_trending()
    hn_data = fetch_hackernews()
    awesome_data = fetch_awesome_updates()
    reddit_data = fetch_reddit_ml()
    arxiv_data = fetch_arxiv_papers()

    # ── 阶段 1.5：生成每日简报 ──
    digest_md = generate_digest(github_data, hn_data, awesome_data, reddit_data, arxiv_data)
    with open(DIGEST_FILE, 'w', encoding='utf-8') as f:
        f.write(digest_md)
    print(f"📋 每日简报已生成: {DIGEST_FILE}")

    # ── 阶段 1.5：生成浅层趋势技能卡（保持向后兼容） ──
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    shallow_cards = 0
    high_value = [r for r in github_data if r.get('stars', 0) > 1000]
    for repo in high_value[:5]:
        safe_name, card_content = generate_skill_card(repo)
        card_path = os.path.join(TRENDING_DIR, f"{date_prefix}_{safe_name}.agskill.md")
        if not os.path.exists(card_path):
            with open(card_path, 'w', encoding='utf-8') as f:
                f.write(card_content)
            shallow_cards += 1
            print(f"  🃏 浅层技能卡: {os.path.basename(card_path)}")

    # ── 阶段 2：深度学习（V2.0 核心） ──
    print("\n═══ 阶段 2/4：深度学习解析 ═══")
    deep_threshold = 5000  # Stars > 5000 的仓库才值得深度解析
    deep_candidates = [r for r in github_data if r.get('stars', 0) > deep_threshold]
    deep_cards = 0
    REFRESH_DAYS = 7  # 已有深度卡超过 7 天则重新解析

    for repo in deep_candidates[:3]:
        safe_name = repo['name'].split('/')[-1].replace(' ', '_').replace('.', '_').lower()
        deep_card_path = os.path.join(SKILLS_DIR, f"deep-{safe_name}.agskill.md")

        # 周期性刷新：已有深度卡但超过 REFRESH_DAYS 则重新解析
        if os.path.exists(deep_card_path):
            age_days = (time.time() - os.path.getmtime(deep_card_path)) / 86400
            if age_days < REFRESH_DAYS:
                print(f"  ⏭️  跳过 {safe_name}（深度卡 {age_days:.0f} 天前更新，{REFRESH_DAYS}天内免刷新）")
                continue
            else:
                print(f"  🔄 {safe_name} 深度卡已过期（{age_days:.0f}天），重新解析...")

        try:
            analysis = deep_analyze_repo(repo)
            _, card_content = generate_deep_skill_card(repo, analysis)
            with open(deep_card_path, 'w', encoding='utf-8') as f:
                f.write(card_content)
            deep_cards += 1
            print(f"  🧠 深度技能卡已生成: {os.path.basename(deep_card_path)}")
        except Exception as e:
            print(f"  ⚠️ 深度解析失败: {repo['name']} — {e}")
        
        time.sleep(1)  # API 限速间隔

    # ── 阶段 3：汇总报告 ──
    print("\n═══ 阶段 3/4：汇总与验证 ═══")
    elapsed = time.time() - start
    print(f"   GitHub: {len(github_data)} 条 | HN: {len(hn_data)} 条 | Awesome: {len(awesome_data)} 条")
    print(f"   Reddit: {len(reddit_data)} 条 | arXiv: {len(arxiv_data)} 篇")
    print(f"   浅层技能卡: {shallow_cards} 张 | 深度技能卡: {deep_cards} 张")
    print(f"   总耗时: {elapsed:.1f}s")

    # ── 技能匹配引擎自检 ──
    total_skills = 0
    deep_skills = 0
    for root, dirs, files in os.walk(SKILLS_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith('.agskill.md'):
                total_skills += 1
                fpath = os.path.join(root, f)
                with open(fpath, 'r', encoding='utf-8') as fh:
                    if 'depth: "deep"' in fh.read():
                        deep_skills += 1
    print(f"   技能库总计: {total_skills} 张 (深度: {deep_skills}, 浅层: {total_skills - deep_skills})")

    # ── 自动生成 AI 学习简报 ──
    print("\n🧠 正在汇总 AI 突触学习记忆 (ag_learning)...")
    try:
        base_dir = os.path.dirname(SKILLS_DIR)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from ag_learning import get_recent_learnings
        learning_data = get_recent_learnings(base_dir)
        learn_path = os.path.join(SKILLS_DIR, "_learning_digest.json")
        with open(learn_path, 'w', encoding='utf-8') as f:
            json.dump(learning_data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 学习简报已更新")
    except Exception as e:
        print(f"  ⚠️ 学习简报生成失败: {e}")

    print(f"\n✅ ag_evolve V2.0 深度自进化引擎执行完毕 ({elapsed:.1f}s)")


if __name__ == '__main__':
    main()
