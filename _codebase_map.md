# 📊 项目代码图谱: 全局技能库_AG_Skills
> 自动生成 by `ag_indexer` | 更新时间: 2026-04-19 22:22
> ⚠️ 此文件由机器自动生成，请勿手动编辑

## 概览
- **总文件数**: 65
- **总代码行数**: 7,446

| 语言 | 文件数 | 行数 |
|------|--------|------|
| Python | 17 | 3,691 |
| Markdown | 42 | 2,392 |
| CSS | 1 | 663 |
| JavaScript | 1 | 379 |
| Shell | 2 | 156 |
| HTML | 1 | 114 |
| JSON | 1 | 51 |

## 目录结构
```
├── 全局技能库_AG_Skills/ (23 文件)
├── _trending_skills/ (25 文件)
├── ag_core/ (13 文件)
├── dashboard/ (4 文件)
```

## 核心模块索引

| 文件 | 语言 | 行数 | 类 | 函数 | 关键依赖 |
|------|------|------|----|------|----------|
| ag_core/ag_coverage_audit.py | Python | 103 | CoverageAuditor | os, ast, glob, re | 
| ag_core/ag_entity_linker.py | Python | 60 | EntityLinker | re, json, os, uuid | 
| ag_core/ag_evolve.py | Python | 969 | _fetch_json(), _fetch_text(), _translate_text(), _translate_batch() | base64, json, os, re | 
| ag_core/ag_indexer.py | Python | 439 | _safe_read(), _count_lines(), extract_python(), extract_by_regex() | ast, os, re, sys | 
| ag_core/ag_learning.py | Python | 75 | get_recent_learnings() | os, json, time, datetime | 
| ag_core/ag_learnings_manager.py | Python | 77 | LearningsManager | os, json, time | 
| ag_core/ag_post_review.py | Python | 607 | check_scope(), validate_syntax(), validate_bat_syntax(), recall_learnings() | os, sys, ast, re | 
| ag_core/ag_question_tuner.py | Python | 61 | QuestionTuner | json, os, event_logger | 
| ag_core/ag_review_army.py | Python | 152 | SpecialistReviewer | asyncio, json, uuid, re | 
| ag_core/dispatcher.py | Python | 53 | AsyncGlobalDispatcher | asyncio, typing, event_logger, middleware | 
| ag_core/event_logger.py | Python | 40 | log_event() | os, json, time | 
| ag_core/middleware.py | Python | 430 | StrikeTracker, MiddlewareContext, Middleware, build_chain(), _next() | asyncio, typing, sys, os | 
| ag_core/repo_cache.py | Python | 49 | RepoCacheManager, ignore_func() | os, shutil, hashlib, event_logger | 
| ag_memory_mgr.py | Python | 79 | main() | argparse, sys, re | 
| dashboard/script.js | JavaScript | 379 | fetchData() | - | 
| dashboard/server.py | Python | 385 | DashboardHandler | http.server, socketserver, json, os | 
| run_chichat_demo.py | Python | 67 | mock_h5_init(), mock_nginx_config(), mock_issue_sync(), end_issue_sync() | asyncio, sys, os, json | 
| test_pipeline.py | Python | 45 | mock_task_success(), mock_task_fail(), main() | asyncio, sys, os, ag_core.dispatcher | 

## 类结构详情

### `ag_core/ag_coverage_audit.py`
- **CoverageAuditor** (L6): `__init__()`, `_load_tests()`, `audit_file()`

### `ag_core/ag_entity_linker.py`
- **EntityLinker** (L9): `__init__()`, `extract_and_link()`

### `ag_core/ag_learnings_manager.py`
- **LearningsManager** (L5): `__init__()`, `log_learning()`, `search_learnings()`

### `ag_core/ag_question_tuner.py`
- **QuestionTuner** (L5): `__init__()`, `_load_prefs()`, `_save_prefs()`, `teach_preference()`, `tune_question()`

### `ag_core/ag_review_army.py`
- **SpecialistReviewer** (L8): `__init__()`, `_mock_llm_call()`, `run_review_army()`, `_report_findings()`

### `ag_core/dispatcher.py`
- **AsyncGlobalDispatcher** (L6): `__init__()`, `_worker()`, `submit_task()`, `wait_all()`

### `ag_core/middleware.py`
- **StrikeTracker** (L9): `__init__()`, `_read()`, `_write()`, `record_failure()`, `reset_failure()`
- **MiddlewareContext** (L32): `__init__()`
- **Middleware** (L41): `process()`
- **ContextHealthMiddleware** (L46): `process()`
- **DynamicSkillMiddleware** (L75): `process()`
- **AutoMemoryMiddleware** (L119): `process()`
- **SurgicalCheckMiddleware** (L177): `process()`
- **ValidationGateMiddleware** (L270): `process()`
- **MiddlewarePipeline** (L415): `__init__()`, `execute()`

### `ag_core/repo_cache.py`
- **RepoCacheManager** (L8): `_hash_path()`, `create_snapshot()`, `wipe_all()`

### `dashboard/server.py`
- **DashboardHandler** (L11): `end_headers()`, `do_GET()`

---
*由 ag_indexer V1.0 生成 | Antigravity V3.3*