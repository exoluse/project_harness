from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .approvals import approval_status, find_current_approval
from .constants import (
    CAPABILITY_APPROVAL_TYPES,
    HARNESS_DIR,
    NEVER_AGENT_CAPABILITIES,
    OPEN_ITEM_CLOSED_STATES,
)
from .core import (
    HarnessError,
    binding_status,
    git_changed_paths,
    git_head,
    load_json,
    load_record_index,
    normalize_claim_path,
    record_path,
    run_git,
    subject_fingerprint,
    subject_fingerprint_for_path,
)
from .evaluation import EvaluationContext
from .policy import approval_required, record_mode


@dataclass
class GateResult:
    gate: str
    subject_id: str
    passed: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    subject: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "gate": self.gate,
            "subject_id": self.subject_id,
            "passed": self.passed,
            "blockers": self.blockers,
            "warnings": self.warnings,
        }


GLOBAL_INTEGRITY_CODES = {
    "MISSING_STRUCTURE",
    "INVALID_JSON",
    "STATE_PROJECT_MISMATCH",
    "INVALID_LIFECYCLE",
    "MALFORMED_PROJECT",
    "MALFORMED_STATE",
    "DUPLICATE_ID",
    "MISSING_ID",
    "ID_FILENAME_MISMATCH",
    "KIND_DIRECTORY_MISMATCH",
    "ID_PREFIX",
    "SECRET_VALUE",
    "MISSING_ACTIVE_PLAN",
    "MISSING_CURRENT_PLAN",
    "MISSING_WORK_ITEM",
    "MISSING_REQUIRED_FEATURE",
}


def _known_references(value: Any, known_ids: set[str]) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for child in value.values():
            found.update(_known_references(child, known_ids))
    elif isinstance(value, list):
        for child in value:
            found.update(_known_references(child, known_ids))
    elif isinstance(value, str) and value in known_ids:
        found.add(value)
    return found


def _reachable_paths(
    root: Path,
    seeds: set[str],
    *,
    expand_plans: bool,
    context: EvaluationContext | None = None,
) -> set[str]:
    if context is not None:
        context.require_root(root)
        records, paths = context.records, context.paths
    else:
        records, paths = load_record_index(root)
    known = set(records)
    reachable = set(value for value in seeds if value in known)
    changed = True
    while changed:
        changed = False
        for record_id in list(reachable):
            if records.get(record_id, {}).get("kind") == "plan" and not expand_plans:
                continue
            for reference in _known_references(records.get(record_id, {}), known):
                if reference not in reachable:
                    reachable.add(reference)
                    changed = True
        for record_id, record in records.items():
            if record_id in reachable:
                continue
            reverse_relevant = False
            if record.get("kind") == "artifact":
                reverse_relevant = record.get("source_ref") in reachable
            elif record.get("kind") == "open_item":
                reverse_relevant = bool(
                    reachable.intersection(
                        set(record.get("affects", [])) | set(record.get("blocks", []))
                    )
                )
            elif record.get("kind") == "evidence":
                reverse_relevant = bool(
                    reachable.intersection(set(record.get("supports", [])))
                )
            if reverse_relevant:
                reachable.add(record_id)
                changed = True
    return {
        str(paths[record_id].resolve())
        for record_id in reachable
        if record_id in paths
        and not (
            records.get(record_id, {}).get("kind") == "plan"
            and not expand_plans
            and record_id not in seeds
        )
    }


def _validation_blockers(
    root: Path,
    *,
    relevant_ids: set[str] | None = None,
    project_wide: bool = False,
    expand_plans: bool = True,
    context: EvaluationContext | None = None,
) -> list[str]:
    if context is None:
        context = EvaluationContext.load(root)
    else:
        context.require_root(root)
    issues = [issue for issue in context.validation_issues if issue.severity == "ERROR"]
    if project_wide:
        selected = issues
    else:
        relevant_paths: set[str] = set()
        if relevant_ids:
            try:
                relevant_paths = _reachable_paths(
                    root,
                    relevant_ids,
                    expand_plans=expand_plans,
                    context=context,
                )
            except HarnessError:
                # Structural/index corruption is selected through GLOBAL_INTEGRITY_CODES.
                relevant_paths = set()
        selected = [
            issue
            for issue in issues
            if issue.code in GLOBAL_INTEGRITY_CODES
            or (issue.path is not None and str(Path(issue.path).resolve()) in relevant_paths)
        ]
    return [
        f"project validation {issue.code}: {issue.message}" for issue in selected
    ]


def _record(
    root: Path,
    kind: str,
    record_id: str,
    context: EvaluationContext | None = None,
) -> dict[str, Any]:
    if context is not None:
        context.require_root(root)
        record = context.records.get(record_id)
        if record is None or record.get("kind") != kind:
            raise HarnessError(f"Missing {kind} record: {record_id}")
        return record
    path = record_path(root, kind, record_id)
    return load_json(path)


def _open_item_resolution_complete(value: dict[str, Any]) -> bool:
    if value.get("status") not in OPEN_ITEM_CLOSED_STATES:
        return False
    resolution = value.get("resolution")
    if not isinstance(resolution, dict):
        return False
    for field in ("summary", "decided_by", "decision_authority", "resolved_at"):
        if not isinstance(resolution.get(field), str) or not resolution[field].strip():
            return False
    for field in ("propagated_to", "evidence_refs", "baseline_refs"):
        items = resolution.get(field)
        if not isinstance(items, list) or not items or any(
            not isinstance(item, str) or not item.strip() for item in items
        ):
            return False
    return True


def _active_open_items(
    root: Path, context: EvaluationContext | None = None
) -> list[dict[str, Any]]:
    if context is not None:
        context.require_root(root)
        return [
            value
            for value in context.records.values()
            if value.get("kind") == "open_item"
            and not _open_item_resolution_complete(value)
        ]
    directory = root / HARNESS_DIR / "open-items"
    values = []
    for path in directory.glob("OI-*.json"):
        value = load_json(path)
        # Fail closed: unknown states and incompletely resolved records remain open.
        if not _open_item_resolution_complete(value):
            values.append(value)
    return values


def _task_capability_approval_blockers(
    root: Path,
    task: dict[str, Any],
    records: dict[str, dict[str, Any]],
) -> list[str]:
    blockers: list[str] = []
    task_id = str(task.get("id", ""))
    capabilities = set(task.get("capabilities", []))
    task_forbidden = set(task.get("forbidden_actions", []))
    self_conflicts = sorted(capabilities.intersection(task_forbidden))
    if self_conflicts:
        blockers.append(
            f"task {task_id} requests its own forbidden actions: "
            + ", ".join(self_conflicts)
        )
    forbidden = sorted(capabilities.intersection(NEVER_AGENT_CAPABILITIES))
    if forbidden:
        blockers.append(
            f"task {task_id} requests capabilities that agents may never receive: "
            + ", ".join(forbidden)
        )

    approval_refs = task.get("capability_approval_refs", {})
    if approval_refs is None:
        approval_refs = {}
    if not isinstance(approval_refs, dict):
        return [
            *blockers,
            f"task {task_id} capability_approval_refs must be an object",
        ]

    task_scope = {task_id, *task.get("feature_refs", [])}
    for capability, approval_type in CAPABILITY_APPROVAL_TYPES.items():
        if capability not in capabilities:
            continue
        references = approval_refs.get(capability)
        if (
            not isinstance(references, list)
            or not references
            or any(not isinstance(item, str) for item in references)
        ):
            blockers.append(
                f"task {task_id} capability {capability} requires explicit "
                f"{approval_type} approval refs"
            )
            continue
        reasons: list[str] = []
        authorized = False
        for reference in references:
            approval = records.get(reference)
            if not approval or approval.get("kind") != "approval":
                reasons.append(f"{reference} is not an approval")
                continue
            if approval.get("approval_type") != approval_type:
                reasons.append(
                    f"{reference} is {approval.get('approval_type')}, not {approval_type}"
                )
                continue
            if capability not in set(approval.get("authorized_actions", [])):
                reasons.append(f"{reference} does not authorize {capability}")
                continue
            if capability in set(approval.get("excluded_actions", [])):
                reasons.append(f"{reference} excludes {capability}")
                continue
            if approval_type in {
                "PRODUCTION_DATA_CHANGE",
                "DESTRUCTIVE_ACTION",
                "SECRET_ACCESS",
                "EXCEPTION",
            }:
                change = records.get(str(approval.get("subject_id", "")), {})
                if not task_scope.intersection(set(change.get("affects", []))):
                    reasons.append(f"{reference} change subject does not affect {task_id}")
                    continue
            status, reason = approval_status(root, approval)
            if status != "CURRENT":
                reasons.append(f"{reference} is {status}: {reason}")
                continue
            condition_refs = approval.get("condition_refs", [])
            if approval.get("decision") == "APPROVED_WITH_CONDITIONS" and (
                not isinstance(condition_refs, list) or not condition_refs
            ):
                reasons.append(f"{reference} has no enforceable condition refs")
                continue
            unresolved_conditions: list[str] = []
            if isinstance(condition_refs, list):
                for condition_ref in condition_refs:
                    condition = records.get(str(condition_ref), {})
                    if condition.get("kind") != "open_item":
                        unresolved_conditions.append(
                            f"{condition_ref} is missing or not an open item"
                        )
                    elif not _open_item_resolution_complete(condition):
                        unresolved_conditions.append(str(condition_ref))
            if unresolved_conditions:
                reasons.append(
                    f"{reference} has unresolved conditions: "
                    + ", ".join(unresolved_conditions)
                )
                continue
            authorized = True
            break
        if not authorized:
            blockers.append(
                f"task {task_id} capability {capability} lacks a current "
                f"{approval_type} approval"
                + (f" ({'; '.join(reasons)})" if reasons else "")
            )
    return blockers


def plan_preflight_gate(
    root: Path,
    plan_id: str,
    *,
    require_approval: bool = False,
    context: EvaluationContext | None = None,
) -> GateResult:
    context = context or EvaluationContext.load(root)
    context.require_root(root)
    plan = _record(root, "plan", plan_id, context)
    records = context.records
    subject = plan.get("approval_subject", {})
    blockers: list[str] = []
    warnings: list[str] = []
    validation_errors = _validation_blockers(
        root, relevant_ids={plan_id}, context=context
    )
    if validation_errors:
        return GateResult(
            gate="PLAN_AUTHORIZED" if require_approval else "PLAN_PREFLIGHT",
            subject_id=plan_id,
            passed=False,
            blockers=validation_errors,
            subject=plan,
        )

    expected_dependencies: set[str] = set()
    for field_name, expected_kind in (
        ("requirement_refs", "requirement"),
        ("feature_refs", "feature"),
        ("work_item_refs", "work_item"),
    ):
        refs = subject.get(field_name, [])
        if not isinstance(refs, list) or not refs:
            blockers.append(f"{field_name} is empty")
            continue
        for reference in refs:
            record = records.get(reference)
            if record is None:
                blockers.append(f"{field_name} references missing {reference}")
            elif record.get("kind") != expected_kind:
                blockers.append(f"{reference} is not a {expected_kind}")
            else:
                expected_dependencies.add(
                    record_path(root, expected_kind, reference).relative_to(root).as_posix()
                )

    actual_dependencies = set(plan.get("approval_dependencies", []))
    missing_dependencies = expected_dependencies - actual_dependencies
    if missing_dependencies:
        blockers.append(
            "approval_dependencies omit planned records: "
            + ", ".join(sorted(missing_dependencies))
        )
    for dependency in actual_dependencies:
        try:
            normalized_dependency = normalize_claim_path(root, dependency)
            dependency_path = root / normalized_dependency
        except (HarnessError, TypeError) as exc:
            blockers.append(f"invalid approval dependency {dependency!r}: {exc}")
            continue
        if not dependency_path.is_file():
            blockers.append(f"approval dependency is missing: {dependency}")

    for feature_id in subject.get("feature_refs", []):
        feature = records.get(feature_id, {})
        criteria = feature.get("completion_criteria", [])
        if feature.get("required", True) and not criteria:
            blockers.append(f"required feature {feature_id} has no completion criteria")
        for criterion in criteria:
            if criterion.get("required", True) and not criterion.get("verification_plan"):
                blockers.append(f"required criterion {criterion.get('id')} has no verification plan")

    planned_requirements = set(subject.get("requirement_refs", []))
    planned_features = set(subject.get("feature_refs", []))
    for requirement_id in planned_requirements:
        realizing_features = [
            feature_id
            for feature_id in planned_features
            if requirement_id in records.get(feature_id, {}).get("requirement_refs", [])
        ]
        if not realizing_features:
            blockers.append(
                f"planned requirement {requirement_id} has no realizing feature"
            )
    for feature_id in planned_features:
        outside_requirements = set(
            records.get(feature_id, {}).get("requirement_refs", [])
        ) - planned_requirements
        if outside_requirements:
            blockers.append(
                f"feature {feature_id} traces to requirements outside plan scope: "
                + ", ".join(sorted(outside_requirements))
            )
    plan_authorized = set(subject.get("authorized_actions", []))
    plan_excluded = set(subject.get("excluded_actions", []))
    planned_tasks = set(subject.get("work_item_refs", []))
    for task_id in planned_tasks:
        task = records.get(task_id, {})
        if task.get("plan_id") != plan_id:
            blockers.append(f"task {task_id} does not point back to {plan_id}")
        if not task.get("feature_refs"):
            blockers.append(f"task {task_id} has no feature or scope basis")
        outside_features = set(task.get("feature_refs", [])) - planned_features
        if outside_features:
            blockers.append(
                f"task {task_id} references features outside plan scope: "
                + ", ".join(sorted(outside_features))
            )
        task_feature_criteria = {
            criterion.get("id")
            for feature_id in task.get("feature_refs", [])
            for criterion in records.get(feature_id, {}).get("completion_criteria", [])
            if isinstance(criterion, dict) and isinstance(criterion.get("id"), str)
        }
        task_criterion_refs = set(task.get("criterion_refs", []))
        if not task_criterion_refs:
            blockers.append(f"task {task_id} has no completion criterion scope")
        outside_criteria = task_criterion_refs - task_feature_criteria
        if outside_criteria:
            blockers.append(
                f"task {task_id} references criteria outside its feature scope: "
                + ", ".join(sorted(outside_criteria))
            )
        if not task.get("verification"):
            blockers.append(f"task {task_id} has no verification commands")
        capabilities = set(task.get("capabilities", []))
        blockers.extend(_task_capability_approval_blockers(root, task, records))
        unauthorized = capabilities - plan_authorized
        if unauthorized:
            blockers.append(
                f"task {task_id} requests unauthorized actions: "
                + ", ".join(sorted(unauthorized))
            )
        excluded = capabilities.intersection(plan_excluded)
        if excluded:
            blockers.append(
                f"task {task_id} requests excluded actions: "
                + ", ".join(sorted(excluded))
            )
    for feature_id in planned_features:
        implementing_tasks = [
            task_id
            for task_id in planned_tasks
            if feature_id in records.get(task_id, {}).get("feature_refs", [])
        ]
        if not implementing_tasks:
            blockers.append(f"planned feature {feature_id} has no implementing task")
        for criterion in records.get(feature_id, {}).get("completion_criteria", []):
            if not isinstance(criterion, dict) or not criterion.get("required", True):
                continue
            criterion_id = criterion.get("id")
            if not any(
                criterion_id in records.get(task_id, {}).get("criterion_refs", [])
                for task_id in implementing_tasks
            ):
                blockers.append(
                    f"required criterion {criterion_id} has no implementing task"
                )

    for item in _active_open_items(root, context):
        if item.get("gate_level") == "G0":
            blockers.append(f"G0 open item {item.get('id')}: {item.get('title')}")
        elif item.get("gate_level") == "G2":
            warnings.append(f"G2 assumption remains: {item.get('id')}")

    if not subject.get("verification_strategy"):
        blockers.append("plan verification_strategy is empty")
    if require_approval:
        approval, reason = find_current_approval(root, subject_id=plan_id, approval_type="PLAN")
        if approval is None:
            blockers.append(reason)
        else:
            approval_authorized = set(approval.get("authorized_actions", []))
            approval_excluded = set(approval.get("excluded_actions", []))
            for task_id in planned_tasks:
                capabilities = set(records.get(task_id, {}).get("capabilities", []))
                unauthorized = capabilities - approval_authorized
                if unauthorized:
                    blockers.append(
                        f"approval does not authorize {task_id} actions: "
                        + ", ".join(sorted(unauthorized))
                    )
                excluded = capabilities.intersection(approval_excluded)
                if excluded:
                    blockers.append(
                        f"approval excludes {task_id} actions: "
                        + ", ".join(sorted(excluded))
                    )
            if approval.get("decision") == "APPROVED_WITH_CONDITIONS":
                warnings.extend(
                    f"approval condition: {condition}"
                    for condition in approval.get("conditions", [])
                )
                condition_refs = approval.get("condition_refs", [])
                if not condition_refs:
                    blockers.append("conditional approval has no enforceable condition_refs")
                for condition_ref in condition_refs:
                    condition = records.get(condition_ref)
                    if not condition or condition.get("kind") != "open_item":
                        blockers.append(
                            f"conditional approval references missing open item {condition_ref}"
                        )
                    elif not _open_item_resolution_complete(condition):
                        gate_level = condition.get("gate_level")
                        if gate_level == "G0" or gate_level not in {
                            "G1",
                            "G2",
                            "G3",
                        }:
                            blockers.append(
                                f"approval condition remains unresolved: {condition_ref}"
                            )
                        else:
                            warnings.append(
                                "approval condition remains task-scoped: "
                                f"{condition_ref} ({gate_level})"
                            )

    return GateResult(
        gate="PLAN_AUTHORIZED" if require_approval else "PLAN_PREFLIGHT",
        subject_id=plan_id,
        passed=not blockers,
        blockers=blockers,
        warnings=warnings,
        subject=plan,
    )


def _record_number(value: dict[str, Any]) -> int:
    record_id = str(value.get("id", ""))
    try:
        return int(record_id.rsplit("-", 1)[1])
    except (IndexError, ValueError):
        return -1


def _latest_task_result_assessment(
    root: Path,
    task_id: str,
    records: dict[str, dict[str, Any]],
    *,
    current_task_fingerprint: str | None = None,
    current_plan_fingerprint: str | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    from .collaboration import result_currentness

    results = [
        record
        for record in records.values()
        if record.get("kind") == "result" and record.get("task_id") == task_id
    ]
    if not results:
        return None, None, ["no submitted result"]
    result = max(results, key=_record_number)
    reasons: list[str] = []
    if current_task_fingerprint is not None and result.get(
        "task_fingerprint"
    ) != current_task_fingerprint:
        reasons.append("latest result task fingerprint is stale")
    if current_plan_fingerprint is not None and result.get(
        "plan_fingerprint"
    ) != current_plan_fingerprint:
        reasons.append("latest result plan fingerprint is stale")
    if result.get("verification_state") != "PASS":
        reasons.append(
            f"latest result verification_state is {result.get('verification_state')}"
        )
    if not result.get("base_commit") or not result.get("head_commit"):
        reasons.append("latest result lacks a committed Git baseline")
    else:
        current_head = git_head(root)
        if current_head is None:
            reasons.append("current integration checkout has no Git HEAD")
        else:
            base_commit = str(result["base_commit"])
            result_head = str(result["head_commit"])
            result_lineage, _output = run_git(
                root,
                "merge-base",
                "--is-ancestor",
                base_commit,
                result_head,
            )
            if result_lineage != 0:
                reasons.append("latest result head is not descended from its base commit")
            integration_lineage, _output = run_git(
                root,
                "merge-base",
                "--is-ancestor",
                result_head,
                current_head,
            )
            if integration_lineage != 0:
                reasons.append(
                    "latest result head is not integrated in the current Git history"
                )
        dirty = git_changed_paths(root)
        if dirty is None:
            reasons.append("latest result is not in a Git worktree")
        else:
            unintegrated = set(result.get("changed_files", [])).intersection(dirty)
            if unintegrated:
                reasons.append(
                    "latest result files are not committed/integrated: "
                    + ", ".join(sorted(unintegrated))
                )
    current, currentness_reasons = result_currentness(root, result)
    if not current:
        reasons.extend(currentness_reasons)
    reviews = [
        record
        for record in records.values()
        if record.get("kind") == "review"
        and record.get("result_id") == result.get("id")
    ]
    if not reviews:
        return result, None, [*reasons, "latest result has no review"]
    review = max(reviews, key=_record_number)
    if review.get("decision") != "PASS":
        reasons.append(f"latest review decision is {review.get('decision')}")
    if review.get("result_fingerprint") != subject_fingerprint(result):
        reasons.append("latest review result fingerprint is stale")
    if review.get("result_build_fingerprint") != result.get("build_fingerprint"):
        reasons.append("latest review build fingerprint is stale")
    if str(review.get("reviewer", "")).casefold() == str(
        result.get("agent", "")
    ).casefold():
        reasons.append("latest result was self-reviewed")
    return result, review, reasons


def task_start_gate(
    root: Path,
    task_id: str,
    *,
    context: EvaluationContext | None = None,
) -> GateResult:
    context = context or EvaluationContext.load(root)
    context.require_root(root)
    task = _record(root, "work_item", task_id, context)
    blockers: list[str] = []
    warnings: list[str] = []
    validation_errors = _validation_blockers(
        root, relevant_ids={task_id}, expand_plans=False, context=context
    )
    if validation_errors:
        return GateResult(
            gate="TASK_START",
            subject_id=task_id,
            passed=False,
            blockers=validation_errors,
            subject=task,
        )
    records = context.records
    task_features = set(task.get("feature_refs", []))
    task_criteria = set(task.get("criterion_refs", []))
    task_scope_ids = {task_id, *task_features, *task_criteria}
    plan_id = task.get("plan_id")
    if not isinstance(plan_id, str) or not plan_id:
            blockers.append("task has no plan_id")
    else:
            plan = _record(root, "plan", plan_id, context)
            plan_subject = plan.get("approval_subject", {})
            if not isinstance(plan_subject, dict):
                blockers.append("task plan approval_subject is malformed")
                plan_subject = {}
            if task_id not in plan_subject.get("work_item_refs", []):
                blockers.append(f"task {task_id} is outside the approved plan subject")
            state = load_json(root / HARNESS_DIR / "state.json")
            if state.get("active_plan") != plan_id:
                blockers.append(
                    f"task plan {plan_id} is not the active plan {state.get('active_plan')}"
                )
            if state.get("lifecycle_state") not in {
                "APPROVED",
                "BUILDING",
                "VERIFYING",
                "MAINTAINING",
            }:
                blockers.append(
                    f"lifecycle state {state.get('lifecycle_state')} is not executable"
                )
            if plan.get("status") not in {
                "APPROVED",
                "APPROVED_WITH_CONDITIONS",
                "ACTIVE",
            }:
                blockers.append(
                    f"plan status {plan.get('status')} is not executable"
                )
            approval, reason = find_current_approval(
                root, subject_id=plan_id, approval_type="PLAN"
            )
            if approval is None:
                blockers.append(reason)
            else:
                if plan.get("decision_ref") != approval.get("id"):
                    blockers.append(
                        "plan has not materialized the latest approval decision"
                    )
                if state.get("active_decision") != approval.get("id"):
                    blockers.append(
                        "project state has not materialized the latest approval decision"
                    )
                task_capabilities = set(task.get("capabilities", []))
                plan_authorized = set(plan_subject.get("authorized_actions", []))
                plan_excluded = set(plan_subject.get("excluded_actions", []))
                approval_authorized = set(approval.get("authorized_actions", []))
                approval_excluded = set(approval.get("excluded_actions", []))
                unauthorized = task_capabilities - plan_authorized
                unauthorized.update(task_capabilities - approval_authorized)
                excluded = task_capabilities.intersection(
                    plan_excluded | approval_excluded
                )
                if unauthorized:
                    blockers.append(
                        "task requests actions outside the current plan approval: "
                        + ", ".join(sorted(unauthorized))
                    )
                if excluded:
                    blockers.append(
                        "task requests explicitly excluded actions: "
                        + ", ".join(sorted(excluded))
                    )
                for condition_ref in approval.get("condition_refs", []):
                    condition = records.get(condition_ref)
                    if not condition or condition.get("kind") != "open_item":
                        blockers.append(
                            f"approval condition references missing open item {condition_ref}"
                        )
                        continue
                    if _open_item_resolution_complete(condition):
                        continue
                    affected = set(condition.get("affects", [])) | set(
                        condition.get("blocks", [])
                    )
                    if condition.get("gate_level") == "G0" or task_scope_ids.intersection(
                        affected
                    ):
                        blockers.append(
                            f"approval condition blocks this task: {condition_ref}"
                        )
                    else:
                        warnings.append(
                            f"unresolved approval condition is outside this task: {condition_ref}"
                        )
    blockers.extend(_task_capability_approval_blockers(root, task, records))

    if task.get("status") not in {"READY", "APPROVED", "RUNNING"}:
        blockers.append(f"task status {task.get('status')} is not startable")
    for declared_blocker in task.get("blocked_by", []):
        record = records.get(declared_blocker)
        if record is None:
            blockers.append(f"declared blocker {declared_blocker} is missing")
            continue
        if record.get("kind") == "open_item":
            resolved = _open_item_resolution_complete(record)
        elif record.get("kind") == "work_item" and record_mode(root) == "REQUIRED":
            resolved = record.get("status") in {"INTEGRATED", "DONE", "CLOSED"}
        else:
            resolved = record.get("status") in {
                "DONE",
                "CLOSED",
                "VERIFIED",
                "ACCEPTED",
                "RESOLVED",
            }
        if not resolved:
            blockers.append(
                f"declared blocker {declared_blocker} is unresolved"
            )
    for dependency in task.get("dependencies", []):
        record = records.get(dependency)
        if not record:
            blockers.append(f"dependency {dependency} is not complete")
        elif record.get("kind") == "work_item":
            if record.get("status") not in {"INTEGRATED", "DONE", "CLOSED"}:
                blockers.append(f"dependency {dependency} is not complete")
            elif record_mode(root) == "REQUIRED":
                dependency_plan = record.get("plan_id")
                dependency_plan_path = (
                    record_path(root, "plan", dependency_plan)
                    if isinstance(dependency_plan, str)
                    else None
                )
                result, review, reasons = _latest_task_result_assessment(
                    root,
                    dependency,
                    records,
                    current_task_fingerprint=subject_fingerprint(record),
                    current_plan_fingerprint=(
                        subject_fingerprint_for_path(dependency_plan_path)
                        if dependency_plan_path is not None
                        else None
                    ),
                )
                if result is None or review is None or reasons:
                    blockers.append(
                        f"dependency {dependency} lacks a current independently reviewed PASS result"
                        + (f" ({'; '.join(reasons)})" if reasons else "")
                    )
        elif record.get("status") not in {"DONE", "CLOSED", "VERIFIED", "ACCEPTED", "INTEGRATED"}:
            blockers.append(f"dependency {dependency} is not complete")
    for item in _active_open_items(root, context):
        affected = set(item.get("blocks", [])) | set(item.get("affects", []))
        if item.get("gate_level") == "G0" or (
            item.get("gate_level") == "G1"
            and task_scope_ids.intersection(affected)
        ):
            blockers.append(f"open item {item.get('id')} blocks task {task_id}")

    return GateResult(
        gate="TASK_START",
        subject_id=task_id,
        passed=not blockers,
        blockers=blockers,
        warnings=warnings,
        subject=task,
    )


def _basic_evidence_reasons(root: Path, evidence: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if evidence.get("result") != "VERIFIED":
        reasons.append(f"result is {evidence.get('result')}")
    for field in ("claim", "method", "environment", "expected", "actual"):
        if not isinstance(evidence.get(field), str) or not evidence.get(field).strip():
            reasons.append(f"{field} is missing")
    ambiguity = evidence.get("ambiguity")
    level = ambiguity.get("level") if isinstance(ambiguity, dict) else None
    if level not in {"NONE", "LOW"}:
        reasons.append(f"ambiguity is {level}")
    bindings = evidence.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        reasons.append("no immutable file binding records the observed subject")
        bindings = []
    for binding in bindings:
        if not isinstance(binding, dict):
            reasons.append("binding is malformed")
            continue
        current, reason = binding_status(root, binding)
        if not current:
            reasons.append(reason)
    return reasons


def _evidence_is_eligible(
    root: Path,
    evidence: dict[str, Any],
    *,
    criterion: dict[str, Any],
    feature_id: str,
    required_profile: str | None,
) -> tuple[bool, list[str]]:
    reasons = _basic_evidence_reasons(root, evidence)
    criterion_id = criterion.get("id")
    supports = evidence.get("supports")
    if not isinstance(supports, list) or criterion_id not in supports:
        reasons.append(f"does not support {criterion_id}")
    if required_profile and evidence.get("profile") != required_profile:
        reasons.append(
            f"profile is {evidence.get('profile')}, required {required_profile}"
        )
    bound_paths = {
        binding.get("path")
        for binding in evidence.get("bindings", [])
        if isinstance(binding, dict) and isinstance(binding.get("path"), str)
    }
    missing_bindings = set(criterion.get("required_bindings", [])) - bound_paths
    if missing_bindings:
        reasons.append(
            "missing required subject bindings: " + ", ".join(sorted(missing_bindings))
        )
    criterion_record = {
        **criterion,
        "kind": "completion_criterion",
        "feature_id": feature_id,
    }
    expected_fingerprint = subject_fingerprint(criterion_record)
    subject = evidence.get("subject")
    fingerprint_map = subject.get("criterion_fingerprints") if isinstance(subject, dict) else None
    recorded_fingerprint = (
        fingerprint_map.get(criterion_id) if isinstance(fingerprint_map, dict) else None
    )
    if recorded_fingerprint != expected_fingerprint:
        reasons.append(f"criterion fingerprint for {criterion_id} is missing or stale")
    return not reasons, reasons


def feature_completion_gate(
    root: Path,
    feature_id: str,
    *,
    require_customer_approval: bool = True,
    context: EvaluationContext | None = None,
) -> GateResult:
    context = context or EvaluationContext.load(root)
    context.require_root(root)
    feature = _record(root, "feature", feature_id, context)
    records = context.records
    blockers: list[str] = []
    warnings: list[str] = []
    validation_errors = _validation_blockers(
        root, relevant_ids={feature_id}, context=context
    )
    if validation_errors:
        return GateResult(
            gate="FEATURE_COMPLETION",
            subject_id=feature_id,
            passed=False,
            blockers=validation_errors,
            subject=feature,
        )
    criteria = feature.get("completion_criteria", [])
    if not criteria:
        blockers.append("feature has no completion criteria")
    for criterion in criteria:
        if not criterion.get("required", True):
            continue
        evidence_refs = criterion.get("evidence_refs", [])
        if not evidence_refs:
            blockers.append(f"criterion {criterion.get('id')} has no evidence")
            continue
        required_profiles = criterion.get("required_profiles", []) or [None]
        for required_profile in required_profiles:
            candidates = [
                evidence
                for evidence in records.values()
                if evidence.get("kind") == "evidence"
                and criterion.get("id") in evidence.get("supports", [])
                and (
                    required_profile is None
                    or evidence.get("profile") == required_profile
                )
            ]
            detail: list[str] = []
            eligible = False
            if not candidates:
                detail.append("no evidence record supports this criterion/profile")
            else:
                latest = max(candidates, key=_record_number)
                latest_id = latest.get("id")
                if latest_id not in evidence_refs:
                    detail.append(
                        f"latest evidence {latest_id} is omitted from the completion contract"
                    )
                passed, reasons = _evidence_is_eligible(
                    root,
                    latest,
                    criterion=criterion,
                    feature_id=feature_id,
                    required_profile=required_profile,
                )
                if passed and latest_id in evidence_refs:
                    eligible = True
                elif reasons:
                    detail.append(f"{latest_id}: {', '.join(reasons)}")
            if not eligible:
                profile_label = required_profile or "ANY"
                blockers.append(
                    f"criterion {criterion.get('id')} lacks eligible {profile_label} "
                    f"evidence ({'; '.join(detail)})"
                )

    criterion_ids = {item.get("id") for item in criteria}
    for item in _active_open_items(root, context):
        affected = set(item.get("affects", [])) | set(item.get("blocks", []))
        if item.get("gate_level") in {"G0", "G1"} and (
            feature_id in affected or criterion_ids.intersection(affected)
        ):
            blockers.append(f"open item {item.get('id')} blocks feature completion")

    if require_customer_approval and feature.get("customer_acceptance_required"):
        approval, reason = find_current_approval(
            root, subject_id=feature_id, approval_type="CUSTOMER_ACCEPTANCE"
        )
        if approval is None:
            blockers.append(reason)

    return GateResult(
        gate="FEATURE_COMPLETION",
        subject_id=feature_id,
        passed=not blockers,
        blockers=blockers,
        warnings=warnings,
        subject=feature,
    )


def project_completion_gate(
    root: Path,
    *,
    require_approval: bool = True,
    context: EvaluationContext | None = None,
) -> GateResult:
    context = context or EvaluationContext.load(root)
    context.require_root(root)
    project = load_json(root / HARNESS_DIR / "project.json")
    state = load_json(root / HARNESS_DIR / "state.json")
    records, paths = context.records, context.paths
    blockers: list[str] = []
    warnings: list[str] = []
    validation_errors = _validation_blockers(
        root, project_wide=True, context=context
    )
    if validation_errors:
        return GateResult(
            gate="PROJECT_COMPLETION",
            subject_id=project.get("id", "PROJECT"),
            passed=False,
            blockers=validation_errors,
            subject=project,
        )
    required_features = project.get("required_features", [])
    if not isinstance(required_features, list) or not required_features:
        blockers.append("project has no required features")
        required_features = []
    active_plan = state.get("active_plan")
    plan: dict[str, Any] = {}
    expected_dependencies: set[str] = set()
    if not isinstance(active_plan, str) or not active_plan:
        blockers.append("project has no active plan")
    elif isinstance(active_plan, str) and active_plan:
        try:
            plan_gate = plan_preflight_gate(
                root,
                active_plan,
                require_approval=True,
                context=context,
            )
        except HarnessError as exc:
            blockers.append(str(exc))
        else:
            plan = plan_gate.subject
            blockers.extend(f"active plan: {value}" for value in plan_gate.blockers)
            warnings.extend(plan_gate.warnings)
            expected_dependencies.add(
                record_path(root, "plan", active_plan).relative_to(root).as_posix()
            )
            expected_dependencies.update(plan.get("approval_dependencies", []))
            if plan.get("status") not in {"ACTIVE", "CLOSED"}:
                blockers.append(f"active plan status {plan.get('status')} is not closable")
            planned_features = set(
                plan.get("approval_subject", {}).get("feature_refs", [])
            )
            outside_plan = set(required_features) - planned_features
            if outside_plan:
                blockers.append(
                    "required features outside the active plan: "
                    + ", ".join(sorted(outside_plan))
                )
            plan_approval, _reason = find_current_approval(
                root, subject_id=active_plan, approval_type="PLAN"
            )
            if plan_approval:
                expected_dependencies.add(
                    record_path(root, "approval", plan_approval["id"])
                    .relative_to(root)
                    .as_posix()
                )

    for feature_id in required_features:
        gate = feature_completion_gate(root, feature_id, context=context)
        blockers.extend(f"{feature_id}: {value}" for value in gate.blockers)
        warnings.extend(gate.warnings)
        expected_dependencies.add(
            record_path(root, "feature", feature_id).relative_to(root).as_posix()
        )
        feature = records.get(feature_id, {})
        for criterion in feature.get("completion_criteria", []):
            for evidence_id in criterion.get("evidence_refs", []):
                evidence_path = paths.get(evidence_id)
                if evidence_path:
                    expected_dependencies.add(evidence_path.relative_to(root).as_posix())
        if feature.get("customer_acceptance_required"):
            acceptance, _reason = find_current_approval(
                root,
                subject_id=feature_id,
                approval_type="CUSTOMER_ACCEPTANCE",
            )
            if acceptance:
                expected_dependencies.add(
                    record_path(root, "approval", acceptance["id"])
                    .relative_to(root)
                    .as_posix()
                )

    task_result_evidence: dict[str, set[str]] = {}
    if plan and record_mode(root) == "REQUIRED":
        current_plan_fingerprint = subject_fingerprint_for_path(
            record_path(root, "plan", active_plan)
        )
        for task_id in plan.get("approval_subject", {}).get("work_item_refs", []):
            task = records.get(task_id, {})
            if task.get("status") not in {"INTEGRATED", "DONE", "CLOSED"}:
                blockers.append(f"task {task_id} is not integrated or closed")
            current_task_fingerprint = subject_fingerprint(task)
            result, review, result_reasons = _latest_task_result_assessment(
                root,
                task_id,
                records,
                current_task_fingerprint=current_task_fingerprint,
                current_plan_fingerprint=current_plan_fingerprint,
            )
            if result is None or review is None or result_reasons:
                blockers.append(
                    f"task {task_id} latest attempt is not a current independently reviewed PASS"
                    + (
                        f" ({'; '.join(result_reasons)})"
                        if result_reasons
                        else ""
                    )
                )
            else:
                task_result_evidence[task_id] = set(result.get("evidence_refs", []))
                expected_dependencies.add(paths[result["id"]].relative_to(root).as_posix())
                expected_dependencies.add(paths[review["id"]].relative_to(root).as_posix())

        planned_task_ids = plan.get("approval_subject", {}).get("work_item_refs", [])
        for feature_id in required_features:
            feature = records.get(feature_id, {})
            for criterion in feature.get("completion_criteria", []):
                if not isinstance(criterion, dict) or not criterion.get("required", True):
                    continue
                criterion_id = criterion.get("id")
                implementing_tasks = [
                    task_id
                    for task_id in planned_task_ids
                    if criterion_id
                    in records.get(task_id, {}).get("criterion_refs", [])
                ]
                bound_evidence = set().union(
                    *(task_result_evidence.get(task_id, set()) for task_id in implementing_tasks)
                ) if implementing_tasks else set()
                for profile in criterion.get("required_profiles", []) or [None]:
                    candidates = [
                        record
                        for record in records.values()
                        if record.get("kind") == "evidence"
                        and criterion_id in record.get("supports", [])
                        and (profile is None or record.get("profile") == profile)
                    ]
                    if not candidates:
                        continue
                    latest_evidence = max(candidates, key=_record_number)
                    if latest_evidence.get("id") not in bound_evidence:
                        blockers.append(
                            f"criterion {criterion_id} latest {profile or 'ANY'} evidence "
                            f"{latest_evidence.get('id')} is not bound to the latest task result"
                        )

    closure_contract = project.get("closure_contract")
    if not isinstance(closure_contract, list) or not closure_contract:
        blockers.append("project closure_contract is empty")
        closure_contract = []
    for contract in closure_contract:
        if not isinstance(contract, dict) or not contract.get("required", True):
            continue
        contract_id = contract.get("id", "UNKNOWN")
        evidence_refs = contract.get("evidence_refs", [])
        if not isinstance(evidence_refs, list) or not evidence_refs:
            blockers.append(f"closure criterion {contract_id} has no evidence")
            continue
        profiles = contract.get("required_profiles", []) or [None]
        for profile in profiles:
            eligible = False
            detail: list[str] = []
            for evidence_id in evidence_refs:
                evidence = records.get(evidence_id)
                if not evidence or evidence.get("kind") != "evidence":
                    detail.append(f"missing {evidence_id}")
                    continue
                reasons = _basic_evidence_reasons(root, evidence)
                if contract_id not in evidence.get("supports", []):
                    reasons.append(f"does not support {contract_id}")
                if profile and evidence.get("profile") != profile:
                    reasons.append(f"profile is {evidence.get('profile')}, required {profile}")
                contract_record = {
                    **contract,
                    "kind": "closure_criterion",
                    "project_id": project.get("id"),
                }
                subject = evidence.get("subject")
                fingerprints = (
                    subject.get("closure_criterion_fingerprints")
                    if isinstance(subject, dict)
                    else None
                )
                recorded = (
                    fingerprints.get(contract_id)
                    if isinstance(fingerprints, dict)
                    else None
                )
                if recorded != subject_fingerprint(contract_record):
                    reasons.append(
                        f"closure criterion fingerprint for {contract_id} is missing or stale"
                    )
                if reasons:
                    detail.append(f"{evidence_id}: {', '.join(reasons)}")
                else:
                    eligible = True
                    expected_dependencies.add(paths[evidence_id].relative_to(root).as_posix())
            if not eligible:
                blockers.append(
                    f"closure criterion {contract_id} lacks eligible {profile or 'ANY'} "
                    f"evidence ({'; '.join(detail)})"
                )

    for item in _active_open_items(root, context):
        if item.get("gate_level") in {"G0", "G1"}:
            blockers.append(f"open item {item.get('id')} blocks project completion")
        elif item.get("gate_level") == "G2":
            warnings.append(f"G2 assumption remains at closure: {item.get('id')}")

    from .collaboration import list_claims

    active_claims = list_claims(root, active_only=True)
    if active_claims:
        blockers.append(
            "active write claims remain: "
            + ", ".join(claim.get("id", "UNKNOWN") for claim in active_claims)
        )
    if state.get("lifecycle_state") not in {
        "CUSTOMER_ACCEPTANCE",
        "DEPLOYING",
        "CLOSED",
    }:
        blockers.append(
            f"lifecycle state {state.get('lifecycle_state')} is not ready for closure"
        )

    actual_dependencies = set(project.get("approval_dependencies", []))
    missing_dependencies = expected_dependencies - actual_dependencies
    if missing_dependencies:
        blockers.append(
            "project closure approval_dependencies omit: "
            + ", ".join(sorted(missing_dependencies))
        )
    for dependency in actual_dependencies:
        try:
            normalized = normalize_claim_path(root, dependency)
        except (HarnessError, TypeError) as exc:
            blockers.append(f"invalid project approval dependency {dependency!r}: {exc}")
            continue
        if not (root / normalized).is_file():
            blockers.append(f"project approval dependency is missing: {dependency}")

    if require_approval and approval_required(root, "PROJECT_CLOSURE"):
        approval, reason = find_current_approval(
            root, subject_id=project.get("id"), approval_type="PROJECT_CLOSURE"
        )
        if approval is None:
            blockers.append(reason)
    return GateResult(
        gate="PROJECT_COMPLETION",
        subject_id=project.get("id", "PROJECT"),
        passed=not blockers,
        blockers=blockers,
        warnings=warnings,
        subject=project,
    )
