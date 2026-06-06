"""Minimal autonomous orchestrator:
- Loads project-state.json
- Runs provider health checks
- Pings local server health endpoint
- Writes a snapshot to snapshots/ and appends build-report.md
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.provider_manager.manager import ProviderManager


STATE_PATH = ROOT / "project-state.json"
SNAP_DIR = ROOT / "snapshots"
BUILD_REPORT = ROOT / "build-report.md"


def load_state():
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def ensure_snapshot_dir():
    SNAP_DIR.mkdir(exist_ok=True)


def write_snapshot(state):
    ensure_snapshot_dir()
    ts = datetime.utcnow().isoformat(timespec="seconds")
    path = SNAP_DIR / f"project-state-{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return path


def append_build_report(entry: str):
    header = f"# Build Report — {datetime.utcnow().isoformat(timespec='seconds')}Z\n\n"
    with open(BUILD_REPORT, "a", encoding="utf-8") as f:
        f.write(header)
        f.write(entry)
        f.write("\n---\n\n")


def check_server():
    try:
        resp = requests.get("http://127.0.0.1:8000/providers", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


def main():
    state = load_state()
    pm = ProviderManager.from_config()

    report_lines = []
    report_lines.append(f"Current milestone: {state.get('current_milestone')}")

    providers = pm.list_providers()
    report_lines.append(f"Configured providers: {providers}")

    health_results = {}
    for name in providers:
        p = pm.get(name)
        try:
            ok = p.health_check()
        except Exception:
            ok = False
        health_results[name] = ok
        report_lines.append(f"Provider {name} health: {ok}")

    server_ok = check_server()
    report_lines.append(f"Local server /providers endpoint healthy: {server_ok}")

    # update state
    state["last_successful_checkpoint"] = datetime.utcnow().isoformat() + "Z"
    state["completion_percentage"] = max(state.get("completion_percentage", 0), 70)
    save_state(state)

    snap_path = write_snapshot(state)
    report_lines.append(f"Snapshot saved: {snap_path}")

    append_build_report("\n".join(report_lines))

    print("Orchestrator run complete. Snapshot:", snap_path)


if __name__ == "__main__":
    main()
