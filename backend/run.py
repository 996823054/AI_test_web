#!/usr/bin/env python3
"""
启动脚本
========

启动方式:
    python run.py              # 开发模式（自动重载）
    python run.py --prod       # 生产模式
    python run.py --init-db    # 仅初始化数据库
"""

import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="AI 自动化测试平台")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8000, help="监听端口")
    parser.add_argument("--prod", action="store_true", help="生产模式")
    parser.add_argument("--init-db", action="store_true", help="仅初始化数据库")

    args = parser.parse_args()

    if args.init_db:
        from app.database import init_db
        init_db()
        print("✅ 数据库初始化完成")
        return

    print(f"""
╔══════════════════════════════════════════════╗
║        🔬 AI 自动化测试平台                   ║
║                                              ║
║   地址: http://{args.host}:{args.port}              ║
║   文档: http://{args.host}:{args.port}/docs         ║
║   模式: {'生产' if args.prod else '开发'}                            ║
╚══════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=not args.prod,
        log_level="info",
    )


if __name__ == "__main__":
    main()

