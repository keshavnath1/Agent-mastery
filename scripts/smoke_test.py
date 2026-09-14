#!/usr/bin/env python3
"""Run architecture-only smoke checks for a clean template checkout."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    command = [sys.executable, *args]
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    run("scripts/validate_project.py")
    run("scripts/validate_agent_architecture.py")
    run("-m", "unittest", "-v", "tests.architecture.test_agent_workflow")
    print("TEMPLATE SMOKE TEST: PASS")
    print("Boundary: this validates repository machinery only; it executes no SAS or migration implementation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
