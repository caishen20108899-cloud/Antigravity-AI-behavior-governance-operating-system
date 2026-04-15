<p align="center">
  <img src="https://img.shields.io/badge/版本-V3.3_Archon--Gate-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/依赖-零外部依赖-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-Private-red?style=for-the-badge" />
</p>

# 🚀 Antigravity (反重力) — AI 行为治理操作系统

> **让每一个 AI 都不再是一次性的工具，而是拥有记忆、纪律和军衔的数字军团。**

Antigravity 不是一个 IDE，也不是一个 Agent 框架。它是一套刻入大模型底层血液的 **行为准则 + 工具链 + 实时可视化大盘** 三位一体架构，目标是让每一个被唤醒的 AI 在任何项目中都具备：

- 🧠 **跨会话永久记忆** — 对话结束不丢失，项目间严格隔离
- 🎖️ **多兵种协同作战** — 7 角色标准池，3 级编制自动适配
- 🛡️ **代码质量物理门禁** — Archon-Gate 4 层洋葱中间件拦截
- 📡 **实时指挥官观盘** — War Room 大屏 + 跨窗口神经元终端
- 🌐 **社区自进化** — 每日自动从全球开发者社区吸收新知识

---

## 📐 系统架构

```
┌─────────────────────── Antigravity V3.3 ───────────────────────┐
│                                                                 │
│  📜 GEMINI.md (11条铁律宪法)         ← AI 行为的最高法律        │
│                                                                 │
│  ⚙️ ag_core/ ─────────────────────── ← 核心引擎层              │
│  ├── middleware.py    4层洋葱中间件管线 (Archon-Gate)            │
│  ├── dispatcher.py    并发调度器 V3.1 (信号量 + payload 透传)   │
│  ├── event_logger.py  事件日志写入器                             │
│  ├── ag_indexer.py    代码图谱引擎 (AST/Regex 多语言解析)       │
│  ├── ag_evolve.py     社区自进化引擎 (6源信息抓取 + 翻译)       │
│  ├── ag_learning.py   深度学习引擎 (README/源码/API 解析)       │
│  └── repo_cache.py    仓库缓存                                  │
│                                                                 │
│  📡 dashboard/ ───────────────────── ← 指挥官大盘 (:8899)       │
│  ├── server.py        后端探针 (4路API: agents/skills/issues/events) │
│  ├── index.html       前端界面 (Kanban + 兵种灯 + 神经元)       │
│  ├── script.js        前端逻辑 (5秒轮询 + 状态映射)             │
│  └── style.css        赛博朋克风格视觉                          │
│                                                                 │
│  🔧 工具链 ───────────────────────── ← 独立可执行工具           │
│  ├── ag_log            跨窗口神经元发报器 (Shell)                │
│  ├── ag_init.sh        项目初始化脚手架                          │
│  ├── ag_memory_mgr.py  记忆管理器                               │
│  └── start_dashboard.sh 大盘一键启动器                           │
│                                                                 │
│  📚 技能卡体系 ───────────────────── ← .agskill.md 格式         │
│  ├── SKILLS_MANIFEST.md     技能路由总表                         │
│  ├── *.agskill.md           手动创建的核心技能卡                 │
│  └── _trending_skills/      自进化引擎自动发现的技能卡           │
│                                                                 │
│  🎖️ AGENTS/ ──────────────────────── ← 多智能体编制             │
│  └── commander/              总司令角色定义 + 任务看板            │
│                                                                 │
│  📊 自动生成物 ───────────────────── ← 机器生成，勿手动编辑      │
│  ├── _codebase_map.md        代码图谱 (ag_indexer 输出)          │
│  ├── _community_digest.md    每日社区情报简报                     │
│  └── _learning_digest.json   学习进度数据                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧠 核心模块详解

### 1. Archon-Gate 中间件管线 (`ag_core/middleware.py`)

所有 AI 任务执行前必须穿透的 4 层洋葱防线：

```
请求 ──→ [ContextHealth] ──→ [AutoMemory] ──→ [SurgicalCheck] ──→ [ValidationGate] ──→ 执行
                                                                         │
                                                                    物理校验
                                                              (go test / npm build)
```

| 层 | 名称 | 职责 |
|----|------|------|
| 1 | `ContextHealthMiddleware` | 评估上下文负荷，触发心理压缩 |
| 2 | `AutoMemoryMiddleware` | 异步捕获关键经验并后台归档 |
| 3 | `SurgicalCheckMiddleware` | 加载 Karpathy 四铁律，确保最小爆炸半径 |
| 4 | `ValidationGateMiddleware` | Archon 物理门禁：运行 `go test` / `npm build` 确认代码正确 |

### 2. 代码图谱引擎 (`ag_core/ag_indexer.py`)

让 AI 在编码前 **1 秒读懂整个项目结构**。

```bash
python3 ag_indexer.py /path/to/your/project
# 输出: /path/to/your/project/_codebase_map.md
```

**支持语言**: Python (AST 精确解析) / Java / JavaScript / TypeScript / Go / Kotlin / Swift / Lua / Rust / C/C++ / Vue

**输出示例**:
```markdown
# 📊 项目代码图谱: ChiChatIM系统
> 自动生成 by ag_indexer | 更新时间: 2026-04-15 08:00

## 概览
- 总文件数: 47
- 总代码行数: 8,234

| 文件 | 语言 | 行数 | 类 | 函数 | 关键依赖 |
|------|------|------|----|------|----------|
| server/auth.py | Python | 142 | AuthService | verify_token() | redis, jwt |
```

### 3. 社区自进化引擎 (`ag_core/ag_evolve.py`)

每日自动从全球开发者社区抓取最新 AI/Agent 动态，转化为 AI 可直接消费的技能卡。

**6 大信息源**:

| 信息源 | API | 输出 |
|--------|-----|------|
| GitHub Trending | GitHub Search API (三级降级策略) | 热门仓库 Top 10 + 中文翻译 |
| Hacker News | Firebase API + 53 个 AI 关键词过滤 | 精选新闻 + 中文标题 |
| Reddit /r/MachineLearning | Reddit JSON API | 热门讨论 + 中文翻译 |
| arXiv | Atom API | 最新 AI 论文摘要 |
| Awesome 列表 | GitHub Commits API | awesome-ai-agents 变更监控 |
| MCP Server Registry | 预留接口 | 新能力插件发现 |

**V2.0 深度学习**: 对 Stars > 5000 的高价值仓库执行深度解析——读取 README、目录结构、核心入口代码、安装命令、代码示例，自动生成**实战级技能卡**。

```bash
python3 -m ag_core.ag_evolve
# 输出: _community_digest.md + _trending_skills/*.agskill.md
```

### 4. 跨窗口神经元发报器 (`ag_log`)

打破大模型物理视窗之间的隔离墙，实现跨对话实时状态广播。

```bash
sh ag_log "@Commander" "MessageStatus" "正在突破网关安全逻辑..."
# → 写入 ~/.gemini/antigravity/events.jsonl
# → War Room 大盘实时显示
```

### 5. War Room 指挥官大盘 (`dashboard/`)

实时可视化指挥控制中心，运行在 `http://localhost:8899`。

**四大面板**:
- 🎖️ **兵种状态灯** — 精准显示每个角色的实时工作状态（基于 task_board + events 双源判定）
- 📋 **任务看板** — 从 AGENTS/commander/task_board.md 实时解析工单状态
- 📡 **神经元终端** — 滚动显示所有 AI 的实时发报数据
- 🧩 **技能卡清单** — 展示已注册的全部能力模块

```bash
sh start_dashboard.sh
```

---

## 🎖️ 多智能体编制体系

### 标准角色池 (7 个)

| 代号 | 化名 | 职责范围 |
|------|------|----------|
| `@Commander` | 总司令 | 任务拆解 + 进度追踪 + 看板管理 (**唯一必选**) |
| `@Architect` | 发改委 | 架构设计 + API 契约 + 技术选型 |
| `@Backend` | 基建部 | 后端开发 + 数据库 + 微服务 |
| `@Frontend` | 宣发部 | 前端 / Web / H5 / 管理后台 |
| `@Mobile` | 装备部 | Android + iOS 双端 |
| `@Security` | 国安部 | 网关安全 + 加密 + 鉴权 |
| `@DevOps` | 后勤部 | 部署运维 + CI/CD + 质量验收 |

### 三级编制自动适配

| 级别 | 角色数 | 适用场景 | 启用角色 |
|------|--------|----------|----------|
| **轻量级** | 2 | 脚本 / 修复 / 配置 | Commander + Backend |
| **标准级** | 4-5 | 中型项目 / 网站 | Commander + Architect + Backend + Frontend + DevOps |
| **旗舰级** | 6-7 | 大型系统 / 多端 APP | 全部 7 角色按需裁剪 |

---

## 📚 技能卡体系 (`.agskill.md`)

技能卡是 Antigravity 的能力扩展单元。每张卡片定义了：
- **触发条件** — 什么关键词/场景下自动挂载
- **标准执行流** — AI 消费卡片后的操作步骤
- **安全约束** — 哪些操作需要备份/审批

**已注册技能卡**:

| 技能 | 类型 | 描述 |
|------|------|------|
| `ag-team-issue-protocol` | 核心 | 多角色工单协同 + Blocker 机制 |
| `surgical-code-repair` | 核心 | Karpathy 法则代码手术操作规范 |
| `template` | 模板 | 技能卡创建模板 v2.0 |
| `deep-langchain` | 自进化 | LangChain 实战深度技能卡 |
| `deep-dify` | 自进化 | Dify 工作流深度技能卡 |
| `deep-langflow` | 自进化 | LangFlow 低代码深度技能卡 |
| `deep-firecrawl` | 自进化 | Firecrawl 数据采集深度技能卡 |

> 💡 `_trending_skills/` 目录下的技能卡由自进化引擎每日自动生成和更新。

---

## 📜 11 条全局铁律 (GEMINI.md)

Antigravity 的行为治理核心。所有 AI Agent 降生时的第一份读物。

| # | 名称 | 核心要求 |
|---|------|----------|
| 一 | **超级记忆体系** | 热延续协议 / 强制落盘 / 项目隔离 / 触发词系统 / 多智能体编制 |
| 二 | **侦探式排障** | 不闭环不行动 + 修后三验 |
| 三 | **操作隔离与灾备** | 动刀前必备份 + 10 秒回滚预案 |
| 三½ | **强制备份协议** | 没有 `cp` 就不能出 `rm` |
| 四 | **执行权与极速模式** | 免审直达 + 危险拦截底线 |
| 五 | **中文锁定** | 排他性使用纯简体中文 |
| 五½ | **上下文健康管理** | 心理压缩 + 进度锚点 |
| 六 | **资产隔离** | 不可私自动用非本项目资产 |
| 七 | **Archon 门禁** | Karpathy 手术刀 + 物理校验门禁 |
| 八 | **Kanban 同步** | 开工必点亮 / 完工必归档 |
| 九 | **神经元发报** | 跨窗口实况转播协议 (ag_log) |
| 十 | **防盲写阻断** | 前置侦查强制 + 自我阻断机制 |
| 十一 | **硬件拓扑认知** | MacBook=轻量端 / Mac mini=算力核心 |

---

## 🛠️ 安装与部署

### 环境要求
- Python 3.10+
- **零外部依赖** — 全部使用 Python 标准库

### 快速启动

```bash
# 1. 克隆仓库
git clone git@github.com:caishen20108899-cloud/AI-.git
cd AI-

# 2. 启动 War Room 大盘
sh start_dashboard.sh
# → 浏览器访问 http://localhost:8899

# 3. 扫描项目生成代码图谱
python3 ag_core/ag_indexer.py /path/to/your/project

# 4. 运行社区自进化 (手动触发)
python3 -m ag_core.ag_evolve

# 5. 跨窗口发报测试
sh ag_log "@Commander" "MessageStatus" "系统已就绪"
```

### Cron 定时任务 (Mac mini)

```bash
# 每 2 小时扫描项目结构
0 */2 * * * /usr/bin/python3 ~/Antigravity/全局技能库_AG_Skills/ag_core/ag_indexer.py ~/Antigravity/ChiChatIM系统

# 每日凌晨抓取社区动态
0 0 * * * /usr/bin/python3 -m ag_core.ag_evolve --output ~/Antigravity/全局技能库_AG_Skills
```

---

## 📊 与主流 AI IDE 对标

| 维度 | Cursor 3 | Claude Code | **Antigravity** |
|------|:--------:|:-----------:|:---------------:|
| 跨会话记忆 | 6/10 | 4/10 | **9/10** ★ |
| 实时可视化 | 5/10 | 2/10 | **9/10** ★ |
| 安全红线 | 6/10 | 5/10 | **9/10** ★ |
| 硬件拓扑感知 | 3/10 | 2/10 | **8/10** ★ |
| 代码索引/RAG | **9/10** | 8/10 | 7/10 |
| 多智能体协作 | 8/10 | 3/10 | 7/10 |

> **定位**: Cursor 解决"怎么写代码"，Antigravity 解决"怎么让 AI 为你安全、可控、有记忆地工作"。

---

## 📁 项目结构

```
全局技能库_AG_Skills/
├── ag_core/                    # 核心引擎
│   ├── middleware.py           # 4层洋葱中间件
│   ├── dispatcher.py           # 并发调度器
│   ├── event_logger.py         # 事件日志
│   ├── ag_indexer.py           # 代码图谱引擎
│   ├── ag_evolve.py            # 社区自进化引擎
│   ├── ag_learning.py          # 深度学习引擎
│   └── repo_cache.py           # 仓库缓存
├── dashboard/                  # War Room 大盘
│   ├── server.py               # 后端 (Python HTTP)
│   ├── index.html              # 前端界面
│   ├── script.js               # 前端逻辑
│   └── style.css               # 赛博朋克样式
├── AGENTS/                     # 多智能体定义
│   └── commander/              # 总司令
│       ├── role.md             # 角色定义
│       └── task_board.md       # 任务看板
├── _trending_skills/           # 自进化技能卡 (自动生成)
├── ag_log                      # 跨窗口神经元发报器
├── ag_init.sh                  # 项目初始化脚手架
├── ag_memory_mgr.py            # 记忆管理器
├── start_dashboard.sh          # 大盘启动器
├── SKILLS_MANIFEST.md          # 技能路由总表
├── *.agskill.md                # 核心技能卡
├── _codebase_map.md            # 代码图谱 (自动生成)
├── _community_digest.md        # 社区简报 (自动生成)
└── _learning_digest.json       # 学习数据 (自动生成)
```

---

## 🔮 路线图

- [x] V3.0 — 超级记忆体系 + 项目隔离
- [x] V3.1 — 多智能体协作框架 + War Room 大盘
- [x] V3.2 — Archon-Gate 中间件 + 神经元发报 + 11条铁律
- [x] V3.3 — 代码图谱引擎 + 社区自进化 + 深度学习技能卡
- [ ] V3.4 — MCP 协议接入 (让任何 IDE 调用 Antigravity 记忆)
- [ ] V3.5 — 基于 Neo4j 的项目知识图谱
- [ ] V4.0 — 真并行 Agent 隔离 (Docker 容器级)

---

## ⚖️ 许可

本项目为个人私有项目，仅供学习参考。

---

<p align="center">
  <b>Antigravity — 反重力。让 AI 突破一次性工具的重力束缚，飞升为可信赖的数字军团。</b>
</p>
