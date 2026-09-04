from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLING = ROOT / ".harness" / "tooling"

COMPILE_CANDIDATES = (".harness/tooling", "src", "scripts", "tests")


def run(label: str, command: list[str]) -> bool:
    print(f"\n[{label}] {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT, check=False)
    print(f"[{label}] exit={result.returncode}")
    return result.returncode == 0


def skip(label: str, reason: str) -> bool:
    print(f"\n[{label}] SKIPPED: {reason}")
    return True


def _discover(tests: Path, top: Path | None) -> list[str] | None:
    if not tests.is_dir() or not any(tests.rglob("test_*.py")):
        return None
    command = [sys.executable, "-m", "unittest", "discover", "-s", str(tests.relative_to(ROOT))]
    if top is not None and (tests / "__init__.py").is_file():
        command += ["-t", str(top.relative_to(ROOT))]
    return command + ["-p", "test_*.py", "-v"]


def checks_for(tier: str, self_test: bool) -> list[tuple[str, list[str] | None]]:
    compile_targets = [name for name in COMPILE_CANDIDATES if (ROOT / name).exists()]
    checks: list[tuple[str, list[str] | None]] = [
        ("compile", [sys.executable, "-m", "compileall", "-q", *compile_targets]),
    ]
    if tier == "full":
        # The project's own tests; the harness self-tests only when asked, so a
        # project's verification is about the project.
        checks.append(("tests-full", _discover(ROOT / "tests", ROOT)))
        if self_test:
            checks.append(("harness-self-test", _discover(TOOLING / "tests", TOOLING)))
    if (ROOT / ".harness" / "project.json").is_file():
        checks.append(
            ("harness-strict", [sys.executable, "scripts/harness.py", "validate", "--strict"])
        )
    else:
        checks.append(("harness-strict", None))
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
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="also run the harness runtime's own tests under .harness/tooling/tests",
    )
    args = parser.parse_args(argv)
    print(f"[check-repo] tier={args.tier}")
    outcomes = [
        run(label, command)
        if command is not None
        else skip(
            label,
            "no harness records yet; run `scripts/harness.py init`"
            if label == "harness-strict"
            else "no test modules found",
        )
        for label, command in checks_for(args.tier, args.self_test)
    ]
    return 0 if all(outcomes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
