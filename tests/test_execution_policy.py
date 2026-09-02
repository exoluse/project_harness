from __future__ import annotations

import tempfile
from pathlib import Path

from project_harness.core import atomic_write_json, load_json, record_path
from project_harness.gates import task_start_gate
from project_harness.lifecycle_mutations import transition_record
from project_harness.reporting import doctor_report, status_report
from project_harness.scaffold import init_project

from .helpers import HarnessTestCase, create_ready_project


class ExecutionPolicyTests(HarnessTestCase):
    def _enable_user_directed(self, root: Path) -> None:
        project_path = root / ".harness" / "project.json"
        project = load_json(project_path)
        project["policy"].update(
            {
                "execution_mode": "USER_DIRECTED",
                "claim_mode": "WHEN_CONCURRENT",
                "record_mode": "ON_DEMAND",
                "human_approval_required_for": [
                    "PRODUCTION_DEPLOYMENT",
                    "PRODUCTION_DATA_CHANGE",
                    "DESTRUCTIVE_ACTION",
                    "SECRET_ACCESS",
                    "CUSTOMER_ACCEPTANCE",
                ],
                "approval_assurance": {
                    "default": "PROCEDURAL",
                    "by_type": {
                        "PRODUCTION_DEPLOYMENT": "CRYPTOGRAPHIC",
                        "PRODUCTION_DATA_CHANGE": "CRYPTOGRAPHIC",
                        "DESTRUCTIVE_ACTION": "CRYPTOGRAPHIC",
                        "SECRET_ACCESS": "CRYPTOGRAPHIC",
                        "CUSTOMER_ACCEPTANCE": "CRYPTOGRAPHIC",
                    },
                },
            }
        )
        atomic_write_json(project_path, project)
        state_path = root / ".harness" / "state.json"
        state = load_json(state_path)
        state["active_plan"] = None
        state["active_decision"] = None
        atomic_write_json(state_path, state)

    def test_new_project_defaults_to_user_directed_on_demand_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_project(Path(temp) / "demo", "DEMO", "Demo")

            project = load_json(root / ".harness" / "project.json")
            self.assertEqual(project["policy"]["execution_mode"], "USER_DIRECTED")
            self.assertEqual(project["policy"]["claim_mode"], "WHEN_CONCURRENT")
            self.assertEqual(project["policy"]["record_mode"], "ON_DEMAND")
            self.assertNotIn("PLAN", project["policy"]["human_approval_required_for"])
            self.assertEqual(
                doctor_report(root)["plan_approval_assurance"]["required"],
                "NOT_REQUIRED",
            )

    def test_task_runs_without_active_plan_or_plan_approval_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            self._enable_user_directed(root)
            task_path = record_path(root, "work_item", "TASK-0001")
            task = load_json(task_path)
            task["capabilities"].append("EXTERNAL_WRITE")
            atomic_write_json(task_path, task)

            gate = task_start_gate(root, "TASK-0001")

            self.assertTrue(gate.passed, gate.blockers)
            self.assertIsNone(status_report(root)["active_plan"])

    def test_claimless_transition_is_allowed_when_no_concurrent_owner_exists(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            self._enable_user_directed(root)

            result = transition_record(
                root,
                claim_id=None,
                agent="codex",
                kind="work_item",
                record_id="TASK-0001",
                target_status="RUNNING",
                reason="Explicit user-directed implementation",
            )

            self.assertEqual(result["record"]["status"], "RUNNING")
            self.assertTrue(str(result["transaction"]["event_id"]).startswith("EVT-"))
