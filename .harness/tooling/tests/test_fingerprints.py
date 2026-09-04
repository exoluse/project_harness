from __future__ import annotations

import tempfile
from pathlib import Path

from project_harness.core import (
    atomic_write_json,
    load_json,
    subject_fingerprint_for_path,
)

from .helpers import HarnessTestCase, create_ready_project


class FingerprintTests(HarnessTestCase):
    def test_plan_fingerprint_excludes_closure_evidence_but_binds_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            plan_path = root / ".harness" / "plans" / "PLAN-0001.md"
            project_path = root / ".harness" / "project.json"

            plan = load_json(plan_path)
            plan["approval_dependencies"].append(".harness/project.json")
            atomic_write_json(plan_path, plan)
            original = subject_fingerprint_for_path(plan_path)

            project = load_json(project_path)
            project["closure_contract"][0]["evidence_refs"] = ["EVD-DELIVERY-001"]
            atomic_write_json(project_path, project)
            with_evidence = subject_fingerprint_for_path(plan_path)

            project["closure_contract"][0]["required_profiles"] = [
                "DELIVERY",
                "STATIC",
            ]
            atomic_write_json(project_path, project)
            changed_contract = subject_fingerprint_for_path(plan_path)

            self.assertEqual(original, with_evidence)
            self.assertNotEqual(with_evidence, changed_contract)
