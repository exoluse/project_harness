from __future__ import annotations

import tempfile
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from project_harness.approvals import approval_status
from project_harness.core import atomic_write_json, load_json, record_path
from project_harness.gates import (
    feature_completion_gate,
    plan_preflight_gate,
    task_start_gate,
)
from project_harness.scaffold import init_project

from .helpers import HarnessTestCase, add_verified_evidence, create_ready_project, write_record


class ApprovalGateTests(HarnessTestCase):
    def test_declared_blocked_by_is_enforced_without_reverse_open_item_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            task_path = record_path(root, "work_item", "TASK-0001")
            task = load_json(task_path)
            task["blocked_by"] = ["OI-0001"]
            atomic_write_json(task_path, task)
            write_record(
                root,
                "open_item",
                "OI-0001",
                {
                    "schema": "harness.open_item/v1",
                    "id": "OI-0001",
                    "kind": "open_item",
                    "title": "Explicit task blocker",
                    "category": "DEPENDENCY",
                    "gate_level": "G3",
                    "status": "OPEN",
                    "owner": "coordinator",
                    "decision_authority": "HUMAN_PROJECT_OWNER",
                    "affects": [],
                    "blocks": [],
                    "if_unresolved": "TASK-0001 must not start",
                    "resolution": None,
                },
            )

            gate = task_start_gate(root, "TASK-0001")
            self.assertFalse(gate.passed)
            self.assertIn(
                "declared blocker OI-0001 is unresolved",
                gate.blockers,
            )

    def test_plan_preflight_and_authorization_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            self.assertTrue(plan_preflight_gate(root, "PLAN-0001").passed)
            self.assertTrue(
                plan_preflight_gate(root, "PLAN-0001", require_approval=True).passed
            )

    def test_task_scope_change_makes_plan_approval_stale(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            task_path = record_path(root, "work_item", "TASK-0001")
            task = load_json(task_path)
            task["write_scope"].append("docs")
            atomic_write_json(task_path, task)
            approval = load_json(record_path(root, "approval", "APR-0001"))
            status, _reason = approval_status(root, approval)
            self.assertEqual(status, "STALE")
            self.assertFalse(
                plan_preflight_gate(root, "PLAN-0001", require_approval=True).passed
            )

    def test_feature_requires_current_unambiguous_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            self.assertFalse(feature_completion_gate(root, "FUNC-0001").passed)
            add_verified_evidence(root, bind=True)
            self.assertTrue(feature_completion_gate(root, "FUNC-0001").passed)
            (root / "artifacts" / "test-result.txt").write_text("changed\n", encoding="utf-8")
            self.assertFalse(feature_completion_gate(root, "FUNC-0001").passed)

    def test_medium_ambiguity_cannot_complete_feature(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root, ambiguity="MEDIUM")
            self.assertFalse(feature_completion_gate(root, "FUNC-0001").passed)

    def test_wrong_profile_or_stale_criterion_cannot_complete_feature(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            evidence_path = add_verified_evidence(root)
            evidence = load_json(evidence_path)
            evidence["profile"] = "STATIC"
            atomic_write_json(evidence_path, evidence)
            self.assertFalse(feature_completion_gate(root, "FUNC-0001").passed)

            evidence["profile"] = "INTEGRATION"
            atomic_write_json(evidence_path, evidence)
            feature_path = record_path(root, "feature", "FUNC-0001")
            feature = load_json(feature_path)
            feature["completion_criteria"][0]["statement"] = "Changed behavior"
            atomic_write_json(feature_path, feature)
            self.assertFalse(feature_completion_gate(root, "FUNC-0001").passed)

    def test_latest_revocation_overrides_earlier_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            from project_harness.approvals import record_approval

            record_approval(
                root,
                approval_type="PLAN",
                subject_path=".harness/plans/PLAN-0001.json",
                decision="REVOKED",
                approver="human-test-owner",
                authority_role="HUMAN_PROJECT_OWNER",
                basis="Implementation authorization withdrawn",
                attestation={"mode": "TEST_MOCK"},
            )
            old_approval_path = record_path(root, "approval", "APR-0001")
            old_approval = load_json(old_approval_path)
            old_approval["recorded_at"] = "2999-01-01T00:00:00Z"
            atomic_write_json(old_approval_path, old_approval)
            self.assertFalse(
                plan_preflight_gate(root, "PLAN-0001", require_approval=True).passed
            )

    def test_approval_type_cannot_target_the_wrong_record_kind(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            from project_harness.approvals import record_approval
            from project_harness.core import HarnessError

            with self.assertRaises(HarnessError):
                record_approval(
                    root,
                    approval_type="PLAN",
                    subject_path=".harness/project.json",
                    decision="APPROVED",
                    approver="human-test-owner",
                    authority_role="HUMAN_PROJECT_OWNER",
                    basis="wrong target",
                )

    def test_fresh_project_cannot_be_approved_for_closure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_project(Path(temp) / "demo", "DEMO", "Demo")
            from project_harness.approvals import record_approval
            from project_harness.core import HarnessError

            with self.assertRaises(HarnessError):
                record_approval(
                    root,
                    approval_type="PROJECT_CLOSURE",
                    subject_path=".harness/project.json",
                    decision="APPROVED",
                    approver="human-test-owner",
                    authority_role="HUMAN_PROJECT_OWNER",
                    basis="premature closure",
                )

    @unittest.skipUnless(shutil.which("ssh-keygen"), "ssh-keygen is required")
    def test_signed_human_approval_is_verified_against_external_trust(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = create_ready_project(base / "demo", approve=False)
            trust = base / "external-trust"
            trust.mkdir()
            key = trust / "owner-key"
            generated = subprocess.run(
                ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(generated.returncode, 0, generated.stdout)
            public_parts = (key.with_suffix(".pub")).read_text(encoding="utf-8").split()
            allowed = trust / "allowed_signers"
            allowed.write_text(
                f"human-test-owner {public_parts[0]} {public_parts[1]}\n",
                encoding="utf-8",
            )
            ledger = trust / "ledger"
            ledger.mkdir()
            authority_config = trust / "authority.json"
            from project_harness.approvals import (
                prepare_approval_request,
                record_signed_approval,
            )
            from project_harness.core import sha256_file

            atomic_write_json(
                authority_config,
                {
                    "schema": "harness.authority/v1",
                    "project_id": "TESTPROJ",
                    "authority_id": "test-owner-ledger",
                    "repository_root": str(root.resolve()),
                    "protection": "OS_ACL_OR_EXTERNAL_BROKER",
                    "signature_namespace": "project-harness",
                    "allowed_signers_path": str(allowed.resolve()),
                    "allowed_signers_sha256": sha256_file(allowed),
                    "decision_ledger_path": str(ledger.resolve()),
                    "approval_types": [
                        "PLAN",
                        "CUSTOMER_ACCEPTANCE",
                        "PROJECT_CLOSURE",
                        "CHANGE",
                        "PRODUCTION_DEPLOYMENT",
                        "PRODUCTION_DATA_CHANGE",
                        "EXCEPTION",
                    ],
                },
            )
            project_path = root / ".harness" / "project.json"
            project = load_json(project_path)
            project["policy"]["approval_identity_mode"] = "TEST_ONLY_UNAUTHENTICATED"
            atomic_write_json(project_path, project)

            request_relative = ".harness/decisions/PLAN-0001.request.json"
            self._approval_verifier_patcher.stop()
            try:
                with patch(
                    "project_harness.approvals.authority_config_path",
                    return_value=authority_config,
                ):
                    prepare_approval_request(
                        root,
                        output_path=request_relative,
                        approval_type="PLAN",
                        subject_path=".harness/plans/PLAN-0001.json",
                        decision="APPROVED",
                        approver="human-test-owner",
                        authority_role="HUMAN_PROJECT_OWNER",
                        basis="Signed local implementation authorization",
                        authorized_actions=["LOCAL_IMPLEMENTATION", "LOCAL_TESTS"],
                        excluded_actions=["PRODUCTION_DEPLOYMENT"],
                    )
                    request_path = root / request_relative
                    signed = subprocess.run(
                        [
                            "ssh-keygen",
                            "-Y",
                            "sign",
                            "-f",
                            str(key),
                            "-n",
                            "project-harness",
                            str(request_path),
                        ],
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertEqual(signed.returncode, 0, signed.stdout)
                    signature_path = Path(str(request_path) + ".sig")
                    shutil.copy2(request_path, ledger / "000001.request.json")
                    shutil.copy2(signature_path, ledger / "000001.request.json.sig")
                    approval = record_signed_approval(
                        root,
                        request_path=request_relative,
                        signature_path=request_relative + ".sig",
                    )
                    self.assertEqual(approval_status(root, approval)[0], "CURRENT")
                    revoke_relative = ".harness/decisions/PLAN-0001.revoke.request.json"
                    prepare_approval_request(
                        root,
                        output_path=revoke_relative,
                        approval_type="PLAN",
                        subject_path=".harness/plans/PLAN-0001.json",
                        decision="REVOKED",
                        approver="human-test-owner",
                        authority_role="HUMAN_PROJECT_OWNER",
                        basis="Protected authority revokes implementation",
                    )
                    revoke_path = root / revoke_relative
                    revoked = subprocess.run(
                        [
                            "ssh-keygen",
                            "-Y",
                            "sign",
                            "-f",
                            str(key),
                            "-n",
                            "project-harness",
                            str(revoke_path),
                        ],
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertEqual(revoked.returncode, 0, revoked.stdout)
                    revoke_signature = Path(str(revoke_path) + ".sig")
                    shutil.copy2(revoke_path, ledger / "000002.request.json")
                    shutil.copy2(
                        revoke_signature, ledger / "000002.request.json.sig"
                    )
                    self.assertEqual(
                        approval_status(root, approval)[0], "SUPERSEDED"
                    )
                    config = load_json(authority_config)
                    config["allowed_signers_sha256"] = "0" * 64
                    atomic_write_json(authority_config, config)
                    self.assertEqual(approval_status(root, approval)[0], "INVALID")
            finally:
                self._approval_verifier_patcher.start()

    def test_g0_blocks_plan_and_g1_blocks_feature(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            open_item = {
                "schema": "harness.open_item/v1",
                "id": "OI-0001",
                "kind": "open_item",
                "title": "Critical unknown",
                "category": "EVIDENCE_AMBIGUITY",
                "gate_level": "G1",
                "status": "OPEN",
                "owner": "human",
                "decision_authority": "human",
                "affects": ["FUNC-0001"],
                "blocks": ["AC-FUNC-0001-001"],
                "if_unresolved": "feature remains incomplete",
                "resolution": None,
            }
            write_record(root, "open_item", "OI-0001", open_item)
            self.assertFalse(feature_completion_gate(root, "FUNC-0001").passed)
            open_item["gate_level"] = "G0"
            atomic_write_json(record_path(root, "open_item", "OI-0001"), open_item)
            self.assertFalse(plan_preflight_gate(root, "PLAN-0001").passed)

    def test_unknown_open_item_status_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            open_item = {
                "schema": "harness.open_item/v1",
                "id": "OI-0001",
                "kind": "open_item",
                "title": "Malformed blocker",
                "category": "REQUIREMENT",
                "gate_level": "G1",
                "status": "TYPO_CLOSED",
                "owner": "human",
                "decision_authority": "human",
                "affects": ["TASK-0001"],
                "blocks": ["TASK-0001"],
                "if_unresolved": "task must stop",
                "resolution": None,
            }
            write_record(root, "open_item", "OI-0001", open_item)
            gate = task_start_gate(root, "TASK-0001")
            self.assertFalse(gate.passed)
            self.assertTrue(
                any(
                    "SCHEMA_VIOLATION" in item and "status" in item
                    for item in gate.blockers
                ),
                gate.blockers,
            )

    def test_unrelated_missing_ui_artifact_does_not_block_backend_task(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            now = "2026-01-01T00:00:00Z"
            write_record(
                root,
                "source",
                "SRC-0002",
                {
                    "schema": "harness.source/v1",
                    "id": "SRC-0002",
                    "kind": "source",
                    "title": "Future UI delivery",
                    "authority": "RAW_INPUT",
                    "artifact_role": "VISUAL_BASELINE",
                    "interpretation_status": "UNKNOWN",
                    "origin": "customer",
                    "summary": "UI is expected later",
                    "created_at": now,
                },
            )
            write_record(
                root,
                "artifact",
                "ART-0001",
                {
                    "schema": "harness.artifact/v1",
                    "id": "ART-0001",
                    "kind": "artifact",
                    "title": "Pending storyboard",
                    "source_ref": "SRC-0002",
                    "path": "inputs/ui/storyboard.png",
                    "sha256": "0" * 64,
                    "media_type": "image/png",
                    "artifact_role": "VISUAL_BASELINE",
                    "execution_trust": "UNTRUSTED",
                    "safe_to_execute": False,
                    "created_at": now,
                },
            )
            self.assertTrue(task_start_gate(root, "TASK-0001").passed)

    def test_newer_failed_evidence_overrides_older_verified_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            first_path = add_verified_evidence(root)
            failed = load_json(first_path)
            failed["id"] = "EVD-0002"
            failed["title"] = "New failed integration observation"
            failed["result"] = "FAILED"
            failed["actual"] = "required behavior was not observed"
            write_record(root, "evidence", "EVD-0002", failed)
            self.assertFalse(feature_completion_gate(root, "FUNC-0001").passed)


if __name__ == "__main__":
    unittest.main()
