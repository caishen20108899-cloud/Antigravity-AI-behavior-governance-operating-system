# Antigravity 全局技能库引擎记忆档案 (MEMORY)

## 📌 项目元数据
- **项目名**: 全局技能库_AG_Skills (Antigravity Core Engine)
- **核心定位**: 整个舰队的全军指挥大脑、技能分发器与防御检测网段。
- **GitHub**: https://github.com/caishen20108899-cloud/Antigravity-AI-behavior-governance-operating-system

## 📅 版本演进与核心里程碑

### [2026-04-25] V3.6.1 Unattended Physical Gate Validation
**核心突破：全域操作系统门禁实现无人值守物理级验收。**
1. **自动化闭环测试**：通过完全无人干预的脚本流程，在独立的 `AG_OS_Testbed` 中证实了所有门禁系统的真实拦截力。
2. **多智能体编队证明**：验证了通过 `task_board.md` 看板进行物理同步的跨节点能力。
3. **防盲写与微步进验证**：测试通过了 `ag_indexer.py` 的秒级代码扫描，并实锤证明了违反 Rule 13 时会被 `ag_post_review.py` 与 `ag_gate_hook.sh` 的强制物理链条打断（三道闸门联防测试）。系统从"提示词软约束"向"操作系统级强中断"演化。

### [2026-04-19] V3.6.0 Physical-Gate (当前版本)
**核心突破：审查权从"AI自觉"彻底转移到"Git物理闸门"。**
1. **全功能真实性审计**：对仓库 README 声称的每一个功能进行逐一验证（Python 导入测试 + 实际运行 + 源码审读）。发现 6 项名不副实 + 3 项根本缺陷并全部修复。
2. **Review Army v2.0 重写**：从 `_mock_llm_call()` 桩函数升级为基于 AST + Regex 的真实静态分析。三路并行：Testing（裸except/过长函数/嵌套过深）、Security（硬编码密钥/eval注入/SQL拼接）、Consistency（未使用导入/print遗留/pdb断点）。扫描 18 个文件发现 130 项真实问题。
3. **ag_gate 物理闸门**：Git pre-commit hook，三层检查（ag_post_review + Review Army + 语法验证），ASK 级安全风险自动拦截 commit。**AI 绕不过去**。一键安装到任何 git 项目：`sh ag_gate_install.sh <路径>`。
4. **GEMINI.md 落地**：将 user_rules 中的 11 条铁律导出为仓库中实际存在的 180 行文件。
5. **ag_core 包正规化**：创建 `__init__.py`，使 ag_core 成为合法 Python 包，不再需要 sys.path hack。
6. **ag_evolve 去重**：新增内容级去重逻辑，相同仓库不再每天重复生成完全相同的技能卡。
7. **README 全面对齐**：中间件适用范围标注、Review Army v2.0 描述、架构图补全、clone URL 修正。

### [2026-04-19] V3.5.0 Execution Discipline
**核心突破：从"规则靠自觉"到"物理闸门不可绕"。**
1. **执行纪律断裂根因诊断**：系统性分析了 6 层防线的设计完成度 vs 实际激活率。识别核心矛盾——中间件管线（middleware/dispatcher/review_army）只在 Python 编排系统中生效，对话窗口完全绕过。
2. **ag_post_review.py 物理审查闸门**：对话窗口中可通过 `run_command` 调用的独立审查脚本。5 维审查（范围检测 + 语法验证 + 历史经验回溯 + 缺陷扫描 + 测试框架建议）。BAT 文件专项 6 项检测。
3. **行为锚定协议**：强制角色切换（写代码→@Architect 审查→@DevOps 验证）+ 结构化交付单格式。
4. **中间件管线扩展至第 5 层**：新增 DynamicSkillMiddleware，实现运行时技能卡自动挂载。

### [2026-04-18] V3.4.0 Gstack Fusion
**核心突破：操作规范向"分步操作手册"与"物理屏障"方向蜕变。**
1. 深入解构并熔铸 Garry Tan 的 `gstack` 理念，完全覆盖了其核心长板。
2. **Archon-Gate 断头台**: 对于底层代码修改，从以往的"日志播报"升级为物理锁死。所有任务必须在退出前看到 `go test`/`npm run build` 等指令报出 Exit Code 0，否则直接熔断。
3. **极简 DX 与审美净化**: 
   - `script-dx`: TTHW<2min 约束，全静默无跳红的脚本交互范式。
   - `design-audit`: 好感度蓄水池（Goodwill Reservoir），剥离廉价大圆角、丑陋紫水晶等"初级大模型审美"，只保留克制、留白的苹果级冷感界面。
4. **平行 Review Army**: 将原有的多智能体线状链式，转换为"主AI生成大 PR，分发三路子AI (覆盖率测绘/安全防线/合规纠错) 并行排雷去重"的立体军团模式。
5. **记忆动态校准**: 在 `_learnings.jsonl` 中自动收录已处理误报（False Positive），并动态调低置信阀值。

### [2026-04-15] V3.3.x 社区进化与图谱纪元
- 实装 `ag_indexer`，一秒种遍历全项目生成 AST `_codebase_map.md` 代码微缩地图。
- 部署 `ag_evolve` 每日轮询抓取 Github Trending, HN, Awesome 等全球六路 AI 黑客情报，生成专属 `.agskill.md`。

## 🛡️ ag_gate 物理闸门使用指南
- **安装**: `sh ag_gate_install.sh <项目路径>`
- **效果**: 每次 git commit 自动运行三层审查，安全风险自动拦截
- **跳过**: `git commit --no-verify`（仅限紧急情况）
- **核心文件**: `ag_gate_hook.sh`（hook 本体）+ `ag_gate_install.sh`（安装器）

## 🚨 高危防线 / Triage 分诊雷区
- `[AUTO-FIX]` 强力收割，不容许反复确认浪费用户精力。
- 坚守 11 条天条（GEMINI.md 法典）：凡覆盖型操作（`rm`/`sed -i`），必须先挂 `cp` 分身。绝对禁止把多个操作链起来赌概率！
- Review Army v2.0 仅拦截 ASK 级安全风险，INFO 级建议只报告不拦截。
