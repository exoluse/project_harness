from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from project_harness.approvals import approval_status, find_current_approval
from project_harness.authoring import create_work_item, sync_plan
from project_harness.collaboration import result_build_fingerprint, result_currentness
from project_harness.core import HarnessError, atomic_write_json, load_json, record_path, sha256_file, subject_fingerprint, subject_fingerprint_for_path
from project_harness.decision_scope import prepare_scope
from project_harness.gates import task_start_gate
from project_harness.guidance import next_step
from project_harness.lifecycle import apply_plan_decision
from project_harness.lifecycle_mutations import transition_record
from project_harness.validation import validate_project

from .helpers import copy_harness_tree, create_ready_project, write_record
from . import test_procedural_approvals as procedural_tests


class ScopeRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="harness-scope-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = create_ready_project(Path(self.temp.name) / "project", approve=False)
        project_path = self.root / ".harness/project.json"
        project = load_json(project_path)
        project["policy"].update(claim_mode="WHEN_CONCURRENT", record_mode="ON_DEMAND")
        atomic_write_json(project_path, project)

    def prepare(self, **kwargs):
        return prepare_scope(self.root, plan_id="PLAN-0001", write_scope=["src", "tests"], max_risk="MEDIUM", **kwargs)

    def confirm(self, **kwargs):
        return procedural_tests.ProceduralApprovalTests()._confirm(self.root, **kwargs)

    def mutate(self, kind, record_id, edit):
        path = record_path(self.root, kind, record_id)
        value = load_json(path)
        edit(value)
        atomic_write_json(path, value)

    def add_task(self, task_id="TASK-0002", plan_id="PLAN-0001"):
        create_work_item(self.root, task_id=task_id, title="Refine the same agreed outcome", plan_id=plan_id,
                         feature_refs=["FUNC-0001"], criterion_refs=["AC-FUNC-0001-001"],
                         capabilities=["LOCAL_IMPLEMENTATION", "LOCAL_TESTS"],
                         write_scope=["src/component"], verification=["python -m unittest"], risk="LOW")
        transition_record(self.root, kind="work_item", record_id=task_id, target_status="READY",
                          agent="test", claim_id=None, reason="Covered task detail")

    def test_in_scope_task_split_preserves_decision_and_unaffected_task_fingerprints(self):
        self.prepare()
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        fingerprint = subject_fingerprint_for_path(record_path(self.root, "plan", "PLAN-0001"))
        self.add_task()
        self.assertEqual(fingerprint, subject_fingerprint_for_path(record_path(self.root, "plan", "PLAN-0001")))
        self.assertEqual(approval_status(self.root, decision)[0], "CURRENT")
        self.assertTrue(task_start_gate(self.root, "TASK-0001").passed)
        self.assertTrue(task_start_gate(self.root, "TASK-0002").passed)
        self.assertEqual(len(list((self.root / ".harness/approvals").glob("APR-*.json"))), 1)
        self.assertEqual(validate_project(self.root), [])

    def test_unordered_paths_and_version_labels_preserve_scoped_fingerprints(self):
        self.prepare()
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        task = record_path(self.root, "work_item", "TASK-0001")
        before = subject_fingerprint(load_json(task))
        self.mutate("work_item", "TASK-0001", lambda v: v.update(write_scope=list(reversed(v["write_scope"])), version="9.0"))
        self.mutate("plan", "PLAN-0001", lambda v: v.update(version="9.0"))
        self.assertEqual(before, subject_fingerprint(load_json(task)))
        self.assertTrue(task_start_gate(self.root, "TASK-0001").passed)

    def test_paths_capabilities_risk_and_verification_cannot_expand_silently(self):
        self.prepare()
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        path = record_path(self.root, "work_item", "TASK-0001")
        original = load_json(path)
        for delta in ({"write_scope": ["other"]}, {"risk": "HIGH"}, {"verification": []},
                      {"capabilities": ["SECRET_ACCESS"]}):
            with self.subTest(delta=delta):
                atomic_write_json(path, original | delta)
                self.assertFalse(task_start_gate(self.root, "TASK-0001").passed)
        atomic_write_json(path, original)
        self.assertTrue(task_start_gate(self.root, "TASK-0001").passed)

    def test_changed_outcome_blocks_execution_without_destroying_history(self):
        self.prepare()
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        self.mutate("requirement", "REQ-0001", lambda v: v.update(statement="A materially different outcome"))
        self.assertFalse(task_start_gate(self.root, "TASK-0001").passed)
        self.assertEqual(approval_status(self.root, decision, historical=True)[0], "HISTORICAL")

    def test_shared_scope_runs_two_plans_with_one_prompt_decision(self):
        self.prepare()
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        original = load_json(record_path(self.root, "plan", "PLAN-0001"))
        second = deepcopy(original)
        second.update(id="PLAN-0002", status="DRAFT", approval_dependencies=[], derived_approval_dependencies=[])
        second.pop("decision_ref", None)
        second.pop("decision_applied_at", None)
        second["approval_subject"]["work_item_refs"] = []
        write_record(self.root, "plan", "PLAN-0002", second)
        self.add_task(plan_id="PLAN-0002")
        sync_plan(self.root, plan_id="PLAN-0002")
        self.assertFalse(task_start_gate(self.root, "TASK-0002").passed)
        apply_plan_decision(self.root, approval_id=decision["id"], plan_id="PLAN-0002")
        self.assertTrue(task_start_gate(self.root, "TASK-0001").passed)
        self.assertTrue(task_start_gate(self.root, "TASK-0002").passed)
        self.assertEqual(validate_project(self.root), [])
        self.assertFalse(apply_plan_decision(self.root, approval_id=decision["id"], plan_id="PLAN-0002")["changed"])
        self.confirm(confirmation_id="HCONF-revoked-scope", decision="REVOKED", basis="Synthetic owner revokes the shared scope")
        self.assertFalse(task_start_gate(self.root, "TASK-0001").passed)
        self.assertFalse(task_start_gate(self.root, "TASK-0002").passed)

    def test_legacy_decisions_are_not_reinterpreted_as_scope_coverage(self):
        decision = self.confirm()
        self.prepare()
        self.assertNotEqual(approval_status(self.root, decision)[0], "CURRENT")
        self.assertIsNone(find_current_approval(self.root, subject_id="PLAN-0001", approval_type="PLAN")[0])

    def test_legacy_material_change_resumes_building_and_history_validates(self):
        first = self.confirm()
        apply_plan_decision(self.root, approval_id=first["id"])
        state_path = self.root / ".harness/state.json"
        state = load_json(state_path); state["lifecycle_state"] = "BUILDING"; atomic_write_json(state_path, state)
        self.mutate("work_item", "TASK-0001", lambda v: v.update(write_scope=["src", "tests", "docs"]))
        second = self.confirm(confirmation_id="HCONF-changed", basis="Synthetic owner approves the concrete delta")
        self.assertEqual(apply_plan_decision(self.root, approval_id=second["id"])["lifecycle_state"], "BUILDING")
        self.assertEqual(validate_project(self.root), [])

    def test_scoped_material_change_routes_to_application_and_resumes_building(self):
        self.prepare()
        first = self.confirm()
        apply_plan_decision(self.root, approval_id=first["id"])
        transition_record(self.root, kind="project", record_id="PROJECT", target_status="BUILDING",
                          agent="test", claim_id=None, reason="Synthetic implementation begins")
        self.mutate("requirement", "REQ-0001", lambda v: v.update(statement="Reviewed revised outcome"))
        self.prepare()
        self.assertEqual(next_step(self.root)["state"], "NEEDS_PLAN_APPROVAL")
        second = self.confirm(confirmation_id="HCONF-scope-delta", basis="Synthetic owner approves revised outcome")
        self.assertEqual(next_step(self.root)["state"], "NEEDS_DECISION_APPLIED")
        self.assertEqual(apply_plan_decision(self.root, approval_id=second["id"])["lifecycle_state"], "BUILDING")
        self.assertTrue(task_start_gate(self.root, "TASK-0001").passed)

    def test_unaffected_result_survives_refinement_but_not_changed_outputs_or_outcomes(self):
        self.prepare()
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        artifact = self.root / "src/checked.txt"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("original checked output", encoding="utf-8")
        result = {"task_id": "TASK-0001", "claim_id": None,
                  "task_fingerprint": subject_fingerprint(load_json(record_path(self.root, "work_item", "TASK-0001"))),
                  "plan_fingerprint": subject_fingerprint_for_path(record_path(self.root, "plan", "PLAN-0001")),
                  "base_commit": None, "head_commit": None, "changed_files": ["src/checked.txt"],
                  "changed_file_states": {"src/checked.txt": "FILE:" + sha256_file(artifact)},
                  "evidence_refs": [], "evidence_fingerprints": {}}
        result["build_fingerprint"] = result_build_fingerprint(result)
        self.add_task()
        self.assertEqual(result_currentness(self.root, result), (True, []))
        artifact.write_text("changed output", encoding="utf-8")
        self.assertFalse(result_currentness(self.root, result)[0])
        artifact.write_text("original checked output", encoding="utf-8")
        self.mutate("requirement", "REQ-0001", lambda v: v.update(statement="Different outcome"))
        self.assertFalse(result_currentness(self.root, result)[0])
        self.assertEqual(validate_project(self.root), [])

    def test_explicit_dependency_changes_require_review(self):
        path = ".harness/sources/SRC-0001.json"
        self.mutate("plan", "PLAN-0001", lambda v: v["approval_dependencies"].append(path))
        self.prepare()
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        self.mutate("plan", "PLAN-0001", lambda v: v["approval_dependencies"].remove(path))
        self.assertFalse(task_start_gate(self.root, "TASK-0001").passed)

    def test_valid_superseded_history_does_not_fail_strict_validation(self):
        first = self.confirm()
        apply_plan_decision(self.root, approval_id=first["id"])
        second = self.confirm(confirmation_id="HCONF-second", basis="Synthetic replacement")
        apply_plan_decision(self.root, approval_id=second["id"])
        self.assertEqual(validate_project(self.root), [])
        first_path = record_path(self.root, "approval", first["id"])
        first["attestation"]["confirmation_reference"] = "tampered"
        atomic_write_json(first_path, first)
        self.assertIn("INVALID_APPROVAL", [issue.code for issue in validate_project(self.root)])

    def test_scope_covers_only_the_change_actually_reviewed(self):
        change = {"schema": "harness.change/v1", "id": "CR-0001", "kind": "change", "status": "DECISION_READY",
                  "classification": "CLARIFICATION", "source_refs": ["SRC-0001"], "affects": ["REQ-0001"],
                  "impact": {"scope": "Clarification of the same behavior"}, "decision_ref": None}
        write_record(self.root, "change", "CR-0001", change)
        self.prepare(change_refs=["CR-0001"])
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        change.update(status="APPROVED", decision_ref=decision["id"])
        write_record(self.root, "change", "CR-0001", change)
        self.assertEqual(validate_project(self.root), [])
        second = self.confirm(confirmation_id="HCONF-change-history", basis="Synthetic later scope decision")
        apply_plan_decision(self.root, approval_id=second["id"])
        self.assertEqual(validate_project(self.root), [])
        change["impact"] = {"scope": "An unreviewed new feature"}
        write_record(self.root, "change", "CR-0001", change)
        self.assertIn("CHANGE_DECISION_INVALID", [issue.code for issue in validate_project(self.root)])

    def test_sync_removes_only_proven_derived_dependencies(self):
        self.add_task()
        self.mutate("plan", "PLAN-0001", lambda v: v["approval_subject"]["work_item_refs"].remove("TASK-0002"))
        result = sync_plan(self.root, plan_id="PLAN-0001")
        self.assertIn(".harness/work-items/TASK-0002.md", result["removed_dependencies"])

    def test_snapshot_tampering_cannot_be_hidden_by_recomputing_file_checksum(self):
        decision = self.confirm()
        entry = next(item for item in decision["snapshot_manifest"] if item["path"].endswith("TASK-0001.md"))
        snapshot = self.root / entry["snapshot_path"]
        value = load_json(snapshot); value["write_scope"] = ["unreviewed"]
        atomic_write_json(snapshot, value)
        entry["sha256"] = sha256_file(snapshot)
        atomic_write_json(record_path(self.root, "approval", decision["id"]), decision)
        self.assertEqual(approval_status(self.root, decision, historical=True)[0], "INVALID")

    def test_workstream_progress_does_not_require_another_scope_decision(self):
        self.prepare()
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        self.mutate("plan", "PLAN-0001", lambda v: v["approval_subject"]["workstreams"][1].update(readiness="READY_TO_BUILD"))
        self.assertTrue(task_start_gate(self.root, "TASK-0001").passed)

    def test_malformed_or_widened_declared_scope_fails_closed(self):
        self.prepare()
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        path = record_path(self.root, "plan", "PLAN-0001")
        original = load_json(path)
        for update in ({"write_scope": ["**"]}, {"max_risk": []}, {"schema": "unknown"}):
            with self.subTest(update=update):
                changed = deepcopy(original)
                changed["approval_subject"]["decision_scope"].update(update)
                atomic_write_json(path, changed)
                self.assertFalse(task_start_gate(self.root, "TASK-0001").passed)
        atomic_write_json(path, original)

    def test_changed_independent_feature_blocks_only_its_covered_task(self):
        requirement = load_json(record_path(self.root, "requirement", "REQ-0001"))
        requirement.update(id="REQ-0002", acceptance_criteria=["AC-FUNC-0002-001"])
        write_record(self.root, "requirement", "REQ-0002", requirement)
        feature = load_json(record_path(self.root, "feature", "FUNC-0001"))
        feature.update(id="FUNC-0002", requirement_refs=["REQ-0002"])
        feature["completion_criteria"][0]["id"] = "AC-FUNC-0002-001"
        write_record(self.root, "feature", "FUNC-0002", feature)
        self.mutate("plan", "PLAN-0001", lambda v: v["approval_subject"].update(
            requirement_refs=["REQ-0001", "REQ-0002"], feature_refs=["FUNC-0001", "FUNC-0002"]))
        create_work_item(self.root, task_id="TASK-0002", title="Independent feature", plan_id="PLAN-0001",
                         feature_refs=["FUNC-0002"], criterion_refs=["AC-FUNC-0002-001"],
                         capabilities=["LOCAL_IMPLEMENTATION"], write_scope=["src/second"],
                         verification=["python -m unittest tests.second_feature"])
        self.prepare()
        decision = self.confirm()
        apply_plan_decision(self.root, approval_id=decision["id"])
        transition_record(self.root, kind="work_item", record_id="TASK-0002", target_status="READY",
                          agent="test", claim_id=None, reason="Independent task ready")
        self.assertTrue(task_start_gate(self.root, "TASK-0002").passed)
        self.assertEqual(load_json(record_path(self.root, "work_item", "TASK-0001"))["verification"], ["python -m unittest"])
        original = load_json(record_path(self.root, "work_item", "TASK-0002"))
        self.mutate("work_item", "TASK-0002", lambda v: v.update(verification=["python -m unittest"]))
        self.assertFalse(task_start_gate(self.root, "TASK-0002").passed)
        atomic_write_json(record_path(self.root, "work_item", "TASK-0002"), original)
        self.mutate("requirement", "REQ-0002", lambda v: v.update(statement="Changed second outcome"))
        self.assertTrue(task_start_gate(self.root, "TASK-0001").passed)
        self.assertFalse(task_start_gate(self.root, "TASK-0002").passed)
        self.assertEqual(next_step(self.root)["state"], "READY")


class FullCliPathTests(unittest.TestCase):
    def test_init_planning_prompt_apply_refine_retire_and_second_plan_without_state_edits(self):
        with tempfile.TemporaryDirectory(prefix="harness-cli-test-") as tmp:
            root = copy_harness_tree(Path(tmp) / "project")

            def cli(*args):
                result = subprocess.run([sys.executable, "scripts/harness.py", *args], cwd=root,
                                        capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return json.loads(result.stdout) if result.stdout.lstrip().startswith("{") else None

            cli("init")
            cli("new", "source", "SRC-0001", "Synthetic customer request")
            cli("new", "requirement", "REQ-0001", "A local greeting", "--statement", "Show a greeting",
                "--source", "SRC-0001", "--acceptance-criterion", "AC-FUNC-0001-001")
            cli("new", "feature", "FUNC-0001", "Greeting", "--requirement", "REQ-0001",
                "--criterion", "AC-FUNC-0001-001|Greeting is shown", "--verification-command", "python scripts/check_repo.py full",
                "--profile", "STATIC", "--binding", "src")
            cli("new", "plan", "PLAN-0001", "Deliver greeting", "--requirement", "REQ-0001", "--feature", "FUNC-0001")
            def task(task_id, plan_id):
                cli("new", "task", task_id, "Implement greeting", "--plan", plan_id, "--feature", "FUNC-0001",
                    "--criterion", "AC-FUNC-0001-001", "--capability", "LOCAL_IMPLEMENTATION",
                    "--write-scope", "src", "--verification", "python scripts/check_repo.py full")
            task("TASK-0001", "PLAN-0001")
            cli("plan", "prepare-scope", "PLAN-0001", "--write-boundary", "src", "--max-risk", "LOW")
            cli("validate", "--strict")
            package = cli("report", "decision-package", "PLAN-0001")
            self.assertTrue(package["preflight"]["passed"])
            self.assertEqual(list((root / ".harness/approvals").glob("APR-*.json")), [])
            guidance = cli("next")
            self.assertEqual(guidance["state"], "NEEDS_PLAN_APPROVAL")
            self.assertTrue(any("approval confirm" in cmd for cmd in guidance["commands"]))
            decision = cli("approval", "confirm", "--type", "PLAN", "--subject", ".harness/plans/PLAN-0001.md",
                           "--decision", "APPROVED", "--approver", "synthetic-owner", "--basis", "Synthetic owner approves the presented scope",
                           "--confirm-fingerprint", package["plan_fingerprint"], "--confirmation-id", "HCONF-cli-scope",
                           "--confirmation-channel", "UNIT_TEST", "--confirmation-reference", "synthetic-message",
                           "--authorized-action", "LOCAL_IMPLEMENTATION", "--acknowledge-procedural")
            self.assertEqual(cli("next")["state"], "NEEDS_DECISION_APPLIED")
            cli("plan", "apply-decision", "--approval", decision["id"])
            cli("transition", "--kind", "work_item", "--id", "TASK-0001", "--to", "READY", "--agent", "test", "--reason", "Prepared")
            self.assertTrue(cli("gate", "task", "TASK-0001")["passed"])
            task("TASK-0002", "PLAN-0001")
            cli("transition", "--kind", "work_item", "--id", "TASK-0002", "--to", "READY", "--agent", "test", "--reason", "Refinement")
            self.assertTrue(cli("gate", "task", "TASK-0002")["passed"])
            for task_id in ("TASK-0001", "TASK-0002"):
                for status in ("RUNNING", "SUBMITTED", "REVIEWED", "INTEGRATED", "DONE", "CLOSED"):
                    cli("transition", "--kind", "work_item", "--id", task_id, "--to", status, "--agent", "test", "--reason", "Synthetic lifecycle transition; no verification claim")
            self.assertEqual(cli("next")["state"], "SCOPE_COMPLETE")
            cli("transition", "--kind", "plan", "--id", "PLAN-0001", "--to", "CLOSED", "--agent", "test", "--reason", "Synthetic scope complete")
            cli("new", "plan", "PLAN-0002", "Second delivery step", "--scope-from", "PLAN-0001")
            task("TASK-0003", "PLAN-0002")
            cli("plan", "apply-decision", "--approval", decision["id"], "--plan", "PLAN-0002")
            cli("transition", "--kind", "work_item", "--id", "TASK-0003", "--to", "READY", "--agent", "test", "--reason", "Covered step")
            self.assertTrue(cli("gate", "task", "TASK-0003")["passed"])
            cli("validate", "--strict")
            self.assertEqual(len(list((root / ".harness/approvals").glob("APR-*.json"))), 1)
