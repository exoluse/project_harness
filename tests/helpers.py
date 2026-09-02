from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from project_harness.approvals import record_approval
from project_harness.core import (
    atomic_write_json,
    load_json,
    record_path,
    sha256_file,
    sha256_path,
    subject_fingerprint,
    utc_now,
)
from project_harness.lifecycle import apply_plan_decision
from project_harness.scaffold import init_project


class HarnessTestCase(unittest.TestCase):
    """Unit-test-only approval verifier injection.

    Production runtime contains no unauthenticated approval mode.  Most tests
    replace only the external trust boundary; the dedicated signing tests run
    the real verifier against a temporary protected-ledger fixture.
    """

    def setUp(self) -> None:
        super().setUp()
        self._approval_verifier_patcher = patch(
            "project_harness.approvals._verify_attestation",
            return_value=(True, "unit-test authority verifier"),
        )
        self._approval_verifier_patcher.start()

    def tearDown(self) -> None:
        self._approval_verifier_patcher.stop()
        super().tearDown()


def write_record(root: Path, kind: str, record_id: str, value: dict) -> Path:
    path = record_path(root, kind, record_id)
    atomic_write_json(path, value)
    return path


def create_ready_project(root: Path, *, approve: bool = True) -> Path:
    init_project(root, "TESTPROJ", "Test Project")
    # Most historical fixtures intentionally exercise the legacy, plan-gated
    # compatibility mode. New-project behavior is covered separately.
    project_path = root / ".harness" / "project.json"
    project = load_json(project_path)
    project["policy"].update(
        {
            "execution_mode": "PLAN_GATED",
            "claim_mode": "REQUIRED",
            "record_mode": "REQUIRED",
            "human_approval_required_for": [
                "PLAN",
                "PRODUCTION_DEPLOYMENT",
                "PRODUCTION_DATA_CHANGE",
                "EXCEPTION",
                "PROJECT_CLOSURE",
            ],
            "approval_assurance": {
                "default": "CRYPTOGRAPHIC",
                "by_type": {"PLAN": "PROCEDURAL"},
            },
        }
    )
    atomic_write_json(project_path, project)
    now = utc_now()
    source = {
        "schema": "harness.source/v1",
        "id": "SRC-0001",
        "kind": "source",
        "title": "Customer request",
        "authority": "RAW_INPUT",
        "artifact_role": "REFERENCE",
        "interpretation_status": "EXPLICIT",
        "origin": "test",
        "summary": "Build the feature",
        "created_at": now,
    }
    requirement = {
        "schema": "harness.requirement/v1",
        "id": "REQ-0001",
        "kind": "requirement",
        "title": "Required behavior",
        "version": "1.0.0",
        "status": "APPROVED",
        "required": True,
        "priority": "MUST",
        "statement": "The system performs the required behavior.",
        "source_refs": ["SRC-0001"],
        "acceptance_criteria": ["AC-FUNC-0001-001"],
        "created_at": now,
    }
    feature = {
        "schema": "harness.feature/v1",
        "id": "FUNC-0001",
        "kind": "feature",
        "title": "Core feature",
        "version": "1.0.0",
        "status": "PLANNED",
        "required": True,
        "requirement_refs": ["REQ-0001"],
        "customer_acceptance_required": False,
        "completion_criteria": [
            {
                "id": "AC-FUNC-0001-001",
                "statement": "The required behavior is observed.",
                "required": True,
                "verification_plan": ["python -m unittest"],
                "required_profiles": ["INTEGRATION"],
                "required_bindings": ["src"],
                "evidence_refs": [],
            }
        ],
        "created_at": now,
    }
    task = {
        "schema": "harness.work_item/v1",
        "id": "TASK-0001",
        "kind": "work_item",
        "title": "Implement core feature",
        "status": "READY",
        "plan_id": "PLAN-0001",
        "feature_refs": ["FUNC-0001"],
        "criterion_refs": ["AC-FUNC-0001-001"],
        "dependencies": [],
        "blocked_by": [],
        "write_scope": ["src", "tests"],
        "preexisting_dirty_paths": [],
        "logical_locks": ["public-api"],
        "verification": ["python -m unittest"],
        "risk": "MEDIUM",
        "capabilities": ["LOCAL_IMPLEMENTATION", "LOCAL_TESTS"],
        "forbidden_actions": ["PRODUCTION_DEPLOYMENT"],
        "created_at": now,
    }
    plan = {
        "schema": "harness.plan/v1",
        "id": "PLAN-0001",
        "kind": "plan",
        "title": "Initial plan",
        "version": "1.0.0",
        "status": "DECISION_READY",
        "approval_dependencies": [
            ".harness/requirements/REQ-0001.json",
            ".harness/features/FUNC-0001.json",
            ".harness/work-items/TASK-0001.json",
        ],
        "approval_subject": {
            "requirement_refs": ["REQ-0001"],
            "feature_refs": ["FUNC-0001"],
            "work_item_refs": ["TASK-0001"],
            "workstreams": [
                {"id": "backend", "readiness": "READY_TO_BUILD"},
                {"id": "ui", "readiness": "PENDING_INPUT"},
            ],
            "verification_strategy": {"required_profiles": ["INTEGRATION"]},
            "authorized_actions": ["LOCAL_IMPLEMENTATION", "LOCAL_TESTS"],
            "excluded_actions": ["PRODUCTION_DEPLOYMENT"],
            "invalidation_triggers": ["requirement change", "task scope change"],
        },
        "created_at": now,
    }
    write_record(root, "source", "SRC-0001", source)
    write_record(root, "requirement", "REQ-0001", requirement)
    write_record(root, "feature", "FUNC-0001", feature)
    write_record(root, "work_item", "TASK-0001", task)
    write_record(root, "plan", "PLAN-0001", plan)

    project = load_json(project_path)
    project["required_features"] = ["FUNC-0001"]
    atomic_write_json(project_path, project)
    state_path = root / ".harness" / "state.json"
    state = load_json(state_path)
    state["lifecycle_state"] = "DECISION_READY"
    state["active_plan"] = "PLAN-0001"
    atomic_write_json(state_path, state)
    if approve:
        approval = record_approval(
            root,
            approval_type="PLAN",
            subject_path=".harness/plans/PLAN-0001.json",
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
    return root


def add_verified_evidence(root: Path, *, ambiguity: str = "NONE", bind: bool = True) -> Path:
    source = root / "src" / "core.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        source.write_text("value = 1\n", encoding="utf-8")
    artifact = root / "artifacts" / "test-result.txt"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text("verified result\n", encoding="utf-8")
    evidence = {
        "schema": "harness.evidence/v1",
        "id": "EVD-0001",
        "kind": "evidence",
        "title": "Core feature integration evidence",
        "observed_at": utc_now(),
        "claim": "The required behavior is observed.",
        "supports": ["AC-FUNC-0001-001"],
        "profile": "INTEGRATION",
        "method": "unittest integration fixture",
        "environment": "temporary test project",
        "subject": {
            "build": "TEST-BUILD-001",
            "criterion_fingerprints": {
                "AC-FUNC-0001-001": subject_fingerprint(
                    {
                        **load_json(record_path(root, "feature", "FUNC-0001"))[
                            "completion_criteria"
                        ][0],
                        "kind": "completion_criterion",
                        "feature_id": "FUNC-0001",
                    }
                )
            },
        },
        "expected": "behavior observed",
        "actual": "behavior observed",
        "result": "VERIFIED",
        "ambiguity": {"level": ambiguity, "reasons": [] if ambiguity == "NONE" else ["test ambiguity"]},
        "bindings": [
            {"path": "src", "sha256": sha256_path(root / "src")},
            {"path": "artifacts/test-result.txt", "sha256": sha256_file(artifact)},
        ] if bind else [],
        "limitations": ["temporary environment only"],
    }
    path = write_record(root, "evidence", "EVD-0001", evidence)
    feature_path = record_path(root, "feature", "FUNC-0001")
    feature = load_json(feature_path)
    feature["completion_criteria"][0]["evidence_refs"] = ["EVD-0001"]
    atomic_write_json(feature_path, feature)
    return path
