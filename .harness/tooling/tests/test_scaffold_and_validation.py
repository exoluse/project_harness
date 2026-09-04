from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from project_harness.constants import RECORD_DIRECTORIES
from project_harness.collaboration import acquire_claim, result_build_fingerprint
from project_harness.core import (
    HarnessError,
    atomic_write_json,
    load_json,
    record_path,
    subject_fingerprint,
    subject_fingerprint_for_path,
    sha256_bytes,
    sha256_file,
    utc_now,
)
from project_harness.reporting import decision_package
from project_harness.schema_validation import SCHEMA_DIR
from project_harness.scaffold import init_project
from project_harness.validation import issue_counts, validate_project

from . import REPO
from .helpers import (
    HarnessTestCase,
    add_verified_evidence,
    copy_harness_tree,
    create_ready_project,
    init_harness,
    write_record,
)


class ScaffoldValidationTests(HarnessTestCase):
    def test_plan_and_task_use_markdown_and_preserve_human_notes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            plan_path = record_path(root, "plan", "PLAN-0001")
            task_path = record_path(root, "work_item", "TASK-0001")
            self.assertEqual(plan_path.suffix, ".md")
            self.assertEqual(task_path.suffix, ".md")
            self.assertTrue(plan_path.read_text(encoding="utf-8").startswith("---\n"))
            fingerprint_before_notes = subject_fingerprint_for_path(plan_path)

            plan_path.write_text(
                plan_path.read_text(encoding="utf-8")
                + "\n## Human notes\n\nKeep this explanation.\n",
                encoding="utf-8",
            )
            self.assertEqual(
                subject_fingerprint_for_path(plan_path), fingerprint_before_notes
            )
            plan = load_json(plan_path)
            plan["title"] = "Updated plan title"
            atomic_write_json(plan_path, plan)

            self.assertEqual(load_json(plan_path)["title"], "Updated plan title")
            self.assertIn(
                "Keep this explanation.", plan_path.read_text(encoding="utf-8")
            )

    def test_malformed_markdown_record_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            path = root / ".harness" / "plans" / "PLAN-0001.md"
            path.write_text("# missing front matter\n", encoding="utf-8")

            issues = validate_project(root)

            self.assertTrue(
                any(issue.code == "INVALID_JSON" for issue in issues),
                [issue.as_dict() for issue in issues],
            )

    def test_force_init_repairs_structure_without_rewriting_records(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            root = init_harness(workspace / "demo")
            project_path = root / ".harness" / "project.json"
            state_path = root / ".harness" / "state.json"
            marker_path = root / ".harness" / "requirements" / "REQ-9999.json"
            marker_path.write_text('{"sentinel": true}\n', encoding="utf-8")
            before = {
                path: path.read_bytes()
                for path in (project_path, state_path, marker_path)
            }
            shutil.rmtree(root / ".harness" / "results")
            (root / "HANDOFF.md").unlink()

            init_project(root, force=True)

            self.assertTrue((root / ".harness" / "results" / ".gitkeep").is_file())
            self.assertTrue((root / "HANDOFF.md").is_file())
            self.assertEqual(
                before,
                {path: path.read_bytes() for path in before},
            )
            with self.assertRaisesRegex(HarnessError, "repair-only"):
                init_project(root, "Other name", force=True)

            orphan_root = workspace / "orphan"
            orphan_record = (
                orphan_root / ".harness" / "requirements" / "REQ-0001.json"
            )
            orphan_record.parent.mkdir(parents=True)
            orphan_record.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(HarnessError, "without a canonical project.json"):
                init_project(orphan_root, "Orphan", force=True)

    def test_active_rework_claim_defers_only_covered_result_file_drift(self):
        def exercise(root: Path, claim_path: str) -> list[str]:
            create_ready_project(root)
            target = root / "src" / "example.py"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("before\n", encoding="utf-8")
            task = load_json(record_path(root, "work_item", "TASK-0001"))
            result = {
                "schema": "harness.result/v1",
                "id": "RES-0001",
                "kind": "result",
                "status": "SUBMITTED",
                "task_id": "TASK-0001",
                "claim_id": "CLM-0000",
                "agent": "codex",
                "summary": "Earlier implementation",
                "changed_files": ["src/example.py"],
                "changed_file_states": {
                    "src/example.py": f"FILE:{sha256_file(target)}"
                },
                "verification": [
                    {"command": "python -m unittest", "outcome": "PASS"}
                ],
                "verification_state": "PASS",
                "evidence_refs": [],
                "evidence_fingerprints": {},
                "limitations": [],
                "task_fingerprint": subject_fingerprint(task),
                "plan_fingerprint": subject_fingerprint_for_path(
                    record_path(root, "plan", "PLAN-0001")
                ),
                "base_commit": None,
                "head_commit": None,
                "submitted_at": utc_now(),
            }
            result["build_fingerprint"] = result_build_fingerprint(result)
            write_record(root, "result", "RES-0001", result)
            acquire_claim(
                root,
                agent="codex",
                task_id="TASK-0001",
                paths=[claim_path],
            )
            target.write_text("during rework\n", encoding="utf-8")
            return [
                issue.code
                for issue in validate_project(root)
                if issue.code == "STALE_RESULT_BUILD"
            ]

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            self.assertEqual(exercise(base / "covered", "src/example.py"), [])
            self.assertEqual(
                exercise(base / "uncovered", "tests/example.py"),
                ["STALE_RESULT_BUILD"],
            )

    def test_event_files_are_part_of_strict_project_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            event = sorted((root / ".harness" / "events").glob("EVT-*.json"))[0]
            atomic_write_json(event, {})

            issues = validate_project(root)
            self.assertTrue(
                any(issue.code == "INVALID_EVENT" for issue in issues),
                [issue.as_dict() for issue in issues],
            )

    def test_init_creates_required_structure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_harness_tree(Path(temp) / "demo")
            init_project(root, "Demo")
            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertTrue((root / "CLAUDE.md").is_file())
            self.assertEqual(
                (root / "AGENTS.md").read_text(encoding="utf-8"),
                (REPO / "AGENTS.md").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertTrue((root / "CODEX_START_PROMPT.md").is_file())
            self.assertTrue((root / "CLAUDE_START_PROMPT.md").is_file())
            self.assertTrue((root / "docs" / "APPROVALS.md").is_file())
            self.assertTrue((root / ".harness" / "project.json").is_file())
            state = load_json(root / ".harness" / "state.json")
            self.assertIsNone(state["current_plan"])
            self.assertEqual(
                list((root / ".harness" / "plans").glob("PLAN-*")), []
            )
            self.assertEqual(
                list((root / ".harness" / "work-items").glob("TASK-*")),
                [],
            )
            self.assertTrue((root / ".harness" / "results").is_dir())
            record_directories = {
                directory for directory, _prefix in RECORD_DIRECTORIES.values()
            }
            for directory in record_directories:
                self.assertTrue(
                    (root / ".harness" / directory / ".gitkeep").is_file(),
                    directory,
                )
            self.assertIn(
                ".harness/runtime/",
                (root / ".gitignore").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                (root / ".harness" / ".gitignore").read_text(encoding="utf-8"),
                "/runtime/\n",
            )
            self.assertEqual(
                (root / ".harness" / ".gitattributes").read_text(
                    encoding="utf-8"
                ),
                (
                    "*.json text eol=lf\n"
                    "plans/*.md text eol=lf\n"
                    "work-items/*.md text eol=lf\n"
                ),
            )
            self.assertEqual(issue_counts(validate_project(root))["errors"], 0)
            result = subprocess.run(
                [sys.executable, "scripts/harness.py", "status"],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_git_clone_preserves_scaffold_and_strict_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            root = copy_harness_tree(workspace / "source")
            init_project(root, "Demo")
            runtime_probe = root / ".harness" / "runtime" / "not-tracked.txt"
            runtime_probe.write_text("ephemeral\n", encoding="utf-8")

            commands = [
                ["git", "init"],
                ["git", "config", "user.name", "Harness Test"],
                ["git", "config", "user.email", "harness@example.invalid"],
                ["git", "config", "core.autocrlf", "true"],
                ["git", "add", "-A"],
                ["git", "commit", "-m", "Initialize harness"],
            ]
            for command in commands:
                result = subprocess.run(
                    command,
                    cwd=root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout)

            tracked_runtime = subprocess.run(
                ["git", "ls-files", ".harness/runtime"],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(tracked_runtime.returncode, 0, tracked_runtime.stdout)
            self.assertEqual(tracked_runtime.stdout.strip(), "")

            clone = workspace / "clone"
            cloned = subprocess.run(
                [
                    "git",
                    "-c",
                    "core.autocrlf=true",
                    "clone",
                    str(root),
                    str(clone),
                ],
                cwd=workspace,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(cloned.returncode, 0, cloned.stdout)
            self.assertFalse((clone / ".harness" / "runtime").exists())
            for directory, _prefix in RECORD_DIRECTORIES.values():
                self.assertTrue(
                    (clone / ".harness" / directory / ".gitkeep").is_file(),
                    directory,
                )
            self.assertEqual(
                issue_counts(validate_project(clone)),
                {"errors": 0, "warnings": 0},
            )
            strict = subprocess.run(
                [sys.executable, "scripts/harness.py", "validate", "--strict"],
                cwd=clone,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(strict.returncode, 0, strict.stdout)

    def test_ready_fixture_validates_cleanly(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            counts = issue_counts(validate_project(root))
            self.assertEqual(counts, {"errors": 0, "warnings": 0})
            package = decision_package(root, "PLAN-0001")
            self.assertTrue(package["preflight"]["passed"])
            self.assertEqual(package["requirements"][0]["id"], "REQ-0001")
            self.assertEqual(package["decision_options"][0], "APPROVED")

    def test_schema_files_are_valid_json(self):
        schema_paths = list(SCHEMA_DIR.glob("*.json"))
        self.assertGreaterEqual(len(schema_paths), 8)
        for path in schema_paths:
            with self.subTest(path=path.name):
                self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    def test_requirement_cannot_borrow_an_unrelated_feature_criterion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            feature = {
                "schema": "harness.feature/v1",
                "id": "FUNC-0002",
                "kind": "feature",
                "title": "Unrelated feature",
                "version": "1.0.0",
                "status": "PLANNED",
                "required": False,
                "requirement_refs": [],
                "customer_acceptance_required": False,
                "completion_criteria": [
                    {
                        "id": "AC-FUNC-0002-001",
                        "statement": "Unrelated behavior is observed.",
                        "required": True,
                        "verification_plan": ["python -m unittest"],
                        "required_profiles": ["INTEGRATION"],
                        "required_bindings": ["src"],
                        "evidence_refs": [],
                    }
                ],
            }
            atomic_write_json(record_path(root, "feature", "FUNC-0002"), feature)
            requirement_path = record_path(root, "requirement", "REQ-0001")
            requirement = load_json(requirement_path)
            requirement["acceptance_criteria"] = ["AC-FUNC-0002-001"]
            atomic_write_json(requirement_path, requirement)
            issues = validate_project(root)
            self.assertTrue(
                any(issue.code == "CROSSED_ACCEPTANCE_TRACE" for issue in issues)
            )

    def test_malformed_record_is_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            plan_path = record_path(root, "plan", "PLAN-0001")
            plan = load_json(plan_path)
            plan["approval_dependencies"] = [{}]
            atomic_write_json(plan_path, plan)
            issues = validate_project(root)
            self.assertTrue(any(issue.code == "MALFORMED_RECORD" for issue in issues))

    def test_declared_json_schema_is_enforced(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            feature_path = record_path(root, "feature", "FUNC-0001")
            feature = load_json(feature_path)
            feature["status"] = "MAGICALLY_COMPLETE"
            atomic_write_json(feature_path, feature)

            issues = validate_project(root)
            self.assertTrue(
                any(issue.code == "SCHEMA_VIOLATION" for issue in issues),
                [issue.as_dict() for issue in issues],
            )

    def test_recovery_audit_hash_is_revalidated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            checks = []
            for name in (
                "process",
                "worktree",
                "diff",
                "outbox",
                "external_side_effects",
            ):
                detail = f"{name} inspected"
                check = {
                    "name": name,
                    "outcome": "PASS",
                    "detail": detail,
                    "detail_sha256": sha256_bytes(detail.encode("utf-8")),
                }
                if name == "external_side_effects":
                    check.update(
                        {
                            "reconciliation": "NONE",
                            "idempotency_keys": [],
                            "receipts": [],
                        }
                    )
                checks.append(check)
            recovery = {
                "schema": "harness.recovery/v1",
                "id": "RCV-0001",
                "kind": "recovery",
                "claim_id": "CLM-0001",
                "recovered_by": "coordinator",
                "observed_at": utc_now(),
                "checks": checks,
                "decision": "ABANDON_AND_RECLAIM",
                "reason": "expired owner was unavailable",
            }
            checks[0]["detail"] = "tampered after recovery"
            write_record(root, "recovery", "RCV-0001", recovery)

            issues = validate_project(root)
            self.assertTrue(
                any(issue.code == "RECOVERY_AUDIT_TAMPER" for issue in issues),
                [issue.as_dict() for issue in issues],
            )

    def test_completion_criterion_rejects_dangling_evidence_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            feature_path = record_path(root, "feature", "FUNC-0001")
            feature = load_json(feature_path)
            feature["completion_criteria"][0]["evidence_refs"] = ["EVD-9999"]
            atomic_write_json(feature_path, feature)

            issues = validate_project(root)
            self.assertTrue(
                any(
                    issue.severity == "ERROR"
                    and issue.code == "DANGLING_REFERENCE"
                    and "EVD-9999" in issue.message
                    for issue in issues
                ),
                [issue.as_dict() for issue in issues],
            )

    def test_verified_feature_requires_latest_eligible_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            feature_path = record_path(root, "feature", "FUNC-0001")
            feature = load_json(feature_path)
            feature["status"] = "VERIFIED"
            atomic_write_json(feature_path, feature)

            issues = validate_project(root)
            self.assertTrue(
                any(
                    issue.code == "FEATURE_STATUS_EVIDENCE_MISMATCH"
                    for issue in issues
                ),
                [issue.as_dict() for issue in issues],
            )

            evidence_path = add_verified_evidence(root)
            issues = validate_project(root)
            self.assertFalse(
                any(
                    issue.code == "FEATURE_STATUS_EVIDENCE_MISMATCH"
                    for issue in issues
                ),
                [issue.as_dict() for issue in issues],
            )

            failed = load_json(evidence_path)
            failed["id"] = "EVD-0002"
            failed["title"] = "Newer failed observation"
            failed["result"] = "FAILED"
            failed["actual"] = "required behavior was not observed"
            write_record(root, "evidence", "EVD-0002", failed)
            issues = validate_project(root)
            self.assertTrue(
                any(
                    issue.code == "FEATURE_STATUS_EVIDENCE_MISMATCH"
                    and "EVD-0002" in issue.message
                    for issue in issues
                ),
                [issue.as_dict() for issue in issues],
            )

    def test_advanced_task_status_requires_current_result_review_and_integration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            task_path = record_path(root, "work_item", "TASK-0001")
            task = load_json(task_path)
            task["status"] = "DONE"
            atomic_write_json(task_path, task)

            issues = validate_project(root)
            self.assertTrue(
                any(
                    issue.code == "TASK_STATUS_INCONSISTENT"
                    and "requires a submitted result" in issue.message
                    for issue in issues
                ),
                [issue.as_dict() for issue in issues],
            )

            result = {
                "schema": "harness.result/v1",
                "id": "RES-0001",
                "kind": "result",
                "status": "SUBMITTED",
                "task_id": "TASK-0001",
                "claim_id": "CLM-0001",
                "agent": "codex",
                "summary": "Implementation attempt",
                "changed_files": [],
                "changed_file_states": {},
                "verification": [
                    {"command": "python -m unittest", "outcome": "PASS"}
                ],
                "verification_state": "PASS",
                "evidence_refs": [],
                "evidence_fingerprints": {},
                "limitations": [],
                "task_fingerprint": subject_fingerprint(task),
                "plan_fingerprint": subject_fingerprint_for_path(
                    record_path(root, "plan", "PLAN-0001")
                ),
                "base_commit": None,
                "head_commit": None,
                "submitted_at": utc_now(),
            }
            result["build_fingerprint"] = result_build_fingerprint(result)
            write_record(root, "result", "RES-0001", result)
            review = {
                "schema": "harness.review/v1",
                "id": "VRD-0001",
                "kind": "review",
                "status": "RECORDED",
                "result_id": "RES-0001",
                "reviewer": "claude",
                "decision": "CHANGES_REQUIRED",
                "basis": "Review found remaining work",
                "checks": ["diff", "tests"],
                "result_fingerprint": subject_fingerprint(result),
                "result_build_fingerprint": result["build_fingerprint"],
                "reviewed_at": utc_now(),
            }
            write_record(root, "review", "VRD-0001", review)

            issues = validate_project(root)
            self.assertTrue(
                any(
                    issue.code == "TASK_STATUS_INCONSISTENT"
                    and "latest review decision is CHANGES_REQUIRED" in issue.message
                    and "committed Git baseline" in issue.message
                    for issue in issues
                ),
                [issue.as_dict() for issue in issues],
            )


if __name__ == "__main__":
    unittest.main()
