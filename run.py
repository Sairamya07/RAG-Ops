"""
KnowRAG — Unified Application & RAG-Ops Runner
------------------------------------------------
Single startup command entrypoint that orchestrates:
1. KnowRAG FastAPI Health Check & Operations Service (Port 8000)
2. KnowRAG Streamlit Interactive Knowledge Assistant Web UI (Port 8501)

Usage:
    python run.py             # Start both Health API and Streamlit UI (Default)
    python run.py --api-only  # Start only the FastAPI Health API
    python run.py --ui-only   # Start only the Streamlit Web Application
"""

import argparse
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load environment securely if available
from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a network port is already open and bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def run_health_api(host: str, port: int):
    """Run the FastAPI health check service with uvicorn."""
    import uvicorn
    from health_api import app as fastapi_app

    print(f"[RAG-Ops API] Starting health API server at http://{host}:{port} ...")
    uvicorn.run(fastapi_app, host=host, port=port, log_level="info")


def main():
    parser = argparse.ArgumentParser(description="KnowRAG Unified Runner")
    parser.add_argument(
        "--api-only", action="store_true", help="Launch only the FastAPI Health service"
    )
    parser.add_argument(
        "--ui-only", action="store_true", help="Launch only the Streamlit Web application"
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=int(os.getenv("API_PORT", 8000)),
        help="Port for the Health API (default: 8000)",
    )
    parser.add_argument(
        "--ui-port",
        type=int,
        default=int(os.getenv("STREAMLIT_PORT", 8501)),
        help="Port for the Streamlit UI (default: 8501)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("API_HOST", "0.0.0.0"),
        help="Host binding (default: 0.0.0.0)",
    )

    args = parser.parse_args()

    print("=" * 65)
    print("  🚀 Starting KnowRAG — AI-Powered Knowledge Assistant & RAG-Ops")
    print("=" * 65)

    if args.ui_only:
        print(f"[KnowRAG UI] Launching Streamlit web application on port {args.ui_port}...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(PROJECT_ROOT / "app.py"),
                "--server.port",
                str(args.ui_port),
                "--server.address",
                args.host,
            ],
            check=True,
        )
        return

    if args.api_only:
        run_health_api(args.host, args.api_port)
        return

    # Default mode: Launch BOTH Health API and Streamlit UI
    if is_port_in_use(args.api_port):
        print(
            f"[RAG-Ops API] Port {args.api_port} is already active (Health API is available)."
        )
    else:
        api_thread = threading.Thread(
            target=run_health_api,
            args=(args.host, args.api_port),
            daemon=True,
        )
        api_thread.start()
        time.sleep(1.0)

    print(f"[KnowRAG UI] Starting Streamlit interface on http://localhost:{args.ui_port} ...")
    print(f"[RAG-Ops] Health Check available at http://localhost:{args.api_port}/health")
    print("=" * 65)

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(PROJECT_ROOT / "app.py"),
                "--server.port",
                str(args.ui_port),
                "--server.address",
                args.host,
            ],
            check=True,
        )
    except KeyboardInterrupt:
        print("\n[KnowRAG] Services shut down gracefully.")


if __name__ == "__main__":
    main()
