# 📊 项目代码图谱: 全局技能库_AG_Skills
> 自动生成 by `ag_indexer` | 更新时间: 2026-04-14 00:07
> ⚠️ 此文件由机器自动生成，请勿手动编辑

## 概览
- **总文件数**: 20
- **总代码行数**: 2,298

| 语言 | 文件数 | 行数 |
|------|--------|------|
| Python | 10 | 1,489 |
| CSS | 1 | 275 |
| Markdown | 5 | 219 |
| JavaScript | 1 | 167 |
| HTML | 1 | 81 |
| Shell | 2 | 67 |

## 目录结构
```
├── 全局技能库_AG_Skills/ (10 文件)
├── ag_core/ (6 文件)
├── dashboard/ (4 文件)
```

## 核心模块索引

| 文件 | 语言 | 行数 | 类 | 函数 | 关键依赖 |
|------|------|------|----|------|----------|
| ag_core/ag_evolve.py | Python | 391 | _fetch_json(), _fetch_text(), fetch_github_trending(), fetch_hackernews() | json, os, ssl, sys | 
| ag_core/ag_indexer.py | Python | 439 | _safe_read(), _count_lines(), extract_python(), extract_by_regex() | ast, os, re, sys | 
| ag_core/dispatcher.py | Python | 52 | AsyncGlobalDispatcher | asyncio, typing, event_logger, middleware | 
| ag_core/event_logger.py | Python | 40 | log_event() | os, json, time | 
| ag_core/middleware.py | Python | 93 | MiddlewareContext, Middleware, ContextHealthMiddleware, build_chain(), _next() | asyncio, typing, event_logger | 
| ag_core/repo_cache.py | Python | 49 | RepoCacheManager, ignore_func() | os, shutil, hashlib, event_logger | 
| ag_memory_mgr.py | Python | 79 | main() | argparse, sys, re | 
| dashboard/script.js | JavaScript | 167 | fetchData() | - | 
| dashboard/server.py | Python | 234 | DashboardHandler | http.server, socketserver, json, os | 
| run_chichat_demo.py | Python | 67 | mock_h5_init(), mock_nginx_config(), mock_issue_sync(), end_issue_sync() | asyncio, sys, os, json | 
| test_pipeline.py | Python | 45 | mock_task_success(), mock_task_fail(), main() | asyncio, sys, os, ag_core.dispatcher | 

## 类结构详情

### `ag_core/dispatcher.py`
- **AsyncGlobalDispatcher** (L6): `__init__()`, `_worker()`, `submit_task()`, `wait_all()`

### `ag_core/middleware.py`
- **MiddlewareContext** (L5): `__init__()`
- **Middleware** (L12): `process()`
- **ContextHealthMiddleware** (L17): `process()`
- **AutoMemoryMiddleware** (L30): `process()`
- **SurgicalCheckMiddleware** (L41): `process()`
- **ValidationGateMiddleware** (L51): `process()`
- **MiddlewarePipeline** (L78): `__init__()`, `execute()`

### `ag_core/repo_cache.py`
- **RepoCacheManager** (L8): `_hash_path()`, `create_snapshot()`, `wipe_all()`

### `dashboard/server.py`
- **DashboardHandler** (L11): `end_headers()`, `do_GET()`

---
*由 ag_indexer V1.0 生成 | Antigravity V3.3*