from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from project_harness.core import HarnessError, load_json
from project_harness.reset import PRESERVED_RUNTIME, reset_project
from project_harness.validation import issue_counts, validate_project

from .helpers import init_harness


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

    def test_reset_reproduces_a_freshly_initialized_project(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._project(Path(temp))
            self._populate(root)
            reference = init_harness(Path(temp) / "reference")

            reset_project(root, confirm="used")

            after, expected = tree(root), tree(reference)
            self.assertEqual(sorted(after), sorted(expected))
            # Two projects created at different times in different directories
            # can only agree on the fields that are not a timestamp or a path.
            volatile = {
                ".harness/project.json": {"created_at"},
                ".harness/state.json": {"updated_at"},
                ".harness/templates/authority-config.example.json": {"repository_root"},
            }
            for relative, content in expected.items():
                if relative not in volatile:
                    self.assertEqual(after[relative], content, relative)
                    continue
                actual, reference_value = json.loads(after[relative]), json.loads(content)
                differing = {
                    field
                    for field in set(actual) | set(reference_value)
                    if actual.get(field) != reference_value.get(field)
                }
                self.assertLessEqual(differing, volatile[relative], relative)

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
            self.assertIn(".harness/state.json", summary["regenerated"])
            self.assertIn("reset --confirm used", summary["confirm_command"])

    def test_snapshot_round_trips_every_removed_record(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._project(Path(temp))
            self._populate(root)
            before = tree(root)

            summary = reset_project(root, confirm="used")

            snapshot = root / summary["snapshot"]
            for relative in summary["removed_records"] + summary["regenerated"]:
                self.assertEqual((snapshot / "tree" / relative).read_bytes(), before[relative])
            manifest = load_json(snapshot / "reset.json")
            self.assertEqual(manifest["root"], str(root))
            self.assertEqual(manifest["removed_records"], summary["removed_records"])

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

    def test_reset_leaves_a_valid_project(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._project(Path(temp))
            self._populate(root)

            reset_project(root, confirm="used")

            state = load_json(root / ".harness" / "state.json")
            self.assertEqual(state["lifecycle_state"], "DISCOVERY")
            self.assertIsNone(state["current_plan"])
            self.assertIsNone(state["active_plan"])
            counts = issue_counts(validate_project(root))
            self.assertEqual(counts["errors"], 0)
            self.assertEqual(counts["warnings"], 0)

    def test_reset_refuses_a_directory_without_a_project(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(HarnessError):
                reset_project(Path(temp), confirm="demo")


if __name__ == "__main__":
    unittest.main()
