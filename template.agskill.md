---
name: "模板名称-中文 (如: redis-fast-unfreeze)"
description: "一句话描述这个技能库的作用，如：一键查杀所有Redis封锁链"
version: 2.0.0
author: "@国家发改委"
compatibility: "Antigravity v2.0"
metadata:
  antigravity:
    tags: [运维, redis, 安全限制解除]
    category: Ops
    requires_tools: [run_command] # 依赖的底层工具
    trigger_conditions: ["Redis堵塞", "紧急冻结处理"] # 用于在 Manifest 索引的触发词库
---

# 🪄 Antigravity 专精技法 / 能力卡片：[填入技能名称]

> 这是 Antigravity 的 v2.0 渐进式技能卡。当你发现自己处于**【触发条件】**时，应当被调度到本能力卡，采用此处的**【执行流】**去操作，放弃从零推演，以大幅度节省时间和容错率。

## 🎯 挂载与触发 (When to Mount)

- 当用户要求……
- 当业务现象呈现出……

## 🛡️ 逻辑沙盒护城河 (Dry-Run Sandbox Gate)

> 依照《强制灾备铁律》，本技能涉及的任何环境切除均不可越过沙盒。

- **预演要求**：在正式执行【写入/覆盖/删除】命令前，必须在内部推演 `sandbox_mock`：
  1. 需要对什么文件/数据库行进行备份？（比如 `cp target.config target.config.bak`）
  2. 备份恢复的回滚命令是什么？
  *(只有当预演通过并显式输出后，才允许向前端抛出真正带破坏性的 Bash 侧发令。)*

## ⚙️ 标准执行流 (Procedure)

> 必须按照此结构一气呵成。

1. **环境侦探与连通 (Observe)**
   - 探活命令，例如 `ls -al` 或查网点连通性。
2. **切削/处理 (Operate - 必须先经沙盒门槛)**
   - 执行具体操作脚本或参数修改。
3. **闭环刷新与抛出信息 (Reload)**
   - 热重启、输出修正摘要给最终用户。

## ⚠️ 绝对禁忌与抗毁指南 (Redlines)

- 🚫 **毁瘫红线**：绝对不可执行的某个参数（比如不要全盘 `FLUSHALL` 或直接覆盖原始凭证）。

## 🔍 后置验收 (Verification)

1. 通过执行什么脚本来确保没有弄崩系统并已达标。
