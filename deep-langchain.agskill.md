---
name: "langchain — 深度学习技能卡 (deep-learn-langchain)"
description: "代理工程平台"
version: 2.0.0
author: "@社区自进化引擎 (深度学习)"
compatibility: "Antigravity v3.3"
metadata:
  antigravity:
    tags: [深度学习, Python, 实战技能]
    category: DeepLearned
    source: "https://github.com/langchain-ai/langchain"
    stars: 133432
    discovered: "2026-04-14"
    depth: "deep"
    requires_tools: [run_command]
    trigger_conditions: ["langchain", "agents", "ai", "ai-agents", "anthropic", "chatgpt"]
---

# 🧠 深度学习技能卡: langchain

> 由 ag_evolve V2.0 深度解析引擎自动生成 | 2026-04-14
> 原始仓库: [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | ⭐ 133,432 | Python

## 📋 概要
代理工程平台

## 🎯 挂载与触发 (When to Mount)

- 当任务涉及以下关键词时自动挂载: langchain, agents, ai, ai-agents, anthropic, chatgpt
- 当需要 代理工程平台 的能力时

## ⚙️ 安装与部署 (Installation)

```bash
pip install langchain
```
## 📖 核心概念 (Key Concepts)

- Quickstart
- LangChain ecosystem
- Why use LangChain?
## ⚙️ 标准执行流 (Procedure)

> 以下基于官方 Quick Start 提炼。

````bash
pip 安装 langchain
# 或
uv 添加 langchain
````

````蟒蛇
从 langchain.chat_models 导入 init_chat_model

模型 = init_chat_model("openai:gpt-5.4")
result = model.invoke("你好，世界！")
````

如果您正在寻找更高级的自定义或代理编排，请查看 [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)，这是我们用于构建可控代理工作流程的框架。

> [!提示]
> 用于开发、调试和部署 AI 代理和 LLM 应用程序，
## 💻 代码示例 (Code Examples)

### 示例 1
```
pip install langchain
# or
uv add langchain
```

### 示例 2
```
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-5.4")
result = model.invoke("Hello, world!")
```

## 📁 项目结构概览

```
  .devcontainer
  .devcontainer/README.md
  .devcontainer/devcontainer.json
  .devcontainer/docker-compose.yaml
  .dockerignore
  .editorconfig
  .gitattributes
  .github
  .github/CODEOWNERS
  .github/ISSUE_TEMPLATE
  .github/PULL_REQUEST_TEMPLATE.md
  .github/actions
  .github/dependabot.yml
  .github/images
  .github/scripts
  .github/tools
  .github/workflows
  .gitignore
  .markdownlint.json
  .mcp.json
```

## 🔗 与 Antigravity 集成点 (Integration Points)

> 此技能可在以下场景被 `match_skills_for_task()` 自动匹配并挂载:
> - 多智能体工作流中需要 langchain 能力时
> - 项目构建或技术选型评估时

## ⚠️ 注意
此技能卡由 ag_evolve V2.0 深度学习引擎自动生成。核心信息已从源码和文档中提炼，但可能需要人工审核具体参数后才能投入生产使用。
