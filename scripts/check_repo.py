from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str]) -> bool:
    print(f"\n[{label}] {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT, check=False)
    print(f"[{label}] exit={result.returncode}")
    return result.returncode == 0


def main() -> int:
    checks = [
        ("compile", [sys.executable, "-m", "compileall", "-q", "src", "scripts", "tests"]),
        (
            "tests",
            [sys.executable, "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-v"],
        ),
        ("harness", [sys.executable, "scripts/harness.py", "validate", "--strict"]),
    ]
    passed = all(run(label, command) for label, command in checks)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
