from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

# A generated project carries its pinned runtime under .harness/tooling; the
# distribution's own checkout runs from src.  The vendored runtime wins when
# both exist so a project always runs the tooling it was initialized with.
for candidate in (ROOT / ".harness" / "tooling", ROOT / "src"):
    if (candidate / "project_harness").is_dir():
        sys.path.insert(0, str(candidate))
        break

from project_harness.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
