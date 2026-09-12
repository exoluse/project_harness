from __future__ import annotations

from pathlib import Path
from typing import Any

from .approvals import approval_status, decision_mutex, find_current_approval
from .constants import APPROVED_DECISIONS, HARNESS_DIR
from .core import (
    HarnessError,
    load_json,
    record_path,
    subject_fingerprint_for_path,
    utc_now,
)
from .gates import plan_preflight_gate
from .mutation_service import AtomicMutationService


PROGRESSED_PLAN_STATUSES = {
    "ACTIVE",
    "PARTIALLY_STALE",
    "STALE",
    "SUPERSEDED",
    "CLOSED",
}

POST_DECISION_LIFECYCLE_STATES = {
    "APPROVED",
    "BUILDING",
    "VERIFYING",
    "CUSTOMER_ACCEPTANCE",
    "DEPLOYING",
    "CLOSED",
    "MAINTAINING",
    "ON_HOLD",
}

RESUMABLE_LIFECYCLE_STATES = {
    "APPROVED",
    "BUILDING",
    "VERIFYING",
    "MAINTAINING",
    "ON_HOLD",
}

PRE_DECISION_LIFECYCLE_STATES = {
    "DISCOVERY", "CONTRACTED", "SPECIFYING", "PLANNING", "DECISION_READY",
}
TERMINAL_TASK_STATUSES = {"INTEGRATED", "DONE", "CLOSED", "ABORTED"}


def _plan_status_materializes_decision(status: Any, decision: str) -> bool:
    return status == decision or status in PROGRESSED_PLAN_STATUSES


def _replaces_superseded_active_decision(
    root: Path,
    *,
    approval_id: str,
    plan_id: str,
    plan: dict[str, Any],
    state: dict[str, Any],
) -> bool:
    previous_id = state.get("active_decision")
    if (
        not isinstance(previous_id, str)
        or previous_id == approval_id
        or plan.get("decision_ref") != previous_id
    ):
        return False
    previous = load_json(record_path(root, "approval", previous_id))
    previous_status, _reason = approval_status(root, previous)
    return (
        previous.get("approval_type") == "PLAN"
        and previous.get("subject_id") == plan_id
        and previous.get("decision") in APPROVED_DECISIONS
        and previous_status in {"STALE", "SUPERSEDED"}
    )


def _application_events(
    root: Path, approval_id: str, plan_id: str | None = None
) -> list[tuple[Path, dict[str, Any]]]:
    matches: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted((root / HARNESS_DIR / "events").glob("EVT-*.json")):
        value = load_json(path)
        payload = value.get("payload")
        if (
            value.get("event_type") == "PLAN_DECISION_APPLIED"
            and isinstance(payload, dict)
            and payload.get("approval_id") == approval_id
            and (plan_id is None or payload.get("plan_id") == plan_id)
        ):
            matches.append((path, value))
    return matches


def _validate_application_event(
    event: dict[str, Any],
    *,
    approval: dict[str, Any],
    plan_id: str,
    applied_at: str,
) -> None:
    payload = event.get("payload")
    if not isinstance(payload, dict):
        raise HarnessError("PLAN_DECISION_APPLIED event payload is malformed")
    expected = {
        "approval_id": approval.get("id"),
        "decision_id": approval.get("decision_id"),
        "plan_id": plan_id,
        "decision": approval.get("decision"),
        "subject_fingerprint": approval.get("subject_fingerprint"),
        "assurance": approval.get("assurance", "CRYPTOGRAPHIC"),
        "applied_at": applied_at,
    }
    mismatches = [
        field for field, value in expected.items() if payload.get(field) != value
    ]
    if mismatches:
        raise HarnessError(
            "PLAN_DECISION_APPLIED event conflicts with the approval: "
            + ", ".join(sorted(mismatches))
        )


def apply_plan_decision(root: Path, *, approval_id: str, plan_id: str | None = None) -> dict[str, Any]:
    """Materialize the latest current PLAN decision into PLAN and STATE once."""

    with decision_mutex(root, operation="applying a plan decision"):
        approval = load_json(record_path(root, "approval", approval_id))
        if approval.get("id") != approval_id:
            raise HarnessError("Approval file ID does not match its filename")
        if approval.get("approval_type") != "PLAN":
            raise HarnessError("Only PLAN approvals can be applied to lifecycle state")
        if approval.get("decision") not in APPROVED_DECISIONS:
            raise HarnessError(
                f"PLAN decision {approval.get('decision')} is not executable"
            )

        state_path = root / HARNESS_DIR / "state.json"
        state = load_json(state_path)
        plan_id = plan_id or approval.get("subject_id")
        if not isinstance(plan_id, str) or not plan_id:
            raise HarnessError("PLAN decision has no subject")
        previous_plan_id = state.get("active_plan")
        retired_plan = None
        from .decision_scope import plan_scope, scope_fingerprint, snapshot_subject
        approved_scope = plan_scope(snapshot_subject(root, approval))
        if previous_plan_id and previous_plan_id != plan_id:
            previous_path = record_path(root, "plan", previous_plan_id)
            previous_plan = load_json(previous_path)
            shared_scope = approved_scope is not None and plan_scope(previous_plan) is not None and (
                scope_fingerprint(plan_scope(previous_plan)) == scope_fingerprint(approved_scope)
            )
            task_ids = previous_plan.get("approval_subject", {}).get("work_item_refs", [])
            unfinished = [task_id for task_id in task_ids if load_json(
                record_path(root, "work_item", task_id)
            ).get("status") not in TERMINAL_TASK_STATUSES]
            if unfinished and not shared_scope and previous_plan.get("status") not in {"CLOSED", "SUPERSEDED", "STALE"}:
                raise HarnessError(f"Different live plan {previous_plan_id} has unfinished tasks")
            if not shared_scope and previous_plan.get("status") not in {"CLOSED", "SUPERSEDED"}:
                previous_plan["status"] = "SUPERSEDED"
                retired_plan = (previous_path, previous_plan)

        status, reason = approval_status(root, approval)
        if status != "CURRENT":
            raise HarnessError(
                f"Approval {approval_id} is not current: {status}: {reason}"
            )
        latest, latest_reason = find_current_approval(
            root, subject_id=plan_id, approval_type="PLAN"
        )
        if latest is None or latest.get("id") != approval_id:
            raise HarnessError(
                f"Approval {approval_id} is not the latest current PLAN decision: "
                f"{latest_reason}"
            )

        plan_path = record_path(root, "plan", plan_id)
        plan = load_json(plan_path)
        if plan.get("id") != plan_id:
            raise HarnessError("Active plan file ID does not match project state")
        current_fingerprint = subject_fingerprint_for_path(plan_path)
        if current_fingerprint != approval.get("subject_fingerprint"):
            raise HarnessError("PLAN fingerprint no longer matches the approval")

        preflight = plan_preflight_gate(root, plan_id, require_approval=False)
        if not preflight.passed:
            raise HarnessError(
                "PLAN preflight is not ready: " + "; ".join(preflight.blockers)
            )

        events = _application_events(root, approval_id, plan_id)
        if len(events) > 1:
            raise HarnessError(
                f"Approval {approval_id} has duplicate PLAN_DECISION_APPLIED events"
            )

        same_decision = (
            plan.get("decision_ref") == approval_id
            or state.get("active_decision") == approval_id
        )
        replaces_previous = _replaces_superseded_active_decision(
            root,
            approval_id=approval_id,
            plan_id=plan_id,
            plan=plan,
            state=state,
        )
        lifecycle_state = state.get("lifecycle_state")
        if lifecycle_state == "CANCELLED":
            raise HarnessError(
                "A cancelled project cannot be reopened by applying a plan decision"
            )
        if (
            not events
            and not same_decision
            and lifecycle_state not in PRE_DECISION_LIFECYCLE_STATES
            and not (
                (replaces_previous or previous_plan_id != plan_id)
                and lifecycle_state in RESUMABLE_LIFECYCLE_STATES
            )
        ):
            raise HarnessError(
                "A new PLAN decision cannot be applied from this lifecycle state; "
                f"current lifecycle state is {lifecycle_state}"
            )

        event_payload = events[0][1].get("payload", {}) if events else {}
        existing_applied_at = (
            plan.get("decision_applied_at")
            if plan.get("decision_ref") == approval_id
            else None
        )
        if not isinstance(existing_applied_at, str) or not existing_applied_at:
            existing_applied_at = (
                event_payload.get("applied_at")
                if isinstance(event_payload, dict)
                else None
            )
        if not isinstance(existing_applied_at, str) or not existing_applied_at:
            existing_applied_at = (
                state.get("updated_at")
                if state.get("active_decision") == approval_id
                else None
            )
        applied_at = (
            existing_applied_at
            if isinstance(existing_applied_at, str) and existing_applied_at
            else utc_now()
        )

        if events:
            _validate_application_event(
                events[0][1],
                approval=approval,
                plan_id=plan_id,
                applied_at=applied_at,
            )
            if (
                plan.get("decision_ref") == approval_id
                and state.get("active_decision") == approval_id
                and state.get("active_plan") == plan_id
                and plan.get("decision_applied_at") == applied_at
                and _plan_status_materializes_decision(
                    plan.get("status"), str(approval.get("decision"))
                )
                and state.get("lifecycle_state")
                in POST_DECISION_LIFECYCLE_STATES
            ):
                return {
                    "approval_id": approval_id,
                    "plan_id": plan_id,
                    "decision": approval.get("decision"),
                    "plan_status": plan.get("status"),
                    "lifecycle_state": state.get("lifecycle_state"),
                    "applied_at": applied_at,
                    "event": events[0][0].relative_to(root).as_posix(),
                    "changed": False,
                }

        target_plan_status = str(approval.get("decision"))
        before_plan_status = plan.get("status")
        before_lifecycle_state = state.get("lifecycle_state")
        preserve_progress = bool(events) or same_decision or replaces_previous or (
            previous_plan_id != plan_id and lifecycle_state in RESUMABLE_LIFECYCLE_STATES
        )
        applied_plan_status = (
            str(before_plan_status)
            if preserve_progress
            and _plan_status_materializes_decision(
                before_plan_status, target_plan_status
            )
            else target_plan_status
        )
        applied_lifecycle_state = (
            str(before_lifecycle_state)
            if preserve_progress
            and before_lifecycle_state in POST_DECISION_LIFECYCLE_STATES
            else "APPROVED"
        )
        plan["status"] = applied_plan_status
        plan["decision_ref"] = approval_id
        plan["decision_applied_at"] = applied_at
        state["lifecycle_state"] = applied_lifecycle_state
        state["active_decision"] = approval_id
        state["current_plan"] = plan_id
        state["active_plan"] = plan_id
        state["updated_at"] = applied_at

        plan_changed = load_json(plan_path) != plan
        state_changed = load_json(state_path) != state
        event_path = events[0][0] if events else None
        writes = {}
        if plan_changed:
            writes[plan_path.relative_to(root).as_posix()] = plan
        if state_changed:
            writes[state_path.relative_to(root).as_posix()] = state
        if retired_plan:
            writes[retired_plan[0].relative_to(root).as_posix()] = retired_plan[1]
        if event_path is None:
            transaction = AtomicMutationService(root).apply(
                writes=writes,
                event_type="PLAN_DECISION_APPLIED",
                event_payload={
                    "approval_id": approval_id,
                    "decision_id": approval.get("decision_id"),
                    "plan_id": plan_id,
                    "decision": approval.get("decision"),
                    "before_plan_status": before_plan_status,
                    "after_plan_status": applied_plan_status,
                    "before_lifecycle_state": before_lifecycle_state,
                    "after_lifecycle_state": applied_lifecycle_state,
                    "subject_fingerprint": approval.get("subject_fingerprint"),
                    "assurance": approval.get("assurance", "CRYPTOGRAPHIC"),
                    "applied_at": applied_at,
                    "previous_plan_id": previous_plan_id,
                },
            )
            event_path = root / HARNESS_DIR / "events" / f"{transaction['event_id']}.json"
        elif writes:
            AtomicMutationService(root).apply(
                writes=writes, event_type="PLAN_DECISION_REPAIRED",
                event_payload={"plan_id": plan_id, "approval_id": approval_id},
            )

        return {
            "approval_id": approval_id,
            "plan_id": plan_id,
            "decision": approval.get("decision"),
            "plan_status": applied_plan_status,
            "lifecycle_state": applied_lifecycle_state,
            "applied_at": applied_at,
            "event": event_path.relative_to(root).as_posix(),
            "changed": plan_changed or state_changed or not events,
        }
