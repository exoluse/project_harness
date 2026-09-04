from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .constants import HARNESS_DIR, RECORD_DIRECTORIES
from .core import (
    HarnessError,
    load_json,
    load_record_index,
    next_id,
    record_path,
    utc_now,
)
from .mutation_service import (
    AtomicMutationService,
    authorize_claim_targets,
    validate_records,
)
from .scaffold import new_record


EXECUTABLE_PLAN_STATUSES = {"APPROVED", "APPROVED_WITH_CONDITIONS", "ACTIVE"}
RETIRED_PLAN_STATUSES = {"CLOSED", "SUPERSEDED", "STALE"}

# ``approval_dependencies`` is derivable from these subject reference fields.
# Validation requires the stored list to cover every derived path, so the
# harness maintains it here instead of asking an author to mirror it by hand.
SUBJECT_REF_FIELDS = (
    ("requirement_refs", "requirement"),
    ("feature_refs", "feature"),
    ("work_item_refs", "work_item"),
)

DEFAULT_AGENT = "agent"


def _plan_subject(plan: dict[str, Any]) -> dict[str, Any]:
    subject = plan.get("approval_subject")
    if not isinstance(subject, dict):
        raise HarnessError(f"Plan {plan.get('id')} has a malformed approval_subject")
    return subject


def _string_list(subject: dict[str, Any], field: str) -> list[str]:
    value = subject.get(field, [])
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise HarnessError(f"approval_subject.{field} must be a string list")
    return list(value)


def _load_plan(root: Path, plan_id: str) -> tuple[dict[str, Any], Path]:
    path = record_path(root, "plan", plan_id)
    if not path.is_file():
        raise HarnessError(
            f"Plan {plan_id} does not exist; create it with "
            f'\'new plan {plan_id} "<title>"\''
        )
    plan = load_json(path)
    if plan.get("kind") != "plan" or plan.get("id") != plan_id:
        raise HarnessError(f"{path} is not the {plan_id} plan record")
    return plan, path


def next_record_id(root: Path, kind: str) -> str:
    """Return the next unused ID for ``kind`` without allocating it."""
    directory, prefix = RECORD_DIRECTORIES[kind]
    return next_id(root / HARNESS_DIR / directory, prefix)


def derived_plan_dependencies(
    root: Path,
    plan: dict[str, Any],
    record_paths: dict[str, Path],
) -> list[str]:
    """Return the dependency paths implied by a plan's approval subject."""
    subject = _plan_subject(plan)
    derived: list[str] = []
    for field, _kind in SUBJECT_REF_FIELDS:
        for reference in _string_list(subject, field):
            path = record_paths.get(reference)
            if path is None:
                raise HarnessError(
                    f"Plan {plan.get('id')} references missing record {reference}"
                )
            derived.append(path.relative_to(root).as_posix())
    return derived


def synced_plan_dependencies(
    root: Path,
    plan: dict[str, Any],
    record_paths: dict[str, Path],
) -> tuple[list[str], list[str]]:
    """Return the plan's dependency list extended with any missing derived path."""
    existing = plan.get("approval_dependencies", [])
    if not isinstance(existing, list) or any(
        not isinstance(item, str) for item in existing
    ):
        raise HarnessError("approval_dependencies must be a string list")
    dependencies = list(existing)
    added: list[str] = []
    for value in derived_plan_dependencies(root, plan, record_paths):
        if value not in dependencies:
            dependencies.append(value)
            added.append(value)
    return dependencies, added


def sync_plan(
    root: Path,
    *,
    plan_id: str,
    claim_id: str | None = None,
    agent: str = DEFAULT_AGENT,
) -> dict[str, Any]:
    """Rebuild a plan's derived approval_dependencies from its subject refs."""
    root = root.resolve()
    plan, plan_path = _load_plan(root, plan_id)
    _records, record_paths = load_record_index(root)
    dependencies, added = synced_plan_dependencies(root, plan, record_paths)
    if not added:
        return {"plan_id": plan_id, "added_dependencies": [], "changed": False}
    plan["approval_dependencies"] = dependencies
    plan["updated_at"] = utc_now()
    relative_plan = plan_path.relative_to(root).as_posix()
    validate_records(root, [("plan", plan)])
    authorize_claim_targets(
        root, claim_id=claim_id, agent=agent, targets=[relative_plan]
    )
    transaction = AtomicMutationService(root).apply(
        writes={relative_plan: plan},
        event_type="PLAN_DEPENDENCIES_SYNCED",
        event_payload={"plan_id": plan_id, "added_dependencies": added},
    )
    return {
        "plan_id": plan_id,
        "added_dependencies": added,
        "changed": True,
        "transaction": transaction,
    }


def create_work_item(
    root: Path,
    *,
    task_id: str,
    title: str,
    plan_id: str,
    feature_refs: Iterable[str] = (),
    criterion_refs: Iterable[str] = (),
    capabilities: Iterable[str] = (),
    claim_id: str | None = None,
    agent: str = DEFAULT_AGENT,
) -> dict[str, Any]:
    """Create a TASK and link it into its PLAN in a single atomic mutation."""
    root = root.resolve()
    _directory, prefix = RECORD_DIRECTORIES["work_item"]
    if not task_id.startswith(prefix):
        raise HarnessError(f"work item IDs must start with {prefix}")
    task_path = record_path(root, "work_item", task_id)
    if task_path.exists():
        raise HarnessError(f"Record already exists: {task_id}")

    plan, plan_path = _load_plan(root, plan_id)
    subject = _plan_subject(plan)
    authorized = _string_list(subject, "authorized_actions")
    excluded = _string_list(subject, "excluded_actions")

    requested = list(dict.fromkeys(capabilities))
    unauthorized = [value for value in requested if value not in authorized]
    if unauthorized:
        raise HarnessError(
            f"Plan {plan_id} does not authorize: " + ", ".join(sorted(unauthorized))
        )
    blocked = [value for value in requested if value in excluded]
    if blocked:
        raise HarnessError(
            f"Plan {plan_id} excludes: " + ", ".join(sorted(blocked))
        )

    records, record_paths = load_record_index(root)
    features = list(dict.fromkeys(feature_refs))
    unknown = [
        value
        for value in features
        if records.get(value, {}).get("kind") != "feature"
    ]
    if unknown:
        raise HarnessError("Unknown feature reference: " + ", ".join(sorted(unknown)))
    criteria = list(dict.fromkeys(criterion_refs))
    unknown_criteria = [
        value
        for value in criteria
        if records.get(value, {}).get("kind") != "completion_criterion"
    ]
    if unknown_criteria:
        raise HarnessError(
            "Unknown completion criterion: " + ", ".join(sorted(unknown_criteria))
        )

    task = new_record("work_item", task_id, title)
    task["plan_id"] = plan_id
    task["feature_refs"] = features
    task["criterion_refs"] = criteria
    task["capabilities"] = requested
    task["forbidden_actions"] = sorted(excluded)

    linked = _string_list(subject, "work_item_refs")
    if task_id not in linked:
        linked.append(task_id)
    subject["work_item_refs"] = linked
    plan["approval_subject"] = subject
    record_paths[task_id] = task_path
    plan["approval_dependencies"], added = synced_plan_dependencies(
        root, plan, record_paths
    )
    plan["updated_at"] = utc_now()

    warnings: list[str] = []
    if plan.get("decision_ref"):
        warnings.append(
            f"plan {plan_id} carries decision {plan['decision_ref']}; adding a TASK "
            "changes its fingerprint and requires a fresh PLAN decision"
        )

    relative_task = task_path.relative_to(root).as_posix()
    relative_plan = plan_path.relative_to(root).as_posix()
    validate_records(root, [("work_item", task), ("plan", plan)])
    authorize_claim_targets(
        root, claim_id=claim_id, agent=agent, targets=[relative_task, relative_plan]
    )
    transaction = AtomicMutationService(root).apply(
        writes={relative_task: task, relative_plan: plan},
        event_type="WORK_ITEM_CREATED",
        event_payload={
            "task_id": task_id,
            "plan_id": plan_id,
            "capabilities": requested,
            "added_dependencies": added,
        },
    )
    return {
        "task_id": task_id,
        "plan_id": plan_id,
        "record": task,
        "added_dependencies": added,
        "warnings": warnings,
        "transaction": transaction,
    }


def activate_plan(
    root: Path,
    *,
    plan_id: str,
    claim_id: str | None = None,
    agent: str = DEFAULT_AGENT,
) -> dict[str, Any]:
    """Make a plan executable and select it as the current planning reference."""
    root = root.resolve()
    raise HarnessError(
        "Plans become executable only through human approval: "
        "'approval prepare', 'approval record', then 'plan apply-decision'"
    )
    plan, plan_path = _load_plan(root, plan_id)
    status = plan.get("status")
    if status in RETIRED_PLAN_STATUSES:
        raise HarnessError(
            f"Plan {plan_id} is {status} and cannot become the current plan"
        )
    subject = _plan_subject(plan)
    if not _string_list(subject, "work_item_refs"):
        suggested = next_record_id(root, "work_item")
        raise HarnessError(
            f"Plan {plan_id} lists no TASK; create one first with "
            f"'new task {suggested} \"<title>\" --plan {plan_id}'"
        )

    _records, record_paths = load_record_index(root)
    plan["approval_dependencies"], added = synced_plan_dependencies(
        root, plan, record_paths
    )
    before_status = str(status)
    if status not in EXECUTABLE_PLAN_STATUSES:
        plan["status"] = "ACTIVE"
    plan.setdefault("execution_role", "CURRENT_PLANNING_REFERENCE")
    plan["updated_at"] = utc_now()

    state_path = root / HARNESS_DIR / "state.json"
    state = load_json(state_path)
    before_plan = state.get("current_plan")
    state["current_plan"] = plan_id
    state["updated_at"] = plan["updated_at"]
    # Kept accurate only for projects that already track it; this command does
    # not introduce the field where it is absent.
    history = state.get("historical_plan_refs")
    if isinstance(history, list) and isinstance(before_plan, str):
        if before_plan not in history and before_plan != plan_id:
            state["historical_plan_refs"] = [*history, before_plan]

    relative_plan = plan_path.relative_to(root).as_posix()
    relative_state = state_path.relative_to(root).as_posix()
    validate_records(root, [("plan", plan), ("state", state)])
    authorize_claim_targets(
        root, claim_id=claim_id, agent=agent, targets=[relative_plan, relative_state]
    )
    transaction = AtomicMutationService(root).apply(
        writes={relative_plan: plan, relative_state: state},
        event_type="PLAN_ACTIVATED",
        event_payload={
            "plan_id": plan_id,
            "before_plan_status": before_status,
            "after_plan_status": plan["status"],
            "before_current_plan": before_plan,
            "added_dependencies": added,
        },
    )
    return {
        "plan_id": plan_id,
        "plan_status": plan["status"],
        "current_plan": plan_id,
        "previous_current_plan": before_plan,
        "added_dependencies": added,
        "transaction": transaction,
    }
