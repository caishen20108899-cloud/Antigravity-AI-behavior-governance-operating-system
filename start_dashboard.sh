#!/bin/bash
# ═══════════════════════════════════════════════════════════
# Antigravity Dashboard 守护启动器 (V3.3)
# 功能: 自动检测端口→杀僵尸→后台启动→健康检查→自动重启
# ═══════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER_PY="${SCRIPT_DIR}/dashboard/server.py"
PORT=8899
LOG_FILE="${SCRIPT_DIR}/dashboard/.dashboard.log"
PID_FILE="${SCRIPT_DIR}/dashboard/.dashboard.pid"

# ── 颜色 ──
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

# ── 停止旧进程 ──
stop_old() {
    # 方式一: PID 文件
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  检测到旧进程 PID=$OLD_PID，正在终止...${NC}"
            kill "$OLD_PID" 2>/dev/null
            sleep 1
        fi
        rm -f "$PID_FILE"
    fi

    # 方式二: 端口占用探测
    PORT_PID=$(lsof -ti :$PORT 2>/dev/null)
    if [ -n "$PORT_PID" ]; then
        echo -e "${YELLOW}⚠️  端口 $PORT 被 PID=$PORT_PID 占用，正在释放...${NC}"
        kill "$PORT_PID" 2>/dev/null
        sleep 1
    fi
}

# ── 启动服务 ──
start_server() {
    echo -e "${GREEN}🚀 正在启动 Antigravity Dashboard...${NC}"
    nohup python3 "$SERVER_PY" >> "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"
    echo -e "   PID: $NEW_PID"
    echo -e "   日志: $LOG_FILE"
    echo -e "   端口: http://localhost:$PORT"
}

# ── 健康检查 ──
health_check() {
    sleep 2
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/" 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Dashboard 已启动并通过健康检查 (HTTP $HTTP_CODE)${NC}"
        return 0
    else
        echo -e "${RED}❌ 健康检查失败 (HTTP $HTTP_CODE)${NC}"
        return 1
    fi
}

# ── 主流程 ──
case "${1:-start}" in
    start)
        stop_old
        start_server
        health_check
        ;;
    stop)
        stop_old
        echo -e "${GREEN}✅ Dashboard 已停止${NC}"
        ;;
    restart)
        stop_old
        start_server
        health_check
        ;;
    status)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo -e "${GREEN}🟢 Dashboard 运行中 (PID=$(cat "$PID_FILE"))${NC}"
        else
            echo -e "${RED}🔴 Dashboard 未运行${NC}"
        fi
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
