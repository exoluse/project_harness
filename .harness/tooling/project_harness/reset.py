"""Return a harness to the exact shape ``init`` produces.

The reset is defined by construction rather than by a hand-maintained list of
things to undo: it clears everything ``init`` owns and then re-runs ``init``
itself.  A field added to a fresh harness therefore cannot drift away from what
a reset restores.

Files ``init`` does not create are never touched.  A project's own sources, its
extended ``.gitignore``, and its filled-in authority template are not harness
bookkeeping, and deleting them to make a tree look freshly generated would
destroy the project instead of resetting it.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .collaboration import runtime_root
from .constants import HARNESS_DIR, RECORD_DIRECTORIES
from .core import HarnessError, atomic_write_json, load_json, utc_now
from .scaffold import fresh_project_record, fresh_state_record, init_project


# Directories whose whole contents are project history rather than structure.
HISTORY_DIRECTORIES = ("events", "baselines", "decisions")

# Canonical files that ``init`` regenerates once they are absent.
REGENERATED_FILES = (f"{HARNESS_DIR}/project.json", f"{HARNESS_DIR}/state.json", "HANDOFF.md")

# Shared runtime registries describing in-flight coordination and record
# numbering.  They are rebuilt on demand, so clearing them is what makes the
# next record start at 0001 again.
CLEARED_RUNTIME = ("leases", "mailboxes", "mutations", "id-sequences")

# The human decision ledger is deliberately not cleared.  Its monotonic sequence
# and latest-decision markers are what make a recorded human confirmation
# non-replayable, and a reset is reachable by an agent.  A control that bounds
# human authority must not be resettable by the party it bounds.
PRESERVED_RUNTIME = ("human-decisions",)

SNAPSHOT_PREFIX = "reset-"


def _snapshot_root(root: Path) -> Path:
    return root / HARNESS_DIR / "runtime"


def _record_files(root: Path) -> list[Path]:
    """Canonical records and project history, in stable order."""

    harness = root / HARNESS_DIR
    paths: list[Path] = []
    for directory, _prefix in sorted(RECORD_DIRECTORIES.values()):
        for path in sorted((harness / directory).glob("*")):
            if path.is_file() and path.name != ".gitkeep":
                paths.append(path)
    for directory in HISTORY_DIRECTORIES:
        for path in sorted((harness / directory).rglob("*")):
            if path.is_file():
                paths.append(path)
    return paths


def _regenerated_files(root: Path) -> list[Path]:
    """Canonical files that are rewritten rather than left behind."""

    return [path for relative in REGENERATED_FILES if (path := root / relative).is_file()]


def _clearable_runtime(root: Path) -> list[Path]:
    runtime = runtime_root(root)
    return [
        candidate
        for name in CLEARED_RUNTIME
        if (candidate := runtime / name).is_dir()
    ]


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def reset_project(
    root: Path,
    *,
    confirm: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Clear the harness ledger and regenerate it exactly as ``init`` would."""

    root = root.resolve()
    project_path = root / HARNESS_DIR / "project.json"
    if not project_path.is_file():
        raise HarnessError(
            f"No project harness to reset at {root}: {project_path} is missing"
        )
    project = load_json(project_path)
    name = project.get("name")
    if not isinstance(name, str) or not name:
        raise HarnessError("Canonical project record has no usable name")
    # One harness governs one project, so the directory it lives in is the
    # thing an operator must name to prove which tree they meant to clear.
    token = root.name

    records = _record_files(root)
    regenerated = _regenerated_files(root)
    removable = records + regenerated
    runtime = _clearable_runtime(root)
    summary: dict[str, Any] = {
        "name": name,
        "root": str(root),
        "dry_run": dry_run,
        "removed_records": [_relative(root, path) for path in records],
        "regenerated": [_relative(root, path) for path in regenerated],
        "cleared_runtime": [path.name for path in runtime],
        "preserved_runtime": list(PRESERVED_RUNTIME),
        "snapshot": None,
    }
    if dry_run:
        summary["confirm_command"] = (
            f"python scripts/harness.py reset --confirm {token}"
        )
        return summary

    if confirm != token:
        raise HarnessError(
            "reset rewrites this project's harness records and cannot be undone "
            f"from Git alone; re-run it as: reset --confirm {token}"
        )

    # Second-resolution timestamps collide when a reset is repeated quickly, and
    # a snapshot that merges into an earlier one is not a recoverable snapshot.
    stamp = utc_now().replace(":", "")
    snapshot = _snapshot_root(root) / f"{SNAPSHOT_PREFIX}{stamp}"
    for attempt in range(2, 100):
        if not snapshot.exists():
            break
        snapshot = _snapshot_root(root) / f"{SNAPSHOT_PREFIX}{stamp}-{attempt}"
    else:
        raise HarnessError(f"Unable to allocate a reset snapshot directory at {stamp}")
    for path in removable:
        target = snapshot / "tree" / _relative(root, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    for path in runtime:
        shutil.copytree(path, snapshot / "runtime" / path.name, dirs_exist_ok=True)
    atomic_write_json(
        snapshot / "reset.json",
        {
            "schema": "harness.reset/v1",
            "root": str(root),
            "reset_at": utc_now(),
            "removed_records": summary["removed_records"],
            "regenerated": summary["regenerated"],
            "cleared_runtime": summary["cleared_runtime"],
            "preserved_runtime": summary["preserved_runtime"],
        },
    )

    for path in removable:
        path.unlink()
    for path in runtime:
        shutil.rmtree(path)

    # The canonical records come from the same builders ``init`` uses, so a
    # field added to a fresh harness cannot drift away from what a reset
    # restores.  ``init --force`` then repairs the rest of the structure:
    # record directories, their .gitkeep placeholders, the handoff placeholder,
    # and the templates the deletions removed.
    created = utc_now()
    atomic_write_json(project_path, fresh_project_record(name, created))
    atomic_write_json(root / HARNESS_DIR / "state.json", fresh_state_record(created))
    init_project(root, name, force=True)

    summary["snapshot"] = _relative(root, snapshot)
    return summary
