---
name: "UX/UI 设计大师雷达 (design-audit)"
description: "基于好感度蓄水池 (Goodwill Reservoir) 和 AI Slop 侦测法则的高规格前端设计审查标准。"
version: 1.0.0
author: "@Architect"
compatibility: "Antigravity v3.3"
metadata:
  antigravity:
    tags: [前端, UI, 设计, 排版, 交互]
    category: QualityControl
    trigger_conditions: ["前端设计", "好感度", "排版", "UI改善", "CSS审查"]
---

# 🎨 Playbook: 设计天花板审查规范 (Design Audit)

> 作为 @Frontend 或 @Architect，当你接手 H5 (如 ChiChat) 或后台 (EAMPro) 的视图层开发时，你的目标不仅是“长得正常”，而是**干掉廉价的 AI 生成味**（AI Slop），建立符合硅谷工程顶级标准的用户体验。

## 💧 核心基石：好感度蓄水池 (Goodwill Reservoir)
记住：每个用户在进入你的网页时，带着 **100 点好感度水池**。
- 表单少输一个字段：+5点
- 按钮没有 `focus` 态被键盘按空：-10点
- 遭遇突如其来的模态框打断：-20点
**你的审查目标：禁止任何让好感度下降低于 60 点的交互流设计！**

## 🛑 AI Slop (反劣质 AI 审美) 侦测清单
当你生成 HTML/CSS 时，若犯了以下任何一条，你必须打回并立刻自我修正：
1. **排雷 1（滥用圆角）**：禁止将每个按钮或卡片都写成 `border-radius: 9999px` 或者不一致的奇怪弧度。使用系统级的 `4px` 或 `8px`。
2. **排雷 2（寡淡对比度）**：禁止使用“浅灰色字配白背景”。文字必须满足 WCAG AA 级 4.5:1 对比度。
3. **排雷 3（过度拥挤）**：必须使用基于 4px/8px 的网格间距 (`margin/padding`)。不可用 `15px`、`21px` 这种毫无刻度规律的数值。
4. **排雷 4（幽灵状态）**：所有可点按元素（`button`, `a`）必须有明确的 `:hover`, `:active`, `:focus-visible` 态。必须有一眼可见的反馈感。

## 🪂 Trunk Test (降落伞测试)
评估任何路由页面的**首屏呈现**（Hero Space）：如果把一个用户空投（直接 URL 贴入）到此页面，他能否在 **3秒** 内回答：
1. "我在这能干什么？"
2. "网站目前在干嘛？（Loading态是否清晰）"
3. "主按钮（Primary Call To Action）到底在哪儿？"
如果他回答不了，说明 Visual Hierarchy（视觉层级）彻底失败。马上修改你的 `<h1>`、颜色的重量级分布。

## ⚙️ 行动准则
> 在进行 UI 相关任务 (`Task: Frontend Refactor`) 提交代码前，请按照此模板向指挥官做**简短汇报备忘**：
- [ ] 已排查对比度缺陷？ (是/否)
- [ ] 按钮等交互控件已包含完整三态伪类？ (是/否)
- [ ] 本页面降落伞测试得分如何？ (满分10)
- [ ] 当前好感度蓄水池盈亏预估 (如：-5点 增加了一步登录流)
