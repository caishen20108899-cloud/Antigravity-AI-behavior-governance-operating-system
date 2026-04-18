# Antigravity 全局技能库引擎记忆档案 (MEMORY)

## 📌 项目元数据
- **项目名**: 全局技能库_AG_Skills (Antigravity Core Engine)
- **核心定位**: 整个舰队的全军指挥大脑、技能分发器与防御检测网段。

## 📅 版本演进与核心里程碑

### [2026-04-18] V3.4.0 Gstack Fusion (当前版本)
**核心突破：操作规范向“分步操作手册”与“物理屏障”方向蜕变。**
1. 深入解构并熔铸 Garry Tan 的 `gstack` 理念，完全覆盖了其核心长板。
2. **Archon-Gate 断头台**: 对于底层代码修改，从以往的“日志播报”升级为物理锁死。所有任务必须在退出前看到 `go test`/`npm run build` 等指令报出 Exit Code 0，否则直接熔断。
3. **极简 DX 与审美净化**: 
   - `script-dx`: TTHW<2min 约束，全静默无跳红的脚本交互范式。
   - `design-audit`: 好感度蓄水池（Goodwill Reservoir），剥离廉价大圆角、丑陋紫水晶等“初级大模型审美”，只保留克制、留白的苹果级冷感界面。
4. **平行 Review Army**: 将原有的多智能体线状链式，转换为“主AI生成大 PR，分发三路子AI (覆盖率测绘/安全防线/合规纠错) 并行排雷去重”的立体军团模式。
5. **记忆动态校准**: 在 `_learnings.jsonl` 中自动收录已处理误报（False Positive），并动态调低置信阀值，从此 AI 不再对同一坑点烦人复读。

### [2026-04-15] V3.3.x 社区进化与图谱纪元
- 实装 `ag_indexer`，一秒种遍历全项目生成 AST `_codebase_map.md` 代码微缩地图。
- 部署 `ag_evolve` 每日轮询抓取 Github Trending, HN, Awesome 等全球六路 AI 黑客情报，生成专属 `.agskill.md`。

## 🚨 高危防线 / Triage 分诊雷区
- `[AUTO-FIX]` 强力收割，不容许反复确认浪费用户精力。
- 坚守 11 条天条（GEMINI.md 法典）：凡覆盖型操作（`rm`/`sed -i`），必须先挂 `cp` 分身。绝对禁止把多个操作链起来赌概率！
