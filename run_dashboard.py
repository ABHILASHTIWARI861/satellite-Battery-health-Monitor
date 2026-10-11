"""
Launch Script for Satellite Mission Control Web Dashboard
Runs FastAPI + Uvicorn server hosting real-time WebSocket telemetry stream.
"""

import uvicorn
import webbrowser
import threading
import time
import argparse
import os


def open_browser(url: str, delay: float = 1.5):
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Satellite HITL Mission Control Dashboard Launcher")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host IP")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")
    parser.add_argument("--reload", action="store_true", help="Enable development auto-reload (off by default for stable simulator connections)")
    parser.add_argument("--hitl-port", type=str, default="AUTO",
                        help="Arduino serial port: 'VIRTUAL' (no hardware / simulator), 'AUTO' (detect), or e.g. 'COM3'")
    args = parser.parse_args()
    os.environ["HITL_PORT"] = args.hitl_port

    url = f"http://{args.host}:{args.port}"
    print("=" * 65)
    print(" [*] AERO-GUARD SATELLITE TELEMETRY HITL MISSION CONTROL DASHBOARD ")
    print("=" * 65)
    print(f" Dashboard URL: {url}")
    print(f" HITL Arduino port: {args.hitl_port}")
    print(f" Real-time WebSocket: ws://127.0.0.1:{args.port}/ws/telemetry")
    print(" Simulator UI: /arduino-simulator")
    print("=" * 65)

    if not args.no_browser:
        threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    uvicorn.run("src.dashboard.app:app", host=args.host, port=args.port, reload=args.reload, ws="websockets")


if __name__ == "__main__":
    main()
