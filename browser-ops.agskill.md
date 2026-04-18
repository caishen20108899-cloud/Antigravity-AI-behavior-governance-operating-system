---
name: "浏览器驱动手册 (browser-ops)"
description: "规范如何正确、高效、安全地使用 default_api:browser_subagent 来完成网页操作及自动化回归测试。"
version: 1.0.0
author: "@Commander"
compatibility: "Antigravity v3.3"
metadata:
  antigravity:
    tags: [UI测试, 网页搜索, e2e, 爬虫]
    category: OpsManual
    trigger_conditions: ["网页", "浏览器", "录屏", "UI测试", "截图", "访问"]
---

# 🌐 Playbook: 浏览器驱动手册 (Browser Ops)

> 为什么有这本手册？智能体在驱动 `browser_subagent` 时非常容易陷入“迷失、死循环、盲目点击”的陷阱。本兵工手册通过从 `gstack` 提炼的最佳实践，为您加装一层思维导轨。

## 🎯 核心使用法则 (The Golden Rules)

当你需要访问网页以验证 UI 或查询信息时，**必须且只能遵循以下法则**：

1. **精准授权**：不要通过浏览器访问任何没有得到用户批准或授权的受保护资产（除非用户明确给了测试账号）。
2. **目标清晰**：传入给 `browser_subagent` 的 `Task` 必须**具体到步骤级的微操**，比如“登录页面查找用户名输入框，输入 admin，点击提交。截图看报错信息”。**严禁传入**“随便看看这个页面长啥样”。
3. **闭环验收**：子智能体回归后，必须要求其带回特定的 HTML 块 (DOM 摘要) 或者强制生成录制视频 (`RecordingName` 必须带语义)，你不仅要听子智能体说啥，必须亲眼看它返回的上下文。

## 🚀 执行流：如何开出完美的子特工工单？

| 若你想要... | 应填写的 `TaskName` 范例 | `Task` 描述范例 (Prompt for Subagent) |
|---|---|---|
| **验证一个刚刚改好的网页排版** | `Render Form UI` | "Please navigate to `http://localhost:3000/login`. Scroll to the bottom and check if the 'Submit' button overlaps with the footer. Capture a screenshot or save the video under 'login_ui_check' and report the exact bounding box or visual state of the button." |
| **搜刮静态文档** | `Scrape API Docs` | "Navigate to `https://docs.domain.com/api`. Do not waste time clicking. Just extract the CSS selector `#main-content` to markdown and return." |
| **执行端到端登录流程回归找 Bug** | `E2E Login Flow` | "Go to `http://localhost:8080`. Type 'test_user' into `#username`, type '123456' into `#password`. Click `#submit`. Wait for redirection to `/dashboard`. If an error popup appears, read the exact error message and return it." |

## 🛡️ 错误排查 (Troubleshooting)

如果子特工报告“找不到元素”或“页面空白”：
1. **不要一味地盲目重试！** 检查你的 Node 服务/React 服务是否真的还在跑。
2. **端口是否占用？** 去主机终端跑 `curl -I http://localhost:PORT` 查一下返回码。
3. **元素选择器是否有误？** 在让子智能体点击前，应该先让子智能体做个动作：`List DOM elements containing 'Submit' text`。

## ⚠️ 关于视频录制 (`RecordingName`)
Antigravity 会自动把浏览器子智能体的动作录制成 WebP 视频放到工件目录（Artifacts directory）。当你向指挥官汇报任务结果时，请**附着这些视频或者截图的文件名**，比如：
> “我已经完成了浏览器 UI 回归验证，详见录制的视频 `artifacts/login_flow_demo.webp` (嵌入链接)”。

（完）
