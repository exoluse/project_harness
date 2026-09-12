"""Versioned, explicit routine execution coverage; legacy hashes stay unchanged.

A scope is authored before the owner decides and preserved in the approval's
baseline. It describes bounded work, not a mutable permission inferred by an
agent. Tasks and single-level plans may share it only after containment checks.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .core import (
    HarnessError, canonical_json, is_path_within, load_json, normalize_claim_path,
    record_path, sha256_bytes, subject_fingerprint, utc_now,
)

SCOPE_SCHEMA = "harness.execution-scope/v1"
RISKS = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
SET_FIELDS = {
    "requirement_refs", "source_refs", "acceptance_criteria", "feature_refs",
    "required_profiles", "required_bindings", "write_scope", "authorized_actions",
    "excluded_actions", "capabilities", "forbidden_actions", "criterion_refs",
}


def canonical_scope_value(value: Any, field: str = "") -> Any:
    if isinstance(value, dict):
        return {key: canonical_scope_value(item, key) for key, item in value.items()}
    if isinstance(value, list):
        items = [canonical_scope_value(item) for item in value]
        if field in SET_FIELDS or field == "completion_criteria":
            return sorted(items, key=canonical_json)
        return items
    return value


def governed_definition(record: dict[str, Any]) -> dict[str, Any]:
    kind = record.get("kind")
    fields = {
        "requirement": ("required", "priority", "statement", "source_refs", "acceptance_criteria"),
        "feature": ("required", "requirement_refs", "customer_acceptance_required"),
        "change": ("classification", "source_refs", "affects", "impact"),
    }.get(kind)
    if fields is None:
        # Additional explicit dependencies remain conservative and version-bound.
        return {"legacy_fingerprint": subject_fingerprint(record)}
    result = {key: deepcopy(record.get(key)) for key in fields}
    if kind == "feature":
        result["completion_criteria"] = [{key: deepcopy(item.get(key)) for key in (
            "id", "statement", "required", "verification_plan", "required_profiles", "required_bindings"
        )} for item in record.get("completion_criteria", [])]
    return canonical_scope_value(result)


def plan_scope(plan: dict[str, Any]) -> dict[str, Any] | None:
    subject = plan.get("approval_subject", {})
    if not isinstance(subject, dict) or "decision_scope" not in subject:
        return None
    scope = subject["decision_scope"]
    if not isinstance(scope, dict) or scope.get("schema") != SCOPE_SCHEMA:
        raise HarnessError("Unsupported or malformed execution scope")
    required = {"schema", "scope_id", "requirements", "features", "changes", "dependencies",
                "write_scope", "authorized_actions", "excluded_actions", "max_risk",
                "verification", "criterion_verification", "constraints"}
    if set(scope) != required or not isinstance(scope.get("scope_id"), str):
        raise HarnessError("Execution scope fields are incomplete or unknown")
    for field in ("requirements", "features", "changes", "constraints"):
        if not isinstance(scope[field], dict):
            raise HarnessError(f"Execution scope {field} must be an object")
    for field in ("requirements", "features", "changes"):
        if any(not isinstance(value, dict) for value in scope[field].values()):
            raise HarnessError(f"Execution scope {field} definitions must be objects")
    dependencies = scope["dependencies"]
    if not isinstance(dependencies, list) or any(
        not isinstance(item, dict) or set(item) != {"path", "definition"}
        or not isinstance(item["path"], str) or not isinstance(item["definition"], dict)
        for item in dependencies
    ):
        raise HarnessError("Execution scope dependencies must list paths and definitions")
    if len({item["path"] for item in dependencies}) != len(dependencies):
        raise HarnessError("Execution scope contains duplicate dependencies")
    for field in ("write_scope", "authorized_actions", "excluded_actions", "verification"):
        if not isinstance(scope[field], list) or any(not isinstance(x, str) or not x.strip() for x in scope[field]):
            raise HarnessError(f"Execution scope {field} must be a string list")
    obligations = scope["criterion_verification"]
    if not isinstance(obligations, dict) or any(
        not isinstance(commands, list) or not commands
        or any(not isinstance(command, str) or not command.strip() for command in commands)
        for commands in obligations.values()
    ):
        raise HarnessError("Execution scope criterion verification must map criteria to commands")
    if not scope["requirements"] or not scope["features"] or not scope["write_scope"] or not obligations:
        raise HarnessError("Execution scope needs outcomes, write boundaries and verification")
    if not isinstance(scope["max_risk"], str) or scope["max_risk"] not in RISKS:
        raise HarnessError("Execution scope has an unknown risk ceiling")
    return scope


def scope_fingerprint(scope: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(canonical_scope_value(scope)).encode("utf-8"))


def plan_constraints(subject: dict[str, Any]) -> dict[str, Any]:
    result = {key: canonical_scope_value(value, key) for key, value in subject.items()
              if key not in {"requirement_refs", "feature_refs", "work_item_refs", "decision_scope",
                             "authorized_actions", "excluded_actions"}}
    streams = result.get("workstreams")
    if isinstance(streams, list):
        result["workstreams"] = [{key: value for key, value in stream.items()
                                  if key not in {"readiness", "status", "progress"}}
                                 if isinstance(stream, dict) else stream for stream in streams]
    return result


def snapshot_subject(root: Path, approval: dict[str, Any]) -> dict[str, Any]:
    subject_path = approval.get("subject_path")
    matches = [entry for entry in approval.get("snapshot_manifest", [])
               if isinstance(entry, dict) and entry.get("path") == subject_path]
    if len(matches) != 1:
        raise HarnessError("Approval needs exactly one original subject snapshot")
    path = normalize_claim_path(root, matches[0]["snapshot_path"])
    return load_json(root / path)


def snapshot_fingerprint(root: Path, approval: dict[str, Any]) -> str:
    original = snapshot_subject(root, approval)
    if original.get("kind") == "plan" and plan_scope(original) is not None:
        return scope_fingerprint(plan_scope(original))
    entries = approval.get("snapshot_manifest", [])
    paths = {entry["path"]: entry["snapshot_path"] for entry in entries}
    if len(paths) != len(entries):
        raise HarnessError("Approval snapshot has duplicate source paths")
    dependencies = {}
    for relative in original.get("approval_dependencies", []):
        normalized = normalize_claim_path(root, relative)
        if normalized not in paths:
            raise HarnessError(f"Approval dependency snapshot is missing: {normalized}")
        dependencies[normalized] = subject_fingerprint(load_json(
            root / normalize_claim_path(root, paths[normalized])
        ))
    return sha256_bytes(canonical_json({"subject": subject_fingerprint(original),
                                      "dependencies": dependencies}).encode("utf-8"))


def coverage_blockers(root: Path, plan: dict[str, Any], scope: dict[str, Any],
                      *, task_id: str | None = None) -> list[str]:
    """Check current work against an authenticated scope, without granting it."""
    declared = plan_scope(plan)
    if declared is None or scope_fingerprint(declared) != scope_fingerprint(scope):
        return ["plan does not reference the reviewed execution scope"]
    subject = plan["approval_subject"]
    blockers: list[str] = []
    for boundary in scope["write_scope"]:
        if normalize_claim_path(root, boundary) != boundary:
            blockers.append("execution scope contains a noncanonical write boundary")
    for field in ("authorized_actions", "excluded_actions"):
        if set(subject.get(field, [])) != set(scope[field]):
            blockers.append(f"plan {field} differs from the reviewed scope")
    current_constraints = plan_constraints(subject)
    if current_constraints != scope["constraints"]:
        blockers.append("plan constraints differ from the reviewed scope")
    refs = subject.get("work_item_refs", [])
    if task_id is not None and task_id not in refs:
        return [f"task {task_id} is outside the plan"]
    tasks = [load_json(record_path(root, "work_item", item)) for item in ([task_id] if task_id else refs)]
    requirement_ids = set(subject.get("requirement_refs", []))
    feature_ids = set(subject.get("feature_refs", []))
    if task_id:
        feature_ids = {ref for task in tasks for ref in task.get("feature_refs", [])}
        requirement_ids = {ref for fid in feature_ids for ref in load_json(
            record_path(root, "feature", fid)
        ).get("requirement_refs", [])}
    for kind, ids, definitions in (
        ("requirement", requirement_ids, scope["requirements"]),
        ("feature", feature_ids, scope["features"]),
    ):
        for ref in ids:
            if ref not in definitions or governed_definition(load_json(record_path(root, kind, ref))) != definitions[ref]:
                blockers.append(f"{kind} {ref} is outside or changed from the reviewed scope")
    for dependency in scope["dependencies"]:
        relative, expected = dependency["path"], dependency["definition"]
        path = root / normalize_claim_path(root, relative)
        if not path.is_file() or governed_definition(load_json(path)) != expected:
            blockers.append(f"explicit scope dependency changed: {relative}")
    derived = {record_path(root, kind, ref).relative_to(root).as_posix()
               for field, kind in (("requirement_refs", "requirement"), ("feature_refs", "feature"),
                                   ("work_item_refs", "work_item")) for ref in subject.get(field, [])}
    extras = {normalize_claim_path(root, ref) for ref in plan.get("approval_dependencies", [])} - derived
    if extras != {item["path"] for item in scope["dependencies"]}:
        blockers.append("explicit plan dependencies differ from the reviewed scope")
    for task in tasks:
        label = task.get("id", "TASK")
        if not task.get("write_scope"):
            blockers.append(f"{label} has no concrete write scope")
        if task.get("risk") not in RISKS or RISKS[task["risk"]] > RISKS[scope["max_risk"]]:
            blockers.append(f"{label} exceeds the reviewed risk ceiling")
        for path in task.get("write_scope", []):
            if not is_path_within(normalize_claim_path(root, path), scope["write_scope"]):
                blockers.append(f"{label} write scope is outside the decision: {path}")
        if not set(task.get("capabilities", [])) <= set(scope["authorized_actions"]):
            blockers.append(f"{label} capabilities exceed the decision")
        if set(task.get("capabilities", [])) & set(scope["excluded_actions"]):
            blockers.append(f"{label} requests an excluded action")
        required_commands = set(scope["verification"])
        for criterion in task.get("criterion_refs", []):
            commands = scope["criterion_verification"].get(criterion)
            if commands is None:
                blockers.append(f"{label} criterion {criterion} has no reviewed verification obligations")
            else:
                required_commands.update(commands)
        if not required_commands <= set(task.get("verification", [])):
            blockers.append(f"{label} omits reviewed verification obligations")
    return blockers


def prepare_scope(root: Path, *, plan_id: str, write_scope: list[str], max_risk: str,
                  change_refs: list[str] | None = None, claim_id: str | None = None,
                  agent: str = "agent") -> dict[str, Any]:
    """Author a reviewable scope. This command never records a human decision."""
    from .authoring import sync_plan
    from .mutation_service import AtomicMutationService, authorize_claim_targets, validate_records
    path = record_path(root, "plan", plan_id)
    plan = load_json(path)
    subject = plan["approval_subject"]
    tasks = [load_json(record_path(root, "work_item", item)) for item in subject["work_item_refs"]]
    command_sets = [set(task["verification"]) for task in tasks]
    required_verification = sorted(set.intersection(*command_sets)) if command_sets else []
    criterion_verification: dict[str, set[str]] = {}
    for task in tasks:
        for criterion in task.get("criterion_refs", []):
            criterion_verification.setdefault(criterion, set()).update(task["verification"])
    derived = {record_path(root, kind, ref).relative_to(root).as_posix()
               for field, kind in (("requirement_refs", "requirement"), ("feature_refs", "feature"),
                                   ("work_item_refs", "work_item")) for ref in subject.get(field, [])}
    changes = {ref: governed_definition(load_json(record_path(root, "change", ref))) for ref in change_refs or []}
    scope = {
        "schema": SCOPE_SCHEMA, "scope_id": plan_id,
        "requirements": {ref: governed_definition(load_json(record_path(root, "requirement", ref))) for ref in subject["requirement_refs"]},
        "features": {ref: governed_definition(load_json(record_path(root, "feature", ref))) for ref in subject["feature_refs"]},
        "changes": changes,
        "dependencies": [{"path": normalize_claim_path(root, ref),
                          "definition": governed_definition(load_json(root / normalize_claim_path(root, ref)))}
                         for ref in sorted(set(plan["approval_dependencies"]) - derived)],
        "write_scope": sorted({normalize_claim_path(root, item) for item in write_scope}),
        "authorized_actions": sorted(set(subject["authorized_actions"])),
        "excluded_actions": sorted(set(subject["excluded_actions"])),
        "max_risk": max_risk, "verification": required_verification,
        "criterion_verification": {criterion: sorted(commands) for criterion, commands in criterion_verification.items()},
        "constraints": plan_constraints(subject),
    }
    subject["decision_scope"] = scope
    plan_scope(plan)
    blockers = coverage_blockers(root, plan, scope)
    if blockers:
        raise HarnessError("Scope preparation failed: " + "; ".join(blockers))
    plan["updated_at"] = utc_now()
    relative = path.relative_to(root).as_posix()
    writes = {relative: plan}
    for task in tasks:
        task["fingerprint_schema"] = "harness.task-scope/v1"
        writes[record_path(root, "work_item", task["id"]).relative_to(root).as_posix()] = task
    authorize_claim_targets(root, claim_id=claim_id, agent=agent, targets=list(writes))
    validate_records(root, [("plan", plan)])
    AtomicMutationService(root).apply(writes=writes, event_type="PLAN_SCOPE_PREPARED",
                                     event_payload={"plan_id": plan_id, "scope_fingerprint": scope_fingerprint(scope)})
    sync_plan(root, plan_id=plan_id, claim_id=claim_id, agent=agent)
    return {"plan_id": plan_id, "scope": scope, "approval_recorded": False}
