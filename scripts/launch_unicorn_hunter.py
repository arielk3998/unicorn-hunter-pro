"""Launcher for The Unicorn Hunter desktop application.

Features:
- Optional start of FastAPI backend (for API-dependent GUI features) on a dynamic free port.
- Launches the Tkinter GUI.
- Opens a browser tab pointing to the API root if server started.

Usage:
  python scripts/launch_unicorn_hunter.py            # GUI only
  python scripts/launch_unicorn_hunter.py --api      # Start API + GUI
  python scripts/launch_unicorn_hunter.py --api --port 8090  # Specify port

The script will fall back gracefully if a chosen port is unavailable.
"""
from __future__ import annotations

import argparse
import contextlib
import os
import socket
import subprocess
import sys
import time
import webbrowser

from pathlib import Path

# Relative path to GUI entry point
GUI_SCRIPT = Path(__file__).parent.parent / "unicorn_hunter_gui.py"
API_APP_IMPORT = "app.presentation.api.main:app"


def find_free_port(preferred: int | None = None) -> int:
    """Return a free TCP port. If preferred given, try it first."""
    if preferred is not None:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.bind(("127.0.0.1", preferred))
                return preferred
            except OSError:
                pass  # fall through to dynamic selection
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return int(s.getsockname()[1])


def start_api(port: int) -> subprocess.Popen:
    """Start the FastAPI server via uvicorn on given port; return process handle."""
    python_exe = sys.executable
    cmd = [
        python_exe,
        "-m",
        "uvicorn",
        API_APP_IMPORT,
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--log-level",
        "info",
    ]
    # Use creationflags to keep separate window minimal (Windows only)
    creationflags = 0
    if os.name == "nt":  # Avoid spawning new console window if not needed
        creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc


def wait_for_api(port: int, timeout: float = 10.0) -> bool:
    """Poll until API port responds or timeout reached."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(0.5)
            try:
                s.connect(("127.0.0.1", port))
                return True
            except OSError:
                time.sleep(0.3)
    return False


def launch_gui():
    """Run the Tkinter GUI script in the current process."""
    # Execute via runpy to avoid changing cwd; simpler: exec file contents
    with open(GUI_SCRIPT, "r", encoding="utf-8") as f:
        code = f.read()
    globals_dict = {"__name__": "__main__", "__file__": str(GUI_SCRIPT)}
    exec(code, globals_dict)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Launcher for The Unicorn Hunter desktop app")
    p.add_argument("--api", action="store_true", help="Start FastAPI backend before launching GUI")
    p.add_argument("--port", type=int, default=None, help="Preferred API port (optional)")
    p.add_argument("--browser", action="store_true", help="Open browser to API root after start")
    return p.parse_args()


def main():
    args = parse_args()

    api_proc = None
    api_port = None

    if args.api:
        api_port = find_free_port(args.port)
        print(f"[launcher] Starting API server on 127.0.0.1:{api_port} ...")
        api_proc = start_api(api_port)
        if wait_for_api(api_port):
            print(f"[launcher] API server ready at http://127.0.0.1:{api_port}/")
            if args.browser:
                webbrowser.open_new_tab(f"http://127.0.0.1:{api_port}/")
        else:
            print("[launcher] WARNING: API server did not become ready before timeout.")

    try:
        print("[launcher] Launching GUI ...")
        launch_gui()
    finally:
        if api_proc:
            print("[launcher] Shutting down API server ...")
            api_proc.terminate()
            with contextlib.suppress(Exception):
                api_proc.wait(timeout=5)


if __name__ == "__main__":
    main()
