"""
run.py
------
Uvicorn entry point for AgriSmart AI backend.

Usage:
    python run.py                   # dev mode (auto-reload, port 8000)
    python run.py --port 8080       # custom port
    python run.py --no-reload       # disable auto-reload (staging / CI)

Environment variables (set in .env or shell):
    HOST        bind host      (default: 0.0.0.0)
    PORT        bind port      (default: 8000)
    WORKERS     worker count   (default: 1 for dev, set higher in production)
"""

from __future__ import annotations

import argparse
import os

import uvicorn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AgriSmart AI — FastAPI backend server")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"), help="Bind host")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")), help="Bind port")
    parser.add_argument(
        "--no-reload",
        action="store_true",
        default=False,
        help="Disable auto-reload (use in production / CI)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("WORKERS", "1")),
        help="Number of Uvicorn worker processes (use > 1 in production)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    reload = not args.no_reload

    print(f"\n🌱 AgriSmart AI Backend")
    print(f"   Host    : {args.host}")
    print(f"   Port    : {args.port}")
    print(f"   Reload  : {reload}")
    print(f"   Workers : {args.workers}")
    print(f"   Docs    : http://localhost:{args.port}/docs\n")

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=reload,
        workers=1 if reload else args.workers,  # reload requires single worker
        log_level="debug" if reload else "info",
        access_log=True,
    )
