from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from project_harness.reporting import completion_report, trace_report
from project_harness.validation import validate_project

from .helpers import (
    HarnessTestCase,
    add_verified_evidence,
    create_ready_project,
    write_record,
)


class TraceReportingTests(HarnessTestCase):
    def test_completion_report_validates_once_per_command(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            with patch(
                "project_harness.evaluation.validate_project",
                wraps=validate_project,
            ) as mocked:
                completion_report(root)
            self.assertEqual(mocked.call_count, 1)

    def test_trace_connects_criteria_tasks_evidence_results_and_reviews(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            write_record(
                root,
                "result",
                "RES-0001",
                {
                    "schema": "harness.result/v1",
                    "id": "RES-0001",
                    "kind": "result",
                    "task_id": "TASK-0001",
                    "evidence_refs": ["EVD-0001"],
                },
            )
            write_record(
                root,
                "review",
                "VRD-0001",
                {
                    "schema": "harness.review/v1",
                    "id": "VRD-0001",
                    "kind": "review",
                    "result_id": "RES-0001",
                },
            )

            report = trace_report(root, "RES-0001")
            nodes = {node["id"]: node for node in report["nodes"]}

            self.assertEqual(
                set(nodes["RES-0001"]["outgoing"]),
                {"EVD-0001", "TASK-0001"},
            )
            self.assertIn("VRD-0001", nodes["RES-0001"]["incoming"])
            self.assertIn("AC-FUNC-0001-001", nodes["TASK-0001"]["outgoing"])
            self.assertIn("FUNC-0001", nodes["AC-FUNC-0001-001"]["outgoing"])
            self.assertIn("AC-FUNC-0001-001", nodes["EVD-0001"]["outgoing"])
            self.assertEqual(nodes["VRD-0001"]["outgoing"], ["RES-0001"])
            self.assertIn(
                {"field": "task_id", "target": "TASK-0001"},
                nodes["RES-0001"]["outgoing_edges"],
            )
            self.assertIn(
                {"field": "result_id", "source": "VRD-0001"},
                nodes["RES-0001"]["incoming_edges"],
            )

    def test_trace_indexes_project_and_nested_closure_criteria(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")

            report = trace_report(root, "PROJECT")
            nodes = {node["id"]: node for node in report["nodes"]}

            # The project is one node keyed by its fixed marker; the closure
            # criteria nested inside it point back at it the way a completion
            # criterion points at its feature.
            self.assertIn("FUNC-0001", nodes["PROJECT"]["outgoing"])
            self.assertIn("DELIVERY", nodes["PROJECT"]["incoming"])
            self.assertEqual(nodes["DELIVERY"]["outgoing"], ["PROJECT"])
            self.assertIn(
                {"field": "project_id", "source": "DELIVERY"},
                nodes["PROJECT"]["incoming_edges"],
            )
