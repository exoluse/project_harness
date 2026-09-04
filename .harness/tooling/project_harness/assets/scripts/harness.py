from pathlib import Path
import sys

# The harness runtime lives inside the project it governs.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".harness" / "tooling"))

from project_harness.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
