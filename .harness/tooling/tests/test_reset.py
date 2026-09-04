from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from project_harness.core import HarnessError, load_json
from project_harness.guidance import next_step
from project_harness.reset import PRESERVED_RUNTIME, reset_project
from project_harness.scaffold import init_project
from project_harness.validation import issue_counts, validate_project

from . import REPO
from .helpers import HARNESS_GUIDANCE, init_harness


# Files ``init`` generates that a reset leaves behind.  It writes each of them
# only when absent, so an operator may have extended or filled one in, and
# removing them would take a hand-written file with the project.
SURVIVING_INIT_FILES = {
    ".gitignore",
    ".harness/.gitattributes",
    ".harness/.gitignore",
    ".harness/templates/allowed_signers.example",
    ".harness/templates/authority-config.example.json",
}


def tree(root: Path, *, skip_runtime: bool = True) -> dict[str, bytes]:
    """Every file a project carries, keyed by repository-relative path."""

    contents: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if skip_runtime and relative.startswith(".harness/runtime/"):
            continue
        contents[relative] = path.read_bytes()
    return contents


class ResetTests(unittest.TestCase):
    def _project(self, temp: Path, name: str = "used") -> Path:
        return init_harness(temp / name)

    def _copied_harness(self, path: Path) -> Path:
        """A folder carrying the harness, before any command makes it a project."""

        path.mkdir(parents=True, exist_ok=True)
        for name in HARNESS_GUIDANCE:
            (path / name).write_text(
                (REPO / name).read_text(encoding="utf-8"), encoding="utf-8"
            )
        return path

    def _populate(self, root: Path) -> list[Path]:
        """Write records across every shape a reset has to clear."""

        from project_harness.authoring import create_work_item
        from project_harness.core import atomic_write_json, record_path
        from project_harness.scaffold import new_record

        created: list[Path] = []
        for kind, record_id in (
            ("plan", "PLAN-0001"),
            ("source", "SRC-0001"),
            ("requirement", "REQ-0001"),
            ("open_item", "OI-0001"),
        ):
            path = record_path(root, kind, record_id)
            atomic_write_json(path, new_record(kind, record_id, "Something"))
            created.append(path)
        create_work_item(
            root, task_id="TASK-0001", title="Task", plan_id="PLAN-0001", agent="tester"
        )
        created.append(record_path(root, "work_item", "TASK-0001"))
        return created

    def test_reset_returns_the_tree_to_its_pre_init_state(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._copied_harness(Path(temp) / "used")
            before = tree(root)
            init_harness(root)
            self._populate(root)

            reset_project(root, confirm="used")

            after = tree(root)
            # A reset undoes `init`, so the only files it may leave behind are
            # the generated ones it deliberately does not reclaim.
            self.assertEqual(set(after) - set(before), SURVIVING_INIT_FILES)
            for relative, content in before.items():
                self.assertEqual(after[relative], content, relative)

    def test_reset_leaves_a_harness_that_needs_init(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._project(Path(temp))
            self._populate(root)

            summary = reset_project(root, confirm="used")

            for relative in (
                ".harness/project.json",
                ".harness/state.json",
                "HANDOFF.md",
            ):
                self.assertFalse((root / relative).exists(), relative)
            self.assertIn(".harness/plans", summary["removed_directories"])
            for relative in summary["removed_directories"]:
                self.assertFalse((root / relative).exists(), relative)
            self.assertEqual(next_step(root)["state"], "NEEDS_INIT")

    def test_reset_lets_init_name_the_next_project(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._project(Path(temp))
            self._populate(root)

            reset_project(root, confirm="used")

            # The authority template outlives the reset, and it is a `.json`
            # under `.harness/`: initializing again has to see it for what it
            # is rather than mistake it for an orphaned record.
            template = root / ".harness" / "templates" / "authority-config.example.json"
            self.assertTrue(template.is_file())

            init_project(root, "Renamed")

            project = load_json(root / ".harness" / "project.json")
            state = load_json(root / ".harness" / "state.json")
            self.assertEqual(project["name"], "Renamed")
            self.assertEqual(state["lifecycle_state"], "DISCOVERY")
            self.assertIsNone(state["current_plan"])
            self.assertIsNone(state["active_plan"])
            counts = issue_counts(validate_project(root))
            self.assertEqual(counts["errors"], 0)
            self.assertEqual(counts["warnings"], 0)

    def test_reset_leaves_files_init_does_not_create(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._project(Path(temp))
            self._populate(root)
            source = root / "src" / "app.py"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("print('hello')\n", encoding="utf-8")
            extended = root / ".gitignore"
            extended.write_text("__pycache__/\nbuild/\n", encoding="utf-8")

            reset_project(root, confirm="used")

            self.assertEqual(source.read_text(encoding="utf-8"), "print('hello')\n")
            self.assertEqual(extended.read_text(encoding="utf-8"), "__pycache__/\nbuild/\n")

    def test_reset_requires_the_exact_directory_name(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._project(Path(temp))
            before = tree(root)

            for confirm in (None, "", "Demo", "used-2"):
                with self.assertRaises(HarnessError) as raised:
                    reset_project(root, confirm=confirm)
                self.assertIn("--confirm used", str(raised.exception))
            self.assertEqual(tree(root), before)

    def test_dry_run_reports_without_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._project(Path(temp))
            self._populate(root)
            before = tree(root)

            summary = reset_project(root, dry_run=True)

            self.assertEqual(tree(root), before)
            self.assertTrue(summary["dry_run"])
            self.assertIsNone(summary["snapshot"])
            self.assertIn(".harness/plans/PLAN-0001.md", summary["removed_records"])
            self.assertIn(".harness/state.json", summary["removed_identity"])
            self.assertIn("HANDOFF.md", summary["removed_identity"])
            self.assertIn(".harness/plans", summary["removed_directories"])
            self.assertIn("reset --confirm used", summary["confirm_command"])

    def test_snapshot_round_trips_every_removed_record(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._project(Path(temp))
            self._populate(root)
            before = tree(root)

            summary = reset_project(root, confirm="used")

            snapshot = root / summary["snapshot"]
            removed = summary["removed_records"] + summary["removed_identity"]
            for relative in removed:
                self.assertEqual((snapshot / "tree" / relative).read_bytes(), before[relative])
            manifest = load_json(snapshot / "reset.json")
            self.assertEqual(manifest["root"], str(root))
            self.assertEqual(manifest["name"], "Demo")
            self.assertEqual(manifest["removed_records"], summary["removed_records"])
            self.assertEqual(manifest["removed_identity"], summary["removed_identity"])

    def test_reset_preserves_the_human_decision_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._project(Path(temp))
            from project_harness.collaboration import runtime_root

            runtime = runtime_root(root)
            for name in ("leases", *PRESERVED_RUNTIME):
                (runtime / name).mkdir(parents=True, exist_ok=True)
                (runtime / name / "marker.txt").write_text("kept", encoding="utf-8")

            reset_project(root, confirm="used")

            self.assertFalse((runtime / "leases").exists())
            for name in PRESERVED_RUNTIME:
                self.assertEqual(
                    (runtime / name / "marker.txt").read_text(encoding="utf-8"), "kept"
                )

    def test_reset_refuses_a_directory_without_a_project(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(HarnessError):
                reset_project(Path(temp), confirm="demo")


if __name__ == "__main__":
    unittest.main()
