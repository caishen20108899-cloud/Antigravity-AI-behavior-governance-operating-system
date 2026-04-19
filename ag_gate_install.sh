#!/bin/bash
# ══════════════════════════════════════════════════════════════
#  Antigravity Gate 一键安装器
#  用法: sh ag_gate_install.sh <项目路径>
#  效果: 在目标项目的 .git/hooks/pre-commit 中安装物理审查闸门
# ══════════════════════════════════════════════════════════════

HOOK_SOURCE="/Users/qianxiangyunji/Antigravity/全局技能库_AG_Skills/ag_gate_hook.sh"
TARGET_DIR="${1:-.}"
TARGET_DIR=$(cd "$TARGET_DIR" && pwd)

echo ""
echo "🛡️  Antigravity Gate 安装器"
echo "   目标项目: $TARGET_DIR"
echo ""

# 检查是否是 git 仓库
if [ ! -d "$TARGET_DIR/.git" ]; then
    echo "❌ 错误: $TARGET_DIR 不是 git 仓库"
    exit 1
fi

# 检查 hook 源文件
if [ ! -f "$HOOK_SOURCE" ]; then
    echo "❌ 错误: 找不到 $HOOK_SOURCE"
    exit 1
fi

# 备份已有的 pre-commit hook
HOOK_PATH="$TARGET_DIR/.git/hooks/pre-commit"
if [ -f "$HOOK_PATH" ]; then
    BACKUP="${HOOK_PATH}.bak_$(date +%Y%m%d_%H%M%S)"
    cp "$HOOK_PATH" "$BACKUP"
    echo "📦 已备份原有 hook → $BACKUP"
fi

# 安装
cp "$HOOK_SOURCE" "$HOOK_PATH"
chmod +x "$HOOK_PATH"

echo "✅ Pre-commit 闸门已安装到: $HOOK_PATH"
echo ""
echo "   每次 git commit 时将自动运行:"
echo "   1️⃣  ag_post_review  (范围/语法/缺陷扫描)"
echo "   2️⃣  Review Army v2.0 (AST 安全分析，有风险则拦截)"
echo "   3️⃣  Python 语法验证"
echo ""
echo "   跳过闸门: git commit --no-verify"
echo ""
