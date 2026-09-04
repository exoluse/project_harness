from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from project_harness.scaffold import ASSETS, GUIDANCE_FILES, SCRIPT_FILES

TOOLING = Path(__file__).resolve().parents[1]
REPO = TOOLING.parents[1]
PACKAGE = TOOLING / "project_harness"


def _run(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        env=env,
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


class DistributionAssetTests(unittest.TestCase):
    """The package's ``assets`` directory is the single source of every file a
    project receives; this repository's own copies are instances of it."""

    def _assert_same(self, instance: Path, asset: Path) -> None:
        self.assertTrue(asset.is_file(), f"missing asset {asset}")
        self.assertTrue(instance.is_file(), f"missing instance copy {instance}")
        self.assertEqual(
            instance.read_text(encoding="utf-8"),
            asset.read_text(encoding="utf-8"),
            f"{instance.relative_to(REPO)} has drifted from {asset.relative_to(PACKAGE)}",
        )

    def test_repository_guidance_matches_packaged_assets(self):
        for name in GUIDANCE_FILES:
            self._assert_same(REPO / name, ASSETS / "guidance" / name)
        for asset in sorted((ASSETS / "guidance" / "docs").glob("*.md")):
            self._assert_same(REPO / "docs" / asset.name, asset)

    def test_repository_scripts_match_packaged_assets(self):
        for name in SCRIPT_FILES:
            self._assert_same(REPO / "scripts" / name, ASSETS / "scripts" / name)

    def test_repository_schemas_match_packaged_assets(self):
        assets = sorted((ASSETS / "schemas").glob("*.json"))
        self.assertGreaterEqual(len(assets), 8)
        self.assertEqual(
            [path.name for path in assets],
            [path.name for path in sorted((REPO / "schemas").glob("*.json"))],
        )
        for asset in assets:
            self._assert_same(REPO / "schemas" / asset.name, asset)


class CopiedFolderTests(unittest.TestCase):
    """The repository itself, copied as-is, becomes a project by command only."""

    def test_copied_folder_reports_missing_identity_then_initializes_in_place(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "copy"
            shutil.copytree(
                REPO / ".harness" / "tooling",
                root / ".harness" / "tooling",
                ignore=shutil.ignore_patterns("__pycache__", "tests"),
            )
            for name in (*GUIDANCE_FILES, "scripts", "schemas", "docs"):
                source = REPO / name
                if source.is_dir():
                    shutil.copytree(source, root / name, ignore=shutil.ignore_patterns("__pycache__"))
                else:
                    shutil.copy2(source, root / name)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)

            self.assertEqual(_harness(root, "next")["state"], "NEEDS_PROJECT_IDENTITY")
            runtime_marker = root / ".harness" / "tooling" / "project_harness" / "cli.py"
            before = runtime_marker.stat().st_mtime_ns

            result = _run(
                ["scripts/harness.py", "init", ".", "--project-id", "COPY", "--name", "Copied"],
                cwd=root,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(_harness(root, "next")["state"], "NEEDS_PLAN")
            self.assertEqual(_harness(root, "validate")["counts"]["errors"], 0)
            # The runtime already in place is not rewritten over itself.
            self.assertEqual(runtime_marker.stat().st_mtime_ns, before)
            self.assertEqual(
                (root / "AGENTS.md").read_text(encoding="utf-8"),
                (ASSETS / "guidance" / "AGENTS.md").read_text(encoding="utf-8"),
            )


class GeneratedProjectSmokeTests(unittest.TestCase):
    """A project generated from the package alone, driven only by commands."""

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        workspace = Path(self._temp.name)
        # Simulate an installed package: the package directory with nothing
        # from the source checkout around it.
        site = workspace / "site"
        shutil.copytree(
            PACKAGE,
            site / "project_harness",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        self.root = workspace / "project"
        env = {**os.environ, "PYTHONPATH": str(site)}
        result = _run(
            [
                "-c",
                "import sys; from project_harness.cli import main; "
                f"sys.exit(main(['init', {str(self.root)!r}, "
                "'--project-id', 'SMOKE', '--name', 'Smoke']))",
            ],
            cwd=workspace,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def tearDown(self) -> None:
        self._temp.cleanup()

    def test_generated_project_receives_the_full_policy_and_docs(self):
        for name in GUIDANCE_FILES:
            self.assertEqual(
                (self.root / name).read_text(encoding="utf-8"),
                (ASSETS / "guidance" / name).read_text(encoding="utf-8"),
                name,
            )
        self.assertTrue((self.root / "docs" / "APPROVALS.md").is_file())
        self.assertTrue((self.root / "schemas" / "project.schema.json").is_file())
        vendored = self.root / ".harness" / "tooling" / "project_harness"
        self.assertTrue((vendored / "assets" / "schemas" / "plan.schema.json").is_file())
        self.assertTrue((vendored / "assets" / "guidance" / "AGENTS.md").is_file())

    def test_generated_project_verification_passes_before_any_tests_exist(self):
        for tier in ("fast", "full"):
            result = _run(["scripts/check_repo.py", tier], cwd=self.root)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("[harness-strict] exit=0", result.stdout)
        self.assertIn("[tests-full] SKIPPED", result.stdout)

    def test_generated_project_reaches_a_startable_task_by_command_only(self):
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
        self.assertEqual(_harness(root, "next")["state"], "NEEDS_PLAN_ACTIVATION")

        _harness(root, "plan", "activate", "PLAN-0001")
        self.assertEqual(_harness(root, "next")["state"], "NEEDS_TASK_READY")

        _harness(
            root,
            "transition", "--kind", "work_item", "--id", "TASK-0001",
            "--to", "READY", "--agent", "smoke", "--reason", "user request",
        )
        step = _harness(root, "next")
        self.assertEqual(step["state"], "READY", step)
        self.assertTrue(_harness(root, "gate", "task", "TASK-0001")["passed"])

        validation = _harness(root, "validate")
        self.assertEqual(validation["counts"]["errors"], 0, validation)
        # The only remaining signal is the traceability warning `next` surfaced.
        self.assertEqual(
            [issue["code"] for issue in validation["issues"]], ["ORPHAN_TASK"]
        )
        self.assertTrue(any("ORPHAN_TASK" in value for value in step["warnings"]))


if __name__ == "__main__":
    unittest.main()
