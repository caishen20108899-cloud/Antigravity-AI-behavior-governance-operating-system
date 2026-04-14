---
name: "多智能体大兵团工单协同防线 (ag-team-issue-protocol)"
description: "把混沌的散养式多文件维护，升级为类似 GitHub Issues 的指派工单防死锁状态机。"
version: 2.0.0
author: "@国防部"
compatibility: "Antigravity v2.0"
metadata:
  antigravity:
    tags: [架构协同, 任务编排, 规范防死锁, 管理模型]
    category: Management
    requires_tools: []
    trigger_conditions: ["创建项目", "协同", "多部门", "新建协作", "分配工单"]
---

# 🪄 Antigravity 管理能力卡：基于 Issue 的智能体团队并发协作规范

> 发行说明：基于 Multica 的精华提取构建。抛弃所有口语化、流水账式的 Todo List，改用企业级 Issue 生命周期机制以遏制多兵种同时出击导致的 Git 冲突或上下文混乱。

## 🎯 挂载与触发 (When to Mount)

- 当需要为新系统创建 `AGENTS/` 集群协同架构时。
- 当接收到大型项目需求（如：从零构建一个 Web 前后端项目）需要指挥分工时。

## 🛡️ 逻辑沙盒护城河 (Dry-Run Sandbox Gate)

- **调度流预演断言**：在写入实际的 `task_board.md` 看板前，@国防部 (Commander) 必须在内心沙盒预演这套分发结构是不是过度切割了？如果是 10 分钟能搞定的超简单任务（改行错别字），**绝对不配动用这个引擎协议，直接绕过去单人执行**。

## ⚙️ 标准 Issue 流转流 (Procedure)

> 必须严格在项目的核心看板（如 `AGENTS/commander/task_board.md`）执行以下登记规范：

1. **确立唯一的总控池**
   - 任何子任务进入必须以工单格式落盘。模板范式：
     `[Issue-#001] | 指派: [@前端/工信部] | 状态: [Pending/In-Progress/Done]`
   - 不允许任何 Agent 私下偷偷接活，所有分派必须过明账。

2. **跨部门移交握手 (Handoff)**
   - 当工单 `#001` 下的 `@工信部` 完成其代码推送后，必须它自己进入清单将其改为 `[Done]`，然后通知并指配下一个衔接者：
     `[Issue-#002] | 指派: [@安全部/QA] | 状态: [In-Progress] | 依赖: Issue-#001`

3. **阻断防死循环红线 (Blocker Reporting Protocol)**
   - **绝对防崩断言**：如果某个 Agent 在独立修 bug 时，两次尝试跑不通编译或找不到日志线索，**立即停止一切动作！**
   - 写入状态：`状态: [Blocker]`，并挂载原因备注。向外围抛出异常交接给人类 (即通过“交互问答”抛还给主席)，绝不支持无止境地“再试一次”。
