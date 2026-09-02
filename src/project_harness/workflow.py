from __future__ import annotations

from pathlib import Path
from typing import Any

from .collaboration import (
    _parse_verification,
    _path_state,
    ensure_claim_current,
    get_claim,
    mailbox_directory,
    release_claim,
    result_build_fingerprint,
    result_currentness,
    validate_changed_files,
    verification_state,
)
from .constants import HARNESS_DIR
from .core import (
    HarnessError,
    allocate_record_id,
    atomic_write_json,
    git_head,
    is_path_within,
    load_json,
    normalize_agent_id,
    normalize_claim_path,
    record_event,
    record_path,
    subject_fingerprint,
    subject_fingerprint_for_path,
    utc_now,
)
from .gates import task_start_gate


def dispatch_task(
    root: Path,
    *,
    task_id: str,
    to_agent: str,
    issued_by: str,
    instructions: str,
) -> dict[str, Any]:
    to_agent = normalize_agent_id(to_agent)
    gate = task_start_gate(root, task_id)
    if not gate.passed:
        raise HarnessError("Task cannot be dispatched: " + "; ".join(gate.blockers))
    task = gate.subject
    plan_path = record_path(root, "plan", task["plan_id"])
    target_directory = mailbox_directory(root, "inbox", to_agent)
    dispatch_id = allocate_record_id(root, target_directory, "DSP-")
    envelope = {
        "schema": "harness.dispatch/v1",
        "id": dispatch_id,
        "kind": "dispatch",
        "status": "QUEUED",
        "task_id": task_id,
        "to_agent": to_agent,
        "issued_by": issued_by,
        "instructions": instructions,
        "task_fingerprint": subject_fingerprint(task),
        "plan_fingerprint": subject_fingerprint_for_path(plan_path),
        "issued_at": utc_now(),
    }
    target = target_directory / f"{dispatch_id}.json"
    atomic_write_json(target, envelope)
    record_event(root, "TASK_DISPATCHED", {"task_id": task_id, "to_agent": to_agent})
    return envelope


def submit_result(
    root: Path,
    *,
    claim_id: str,
    agent: str,
    summary: str,
    changed_files: list[str],
    verifications: list[str],
    evidence_refs: list[str],
    limitations: list[str],
) -> dict[str, Any]:
    agent = normalize_agent_id(agent)
    claim, _claim_path = get_claim(root, claim_id)
    if claim.get("status") != "ACTIVE" or claim.get("agent") != agent:
        raise HarnessError("Result requires the submitting agent's active claim")
    ensure_claim_current(root, claim)
    task_id = claim["task_id"]
    task = load_json(record_path(root, "work_item", task_id))
    plan_path = record_path(root, "plan", task["plan_id"])
    normalized_changes = validate_changed_files(root, claim, changed_files)
    checks = _parse_verification(verifications)
    if not checks:
        raise HarnessError("Result requires exact verification commands and outcomes")
    evidence_fingerprints: dict[str, str] = {}
    for evidence_id in evidence_refs:
        evidence_path = record_path(root, "evidence", evidence_id)
        if not evidence_path.is_file():
            raise HarnessError(f"Result references missing evidence {evidence_id}")
        evidence_fingerprints[evidence_id] = subject_fingerprint(load_json(evidence_path))

    directory = root / HARNESS_DIR / "results"
    result_id = allocate_record_id(root, directory, "RES-")
    result_verification_state = verification_state(checks, task.get("verification", []))
    value = {
        "schema": "harness.result/v1",
        "id": result_id,
        "kind": "result",
        "status": "SUBMITTED",
        "task_id": task_id,
        "claim_id": claim_id,
        "agent": agent,
        "summary": summary,
        "changed_files": normalized_changes,
        "changed_file_states": {
            value: _path_state(root, value) for value in normalized_changes
        },
        "verification": checks,
        "verification_state": result_verification_state,
        "evidence_refs": evidence_refs,
        "evidence_fingerprints": evidence_fingerprints,
        "limitations": limitations,
        "task_fingerprint": claim.get("task_fingerprint"),
        "plan_fingerprint": claim.get("plan_fingerprint"),
        "base_commit": claim.get("base_commit"),
        "head_commit": git_head(root),
        "submitted_at": utc_now(),
    }
    value["build_fingerprint"] = result_build_fingerprint(value)
    canonical = directory / f"{result_id}.json"
    atomic_write_json(canonical, value)
    outbox = mailbox_directory(root, "outbox", agent) / f"{result_id}.json"
    atomic_write_json(outbox, value)
    record_event(root, "RESULT_SUBMITTED", {"result_id": result_id, "task_id": task_id, "agent": agent})
    release_claim(
        root,
        claim_id=claim_id,
        agent=agent,
        reason=f"result {result_id} submitted",
        validate_clean=False,
    )
    return value


def review_result(
    root: Path,
    *,
    result_id: str,
    reviewer: str,
    decision: str,
    basis: str,
    checks: list[str],
) -> dict[str, Any]:
    reviewer = normalize_agent_id(reviewer)
    if decision not in {"PASS", "CHANGES_REQUIRED", "REJECTED", "INCONCLUSIVE"}:
        raise HarnessError(f"Unsupported review decision: {decision}")
    result_path = record_path(root, "result", result_id)
    result = load_json(result_path)
    if str(result.get("agent", "")).casefold() == reviewer:
        raise HarnessError("A result author cannot independently review the same result")
    if decision == "PASS" and result.get("verification_state") != "PASS":
        raise HarnessError("A result with incomplete or failed verification cannot receive PASS")
    current, currentness_reasons = result_currentness(root, result)
    if decision == "PASS" and not current:
        raise HarnessError(
            "A stale result cannot receive PASS: " + "; ".join(currentness_reasons)
        )
    if not basis.strip() or not checks:
        raise HarnessError("Review requires a basis and explicit checks")
    directory = root / HARNESS_DIR / "reviews"
    review_id = allocate_record_id(root, directory, "VRD-")
    value = {
        "schema": "harness.review/v1",
        "id": review_id,
        "kind": "review",
        "status": "RECORDED",
        "result_id": result_id,
        "reviewer": reviewer,
        "decision": decision,
        "basis": basis,
        "checks": checks,
        "result_fingerprint": subject_fingerprint(result),
        "result_build_fingerprint": result.get("build_fingerprint"),
        "reviewed_at": utc_now(),
    }
    atomic_write_json(directory / f"{review_id}.json", value)
    record_event(root, "RESULT_REVIEWED", {"review_id": review_id, "result_id": result_id, "decision": decision})
    return value
