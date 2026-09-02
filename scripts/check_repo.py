from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAST_TEST_MODULES = [
    "tests.test_fingerprints",
    "tests.test_reporting",
    "tests.test_mutations",
]


def run(label: str, command: list[str]) -> bool:
    print(f"\n[{label}] {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT, check=False)
    print(f"[{label}] exit={result.returncode}")
    return result.returncode == 0


def checks_for(tier: str) -> list[tuple[str, list[str]]]:
    checks: list[tuple[str, list[str]]] = [
        ("compile", [sys.executable, "-m", "compileall", "-q", "src", "scripts", "tests"]),
    ]
    if tier == "fast":
        checks.append(
            (
                "tests-fast",
                [sys.executable, "-m", "unittest", *FAST_TEST_MODULES, "-v"],
            )
        )
    else:
        checks.append(
            (
                "tests-full",
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    ".",
                    "-p",
                    "test_*.py",
                    "-v",
                ],
            )
        )
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
            "fast runs contract-focused tests; full runs the entire suite "
            "(default, equivalent to omitting the tier)"
        ),
    )
    args = parser.parse_args(argv)
    print(f"[check-repo] tier={args.tier}")
    outcomes = [run(label, command) for label, command in checks_for(args.tier)]
    return 0 if all(outcomes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
