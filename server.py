#!/usr/bin/env python3
"""Simple HTTP dashboard server for zemail sync monitoring."""

import json
import os
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configurable paths — set ZEMAIL_DATA_DIR env var to override
ZEMAIL_DATA = Path(os.environ.get("ZEMAIL_DATA_DIR", "/home/dev/.zemail"))
DASHBOARD_DIR = Path(__file__).parent
STATE_FILE = ZEMAIL_DATA / "full_sync_state.json"
LOG_FILE_V1 = ZEMAIL_DATA / "full_sync.log"
LOG_FILE_V2 = ZEMAIL_DATA / "full_sync_v2.log"
PID_FILE_V1 = ZEMAIL_DATA / "full_sync.pid"
PID_FILE_V2 = ZEMAIL_DATA / "full_sync_v2.pid"


def get_active_log_file() -> Path:
    """Return the most recently modified log file."""
    v2_exists = LOG_FILE_V2.exists()
    v1_exists = LOG_FILE_V1.exists()
    
    if v2_exists and v1_exists:
        return LOG_FILE_V2 if LOG_FILE_V2.stat().st_mtime > LOG_FILE_V1.stat().st_mtime else LOG_FILE_V1
    elif v2_exists:
        return LOG_FILE_V2
    elif v1_exists:
        return LOG_FILE_V1
    return LOG_FILE_V2  # Default to v2


def get_active_pid_file() -> Path:
    """Return the PID file for the active sync process."""
    v2_exists = PID_FILE_V2.exists()
    v1_exists = PID_FILE_V1.exists()
    
    if v2_exists and v1_exists:
        return PID_FILE_V2 if PID_FILE_V2.stat().st_mtime > PID_FILE_V1.stat().st_mtime else PID_FILE_V1
    elif v2_exists:
        return PID_FILE_V2
    elif v1_exists:
        return PID_FILE_V1
    return PID_FILE_V2  # Default to v2


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.serve_file(DASHBOARD_DIR / "index.html", "text/html")
        elif self.path == "/api/status":
            self.serve_status()
        else:
            self.send_error(404)

    def serve_file(self, filepath, content_type):
        try:
            content = filepath.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)

    def serve_status(self):
        status = {
            "indexed": 0,
            "accountTotal": 0,
            "batches": 0,
            "pages": 0,
            "running": False,
            "pid": None,
            "lastActivity": None,
            "logs": [],
        }

        # Read state file
        if STATE_FILE.exists():
            try:
                state = json.loads(STATE_FILE.read_text())
                status["batches"] = state.get("batches_seen", 0)
                status["pages"] = state.get("pages_seen", 0)
                status["lastActivity"] = state.get("last_completed_at")
            except Exception:
                pass

        # Check if process is running
        pid_file = get_active_pid_file()
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip().split()[0])
                status["pid"] = pid
                # Check if process exists
                os.kill(pid, 0)
                status["running"] = True
            except (OSError, ValueError, ProcessLookupError):
                status["running"] = False

        # Get indexed count from zemail
        try:
            result = subprocess.run(
                ["uv", "run", "python", "-c",
                 "from zemail.server import index_status; print(index_status())"],
                capture_output=True, text=True, cwd="/home/dev/zemail",
                env=os.environ
            )
            output = result.stdout.strip()
            # Parse "Email index: N emails indexed"
            if "emails indexed" in output:
                parts = output.split("emails indexed")
                num_part = parts[0].split(":")[-1].strip()
                status["indexed"] = int(num_part)
        except Exception as e:
            status["indexed_error"] = str(e)

        # Get account total from log
        log_file = get_active_log_file()
        if log_file.exists():
            try:
                lines = log_file.read_text().splitlines()
                for line in lines:
                    if "account total:" in line:
                        parts = line.split("account total:")[1].split("messages")[0].strip()
                        status["accountTotal"] = int(parts.replace(",", ""))
                        break
                # Get last 30 log lines
                status["logs"] = lines[-30:]
            except Exception:
                pass

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())


def main():
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    host = "0.0.0.0"  # Bind to all interfaces for Tailscale access

    server = HTTPServer((host, port), DashboardHandler)
    print(f"Zemail dashboard server running on http://{host}:{port}")
    print(f"Tailscale access: http://100.106.122.86:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
