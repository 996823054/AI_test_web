#!/bin/bash
#
# AI 测试平台 - 一键启动脚本
# 用法：
#   ./start.sh          启动前后端
#   ./start.sh stop     停止所有服务
#   ./start.sh restart  重启所有服务
#   ./start.sh clean    清理平台缓存
#   ./start.sh clean-restart 清理缓存并重启所有服务
#   ./start.sh status   查看服务状态

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_PORT=8000
FRONTEND_PORT=5173
LOG_DIR="$PROJECT_DIR/.logs"
ROOT_ENV_FILE="$PROJECT_DIR/.env"
BACKEND_ENV_FILE="$BACKEND_DIR/.env"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

mkdir -p "$LOG_DIR"

load_env_files() {
    if [ -f "$ROOT_ENV_FILE" ]; then
        set -a
        . "$ROOT_ENV_FILE"
        set +a
    fi

    if [ -f "$BACKEND_ENV_FILE" ]; then
        set -a
        . "$BACKEND_ENV_FILE"
        set +a
    fi
}

check_port() {
    lsof -ti:"$1" 2>/dev/null
}

stop_services() {
    echo -e "${YELLOW}正在停止服务...${NC}"
    local be_pid=$(check_port $BACKEND_PORT)
    local fe_pid=$(check_port $FRONTEND_PORT)

    if [ -n "$be_pid" ]; then
        kill -9 $be_pid 2>/dev/null
        echo -e "  后端 (PID $be_pid) ${RED}已停止${NC}"
    else
        echo -e "  后端 未运行"
    fi

    if [ -n "$fe_pid" ]; then
        kill -9 $fe_pid 2>/dev/null
        echo -e "  前端 (PID $fe_pid) ${RED}已停止${NC}"
    else
        echo -e "  前端 未运行"
    fi
}

show_status() {
    echo -e "${CYAN}═══ AI 测试平台服务状态 ═══${NC}"
    local be_pid=$(check_port $BACKEND_PORT)
    local fe_pid=$(check_port $FRONTEND_PORT)

    if [ -n "$be_pid" ]; then
        echo -e "  后端  :$BACKEND_PORT  ${GREEN}运行中${NC} (PID $be_pid)"
    else
        echo -e "  后端  :$BACKEND_PORT  ${RED}未运行${NC}"
    fi

    if [ -n "$fe_pid" ]; then
        echo -e "  前端  :$FRONTEND_PORT  ${GREEN}运行中${NC} (PID $fe_pid)"
    else
        echo -e "  前端  :$FRONTEND_PORT  ${RED}未运行${NC}"
    fi
}

clean_cache() {
    echo -e "${YELLOW}正在清理平台缓存...${NC}"
    # 清理 Python 编译缓存
    find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find "$BACKEND_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
    echo -e "  后端 Python 编译及测试缓存 ${GREEN}清理成功${NC}"
    
    # 清理前端 Vite 缓存
    if [ -d "$FRONTEND_DIR/node_modules/.vite" ]; then
        rm -rf "$FRONTEND_DIR/node_modules/.vite"
        echo -e "  前端 Vite 编译缓存 ${GREEN}清理成功${NC}"
    else
        echo -e "  前端 Vite 编译缓存 未生成"
    fi
}

start_services() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════╗"
    echo "║       AI 测试平台 - 启动中           ║"
    echo "╚══════════════════════════════════════╝"
    echo -e "${NC}"

    load_env_files

    # 清理残留进程
    local be_pid=$(check_port $BACKEND_PORT)
    local fe_pid=$(check_port $FRONTEND_PORT)
    [ -n "$be_pid" ] && kill -9 $be_pid 2>/dev/null && sleep 1
    [ -n "$fe_pid" ] && kill -9 $fe_pid 2>/dev/null && sleep 1

    # 启动后端
    echo -e "${YELLOW}[1/2] 启动后端...${NC}"
    if [ ! -d "$BACKEND_DIR/.venv" ]; then
        echo -e "${RED}错误: 未找到 backend/.venv，请先创建虚拟环境${NC}"
        echo "  cd $BACKEND_DIR && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
        exit 1
    fi
    cd "$BACKEND_DIR"
    nohup .venv/bin/python run.py > "$LOG_DIR/backend.log" 2>&1 < /dev/null &
    BACKEND_PID=$!

    # 等待后端就绪
    for i in {1..10}; do
        if check_port $BACKEND_PORT > /dev/null 2>&1; then
            echo -e "  后端 ${GREEN}已启动${NC} (PID $BACKEND_PID)"
            break
        fi
        sleep 1
    done
    if ! check_port $BACKEND_PORT > /dev/null 2>&1; then
        echo -e "  后端 ${RED}启动失败${NC}，查看日志: $LOG_DIR/backend.log"
        exit 1
    fi

    if [ -z "${LLM_API_KEY:-}" ] && [ -z "${OPENAI_API_KEY:-}" ]; then
        echo -e "  ${YELLOW}提示:${NC} 未检测到 LLM API Key，Phoenix evaluator 将自动使用 fallback 模式"
    else
        echo -e "  Phoenix evaluator 环境 ${GREEN}已加载${NC}"
    fi

    # 启动前端
    echo -e "${YELLOW}[2/2] 启动前端...${NC}"
    cd "$FRONTEND_DIR"
    nohup npx vite --host 0.0.0.0 --port $FRONTEND_PORT > "$LOG_DIR/frontend.log" 2>&1 < /dev/null &
    FRONTEND_PID=$!

    for i in {1..10}; do
        if check_port $FRONTEND_PORT > /dev/null 2>&1; then
            echo -e "  前端 ${GREEN}已启动${NC} (PID $FRONTEND_PID)"
            break
        fi
        sleep 1
    done
    if ! check_port $FRONTEND_PORT > /dev/null 2>&1; then
        echo -e "  前端 ${RED}启动失败${NC}，查看日志: $LOG_DIR/frontend.log"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         启动成功                     ║${NC}"
    echo -e "${GREEN}║                                      ║${NC}"
    echo -e "${GREEN}║  前端: http://localhost:$FRONTEND_PORT        ║${NC}"
    echo -e "${GREEN}║  后端: http://localhost:$BACKEND_PORT         ║${NC}"
    echo -e "${GREEN}║  文档: http://localhost:$BACKEND_PORT/docs    ║${NC}"
    echo -e "${GREEN}║                                      ║${NC}"
    echo -e "${GREEN}║  日志: $LOG_DIR/   ║${NC}"
    echo -e "${GREEN}║  停止: ./start.sh stop               ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
}

case "${1:-start}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    clean)
        stop_services
        clean_cache
        ;;
    restart)
        stop_services
        sleep 1
        start_services
        ;;
    clean-restart)
        stop_services
        clean_cache
        sleep 1
        start_services
        ;;
    status)
        show_status
        ;;
    *)
        echo "用法: $0 {start|stop|restart|clean|clean-restart|status}"
        exit 1
        ;;
esac
