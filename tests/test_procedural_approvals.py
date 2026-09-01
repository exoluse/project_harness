from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from project_harness.approvals import (
    approval_status,
    find_current_approval,
    record_approval,
    record_procedural_approval,
)
from project_harness.core import (
    HarnessError,
    atomic_write_json,
    load_json,
    record_path,
    sha256_file,
    subject_fingerprint_for_path,
)
from project_harness.gates import plan_preflight_gate, task_start_gate
from project_harness.lifecycle import apply_plan_decision
from project_harness.reporting import doctor_report
from project_harness.validation import validate_project

from .helpers import create_ready_project, write_record


class ProceduralApprovalTests(unittest.TestCase):
    def _git(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def _fingerprint(self, root: Path) -> str:
        return subject_fingerprint_for_path(
            record_path(root, "plan", "PLAN-0001")
        )

    def _confirm(
        self,
        root: Path,
        *,
        confirmation_id: str = "HCONF-test-0001",
        confirm_fingerprint: str | None = None,
        basis: str = "Reviewed the exact local implementation plan",
        decision: str = "APPROVED",
        authorized_actions: list[str] | None = None,
        acknowledge_procedural: bool = True,
    ) -> dict:
        return record_procedural_approval(
            root,
            approval_type="PLAN",
            subject_path=".harness/plans/PLAN-0001.json",
            decision=decision,
            approver="human-test-owner",
            basis=basis,
            confirm_fingerprint=confirm_fingerprint or self._fingerprint(root),
            confirmation_id=confirmation_id,
            confirmation_channel="UNIT_TEST",
            confirmation_reference=f"test:{confirmation_id}",
            authorized_actions=(
                authorized_actions
                if authorized_actions is not None
                else ["LOCAL_IMPLEMENTATION", "LOCAL_TESTS"]
            ),
            excluded_actions=["PRODUCTION_DEPLOYMENT"],
            acknowledge_procedural=acknowledge_procedural,
        )

    def test_exact_fingerprint_procedural_approval_is_current(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)

            approval = self._confirm(root)

            status, reason = approval_status(root, approval)
            self.assertEqual(status, "CURRENT", reason)
            self.assertEqual(approval["assurance"], "PROCEDURAL")
            self.assertEqual(
                approval["attestation"]["confirmed_subject_fingerprint"],
                self._fingerprint(root),
            )
            self.assertIn(
                "does not authenticate",
                approval["attestation"]["limitation"],
            )

    def test_cli_confirmation_and_application_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            script = Path(__file__).resolve().parents[1] / "scripts" / "harness.py"
            confirmation = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--root",
                    str(root),
                    "--json",
                    "approval",
                    "confirm",
                    "--type",
                    "PLAN",
                    "--subject",
                    ".harness/plans/PLAN-0001.json",
                    "--decision",
                    "APPROVED",
                    "--approver",
                    "human-test-owner",
                    "--basis",
                    "CLI owner confirmation fixture",
                    "--confirm-fingerprint",
                    self._fingerprint(root),
                    "--confirmation-id",
                    "HCONF-cli-0001",
                    "--confirmation-channel",
                    "UNIT_TEST",
                    "--confirmation-reference",
                    "test:HCONF-cli-0001",
                    "--authorized-action",
                    "LOCAL_IMPLEMENTATION",
                    "--authorized-action",
                    "LOCAL_TESTS",
                    "--excluded-action",
                    "PRODUCTION_DEPLOYMENT",
                    "--acknowledge-procedural",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(confirmation.returncode, 0, confirmation.stdout)
            approval = json.loads(confirmation.stdout)

            application = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--root",
                    str(root),
                    "--json",
                    "plan",
                    "apply-decision",
                    "--approval",
                    approval["id"],
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

            self.assertEqual(application.returncode, 0, application.stdout)
            self.assertTrue(json.loads(application.stdout)["changed"])
            self.assertEqual(
                load_json(root / ".harness" / "state.json")["active_decision"],
                approval["id"],
            )

    def test_wrong_fingerprint_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)

            with self.assertRaisesRegex(
                HarnessError, "fingerprint does not match"
            ):
                self._confirm(root, confirm_fingerprint="0" * 64)

    def test_explicit_procedural_acknowledgement_is_required(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)

            with self.assertRaisesRegex(HarnessError, "acknowledge-procedural"):
                self._confirm(root, acknowledge_procedural=False)

    def test_cryptographic_plan_policy_rejects_procedural_confirmation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            project_path = root / ".harness" / "project.json"
            project = load_json(project_path)
            project["policy"]["approval_assurance"]["by_type"][
                "PLAN"
            ] = "CRYPTOGRAPHIC"
            atomic_write_json(project_path, project)

            with self.assertRaisesRegex(
                HarnessError, "does not permit PROCEDURAL PLAN"
            ):
                self._confirm(root)

    def test_doctor_reports_malformed_assurance_policy_without_crashing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            project_path = root / ".harness" / "project.json"
            project = load_json(project_path)
            project["policy"]["approval_assurance"]["default"] = "TYPO"
            atomic_write_json(project_path, project)

            report = doctor_report(root)

            self.assertEqual(report["plan_approval_assurance"]["required"], "UNKNOWN")
            self.assertFalse(report["plan_approval_assurance"]["ready"])
            self.assertGreater(report["validation"]["errors"], 0)

    def test_strengthened_policy_invalidates_existing_procedural_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            approval = self._confirm(root, confirmation_id="HCONF-policy-0001")
            project_path = root / ".harness" / "project.json"
            project = load_json(project_path)
            project["policy"]["approval_assurance"]["by_type"][
                "PLAN"
            ] = "CRYPTOGRAPHIC"
            atomic_write_json(project_path, project)

            status, reason = approval_status(root, approval)

            self.assertEqual(status, "INVALID")
            self.assertIn("does not satisfy required CRYPTOGRAPHIC", reason)

    def test_procedural_assurance_is_rejected_outside_plan_decisions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)

            with self.assertRaisesRegex(
                HarnessError, "PROCEDURAL assurance is not permitted for CHANGE"
            ):
                record_procedural_approval(
                    root,
                    approval_type="CHANGE",
                    subject_path=".harness/plans/PLAN-0001.json",
                    decision="APPROVED",
                    approver="human-test-owner",
                    basis="A change may not use plan-only assurance",
                    confirm_fingerprint=self._fingerprint(root),
                    confirmation_id="HCONF-change-0001",
                    confirmation_channel="UNIT_TEST",
                    confirmation_reference="test:HCONF-change-0001",
                    authorized_actions=["LOCAL_IMPLEMENTATION"],
                    excluded_actions=[],
                    acknowledge_procedural=True,
                )

    def test_procedural_plan_rejects_high_impact_actions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            plan_path = record_path(root, "plan", "PLAN-0001")
            plan = load_json(plan_path)
            plan["approval_subject"]["authorized_actions"] = [
                "PRODUCTION_DEPLOYMENT"
            ]
            plan["approval_subject"]["excluded_actions"] = []
            atomic_write_json(plan_path, plan)
            task_path = record_path(root, "work_item", "TASK-0001")
            task = load_json(task_path)
            task["capabilities"] = ["PRODUCTION_DEPLOYMENT"]
            task["forbidden_actions"] = []
            atomic_write_json(task_path, task)

            with self.assertRaisesRegex(
                HarnessError, "CRYPTOGRAPHIC assurance is required"
            ):
                self._confirm(
                    root,
                    confirmation_id="HCONF-production-0001",
                    authorized_actions=["PRODUCTION_DEPLOYMENT"],
                )

    def test_high_impact_task_requires_matching_cryptographic_approval_ref(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            plan_path = record_path(root, "plan", "PLAN-0001")
            task_path = record_path(root, "work_item", "TASK-0001")
            plan = load_json(plan_path)
            plan["approval_subject"]["authorized_actions"] = [
                "PRODUCTION_DEPLOYMENT"
            ]
            plan["approval_subject"]["excluded_actions"] = []
            atomic_write_json(plan_path, plan)
            task = load_json(task_path)
            task["capabilities"] = ["PRODUCTION_DEPLOYMENT"]
            task["forbidden_actions"] = []
            atomic_write_json(task_path, task)

            missing = plan_preflight_gate(root, "PLAN-0001")
            self.assertFalse(missing.passed)
            self.assertTrue(
                any("PRODUCTION_DEPLOYMENT" in item for item in missing.blockers),
                missing.blockers,
            )

            with patch(
                "project_harness.approvals._verify_attestation",
                return_value=(True, "unit-test cryptographic authority"),
            ):
                deployment = record_approval(
                    root,
                    approval_type="PRODUCTION_DEPLOYMENT",
                    subject_path=".harness/project.json",
                    decision="APPROVED",
                    approver="human-test-owner",
                    authority_role="HUMAN_PROJECT_OWNER",
                    basis="Fixture authorizes one production deployment capability",
                    authorized_actions=["PRODUCTION_DEPLOYMENT"],
                    excluded_actions=[],
                    attestation={"mode": "TEST_MOCK"},
                    assurance="CRYPTOGRAPHIC",
                )
                task = load_json(task_path)
                task["capability_approval_refs"] = {
                    "PRODUCTION_DEPLOYMENT": [deployment["id"]]
                }
                atomic_write_json(task_path, task)
                self.assertTrue(plan_preflight_gate(root, "PLAN-0001").passed)
                plan_approval = record_approval(
                    root,
                    approval_type="PLAN",
                    subject_path=".harness/plans/PLAN-0001.json",
                    decision="APPROVED",
                    approver="human-test-owner",
                    authority_role="HUMAN_PROJECT_OWNER",
                    basis="Fixture cryptographically authorizes the production plan",
                    authorized_actions=["PRODUCTION_DEPLOYMENT"],
                    excluded_actions=[],
                    attestation={"mode": "TEST_MOCK"},
                    assurance="CRYPTOGRAPHIC",
                )
                apply_plan_decision(root, approval_id=plan_approval["id"])
                gate = task_start_gate(root, "TASK-0001")

            self.assertTrue(gate.passed, gate.blockers)

    def test_high_impact_conditional_approval_blocks_until_conditions_resolve(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            write_record(
                root,
                "open_item",
                "OI-0001",
                {
                    "schema": "harness.open_item/v1",
                    "id": "OI-0001",
                    "kind": "open_item",
                    "title": "Production maintenance window",
                    "category": "RISK",
                    "gate_level": "G3",
                    "status": "OPEN",
                    "affects": ["TASK-0001"],
                    "blocks": ["TASK-0001"],
                    "resolution": None,
                },
            )
            plan_path = record_path(root, "plan", "PLAN-0001")
            task_path = record_path(root, "work_item", "TASK-0001")
            plan = load_json(plan_path)
            plan["approval_subject"]["authorized_actions"] = [
                "PRODUCTION_DEPLOYMENT"
            ]
            plan["approval_subject"]["excluded_actions"] = []
            atomic_write_json(plan_path, plan)
            task = load_json(task_path)
            task["capabilities"] = ["PRODUCTION_DEPLOYMENT"]
            task["forbidden_actions"] = []
            atomic_write_json(task_path, task)

            with patch(
                "project_harness.approvals._verify_attestation",
                return_value=(True, "unit-test cryptographic authority"),
            ):
                deployment = record_approval(
                    root,
                    approval_type="PRODUCTION_DEPLOYMENT",
                    subject_path=".harness/project.json",
                    decision="APPROVED_WITH_CONDITIONS",
                    approver="human-test-owner",
                    authority_role="HUMAN_PROJECT_OWNER",
                    basis="Fixture authorizes deployment after the maintenance window",
                    conditions=["Maintenance window must be confirmed"],
                    condition_refs=["OI-0001"],
                    authorized_actions=["PRODUCTION_DEPLOYMENT"],
                    excluded_actions=[],
                    attestation={"mode": "TEST_MOCK"},
                    assurance="CRYPTOGRAPHIC",
                )
                task = load_json(task_path)
                task["capability_approval_refs"] = {
                    "PRODUCTION_DEPLOYMENT": [deployment["id"]]
                }
                atomic_write_json(task_path, task)
                preflight = plan_preflight_gate(root, "PLAN-0001")

            self.assertFalse(preflight.passed)
            self.assertTrue(
                any("unresolved conditions" in item for item in preflight.blockers),
                preflight.blockers,
            )

    def test_confirmation_replay_is_idempotent_and_conflict_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)

            first = self._confirm(root, confirmation_id="HCONF-replay-0001")
            replay = self._confirm(root, confirmation_id="HCONF-replay-0001")

            self.assertEqual(replay["id"], first["id"])
            self.assertEqual(
                len(list((root / ".harness" / "approvals").glob("APR-*.json"))),
                1,
            )
            with self.assertRaisesRegex(HarnessError, "already used"):
                self._confirm(
                    root,
                    confirmation_id="HCONF-replay-0001",
                    basis="A materially different decision basis",
                )

    def test_exact_replay_repairs_a_missing_shared_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            approval = self._confirm(root)
            marker_directory = (
                root
                / ".harness"
                / "runtime"
                / "human-decisions"
                / "latest-procedural"
            )
            marker = next(marker_directory.glob("*.json"))
            marker.unlink()

            status, reason = approval_status(root, approval)
            self.assertEqual(status, "INVALID")
            self.assertIn("marker is unavailable", reason)

            replay = self._confirm(root)

            self.assertEqual(replay["id"], approval["id"])
            self.assertEqual(len(list(marker_directory.glob("*.json"))), 1)
            self.assertEqual(approval_status(root, replay)[0], "CURRENT")
            self.assertEqual(
                len(list((root / ".harness" / "approvals").glob("APR-*.json"))),
                1,
            )

    def test_tampered_confirmation_provenance_is_invalid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            approval = self._confirm(
                root, confirmation_id="HCONF-provenance-0001"
            )
            approval_path = record_path(root, "approval", approval["id"])
            tampered = load_json(approval_path)
            tampered["attestation"]["confirmation_reference"] = "tampered"
            atomic_write_json(approval_path, tampered)

            status, reason = approval_status(root, load_json(approval_path))

            self.assertEqual(status, "INVALID")
            self.assertIn("provenance hash does not match", reason)

    def test_duplicate_confirmation_and_decision_history_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            approval = self._confirm(root, confirmation_id="HCONF-fork-0001")
            clone = load_json(record_path(root, "approval", approval["id"]))
            clone["id"] = "APR-0002"
            clone["record_sequence"] = 2
            atomic_write_json(record_path(root, "approval", "APR-0002"), clone)

            status, reason = approval_status(root, clone)
            current, current_reason = find_current_approval(
                root, subject_id="PLAN-0001", approval_type="PLAN"
            )
            errors = [
                issue
                for issue in validate_project(root)
                if issue.severity == "ERROR"
            ]

            self.assertEqual(status, "INVALID")
            self.assertTrue(
                "decision_id is duplicated" in reason
                or "authority sequence is duplicated" in reason
                or "confirmation_id is duplicated" in reason,
                reason,
            )
            self.assertIsNone(current)
            self.assertIn("INVALID", current_reason)
            self.assertTrue(
                any(issue.code == "INVALID_APPROVAL" for issue in errors),
                [issue.as_dict() for issue in errors],
            )

    def test_apply_plan_decision_transitions_atomically_and_replay_is_noop(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            plan_path = record_path(root, "plan", "PLAN-0001")
            plan = load_json(plan_path)
            plan["status"] = "DECISION_READY"
            plan.pop("decision_ref", None)
            plan.pop("decision_applied_at", None)
            atomic_write_json(plan_path, plan)
            state_path = root / ".harness" / "state.json"
            state = load_json(state_path)
            state["lifecycle_state"] = "DECISION_READY"
            state.pop("active_decision", None)
            atomic_write_json(state_path, state)
            approved_fingerprint = self._fingerprint(root)
            approval = self._confirm(
                root,
                confirmation_id="HCONF-apply-0001",
                confirm_fingerprint=approved_fingerprint,
            )

            first = apply_plan_decision(root, approval_id=approval["id"])
            applied_plan = load_json(plan_path)
            applied_state = load_json(state_path)
            applied_events = [
                load_json(path)
                for path in (root / ".harness" / "events").glob("EVT-*.json")
                if load_json(path).get("event_type") == "PLAN_DECISION_APPLIED"
            ]

            self.assertTrue(first["changed"])
            self.assertEqual(applied_plan["status"], "APPROVED")
            self.assertEqual(applied_plan["decision_ref"], approval["id"])
            self.assertTrue(applied_plan["decision_applied_at"])
            self.assertEqual(applied_state["lifecycle_state"], "APPROVED")
            self.assertEqual(applied_state["active_decision"], approval["id"])
            self.assertEqual(self._fingerprint(root), approved_fingerprint)
            self.assertEqual(len(applied_events), 1)
            self.assertEqual(
                applied_events[0]["payload"]["approval_id"], approval["id"]
            )
            self.assertTrue(task_start_gate(root, "TASK-0001").passed)

            plan_before_replay = load_json(plan_path)
            state_before_replay = load_json(state_path)
            replay = apply_plan_decision(root, approval_id=approval["id"])
            events_after_replay = [
                load_json(path)
                for path in (root / ".harness" / "events").glob("EVT-*.json")
                if load_json(path).get("event_type") == "PLAN_DECISION_APPLIED"
            ]

            self.assertFalse(replay["changed"])
            self.assertEqual(load_json(plan_path), plan_before_replay)
            self.assertEqual(load_json(state_path), state_before_replay)
            self.assertEqual(len(events_after_replay), 1)

    def test_task_capabilities_must_be_within_approval_actions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            self._confirm(
                root,
                confirmation_id="HCONF-scope-0001",
                authorized_actions=["LOCAL_IMPLEMENTATION"],
            )

            gate = task_start_gate(root, "TASK-0001")

            self.assertFalse(gate.passed)
            self.assertTrue(
                any("LOCAL_TESTS" in blocker for blocker in gate.blockers),
                gate.blockers,
            )

    def test_task_cannot_request_its_own_forbidden_action(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            approval = self._confirm(
                root, confirmation_id="HCONF-forbidden-0001"
            )
            apply_plan_decision(root, approval_id=approval["id"])
            task_path = record_path(root, "work_item", "TASK-0001")
            task = load_json(task_path)
            task["forbidden_actions"] = ["LOCAL_IMPLEMENTATION"]
            atomic_write_json(task_path, task)

            preflight = plan_preflight_gate(root, "PLAN-0001")
            gate = task_start_gate(root, "TASK-0001")

            self.assertFalse(preflight.passed)
            self.assertFalse(gate.passed)
            self.assertTrue(
                any("own forbidden actions" in item for item in preflight.blockers),
                preflight.blockers,
            )
            self.assertTrue(
                any("own forbidden actions" in item for item in gate.blockers),
                gate.blockers,
            )

    def test_apply_repairs_partial_state_without_duplicate_event(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            approval = self._confirm(
                root, confirmation_id="HCONF-repair-0001"
            )
            apply_plan_decision(root, approval_id=approval["id"])
            state_path = root / ".harness" / "state.json"
            state = load_json(state_path)
            state["lifecycle_state"] = "DECISION_READY"
            state.pop("active_decision")
            atomic_write_json(state_path, state)

            repaired = apply_plan_decision(root, approval_id=approval["id"])
            events = [
                load_json(path)
                for path in (root / ".harness" / "events").glob("EVT-*.json")
                if load_json(path).get("event_type") == "PLAN_DECISION_APPLIED"
            ]

            self.assertTrue(repaired["changed"])
            self.assertEqual(load_json(state_path)["lifecycle_state"], "APPROVED")
            self.assertEqual(load_json(state_path)["active_decision"], approval["id"])
            self.assertEqual(len(events), 1)

    def test_cancelled_state_cannot_be_reopened_by_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            approval = self._confirm(
                root, confirmation_id="HCONF-cancelled-0001"
            )
            apply_plan_decision(root, approval_id=approval["id"])
            state_path = root / ".harness" / "state.json"
            state = load_json(state_path)
            state["lifecycle_state"] = "CANCELLED"
            atomic_write_json(state_path, state)

            with self.assertRaisesRegex(HarnessError, "cancelled project"):
                apply_plan_decision(root, approval_id=approval["id"])

            self.assertEqual(load_json(state_path)["lifecycle_state"], "CANCELLED")

    def test_new_decision_requires_decision_ready_and_does_not_reuse_old_time(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            first = self._confirm(root, confirmation_id="HCONF-first-0001")
            apply_plan_decision(root, approval_id=first["id"])
            plan_path = record_path(root, "plan", "PLAN-0001")
            state_path = root / ".harness" / "state.json"
            plan = load_json(plan_path)
            plan["status"] = "CLOSED"
            plan["decision_applied_at"] = "2000-01-01T00:00:00Z"
            atomic_write_json(plan_path, plan)
            state = load_json(state_path)
            state["lifecycle_state"] = "CLOSED"
            atomic_write_json(state_path, state)
            second = self._confirm(root, confirmation_id="HCONF-second-0001")

            with self.assertRaisesRegex(HarnessError, "only from DECISION_READY"):
                apply_plan_decision(root, approval_id=second["id"])

            state = load_json(state_path)
            state["lifecycle_state"] = "DECISION_READY"
            atomic_write_json(state_path, state)
            plan = load_json(plan_path)
            plan["status"] = "DECISION_READY"
            atomic_write_json(plan_path, plan)
            applied = apply_plan_decision(root, approval_id=second["id"])

            self.assertNotEqual(applied["applied_at"], "2000-01-01T00:00:00Z")
            self.assertEqual(load_json(plan_path)["decision_ref"], second["id"])

    def test_new_approval_replaces_superseded_active_decision_without_regression(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            first = self._confirm(root, confirmation_id="HCONF-active-0001")
            apply_plan_decision(root, approval_id=first["id"])
            state_path = root / ".harness" / "state.json"
            plan_path = record_path(root, "plan", "PLAN-0001")
            state = load_json(state_path)
            state["lifecycle_state"] = "BUILDING"
            atomic_write_json(state_path, state)
            plan = load_json(plan_path)
            plan["status"] = "ACTIVE"
            atomic_write_json(plan_path, plan)
            self._confirm(
                root,
                confirmation_id="HCONF-revoked-0001",
                decision="REVOKED",
                basis="Owner revoked the first plan decision",
            )
            replacement = self._confirm(
                root,
                confirmation_id="HCONF-active-0002",
                basis="Owner explicitly re-approved the unchanged plan",
            )

            applied = apply_plan_decision(root, approval_id=replacement["id"])

            self.assertTrue(applied["changed"])
            self.assertEqual(applied["plan_status"], "ACTIVE")
            self.assertEqual(applied["lifecycle_state"], "BUILDING")
            self.assertEqual(load_json(plan_path)["decision_ref"], replacement["id"])
            self.assertEqual(
                load_json(state_path)["active_decision"], replacement["id"]
            )
            self.assertTrue(task_start_gate(root, "TASK-0001").passed)

    def test_concurrent_apply_emits_exactly_one_event(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            approval = self._confirm(
                root, confirmation_id="HCONF-concurrent-apply-0001"
            )

            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(
                    executor.map(
                        lambda _index: apply_plan_decision(
                            root, approval_id=approval["id"]
                        ),
                        range(4),
                    )
                )

            events = [
                load_json(path)
                for path in (root / ".harness" / "events").glob("EVT-*.json")
                if load_json(path).get("event_type") == "PLAN_DECISION_APPLIED"
            ]
            self.assertEqual(sum(result["changed"] for result in results), 1)
            self.assertEqual(len(events), 1)

    def test_concurrent_confirmations_receive_unique_ids_and_sequences(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)

            def confirm(index: int) -> dict:
                return self._confirm(
                    root,
                    confirmation_id=f"HCONF-concurrent-{index:04d}",
                )

            with ThreadPoolExecutor(max_workers=4) as executor:
                approvals = list(executor.map(confirm, range(1, 7)))

            approval_ids = {approval["id"] for approval in approvals}
            record_sequences = {
                approval["record_sequence"] for approval in approvals
            }
            authority_sequences = {
                approval["authority_sequence"] for approval in approvals
            }
            self.assertEqual(len(approval_ids), 6)
            self.assertEqual(record_sequences, set(range(1, 7)))
            self.assertEqual(authority_sequences, set(range(1, 7)))

    def test_shared_marker_supersedes_stale_linked_worktree_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            container = Path(temp)
            root = create_ready_project(container / "main", approve=False)
            linked = container / "linked"
            self._git(root, "init", "-b", "main")
            self._git(root, "config", "user.name", "Harness Test")
            self._git(root, "config", "user.email", "harness@example.invalid")
            self._git(root, "config", "core.autocrlf", "true")
            self._git(root, "add", "--all")
            self._git(root, "commit", "-m", "fixture baseline")

            approval = self._confirm(root)
            apply_plan_decision(root, approval_id=approval["id"])
            self._git(root, "add", "--all")
            self._git(root, "commit", "-m", "fixture approval")
            self._git(root, "worktree", "add", "-b", "linked", str(linked))
            try:
                linked_approval = load_json(
                    linked / ".harness" / "approvals" / f"{approval['id']}.json"
                )
                snapshot_entry = linked_approval["snapshot_manifest"][0]
                linked_snapshot = linked / snapshot_entry["snapshot_path"]
                self.assertNotEqual(
                    sha256_file(linked_snapshot), snapshot_entry["sha256"]
                )
                status, reason = approval_status(linked, linked_approval)
                self.assertEqual(status, "CURRENT", reason)

                with self.assertRaisesRegex(
                    HarnessError, "primary integration worktree"
                ):
                    self._confirm(
                        linked,
                        confirmation_id="HCONF-linked-write-0001",
                    )

                revoked = self._confirm(
                    root,
                    confirmation_id="HCONF-revoked-0001",
                    decision="REVOKED",
                )

                self.assertEqual(approval["authority_sequence"], 1)
                self.assertEqual(revoked["authority_sequence"], 2)
                status, reason = approval_status(linked, linked_approval)
                self.assertEqual(status, "SUPERSEDED")
                self.assertIn("shared procedural decision", reason)
                current, current_reason = find_current_approval(
                    linked,
                    subject_id="PLAN-0001",
                    approval_type="PLAN",
                )
                self.assertIsNone(current)
                self.assertIn("SUPERSEDED", current_reason)
                for directory in (
                    "artifacts",
                    "open-items",
                    "evidence",
                    "changes",
                    "results",
                    "reviews",
                    "handoffs",
                    "recoveries",
                ):
                    (linked / ".harness" / directory).mkdir(
                        parents=True, exist_ok=True
                    )
                gate = task_start_gate(linked, "TASK-0001")
                self.assertFalse(gate.passed)
                self.assertTrue(
                    any("SUPERSEDED" in blocker for blocker in gate.blockers),
                    gate.blockers,
                )
            finally:
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(root),
                        "worktree",
                        "remove",
                        "--force",
                        str(linked),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )


if __name__ == "__main__":
    unittest.main()
