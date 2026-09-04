from pathlib import Path
import sys


# The harness self-tests live beside the runtime they exercise.
TOOLING = Path(__file__).resolve().parents[1]
REPO = TOOLING.parents[1]
sys.path.insert(0, str(TOOLING))
