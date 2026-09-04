"""Return a repository to the state it had before ``init``.

``init`` is what turns a copied harness into a project: it writes the canonical
project record, the lifecycle state, the record directories, and the handoff
placeholder.  A reset removes exactly that, so what is left is the harness a
copied folder carries before it governs anything.  ``next`` reports
``NEEDS_INIT`` afterwards, and ``init`` starts the next project — under a new
name when ``--name`` says so, since nothing survives to insist on the old one.

The reset is defined by construction rather than by a hand-maintained list of
things to undo: it removes what ``init`` owns, so a field added to a fresh
harness cannot drift away from what a reset clears.

Files ``init`` does not create are never touched.  A project's own sources and
its extended ``.gitignore`` are not harness bookkeeping, and deleting them to
make a tree look freshly copied would destroy the project instead of resetting
it.  Two things ``init`` does create also outlive a reset, each for its own
reason: the generated bookkeeping files, because ``init`` writes them only when
absent and an operator may have extended or filled them in, and the human
decision ledger, whose reason is recorded with ``PRESERVED_RUNTIME`` below.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .collaboration import runtime_root
from .constants import HARNESS_DIR
from .core import HarnessError, atomic_write_json, load_json, utc_now
from .scaffold import project_directories


# The canonical files that make a repository a project rather than a copy of
# the harness.  Removing them is what returns the tree to ``NEEDS_INIT``.
IDENTITY_FILES = (
    f"{HARNESS_DIR}/project.json",
    f"{HARNESS_DIR}/state.json",
    "HANDOFF.md",
)

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


def _project_directories(root: Path) -> list[Path]:
    return [path for path in project_directories(root / HARNESS_DIR) if path.is_dir()]


def _record_files(root: Path) -> list[Path]:
    """Canonical records and project history, in stable order."""

    paths: list[Path] = []
    for directory in _project_directories(root):
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.name != ".gitkeep":
                paths.append(path)
    return paths


def _identity_files(root: Path) -> list[Path]:
    """The canonical files that identify the project, in stable order."""

    return [path for relative in IDENTITY_FILES if (path := root / relative).is_file()]


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
    """Remove the project this harness governs and leave the harness itself."""

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
    identity = _identity_files(root)
    removable = records + identity
    directories = _project_directories(root)
    runtime = _clearable_runtime(root)
    summary: dict[str, Any] = {
        "name": name,
        "root": str(root),
        "dry_run": dry_run,
        "removed_records": [_relative(root, path) for path in records],
        "removed_identity": [_relative(root, path) for path in identity],
        "removed_directories": [_relative(root, path) for path in directories],
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
            "reset removes this project's harness records and identity, and cannot "
            f"be undone from Git alone; re-run it as: reset --confirm {token}"
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
            "name": name,
            "removed_records": summary["removed_records"],
            "removed_identity": summary["removed_identity"],
            "removed_directories": summary["removed_directories"],
            "cleared_runtime": summary["cleared_runtime"],
            "preserved_runtime": summary["preserved_runtime"],
        },
    )

    for path in removable:
        path.unlink()
    # The directories go too, placeholders and all: ``init`` creates them, so a
    # reset that left them behind would stop short of the state it restores.
    for path in directories:
        shutil.rmtree(path)
    for path in runtime:
        shutil.rmtree(path)

    summary["snapshot"] = _relative(root, snapshot)
    summary["next_command"] = "python scripts/harness.py init"
    return summary
