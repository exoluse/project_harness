from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from project_harness.authoring import activate_plan, create_work_item, sync_plan
from project_harness.core import HarnessError, atomic_write_json, load_json, record_path
from project_harness.gates import task_start_gate
from project_harness.guidance import next_step
from project_harness.lifecycle_mutations import transition_record
from project_harness.scaffold import new_record
from project_harness.validation import validate_project

from .helpers import init_harness


def _plan(root: Path, plan_id: str = "PLAN-0001") -> dict:
    return load_json(record_path(root, "plan", plan_id))


def _write_plan(root: Path, plan_id: str, title: str) -> dict:
    record = new_record("plan", plan_id, title)
    atomic_write_json(record_path(root, "plan", plan_id), record)
    return record


class AuthoringTests(unittest.TestCase):
    """A newly initialized project must receive a human PLAN decision."""

    def test_new_plan_authorizes_routine_work_and_excludes_high_risk(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            subject = _write_plan(root, "PLAN-0001", "Login")["approval_subject"]
            self.assertEqual(
                subject["authorized_actions"],
                ["DOCUMENTATION", "LOCAL_IMPLEMENTATION", "LOCAL_TESTS"],
            )
            self.assertIn("PRODUCTION_DEPLOYMENT", subject["excluded_actions"])
            self.assertIn("SECRET_ACCESS", subject["excluded_actions"])

    def test_new_feature_is_a_warning_until_it_is_specified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            feature = new_record("feature", "FUNC-0001", "Login")
            path = record_path(root, "feature", "FUNC-0001")
            atomic_write_json(path, feature)
            codes = {(i.severity, i.code) for i in validate_project(root)}
            self.assertIn(("WARNING", "MISSING_COMPLETION_CONTRACT"), codes)
            self.assertNotIn(("ERROR", "MISSING_COMPLETION_CONTRACT"), codes)

            feature["status"] = "SPECIFIED"
            atomic_write_json(path, feature)
            codes = {(i.severity, i.code) for i in validate_project(root)}
            self.assertIn(("ERROR", "MISSING_COMPLETION_CONTRACT"), codes)

    def test_create_work_item_links_both_sides_of_the_plan_relationship(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            _write_plan(root, "PLAN-0001", "Login")
            created = create_work_item(
                root,
                task_id="TASK-0001",
                title="Implement login",
                plan_id="PLAN-0001",
                capabilities=["LOCAL_IMPLEMENTATION"],
            )
            task = created["record"]
            self.assertEqual(task["plan_id"], "PLAN-0001")
            plan = _plan(root)
            self.assertEqual(plan["approval_subject"]["work_item_refs"], ["TASK-0001"])
            self.assertIn(
                ".harness/work-items/TASK-0001.md", plan["approval_dependencies"]
            )
            self.assertEqual(
                created["added_dependencies"], [".harness/work-items/TASK-0001.md"]
            )

    def test_create_work_item_rejects_capabilities_the_plan_does_not_authorize(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            _write_plan(root, "PLAN-0001", "Login")
            with self.assertRaises(HarnessError) as caught:
                create_work_item(
                    root,
                    task_id="TASK-0001",
                    title="Deploy",
                    plan_id="PLAN-0001",
                    capabilities=["PRODUCTION_DEPLOYMENT"],
                )
            self.assertIn("does not authorize", str(caught.exception))
            self.assertFalse(record_path(root, "work_item", "TASK-0001").exists())

    def test_create_work_item_requires_an_existing_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            with self.assertRaises(HarnessError) as caught:
                create_work_item(
                    root, task_id="TASK-0001", title="Login", plan_id="PLAN-0009"
                )
            self.assertIn("PLAN-0009 does not exist", str(caught.exception))

    def test_activate_plan_is_refused_without_a_human_decision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            _write_plan(root, "PLAN-0001", "Login")
            create_work_item(
                root, task_id="TASK-0001", title="Login", plan_id="PLAN-0001"
            )
            with self.assertRaisesRegex(HarnessError, "human approval"):
                activate_plan(root, plan_id="PLAN-0001")

    def test_activate_plan_cannot_bypass_the_approval_workflow(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            for plan_id in ("PLAN-0001", "PLAN-0002"):
                _write_plan(root, plan_id, plan_id)
            create_work_item(
                root, task_id="TASK-0001", title="One", plan_id="PLAN-0001"
            )
            create_work_item(
                root, task_id="TASK-0002", title="Two", plan_id="PLAN-0002"
            )
            with self.assertRaisesRegex(HarnessError, "human approval"):
                activate_plan(root, plan_id="PLAN-0001")

    def test_activate_plan_requires_a_task(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            _write_plan(root, "PLAN-0001", "Login")
            with self.assertRaises(HarnessError) as caught:
                activate_plan(root, plan_id="PLAN-0001")
            self.assertIn("human approval", str(caught.exception))
            self.assertEqual(_plan(root)["status"], "DRAFT")

    def test_execution_mode_cannot_restore_direct_plan_activation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            _write_plan(root, "PLAN-0001", "Login")
            create_work_item(
                root, task_id="TASK-0001", title="Login", plan_id="PLAN-0001"
            )
            with self.assertRaises(HarnessError) as caught:
                activate_plan(root, plan_id="PLAN-0001")
            self.assertIn("apply-decision", str(caught.exception))

    def test_sync_plan_restores_hand_removed_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            _write_plan(root, "PLAN-0001", "Login")
            create_work_item(
                root, task_id="TASK-0001", title="Login", plan_id="PLAN-0001"
            )
            plan_path = record_path(root, "plan", "PLAN-0001")
            plan = load_json(plan_path)
            plan["approval_dependencies"] = []
            atomic_write_json(plan_path, plan)

            result = sync_plan(root, plan_id="PLAN-0001")
            self.assertTrue(result["changed"])
            self.assertEqual(
                load_json(plan_path)["approval_dependencies"],
                [".harness/work-items/TASK-0001.md"],
            )
            self.assertFalse(sync_plan(root, plan_id="PLAN-0001")["changed"])


class GuidanceTests(unittest.TestCase):
    def test_fresh_drafts_need_planning_detail_before_owner_decision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")

            self.assertEqual(next_step(root)["state"], "NEEDS_PLAN")
            _write_plan(root, "PLAN-0001", "Login")

            step = next_step(root)
            self.assertEqual(step["state"], "NEEDS_TASK")
            self.assertIn("--plan PLAN-0001", step["commands"][0])
            create_work_item(
                root,
                task_id="TASK-0001",
                title="Implement login",
                plan_id="PLAN-0001",
                capabilities=["LOCAL_IMPLEMENTATION"],
            )

            step = next_step(root)
            self.assertEqual(step["state"], "NEEDS_PLAN_DETAIL")
            self.assertTrue(any("report decision-package" in command for command in step["commands"]))

    def test_next_points_at_the_repair_command_for_derived_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            _write_plan(root, "PLAN-0001", "Login")
            create_work_item(
                root, task_id="TASK-0001", title="Login", plan_id="PLAN-0001"
            )
            plan_path = record_path(root, "plan", "PLAN-0001")
            plan = load_json(plan_path)
            plan["approval_dependencies"] = []
            atomic_write_json(plan_path, plan)

            step = next_step(root)
            self.assertEqual(step["state"], "PROJECT_INVALID")
            self.assertEqual(
                step["commands"], ["python scripts/harness.py plan sync PLAN-0001"]
            )

    def test_incomplete_plan_gated_project_is_routed_to_planning_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            _write_plan(root, "PLAN-0001", "Login")
            create_work_item(
                root, task_id="TASK-0001", title="Login", plan_id="PLAN-0001"
            )
            project_path = root / ".harness" / "project.json"
            project = load_json(project_path)
            project["policy"]["execution_mode"] = "PLAN_GATED"
            atomic_write_json(project_path, project)

            step = next_step(root)
            self.assertEqual(step["state"], "NEEDS_PLAN_DETAIL")
            self.assertTrue(
                any("report decision-package" in command for command in step["commands"])
            )

    def test_unscoped_draft_is_not_reported_as_ready_for_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            _write_plan(root, "PLAN-0001", "Login")
            create_work_item(
                root, task_id="TASK-0001", title="Login", plan_id="PLAN-0001"
            )
            step = next_step(root)
            self.assertEqual(step["state"], "NEEDS_PLAN_DETAIL")

    def test_next_surfaces_warnings_that_strict_validation_would_fail_on(self):
        with tempfile.TemporaryDirectory() as temp:
            root = init_harness(Path(temp) / "demo")
            _write_plan(root, "PLAN-0001", "Login")
            create_work_item(
                root, task_id="TASK-0001", title="Login", plan_id="PLAN-0001"
            )
            step = next_step(root)
            self.assertTrue(
                any("ORPHAN_TASK" in warning for warning in step["warnings"])
            )


if __name__ == "__main__":
    unittest.main()
