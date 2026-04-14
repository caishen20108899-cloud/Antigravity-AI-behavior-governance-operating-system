# Antigravity 全局技能调度中心 (Skills Manifest)

> [!IMPORTANT]
> 这是 Antigravity 的动态路由入口。为了保护记忆上下文不被污染，未来所有的新增技能都在此打通。
> **调度规则**：@国防部 (Commander) 在接受任何跨项目维保任务时，先静默检索此路由表，仅当任务词汇与 Target Triggers 匹配时，按需单独读取目标能力卡片。禁止一口气读取目录下的所有文件。

## 🎖️ 已注册装甲序列 (Registered Skill Modules)

| 🎯 Target Triggers (触发条件 / 匹配关键词) | 📂 目标挂载点 (Skill File) | ⚙️ 效能简述 (Description) |
|---|---|---|
| `创建项目`, `协同`, `多部门`, `新建协作`, `分配工单` | [ag-team-issue-protocol.agskill.md](./ag-team-issue-protocol.agskill.md) | 采用 Multica 抽离提取的工单 Issue 协同和 Blocker 卡点机制。 |
| `重构代码`, `修改核心逻辑`, `增加新功能`, `大规模改动`, `深入排查` | [surgical-code-repair.agskill.md](./surgical-code-repair.agskill.md) | 基于 Karpathy 法则构建的“无污染、零过度设计”代码手术级操作规范。 |
| `创建新技能`, `新增维保 SOP`, `标准化技能卡片` | [template.agskill.md](./template.agskill.md) | 新增/编写自定义 agskill 的官方 v2.0 模板指南。 |
| `langchain`, `ai`, `ai-agents` | [deep-langchain.agskill.md](./deep-langchain.agskill.md) | 深度技能实战卡：针对 Langchain 的核心挂载 API 库 (V2.0自动进化) |
| `dify`, `agentic-workflow` | [deep-dify.agskill.md](./deep-dify.agskill.md) | 深度技能实战卡：针对 Dify 工作流的系统核心编排代码 (V2.0自动进化) |
| `langflow`, `multiagent` | [deep-langflow.agskill.md](./deep-langflow.agskill.md) | 深度技能实战卡：构建和部署 AI 代理的低代码库 (V2.0自动进化) |
| `firecrawl`, `ai-crawler`, `ai-scraping` | [deep-firecrawl.agskill.md](./deep-firecrawl.agskill.md) | 深度技能实战卡：适用于代理和数据采集的 Web 爬取工具 (V2.0自动进化) |

---
**提示**：所有在此注册的技能，必须遵循《不可逆操作强备逻辑沙盒协议 (Mandatory Sandbox Backup Gate)》。
