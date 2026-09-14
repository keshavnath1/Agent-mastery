#!/usr/bin/env python3
"""Agent-owned deterministic helpers for the reusable SAS migration template."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "artifacts" / "run_state"


def run(script: str, *args: str) -> int:
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], cwd=ROOT).returncode


def state_files() -> list[Path]:
    return sorted(STATE_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)


def status() -> int:
    files = state_files()
    if not files:
        print("Project status: CLEAN_TEMPLATE")
        print("No active module or durable run state exists.")
        print("Copilot next step: /start-migration new <MODULE-ID>")
        return 0
    print(files[0].read_text(encoding="utf-8"))
    return 0


def start(module: str) -> int:
    """Create intake-ready state when invoked by the authorized orchestration flow."""
    manifest = ROOT / "artifacts" / "evidence" / "intake_manifest.json"
    if not manifest.is_file():
        print("Cannot start: the intake skill must create and validate the intake manifest first.", file=sys.stderr)
        return 2
    intake = json.loads(manifest.read_text(encoding="utf-8"))
    if intake.get("file_count", 0) == 0:
        print("Cannot start: intake manifest contains no source files.", file=sys.stderr)
        return 2
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{module}"
    state = {
        "run_id": run_id,
        "module_id": module,
        "stage": "interview",
        "status": "READY",
        "attempts": 0,
        "history": [
            {
                "stage": "intake",
                "status": "PASS",
                "manifest": manifest.relative_to(ROOT).as_posix(),
            }
        ],
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = STATE_DIR / f"{run_id}.json"
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(f"Created {path.relative_to(ROOT)}")
    print("Next permitted skill: interview")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="SAS migration template helper")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("smoke")
    sub.add_parser("intake")
    sub.add_parser("status")
    start_parser = sub.add_parser("start")
    start_parser.add_argument("--module", required=True, help="Explicit neutral module identifier")
    tieout_parser = sub.add_parser("tieout")
    tieout_parser.add_argument("--run-id", required=True, help="Existing durable run identifier")
    tieout_parser.add_argument("--attempt-id", required=True, help="Append-only validation attempt identifier")
    tieout_parser.add_argument("--contract", default="config/tieout.yaml", help="Repository-relative approved contract")
    args = parser.parse_args()

    if args.command == "validate":
        return run("validate_project.py")
    if args.command == "smoke":
        return run("smoke_test.py")
    if args.command == "intake":
        return run("intake.py")
    if args.command == "status":
        return status()
    if args.command == "start":
        return start(args.module)
    if args.command == "tieout":
        return run("run_tieout.py", "--contract", args.contract, "--run-id", args.run_id, "--attempt-id", args.attempt_id)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
