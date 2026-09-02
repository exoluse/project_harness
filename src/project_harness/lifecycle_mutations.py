from __future__ import annotations

from pathlib import Path
from typing import Any

from .approvals import find_current_approval
from .constants import HARNESS_DIR
from .core import (
    HarnessError,
    load_json,
    normalize_agent_id,
    record_path,
    subject_fingerprint,
    utc_now,
)
from .evaluation import EvaluationContext
from .gates import (
    _latest_task_result_assessment,
    feature_completion_gate,
    plan_preflight_gate,
    project_completion_gate,
    task_start_gate,
)
from .mutation_service import (
    AtomicMutationService,
    authorize_claim_targets,
    validate_records,
)
from .policy import record_mode, user_directed


WORK_ITEM_TRANSITIONS = {
    "DRAFT": {"READY"},
    "READY": {"APPROVED", "RUNNING", "BLOCKED", "ABORTED"},
    "APPROVED": {"RUNNING", "BLOCKED", "ABORTED"},
    "RUNNING": {"SUBMITTED", "BLOCKED", "FAILED", "ABORTED"},
    "SUBMITTED": {"REVIEWED", "BLOCKED", "FAILED"},
    "REVIEWED": {"INTEGRATED", "BLOCKED"},
    "INTEGRATED": {"DONE"},
    "DONE": {"CLOSED"},
}

REWORK_STATES = {"BLOCKED", "FAILED", "ABORTED", "STALE", "REVIEWED", "DONE", "CLOSED"}

SIMPLE_TRANSITIONS = {
    "requirement": {
        "CANDIDATE": {"CLARIFICATION_REQUIRED", "APPROVED", "SUPERSEDED"},
        "CLARIFICATION_REQUIRED": {"CANDIDATE", "APPROVED", "SUPERSEDED"},
        "APPROVED": {"PLANNED", "SUPERSEDED"},
        "PLANNED": {"IMPLEMENTED", "SUPERSEDED"},
        "IMPLEMENTED": {"VERIFIED", "SUPERSEDED"},
        "VERIFIED": {"ACCEPTED", "SUPERSEDED"},
    },
    "feature": {
        "CANDIDATE": {"SPECIFIED", "SUPERSEDED"},
        "SPECIFIED": {"PLANNED", "SUPERSEDED"},
        "PLANNED": {"IMPLEMENTED", "PARTIAL", "INCONCLUSIVE", "SUPERSEDED"},
        "IMPLEMENTED": {"VERIFIED", "PARTIAL", "INCONCLUSIVE", "SUPERSEDED"},
        "PARTIAL": {"IMPLEMENTED", "VERIFIED", "INCONCLUSIVE", "SUPERSEDED"},
        "INCONCLUSIVE": {"IMPLEMENTED", "PARTIAL", "VERIFIED", "SUPERSEDED"},
        "VERIFIED": {"ACCEPTED", "SUPERSEDED"},
    },
}

PROJECT_TRANSITIONS = {
    "OPPORTUNITY": {"DISCOVERY", "CANCELLED"},
    "DISCOVERY": {"CONTRACTED", "SPECIFYING", "ON_HOLD", "CANCELLED"},
    "CONTRACTED": {"SPECIFYING", "PLANNING", "ON_HOLD", "CANCELLED"},
    "SPECIFYING": {"PLANNING", "ON_HOLD", "CANCELLED"},
    "PLANNING": {"DECISION_READY", "ON_HOLD", "CANCELLED"},
    "DECISION_READY": {"ON_HOLD", "CANCELLED"},
    "APPROVED": {"BUILDING", "ON_HOLD", "CANCELLED"},
    "BUILDING": {"VERIFYING", "ON_HOLD", "CANCELLED"},
    "VERIFYING": {"BUILDING", "CUSTOMER_ACCEPTANCE", "ON_HOLD", "CANCELLED"},
    "CUSTOMER_ACCEPTANCE": {"DEPLOYING", "CLOSED", "ON_HOLD", "CANCELLED"},
    "DEPLOYING": {"CLOSED", "ON_HOLD", "CANCELLED"},
    "CLOSED": {"MAINTAINING"},
    "MAINTAINING": {"BUILDING", "ON_HOLD", "CANCELLED"},
}


def transition_record(
    root: Path,
    *,
    claim_id: str | None,
    agent: str,
    kind: str,
    record_id: str,
    target_status: str,
    reason: str,
    rework: bool = False,
) -> dict[str, Any]:
    """Apply a governed requirement, feature, work-item, or project transition."""
    root = root.resolve()
    if kind == "project":
        return transition_project(
            root,
            claim_id=claim_id,
            agent=agent,
            target_state=target_status,
            reason=reason,
            resume=rework,
        )
    if kind not in {"requirement", "feature", "work_item"}:
        raise HarnessError(
            "Transition kind must be project, requirement, feature, or work_item"
        )
    path = record_path(root, kind, record_id)
    relative = path.relative_to(root).as_posix()
    authorize_claim_targets(root, claim_id=claim_id, agent=agent, targets=[relative])
    record = load_json(path)
    before = str(record.get("status"))
    if rework:
        if kind != "work_item" or before not in REWORK_STATES or target_status != "READY":
            raise HarnessError("Rework may only resume an eligible work item to READY")
        if not reason.strip():
            raise HarnessError("Rework resume requires a nonempty reason")
    else:
        transitions = WORK_ITEM_TRANSITIONS if kind == "work_item" else SIMPLE_TRANSITIONS[kind]
        if target_status not in transitions.get(before, set()):
            raise HarnessError(f"Illegal {kind} transition: {before} -> {target_status}")

    context = EvaluationContext.load(root)
    if kind == "work_item" and target_status == "RUNNING":
        gate = task_start_gate(root, record_id, context=context)
        if not gate.passed:
            raise HarnessError("Work item cannot enter RUNNING: " + "; ".join(gate.blockers))
    if (
        kind == "work_item"
        and record_mode(root) == "REQUIRED"
        and target_status in {"REVIEWED", "INTEGRATED", "DONE", "CLOSED"}
    ):
        plan_id = str(record.get("plan_id"))
        result, review, reasons = _latest_task_result_assessment(
            root,
            record_id,
            context.records,
            current_task_fingerprint=subject_fingerprint(record),
            current_plan_fingerprint=subject_fingerprint(context.records[plan_id]),
        )
        if result is None or review is None or reasons:
            raise HarnessError(
                "Work item lacks a current independently reviewed PASS: " + "; ".join(reasons)
            )
    if kind == "feature" and target_status in {"VERIFIED", "ACCEPTED"}:
        gate = feature_completion_gate(root, record_id, context=context)
        if not gate.passed:
            raise HarnessError("Feature cannot be verified: " + "; ".join(gate.blockers))

    record["status"] = target_status
    record["updated_at"] = utc_now()
    if rework:
        record["rework"] = {
            "resumed_at": record["updated_at"],
            "resumed_by": normalize_agent_id(agent),
            "reason": reason,
        }
    validate_records(root, [(kind, record)])
    transaction = AtomicMutationService(root).apply(
        writes={relative: record},
        event_type="REWORK_RESUMED" if rework else "RECORD_TRANSITIONED",
        event_payload={
            "record_id": record_id,
            "kind": kind,
            "before": before,
            "after": target_status,
            "reason": reason,
            "claim_id": claim_id,
            "agent": normalize_agent_id(agent),
        },
    )
    return {"record": record, "transaction": transaction}


def transition_project(
    root: Path,
    *,
    claim_id: str | None,
    agent: str,
    target_state: str,
    reason: str,
    resume: bool = False,
) -> dict[str, Any]:
    """Apply project lifecycle policy and persist the state/event atomically."""
    state_path = root / HARNESS_DIR / "state.json"
    relative = state_path.relative_to(root).as_posix()
    authorize_claim_targets(root, claim_id=claim_id, agent=agent, targets=[relative])
    state = load_json(state_path)
    before = str(state.get("lifecycle_state"))
    if before == "ON_HOLD":
        expected = state.get("suspended_lifecycle_state")
        if not resume or target_state != expected:
            raise HarnessError(
                "ON_HOLD may resume only to its recorded suspended lifecycle state"
            )
        if not reason.strip():
            raise HarnessError("Project resume requires a nonempty reason")
    elif target_state not in PROJECT_TRANSITIONS.get(before, set()):
        raise HarnessError(f"Illegal project transition: {before} -> {target_state}")

    context = EvaluationContext.load(root)
    active_plan = state.get("active_plan")
    if target_state == "APPROVED":
        raise HarnessError("APPROVED is materialized only by plan apply-decision")
    if target_state == "BUILDING":
        if user_directed(root):
            pass
        elif not isinstance(active_plan, str):
            raise HarnessError("Project cannot enter BUILDING without an active plan")
        else:
            gate = plan_preflight_gate(root, active_plan, require_approval=True, context=context)
            if not gate.passed:
                raise HarnessError("Project cannot enter BUILDING: " + "; ".join(gate.blockers))
    if target_state == "CUSTOMER_ACCEPTANCE":
        project = load_json(root / HARNESS_DIR / "project.json")
        feature_blockers: list[str] = []
        for feature_id in project.get("required_features", []):
            gate = feature_completion_gate(root, feature_id, context=context)
            feature_blockers.extend(f"{feature_id}: {value}" for value in gate.blockers)
        if feature_blockers:
            raise HarnessError(
                "Project cannot enter CUSTOMER_ACCEPTANCE: " + "; ".join(feature_blockers)
            )
    if target_state == "DEPLOYING":
        project = load_json(root / HARNESS_DIR / "project.json")
        approval, reason_text = find_current_approval(
            root,
            subject_id=project.get("id"),
            approval_type="PRODUCTION_DEPLOYMENT",
        )
        if approval is None:
            raise HarnessError("Project cannot enter DEPLOYING: " + reason_text)
    if target_state == "CLOSED":
        gate = project_completion_gate(root, require_approval=True, context=context)
        if not gate.passed:
            raise HarnessError("Project cannot enter CLOSED: " + "; ".join(gate.blockers))

    now = utc_now()
    if target_state == "ON_HOLD":
        state["suspended_lifecycle_state"] = before
    elif before == "ON_HOLD":
        state.pop("suspended_lifecycle_state", None)
    state["lifecycle_state"] = target_state
    state["updated_at"] = now
    validate_records(root, [("state", state)])
    transaction = AtomicMutationService(root).apply(
        writes={relative: state},
        event_type="PROJECT_LIFECYCLE_TRANSITIONED",
        event_payload={
            "before": before,
            "after": target_state,
            "reason": reason,
            "claim_id": claim_id,
            "agent": normalize_agent_id(agent),
        },
    )
    return {"record": state, "transaction": transaction}
