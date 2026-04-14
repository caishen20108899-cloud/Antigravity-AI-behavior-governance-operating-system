#!/bin/bash

# Antigravity General Workspace Initializer (ag_init.sh)
# Uses the global toolkit to stamp standard Memory and Radar templates in a new project dir.

TARGET_DIR="${1:-.}"
PROJECT_NAME=$(basename $(realpath "$TARGET_DIR"))

echo "🚀 [Antigravity] Initializing new agent context in: $TARGET_DIR (Project: $PROJECT_NAME)"

# Create default MEMORY.md
if [ ! -f "$TARGET_DIR/MEMORY.md" ]; then
    cat <<EOF > "$TARGET_DIR/MEMORY.md"
# $PROJECT_NAME 领域全局记忆 (MEMORY)

> [!NOTE]
> 这是 $PROJECT_NAME 的客观规律、技术栈和常驻记忆档案库。

## 环境基础 (Environment)

## 核心约定 (Conventions)

## 经验冷库 (Lessons Learned)

EOF
    echo "✅ Created MEMORY.md"
else
    echo "⚠️ MEMORY.md already exists, skipping."
fi

# Create default Status Radar
RADAR_FILE="$TARGET_DIR/${PROJECT_NAME}_项目进度与状态雷达.md"
if [ ! -f "$RADAR_FILE" ]; then
    cat <<EOF > "$RADAR_FILE"
# $PROJECT_NAME 进度与状态雷达 (Status Radar)

> 提示：离场归档时必须将本文件的状态变更推送到远端。

## 当前大盘状态 (Overall Status)
- 当前开发阶段： 初始化

## 已结案历史 (Completed)

## 待执行积压 (Pending Tasks)

EOF
    echo "✅ Created $RADAR_FILE"
else
    echo "⚠️ Status Radar already exists, skipping."
fi

# Git initialization if not present
if [ ! -d "$TARGET_DIR/.git" ]; then
    cd "$TARGET_DIR" || exit
    git init
    cat <<EOF > .gitignore
.DS_Store
*.log
_active_task.md
EOF
    echo "✅ Initialized local Git repository (Remember to add remote origin later!)"
fi

echo "🎉 Antigravity context has been seeded successfully."
