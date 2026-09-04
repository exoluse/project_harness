from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from project_harness.schema_validation import SCHEMA_DIR, SCHEMA_FILES

from . import REPO
from .helpers import copy_harness_tree

PACKAGE = REPO / ".harness" / "tooling" / "project_harness"


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _harness(root: Path, *args: str) -> dict:
    result = _run(["scripts/harness.py", *args], cwd=root)
    if result.returncode != 0:
        raise AssertionError(f"harness {' '.join(args)} failed:\n{result.stdout}")
    return json.loads(result.stdout)


class SingleSourceTests(unittest.TestCase):
    """Every file exists once: the harness governs one project, its own."""

    def test_runtime_carries_the_only_copy_of_the_schemas(self):
        self.assertFalse((REPO / "schemas").exists())
        self.assertFalse((PACKAGE / "assets").exists())
        present = {path.name for path in SCHEMA_DIR.glob("*.json")}
        self.assertLessEqual(set(SCHEMA_FILES.values()), present)

    def test_repository_ships_no_project_generator(self):
        # Packaging turned the harness into something that produces other
        # projects; a single-project harness is used by copying the folder.
        self.assertFalse((REPO / "pyproject.toml").exists())
        self.assertNotIn(
            "--project-id",
            (PACKAGE / "cli.py").read_text(encoding="utf-8"),
        )


class CopiedFolderTests(unittest.TestCase):
    """A copy of this repository becomes a project by command only."""

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.root = copy_harness_tree(Path(self._temp.name) / "copy")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def tearDown(self) -> None:
        self._temp.cleanup()

    def test_copy_reports_missing_records_then_initializes_in_place(self):
        self.assertEqual(_harness(self.root, "next")["state"], "NEEDS_INIT")
        runtime_marker = self.root / ".harness" / "tooling" / "project_harness" / "cli.py"
        before = runtime_marker.stat().st_mtime_ns

        result = _run(["scripts/harness.py", "init"], cwd=self.root)

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(_harness(self.root, "next")["state"], "NEEDS_PLAN")
        self.assertEqual(_harness(self.root, "validate")["counts"]["errors"], 0)
        # The runtime already in place is not rewritten over itself.
        self.assertEqual(runtime_marker.stat().st_mtime_ns, before)

    def test_init_names_the_project_after_its_directory(self):
        _run(["scripts/harness.py", "init"], cwd=self.root)

        project = json.loads(
            (self.root / ".harness" / "project.json").read_text(encoding="utf-8")
        )
        state = json.loads(
            (self.root / ".harness" / "state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(project["id"], "PROJECT")
        self.assertEqual(project["name"], "copy")
        self.assertNotIn("project_id", state)
        self.assertEqual(_harness(self.root, "status")["name"], "copy")

    def test_verification_passes_before_any_tests_exist(self):
        _run(["scripts/harness.py", "init"], cwd=self.root)

        for tier in ("fast", "full"):
            result = _run(["scripts/check_repo.py", tier], cwd=self.root)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("[harness-strict] exit=0", result.stdout)
        self.assertIn("[tests-full] SKIPPED", result.stdout)

    def test_project_reaches_a_startable_task_by_command_only(self):
        _run(["scripts/harness.py", "init"], cwd=self.root)
        root = self.root
        self.assertEqual(_harness(root, "next")["state"], "NEEDS_PLAN")

        _harness(root, "new", "plan", "PLAN-0001", "Add login")
        self.assertEqual(_harness(root, "next")["state"], "NEEDS_TASK")

        _harness(
            root,
            "new", "task", "TASK-0001", "Implement login",
            "--plan", "PLAN-0001",
            "--capability", "LOCAL_IMPLEMENTATION",
        )
        step = _harness(root, "next")
        self.assertEqual(step["state"], "NEEDS_PLAN_APPROVAL", step)
        self.assertTrue(any("approval prepare" in command for command in step["commands"]))

        validation = _harness(root, "validate")
        self.assertEqual(validation["counts"]["errors"], 0, validation)
        # The only remaining signal is the traceability warning `next` surfaced.
        self.assertEqual(
            [issue["code"] for issue in validation["issues"]], ["ORPHAN_TASK"]
        )
        self.assertTrue(any("ORPHAN_TASK" in value for value in step["warnings"]))


if __name__ == "__main__":
    unittest.main()
