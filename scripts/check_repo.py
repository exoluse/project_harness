from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# The same script serves this distribution's source checkout and every
# generated project, so it compiles whichever layout is present.
COMPILE_CANDIDATES = ("src", ".harness/tooling", "scripts", "tests")


def run(label: str, command: list[str]) -> bool:
    print(f"\n[{label}] {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT, check=False)
    print(f"[{label}] exit={result.returncode}")
    return result.returncode == 0


def skip(label: str, reason: str) -> bool:
    print(f"\n[{label}] SKIPPED: {reason}")
    return True


def _test_command() -> list[str] | None:
    tests = ROOT / "tests"
    if not tests.is_dir() or not any(tests.rglob("test_*.py")):
        return None
    discover = ["-s", "tests", "-p", "test_*.py", "-v"]
    if (tests / "__init__.py").is_file():
        discover = ["-s", "tests", "-t", ".", "-p", "test_*.py", "-v"]
    return [sys.executable, "-m", "unittest", "discover", *discover]


def checks_for(tier: str) -> list[tuple[str, list[str] | None]]:
    compile_targets = [name for name in COMPILE_CANDIDATES if (ROOT / name).exists()]
    checks: list[tuple[str, list[str] | None]] = [
        ("compile", [sys.executable, "-m", "compileall", "-q", *compile_targets]),
    ]
    if tier == "full":
        checks.append(("tests-full", _test_command()))
    checks.append(
        ("harness-strict", [sys.executable, "scripts/harness.py", "validate", "--strict"])
    )
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run fixed repository verification")
    parser.add_argument(
        "tier",
        nargs="?",
        choices=("fast", "full"),
        default="full",
        help=(
            "fast compiles and runs strict harness validation; full also runs "
            "the test suite (default, equivalent to omitting the tier)"
        ),
    )
    args = parser.parse_args(argv)
    print(f"[check-repo] tier={args.tier}")
    outcomes = [
        run(label, command)
        if command is not None
        else skip(label, "no test modules under tests/")
        for label, command in checks_for(args.tier)
    ]
    return 0 if all(outcomes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
