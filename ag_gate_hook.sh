#!/bin/bash
# ══════════════════════════════════════════════════════════════
#  Antigravity Pre-Commit Gate (ag_gate)
#  物理审查闸门 — 任何 AI / 人类做的 commit 都必须通过此门
#  
#  安装: cp ag_gate_hook.sh <项目>/.git/hooks/pre-commit && chmod +x
#  或用: sh ag_gate_install.sh <项目路径>
# ══════════════════════════════════════════════════════════════

# ag_post_review.py 的全局路径
AG_REVIEW="/Users/qianxiangyunji/Antigravity/全局技能库_AG_Skills/ag_core/ag_post_review.py"
AG_REVIEW_ARMY="/Users/qianxiangyunji/Antigravity/全局技能库_AG_Skills/ag_core/ag_review_army.py"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "${CYAN}══════════════════════════════════════════════════${NC}"
echo "${CYAN}  🛡️  Antigravity Pre-Commit Gate v1.0${NC}"
echo "${CYAN}══════════════════════════════════════════════════${NC}"
echo ""

# 获取暂存文件列表
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
if [ -z "$STAGED_FILES" ]; then
    echo "${GREEN}✅ 无暂存文件，放行。${NC}"
    exit 0
fi

# 统计文件
TOTAL=$(echo "$STAGED_FILES" | wc -l | tr -d ' ')
PY_FILES=$(echo "$STAGED_FILES" | grep '\.py$' || true)
BAT_FILES=$(echo "$STAGED_FILES" | grep -E '\.(bat|cmd)$' || true)
SH_FILES=$(echo "$STAGED_FILES" | grep -E '\.(sh|bash)$' || true)
PY_COUNT=$(echo "$PY_FILES" | grep -c '.' 2>/dev/null || echo 0)
BAT_COUNT=$(echo "$BAT_FILES" | grep -c '.' 2>/dev/null || echo 0)

echo "📋 暂存文件: ${TOTAL} 个 (Python: ${PY_COUNT}, BAT: ${BAT_COUNT})"
echo ""

PROJECT_DIR=$(git rev-parse --show-toplevel)
GATE_FAILED=0

# ─── 第 1 关: ag_post_review 范围 + 语法 + 缺陷扫描 ───
if [ -f "$AG_REVIEW" ]; then
    echo "${YELLOW}┌─── 第 1 关: ag_post_review 审查 ───────────────┐${NC}"
    
    # 构建文件参数
    FILE_ARGS=""
    for f in $STAGED_FILES; do
        full_path="${PROJECT_DIR}/${f}"
        if [ -f "$full_path" ]; then
            FILE_ARGS="$FILE_ARGS $full_path"
        fi
    done
    
    REVIEW_OUTPUT=$(python3 "$AG_REVIEW" "$PROJECT_DIR" $FILE_ARGS 2>&1)
    echo "$REVIEW_OUTPUT"
    
    # 检查是否有高危问题
    if echo "$REVIEW_OUTPUT" | grep -q "🔴\|FAIL\|CRITICAL"; then
        echo "${RED}  ❌ 审查发现高危问题！${NC}"
        GATE_FAILED=1
    elif echo "$REVIEW_OUTPUT" | grep -q "审查结论: PASS"; then
        echo "${GREEN}  ✅ 第 1 关通过${NC}"
    fi
    echo "${YELLOW}└────────────────────────────────────────────────┘${NC}"
    echo ""
else
    echo "${YELLOW}⚠️ ag_post_review.py 未找到，跳过第 1 关${NC}"
fi

# ─── 第 2 关: Review Army 深度静态分析 (仅 Python) ───
if [ -n "$PY_FILES" ] && [ -f "$AG_REVIEW_ARMY" ]; then
    echo "${YELLOW}┌─── 第 2 关: Review Army v2.0 静态分析 ─────────┐${NC}"
    
    PY_FULL_PATHS=""
    for f in $PY_FILES; do
        full_path="${PROJECT_DIR}/${f}"
        if [ -f "$full_path" ]; then
            PY_FULL_PATHS="$PY_FULL_PATHS $full_path"
        fi
    done
    
    if [ -n "$PY_FULL_PATHS" ]; then
        ARMY_OUTPUT=$(python3 -c "
import sys, asyncio, os, json
sys.path.insert(0, '/Users/qianxiangyunji/Antigravity/全局技能库_AG_Skills')
from ag_core.ag_review_army import ReviewArmy

files = sys.argv[1:]
reviewer = ReviewArmy('${PROJECT_DIR}')
result = asyncio.run(reviewer.run_review(file_paths=files))

# 输出摘要
ask_count = len(result.get('ASK', []))
autofix_count = len(result.get('AUTO-FIX', []))
info_count = len(result.get('INFO', []))
total = ask_count + autofix_count + info_count

print(json.dumps({
    'total': total,
    'ask': ask_count,
    'autofix': autofix_count,
    'info': info_count,
    'details': result
}, ensure_ascii=False))
" $PY_FULL_PATHS 2>&1)
        
        # 解析 JSON 结果
        ASK_COUNT=$(echo "$ARMY_OUTPUT" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    ask = data.get('ask', 0)
    autofix = data.get('autofix', 0)
    info = data.get('info', 0)
    total = data.get('total', 0)
    print(f'  扫描发现: {total} 项 (安全风险: {ask}, 可自动修复: {autofix}, 建议: {info})')
    
    # 输出 ASK 级别的详细信息
    if ask > 0:
        print('')
        print('  ⚠️ 安全风险项 (需人工定夺):')
        for item in data.get('details', {}).get('ASK', []):
            print(f'    [{item[\"confidence\"]}/10] {item[\"file\"]}:{item[\"line\"]} — {item[\"description\"]}')
    
    # 退出码: ASK > 0 则返回 1 (拦截)
    sys.exit(1 if ask > 0 else 0)
except Exception as e:
    print(f'  ⚠️ 解析异常: {e}')
    sys.exit(0)
" 2>&1)
        ARMY_EXIT=$?
        echo "$ASK_COUNT"
        
        if [ $ARMY_EXIT -ne 0 ]; then
            echo "${RED}  ❌ Review Army 发现安全风险！${NC}"
            GATE_FAILED=1
        else
            echo "${GREEN}  ✅ 第 2 关通过（无安全风险）${NC}"
        fi
    fi
    echo "${YELLOW}└────────────────────────────────────────────────┘${NC}"
    echo ""
fi

# ─── 第 3 关: Python 语法检查 ───
if [ -n "$PY_FILES" ]; then
    echo "${YELLOW}┌─── 第 3 关: Python 语法验证 ───────────────────┐${NC}"
    SYNTAX_FAIL=0
    for f in $PY_FILES; do
        full_path="${PROJECT_DIR}/${f}"
        if [ -f "$full_path" ]; then
            python3 -c "import py_compile; py_compile.compile('${full_path}', doraise=True)" 2>&1
            if [ $? -ne 0 ]; then
                echo "${RED}  ❌ 语法错误: ${f}${NC}"
                SYNTAX_FAIL=1
            fi
        fi
    done
    if [ $SYNTAX_FAIL -eq 0 ]; then
        echo "${GREEN}  ✅ 全部 ${PY_COUNT} 个 Python 文件语法正确${NC}"
    else
        GATE_FAILED=1
    fi
    echo "${YELLOW}└────────────────────────────────────────────────┘${NC}"
    echo ""
fi

# ─── 最终裁决 ───
echo "${CYAN}══════════════════════════════════════════════════${NC}"
if [ $GATE_FAILED -ne 0 ]; then
    echo "${RED}  ❌ COMMIT 被拦截 — 请修复上述问题后重试${NC}"
    echo "${RED}  💡 跳过闸门: git commit --no-verify${NC}"
    echo "${CYAN}══════════════════════════════════════════════════${NC}"
    echo ""
    exit 1
else
    echo "${GREEN}  ✅ 全部闸门通过 — 放行 COMMIT${NC}"
    echo "${CYAN}══════════════════════════════════════════════════${NC}"
    echo ""
    exit 0
fi
