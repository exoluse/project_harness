from __future__ import annotations

import tempfile
from pathlib import Path

from project_harness.collaboration import acquire_claim
from project_harness.core import (
    HarnessError,
    atomic_write_json,
    load_json,
    record_path,
)
from project_harness.gates import task_start_gate
from project_harness.lifecycle_mutations import transition_project, transition_record
from project_harness.mutation_service import authorize_claim_targets
from project_harness.reporting import doctor_report, status_report
from project_harness.scaffold import init_project

from .helpers import HarnessTestCase, create_ready_project


class ExecutionPolicyTests(HarnessTestCase):
    def _enable_single_writer_mode(self, root: Path) -> None:
        project_path = root / ".harness" / "project.json"
        project = load_json(project_path)
        project["policy"].update(
            {
                "claim_mode": "WHEN_CONCURRENT",
            }
        )
        atomic_write_json(project_path, project)
    def test_new_project_defaults_to_human_plan_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_project(Path(temp) / "demo", "DEMO", "Demo")

            project = load_json(root / ".harness" / "project.json")
            self.assertEqual(project["policy"]["execution_mode"], "PLAN_GATED")
            self.assertEqual(project["policy"]["claim_mode"], "WHEN_CONCURRENT")
            self.assertEqual(project["policy"]["record_mode"], "ON_DEMAND")
            self.assertIn("PLAN", project["policy"]["human_approval_required_for"])
            state = load_json(root / ".harness" / "state.json")
            self.assertIsNone(state["current_plan"])
            self.assertEqual(list((root / ".harness" / "plans").glob("PLAN-*")), [])
            self.assertEqual(
                list((root / ".harness" / "work-items").glob("TASK-*")),
                [],
            )
            with self.assertRaisesRegex(HarnessError, "Missing work_item"):
                task_start_gate(root, "TASK-0001")
            self.assertEqual(
                doctor_report(root)["plan_approval_assurance"]["required"],
                "PROCEDURAL",
            )

    def test_task_cannot_run_without_human_plan_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo", approve=False)

            gate = task_start_gate(root, "TASK-0001")

            self.assertFalse(gate.passed)
            self.assertIn("no PLAN decision for PLAN-0001", gate.blockers)

    def test_discovery_without_plan_or_task_validates_but_execution_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_project(Path(temp) / "demo", "DEMO", "Demo")
            from project_harness.validation import validate_project

            atomic_write_json(
                record_path(root, "source", "SRC-0001"),
                {
                    "schema": "harness.source/v1",
                    "id": "SRC-0001",
                    "kind": "source",
                    "authority": "RAW_INPUT",
                    "artifact_role": "REFERENCE",
                    "interpretation_status": "EXPLICIT",
                    "origin": "user discovery request",
                    "summary": "Discovery can be recorded before planning.",
                },
            )
            self.assertEqual(validate_project(root), [])

            state_path = root / ".harness" / "state.json"
            state = load_json(state_path)
            state["lifecycle_state"] = "BUILDING"
            atomic_write_json(state_path, state)

            codes = {issue.code for issue in validate_project(root)}
            self.assertIn("MISSING_CURRENT_PLAN", codes)
            self.assertIn("MISSING_WORK_ITEM", codes)

            state["lifecycle_state"] = "APPROVED"
            atomic_write_json(state_path, state)
            with self.assertRaisesRegex(HarnessError, "active plan"):
                transition_project(
                    root,
                    claim_id=None,
                    agent="codex",
                    target_state="BUILDING",
                    reason="Execution requires its structure",
                )

    def test_task_must_be_listed_by_its_current_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            plan_path = record_path(root, "plan", "PLAN-0001")
            plan = load_json(plan_path)
            plan["approval_subject"]["work_item_refs"] = []
            plan["approval_dependencies"] = [
                value
                for value in plan["approval_dependencies"]
                if "TASK-0001" not in value
            ]
            atomic_write_json(plan_path, plan)

            gate = task_start_gate(root, "TASK-0001")

            self.assertFalse(gate.passed)
            self.assertTrue(
                any("not listed" in blocker for blocker in gate.blockers),
                gate.blockers,
            )

    def test_claimless_transition_is_allowed_when_no_concurrent_owner_exists(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            self._enable_single_writer_mode(root)

            result = transition_record(
                root,
                claim_id=None,
                agent="codex",
                kind="work_item",
                record_id="TASK-0001",
                target_status="RUNNING",
                reason="Approved plan allows implementation",
            )

            self.assertEqual(result["record"]["status"], "RUNNING")
            self.assertTrue(str(result["transaction"]["event_id"]).startswith("EVT-"))

    def test_claimless_mutation_fails_when_a_concurrent_claim_overlaps(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            self._enable_single_writer_mode(root)
            acquire_claim(
                root,
                agent="codex",
                task_id="TASK-0001",
                paths=["src"],
            )

            with self.assertRaisesRegex(HarnessError, "overlaps active ownership"):
                authorize_claim_targets(
                    root,
                    claim_id=None,
                    agent="claude",
                    targets=["src/core.py"],
                )

    def test_destructive_capability_still_requires_cryptographic_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            task_path = record_path(root, "work_item", "TASK-0001")
            task = load_json(task_path)
            task["capabilities"].append("DESTRUCTIVE_CLEANUP")
            atomic_write_json(task_path, task)

            gate = task_start_gate(root, "TASK-0001")

            self.assertFalse(gate.passed)
            self.assertTrue(
                any("DESTRUCTIVE_ACTION approval refs" in item for item in gate.blockers)
            )
