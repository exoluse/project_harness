from __future__ import annotations

import tempfile
from pathlib import Path

from project_harness.approvals import record_approval
from project_harness.collaboration import acquire_claim
from project_harness.core import atomic_write_json, load_json, record_path
from project_harness.gates import feature_completion_gate
from project_harness.lifecycle import apply_plan_decision
from project_harness.mutations import (
    AtomicMutationService,
    record_evidence,
    transition_record,
)
from project_harness.validation import validate_project

from .helpers import HarnessTestCase, create_ready_project, init_harness


def approve_fixture(root: Path) -> None:
    approval = record_approval(
        root,
        approval_type="PLAN",
        subject_path=".harness/plans/PLAN-0001.md",
        decision="APPROVED",
        approver="human-test-owner",
        authority_role="HUMAN_PROJECT_OWNER",
        basis="Fixture authorizes local implementation and tests",
        conditions=[],
        authorized_actions=["LOCAL_IMPLEMENTATION", "LOCAL_TESTS"],
        excluded_actions=["PRODUCTION_DEPLOYMENT"],
        attestation={"mode": "TEST_MOCK"},
    )
    apply_plan_decision(root, approval_id=approval["id"])


class MutationTests(HarnessTestCase):
    def test_mutation_facade_preserves_authority_boundaries(self):
        self.assertEqual(
            AtomicMutationService.__module__, "project_harness.mutation_service"
        )
        self.assertEqual(record_evidence.__module__, "project_harness.evidence_mutations")
        self.assertEqual(
            transition_record.__module__, "project_harness.lifecycle_mutations"
        )

    def test_project_transition_requires_current_plan_and_updates_state_atomically(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            task_path = record_path(root, "work_item", "TASK-0001")
            task = load_json(task_path)
            task["write_scope"].append(".harness/state.json")
            atomic_write_json(task_path, task)
            approve_fixture(root)
            claim = acquire_claim(
                root,
                agent="codex",
                task_id="TASK-0001",
                paths=[".harness/state.json"],
            )

            result = transition_record(
                root,
                claim_id=claim["id"],
                agent="codex",
                kind="project",
                record_id="TESTPROJ",
                target_status="BUILDING",
                reason="Approved implementation started",
            )

            self.assertEqual(result["record"]["lifecycle_state"], "BUILDING")
            self.assertEqual(
                load_json(root / ".harness" / "state.json")["lifecycle_state"],
                "BUILDING",
            )

    def test_atomic_mutation_rolls_back_every_target_on_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            project_path = root / ".harness" / "project.json"
            original = load_json(project_path)
            changed = {**original, "name": "Changed"}

            with self.assertRaisesRegex(OSError, "injected"):
                AtomicMutationService(root).apply(
                    writes={".harness/project.json": changed},
                    event_type="TEST_MUTATION",
                    event_payload={"test": True},
                    fail_after_writes=2,
                )

            self.assertEqual(load_json(project_path), original)
            self.assertEqual(list((root / ".harness" / "events").glob("EVT-*.json")), [])

    def test_evidence_record_updates_evidence_and_criterion_together(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            task_path = record_path(root, "work_item", "TASK-0001")
            task = load_json(task_path)
            task["write_scope"].extend(
                [".harness/evidence", ".harness/features/FUNC-0001.json"]
            )
            atomic_write_json(task_path, task)
            approve_fixture(root)
            source = root / "src" / "core.py"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("value = 1\n", encoding="utf-8")
            claim = acquire_claim(
                root,
                agent="codex",
                task_id="TASK-0001",
                paths=[".harness/evidence", ".harness/features/FUNC-0001.json"],
            )

            result = record_evidence(
                root,
                claim_id=claim["id"],
                agent="codex",
                claim_text="Integration behavior observed",
                supports=["AC-FUNC-0001-001"],
                profile="INTEGRATION",
                method="python -m unittest",
                environment="temporary test repository",
                expected="Required behavior passes",
                actual="Required behavior passed",
                result="VERIFIED",
                ambiguity_level="NONE",
                ambiguity_reasons=[],
                binding_paths=["src"],
                limitations=["No production execution"],
            )

            evidence_id = result["evidence"]["id"]
            feature = load_json(record_path(root, "feature", "FUNC-0001"))
            self.assertIn(
                evidence_id,
                feature["completion_criteria"][0]["evidence_refs"],
            )
            self.assertTrue(feature_completion_gate(root, "FUNC-0001").passed)
            self.assertFalse(
                [issue for issue in validate_project(root) if issue.severity == "ERROR"]
            )

    def test_rework_resume_uses_a_separate_control_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)
            task_one_path = record_path(root, "work_item", "TASK-0001")
            task_one = load_json(task_one_path)
            task_one["status"] = "FAILED"
            atomic_write_json(task_one_path, task_one)

            task_two = {
                **task_one,
                "id": "TASK-0002",
                "title": "Control rework transitions",
                "status": "READY",
                "write_scope": [".harness/work-items/TASK-0001.md"],
                "logical_locks": ["task-lifecycle"],
            }
            atomic_write_json(record_path(root, "work_item", "TASK-0002"), task_two)
            plan_path = record_path(root, "plan", "PLAN-0001")
            plan = load_json(plan_path)
            plan["approval_subject"]["work_item_refs"].append("TASK-0002")
            plan["approval_dependencies"].append(
                ".harness/work-items/TASK-0002.md"
            )
            atomic_write_json(plan_path, plan)
            approve_fixture(root)
            claim = acquire_claim(
                root,
                agent="coordinator",
                task_id="TASK-0002",
                paths=[".harness/work-items/TASK-0001.md"],
            )

            result = transition_record(
                root,
                claim_id=claim["id"],
                agent="coordinator",
                kind="work_item",
                record_id="TASK-0001",
                target_status="READY",
                reason="A corrected attempt is authorized",
                rework=True,
            )

            self.assertEqual(result["record"]["status"], "READY")
            self.assertEqual(
                load_json(task_one_path)["rework"]["reason"],
                "A corrected attempt is authorized",
            )
