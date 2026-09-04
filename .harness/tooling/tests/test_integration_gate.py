from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from project_harness.collaboration import acquire_claim
from project_harness.core import load_record_index, record_path, subject_fingerprint, subject_fingerprint_for_path
from project_harness.gates import _latest_task_result_assessment
from project_harness.workflow import review_result, submit_result

from .helpers import HarnessTestCase, add_verified_evidence, create_ready_project


def git(root: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stdout)


class IntegrationLineageTests(HarnessTestCase):
    def test_unrelated_same_tree_commit_is_not_integration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            git(root, "init", "-b", "main")
            git(root, "config", "user.email", "harness-tests@example.invalid")
            git(root, "config", "user.name", "Harness Tests")
            git(root, "add", ".")
            git(root, "commit", "-m", "fixture baseline")

            claim = acquire_claim(
                root, agent="codex", task_id="TASK-0001", paths=["src"]
            )
            (root / "src" / "core.py").write_text("value = 2\n", encoding="utf-8")
            result = submit_result(
                root,
                claim_id=claim["id"],
                agent="codex",
                summary="Core implementation",
                changed_files=["src/core.py"],
                verifications=["python -m unittest::PASS"],
                evidence_refs=["EVD-0001"],
                limitations=[],
            )
            review_result(
                root,
                result_id=result["id"],
                reviewer="claude",
                decision="PASS",
                basis="Independent diff and evidence review",
                checks=["diff", "tests"],
            )
            git(root, "add", ".")
            git(root, "commit", "-m", "integrate result")

            records, _paths = load_record_index(root)
            _latest, _review, reasons = _latest_task_result_assessment(
                root,
                "TASK-0001",
                records,
                current_task_fingerprint=subject_fingerprint(records["TASK-0001"]),
                current_plan_fingerprint=subject_fingerprint_for_path(
                    record_path(root, "plan", "PLAN-0001")
                ),
            )
            self.assertEqual(reasons, [])

            git(root, "checkout", "--orphan", "unrelated")
            git(root, "commit", "-m", "same tree without lineage")
            records, _paths = load_record_index(root)
            _latest, _review, reasons = _latest_task_result_assessment(
                root,
                "TASK-0001",
                records,
                current_task_fingerprint=subject_fingerprint(records["TASK-0001"]),
                current_plan_fingerprint=subject_fingerprint_for_path(
                    record_path(root, "plan", "PLAN-0001")
                ),
            )
            self.assertIn(
                "latest result head is not integrated in the current Git history",
                reasons,
            )


if __name__ == "__main__":
    unittest.main()
