---
name: "手术级代码修复 (surgical-code-repair) v3.0"
description: |
  基于 Karpathy 四项铁律 + gstack 操作手册模式构建的"无污染、零过度设计"
  代码手术级操作规范。每一步都有具体的 bash 命令、预期输出和分支逻辑。
version: 3.0.0
author: "@Architect / 发改委"
compatibility: "Antigravity v3.2"
preamble-tier: 2
metadata:
  antigravity:
    tags: [代码修复, 手术刀, Karpathy, 操作手册]
    category: Engineering
    requires_tools: [run_command, view_file, replace_file_content, grep_search]
    trigger_conditions: ["重构代码", "修改核心逻辑", "增加新功能", "大规模改动", "深入排查", "修 bug"]
---

# 🔪 手术级代码修复 — 操作手册 v3.0

> 本技能不是「规则清单」——它是分步操作指南。AI 必须按顺序执行，每步都有验证关卡。
> 来源：Karpathy 编码铁律 × gstack ship/review 操作流程精华

---

## Step 0: 侦查与范围锁定 (Recon & Scope Lock)

> 🚫 **铁律**：在完成此步骤之前，禁止编写任何一行代码。

### 0.1 项目探测

```bash
# 必须执行的侦查命令
ls -la                              # 项目根目录一览
git log --oneline -10               # 最近 10 次提交
git status --porcelain              # 当前工作区状态
git diff --stat HEAD~3              # 最近 3 次改动范围
```

**预期输出**：了解项目当前状态、最近改动方向、未提交的变更。

### 0.2 读取项目记忆

```bash
# 检查项目记忆文件
cat MEMORY.md 2>/dev/null || echo "NO_MEMORY"
cat _codebase_map.md 2>/dev/null || echo "NO_CODEMAP"
cat _active_task.md 2>/dev/null || echo "NO_ACTIVE_TASK"
```

**如果存在 `_codebase_map.md`**：必读，获取全局视野。
**如果存在 `MEMORY.md`**：必读，加载历史上下文。

### 0.3 范围冻结

在内部确认以下三件事，并向用户声明：

```
📐 手术范围声明：
- 目标：{一句话描述修改目标}
- 涉及文件：{预估 N 个文件}
- 预估改动行数：{不超过 M 行}
- 爆炸半径：{LOW / MEDIUM / HIGH}
```

> [!WARNING]
> **范围漂移检测**：如果执行过程中发现需要修改范围外的文件，**必须停下来**向用户声明新增范围，获得批准后才能继续。绝不悄悄扩大范围。

---

## Step 1: 根因追踪 (Root Cause Tracing)

> 不闭环，不行动。

### 1.1 追踪报错链路

```bash
# 如果有具体报错，追踪完整链路
grep -rn "ERROR_KEYWORD" src/ --include="*.{ts,py,go,java,rs}" | head -20
```

### 1.2 三假设法

提出 3 个最可能的根因假设，按置信度 (1-10) 排序：

```
假设 A: {描述} — 置信度 {N}/10 — 验证方法: {怎么验证}
假设 B: {描述} — 置信度 {N}/10 — 验证方法: {怎么验证}
假设 C: {描述} — 置信度 {N}/10 — 验证方法: {怎么验证}
```

### 1.3 验证最高置信度假设

执行验证命令。

**通过** → 进入 Step 2
**失败** → 验证下一个假设
**三个都失败** → 🔴 **Three-Strike Rule**：停止，向用户报告三个失败假设，请求指引。绝不盲猜第四次。

---

## Step 2: 方案设计与用户确认 (Plan & Confirm)

### 2.1 生成方案

输出具体的修改计划：

```
📋 修改方案（共 N 个文件，约 M 行改动）：

1. [MODIFY] path/to/file1.ts
   - 第 42 行：将 X 替换为 Y（原因：Z）
   
2. [MODIFY] path/to/file2.py
   - 第 100-110 行：重构函数签名（原因：Z）

3. [NEW] path/to/new_file.ts（可选）
   - 用途：...

预估风险：LOW / MEDIUM / HIGH
回滚方案：git checkout -- {files}
```

### 2.2 WTF 自检

> 来自 gstack qa 技能的 WTF 可能性检测

在动手前问自己：

```
改之前：这段代码看起来像 bug 的概率是多少？
- > 80%：大概率是真 bug → 改
- 50-80%：可能是 bug 也可能是刻意为之 → ASK 用户确认
- < 50%：可能是刻意设计 → 不改，仅报告
```

### 2.3 分类

对方案中的每个改动点进行三分类：

- **[AUTO-FIX]** 机械性修复（格式、拼写、语法错误、明显 bug）→ 直接执行，不询问
- **[ASK]** 需要判断的修复（架构决策、行为变更）→ 批量询问用户
- **[INFO]** 建议性意见 → 记录，不行动

**如果所有改动都是 AUTO-FIX**：直接进入 Step 3。
**如果有 ASK 项**：等待用户确认后进入 Step 3。

---

## Step 3: 执行修改 (Execute)

### 3.1 备份

```bash
# 每个要修改的文件，执行前先备份
cp path/to/file.ts "path/to/file.ts.bak_$(date +%Y%m%d_%H%M%S)"
```

> [!CAUTION]
> **无备份不动刀**——这不是建议，是硬前置条件。

### 3.2 代码修改

**Karpathy 四项铁律检查清单**（每次提交前过一遍）：

| # | 铁律 | 检查 |
|---|------|------|
| 1 | Think Before Coding | 我是否明确了改动的假设？ |
| 2 | Simplicity First | 我是否用了最少的代码完成目标？ |
| 3 | Surgical Changes | 我是否只改了必须改的行？是否碰了不相关的代码？ |
| 4 | Goal-Driven | 这个改动是否直接服务于用户的原始需求？ |

> **行数红线**：单个修改 PR 超过 200 行新增代码时，必须暂停自问「是否应该拆分？」

### 3.3 保持文档完整性

- ✅ 保留所有不相关的注释和 docstring
- ✅ 保留原有的空行和格式约定
- ❌ 不做「顺手优化」「顺手重构」
- ❌ 不删除「看起来没用」的代码（除非用户明确要求）

---

## Step 4: 物理验证 (Physical Verification)

> 🛡️ **不见绿灯不离场**

### 4.1 检测测试框架

```bash
# 自动检测项目测试命令
[ -f package.json ] && grep -q '"test"' package.json && echo "CMD:npm test"
[ -f Gemfile ] && echo "CMD:bundle exec rspec"
[ -f requirements.txt ] || [ -f pyproject.toml ] && echo "CMD:pytest"
[ -f go.mod ] && echo "CMD:go test ./..."
[ -f Cargo.toml ] && echo "CMD:cargo test"
```

### 4.2 三级验证

| 级别 | 动作 | 通过标准 |
|------|------|---------|
| **L1 编译** | 语法检查/编译 | Exit Code 0，无语法错误 |
| **L2 功能** | 运行检测到的测试命令 | 所有测试通过 |
| **L3 回归** | 如有测试套件，全量运行 | 无新增失败 |

```bash
# L1: 编译/语法检查
{检测到的编译命令}

# L2: 功能测试
{检测到的测试命令}

# L3: 回归（如果项目有完整测试套件）
{全量测试命令}
```

**L1 失败** → 立即修复语法错误，不允许离场
**L2 失败** → 修复一次。仍然失败 → 回滚到备份，报告用户
**L3 失败** → 分析是否是本次改动导致（git stash + 测试 → 确认）

> [!IMPORTANT]
> **验证结果必须是可观测的**——不接受「我看了一下代码觉得没问题」这种自我声明。必须有命令行输出的 Exit Code 0 或测试通过截图。

---

## Step 5: 结案报告 (Completion Report)

### 5.1 格式化输出

```
📋 手术结案报告
━━━━━━━━━━━━━━━━━━
🎯 目标：{一句话}
📐 范围：{N 个文件, M 行改动}
🔪 改动清单：
  - [MODIFIED] path/to/file1.ts (改动 +X/-Y 行)
  - [MODIFIED] path/to/file2.py (改动 +X/-Y 行)
🧪 验证结果：
  - L1 编译: ✅ PASS
  - L2 功能: ✅ PASS (N/N tests)
  - L3 回归: ✅ PASS / ⏭️ SKIP (无测试套件)
💡 学习沉淀：
  - {如果发现了非显而易见的模式/陷阱，记录下来}
📍 备份位置：{备份文件路径}
```

### 5.2 经验沉淀

如果在执行过程中发现了**非显而易见的模式或陷阱**，判断是否值得沉淀：

```
判断标准：这个发现在未来的会话中能节省时间吗？
  YES → 写入项目的 _learnings.jsonl
  NO  → 不记录（不记录显而易见的事情）
```

---

## ⚡ 快速通道 (Fast Path)

如果任务是以下类型之一，跳过 Step 1-2，直接从 Step 3 开始：
- 修复一个明确的拼写错误
- 改一行配置
- 添加一条注释
- 格式化代码

但 **Step 4（物理验证）永远不可跳过**。
