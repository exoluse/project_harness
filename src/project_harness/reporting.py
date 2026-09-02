from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections import Counter, deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from .collaboration import list_claims
from .approvals import (
    authority_config_path,
    authority_status,
    effective_approval_assurance,
    required_approval_assurance,
)
from .constants import HARNESS_DIR
from .core import (
    HarnessError,
    git_head,
    git_status,
    load_json,
    load_record_index,
    parse_utc,
    record_path,
    run_git,
    subject_fingerprint_for_path,
)
from .evaluation import EvaluationContext
from .policy import claim_mode, execution_mode, record_mode, user_directed
from .validation import issue_counts, validate_project


def _run_version(command: str, *args: str) -> str | None:
    executable = shutil.which(command)
    if not executable:
        return None
    process = subprocess.run(
        [executable, *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=10,
    )
    first = process.stdout.strip().splitlines()
    return first[0] if first else executable


def doctor_report(root: Path) -> dict[str, Any]:
    issues = validate_project(root)
    code, _output = run_git(root, "rev-parse", "--is-inside-work-tree")
    authority_state, authority_detail = authority_status(root)
    directed = False
    plan_assurance = "UNKNOWN"
    plan_assurance_detail = "Unable to determine PLAN approval assurance"
    try:
        directed = user_directed(root)
        if directed:
            plan_assurance = "NOT_REQUIRED"
            plan_assurance_detail = "Plans are reference material in USER_DIRECTED mode"
        else:
            plan_assurance = required_approval_assurance(root, "PLAN")
        state = load_json(root / HARNESS_DIR / "state.json")
        active_plan = state.get("active_plan")
        if not directed and isinstance(active_plan, str):
            plan_assurance = effective_approval_assurance(
                root,
                "PLAN",
                subject=load_json(record_path(root, "plan", active_plan)),
            )
        if not directed:
            plan_assurance_detail = (
                "Direct owner confirmation is available; identity is not "
                "cryptographically authenticated"
                if plan_assurance == "PROCEDURAL"
                else authority_detail
            )
    except HarnessError as exc:
        # Doctor must still return the validation diagnosis for malformed state.
        plan_assurance_detail = str(exc)
    return {
        "root": str(root),
        "python": sys.version.split()[0],
        "git": _run_version("git", "--version"),
        "git_repository": code == 0,
        "git_head": git_head(root),
        "dirty_paths": git_status(root),
        "codex": _run_version("codex", "--version"),
        "claude": _run_version("claude", "--version"),
        "human_approval_authority": {
            "state": authority_state,
            "expected_config": str(authority_config_path(root)),
            "detail": authority_detail,
        },
        "plan_approval_assurance": {
            "required": plan_assurance,
            "ready": plan_assurance in {"NOT_REQUIRED", "PROCEDURAL"}
            or (
                plan_assurance == "CRYPTOGRAPHIC"
                and authority_state == "READY"
            ),
            "detail": plan_assurance_detail,
        },
        "validation": issue_counts(issues),
    }


def status_report(root: Path) -> dict[str, Any]:
    from .gates import _open_item_resolution_complete

    project = load_json(root / HARNESS_DIR / "project.json")
    state = load_json(root / HARNESS_DIR / "state.json")
    records, _paths = load_record_index(root)
    counts = Counter(record.get("kind", "unknown") for record in records.values())
    open_items = [
        record
        for record in records.values()
        if record.get("kind") == "open_item"
        and not _open_item_resolution_complete(record)
    ]
    active_claims = list_claims(root, active_only=True)
    for claim in active_claims:
        try:
            claim["lease_state"] = (
                "EXPIRED"
                if parse_utc(str(claim.get("expires_at", ""))) <= datetime.now(UTC)
                else "CURRENT"
            )
        except (TypeError, ValueError):
            claim["lease_state"] = "INVALID"
    return {
        "project_id": project.get("id"),
        "name": project.get("name"),
        "lifecycle_state": state.get("lifecycle_state"),
        "execution_mode": execution_mode(root),
        "claim_mode": claim_mode(root),
        "record_mode": record_mode(root),
        "active_plan": state.get("active_plan"),
        "active_decision": state.get("active_decision"),
        "active_baselines": state.get("active_baselines", {}),
        "active_release": state.get("active_release"),
        "record_counts": dict(sorted(counts.items())),
        "open_items": {
            "total": len(open_items),
            "G0": sum(item.get("gate_level") == "G0" for item in open_items),
            "G1": sum(item.get("gate_level") == "G1" for item in open_items),
            "G2": sum(item.get("gate_level") == "G2" for item in open_items),
            "G3": sum(item.get("gate_level") == "G3" for item in open_items),
        },
        "active_claims": active_claims,
        "git_head": git_head(root),
        "dirty_paths": git_status(root),
    }


REFERENCE_FIELDS = {
    "required_features",
    "source_refs",
    "requirement_refs",
    "feature_refs",
    "criterion_refs",
    "work_item_refs",
    "dependencies",
    "blocked_by",
    "blocks",
    "affects",
    "supports",
    "evidence_refs",
    "acceptance_criteria",
    "condition_refs",
    "propagated_to",
    "decision_ref",
    "plan_id",
    "task_id",
    "result_id",
    "feature_id",
    "project_id",
    "subject_id",
    "source_ref",
}

REFERENCE_MAPPING_FIELDS = {
    "capability_approval_refs",
}


def _direct_refs(value: Any) -> Iterable[str]:
    if isinstance(value, str) and value:
        yield value
    elif isinstance(value, list):
        yield from (item for item in value if isinstance(item, str) and item)


def _collect_reference_edges(value: Any) -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in REFERENCE_FIELDS:
                yield from ((target, key) for target in _direct_refs(child))
            elif key in REFERENCE_MAPPING_FIELDS and isinstance(child, dict):
                for mapping_key, references in child.items():
                    yield from (
                        (target, f"{key}.{mapping_key}")
                        for target in _direct_refs(references)
                    )
            yield from _collect_reference_edges(child)
    elif isinstance(value, list):
        for child in value:
            yield from _collect_reference_edges(child)


def _collect_refs(value: Any, field: str | None = None) -> Iterable[str]:
    del field  # Retained for compatibility with the previous private helper signature.
    yield from (target for target, _edge_field in _collect_reference_edges(value))


def _trace_record_index(root: Path) -> dict[str, dict[str, Any]]:
    records, _paths = load_record_index(root)
    project_path = root / HARNESS_DIR / "project.json"
    project = load_json(project_path)
    project_id = project.get("id")
    if not isinstance(project_id, str) or not project_id:
        raise HarnessError("Project record has no traceable ID")
    if project_id in records:
        raise HarnessError(f"Duplicate project or canonical record ID {project_id}")
    records[project_id] = project
    return records


def trace_report(root: Path, start_id: str) -> dict[str, Any]:
    records = _trace_record_index(root)
    if start_id not in records:
        raise HarnessError(f"Unknown record ID: {start_id}")
    outgoing_edges: dict[str, list[dict[str, str]]] = {}
    incoming_edges: dict[str, list[dict[str, str]]] = {
        record_id: [] for record_id in records
    }
    for source, record in records.items():
        edges = sorted(
            {
                (target, field)
                for target, field in _collect_reference_edges(record)
                if target in records
            },
            key=lambda item: (item[0], item[1]),
        )
        outgoing_edges[source] = [
            {"field": field, "target": target} for target, field in edges
        ]
        for target, field in edges:
            incoming_edges[target].append({"field": field, "source": source})
    for edges in incoming_edges.values():
        edges.sort(key=lambda item: (item["source"], item["field"]))

    visited: set[str] = set()
    queue = deque([start_id])
    nodes: list[dict[str, Any]] = []
    while queue:
        current = queue.popleft()
        if current in visited or current not in records:
            continue
        visited.add(current)
        record = records[current]
        outgoing = sorted({edge["target"] for edge in outgoing_edges[current]})
        incoming = sorted({edge["source"] for edge in incoming_edges[current]})
        nodes.append(
            {
                "id": current,
                "kind": record.get("kind"),
                "title": record.get("title") or record.get("claim") or "",
                "outgoing": outgoing,
                "incoming": incoming,
                "outgoing_edges": outgoing_edges[current],
                "incoming_edges": incoming_edges[current],
            }
        )
        queue.extend(outgoing)
        queue.extend(incoming)
    return {"start": start_id, "nodes": nodes}


def decision_package(root: Path, plan_id: str) -> dict[str, Any]:
    from .gates import _open_item_resolution_complete, plan_preflight_gate

    context = EvaluationContext.load(root)
    records = context.records
    plan = load_json(record_path(root, "plan", plan_id))
    subject = plan.get("approval_subject", {})
    preflight = plan_preflight_gate(
        root, plan_id, require_approval=False, context=context
    )
    requirements = []
    for requirement_id in subject.get("requirement_refs", []):
        requirement = records.get(requirement_id, {})
        realizing = [
            feature_id
            for feature_id in subject.get("feature_refs", [])
            if requirement_id in records.get(feature_id, {}).get("requirement_refs", [])
        ]
        requirements.append(
            {
                "id": requirement_id,
                "title": requirement.get("title"),
                "statement": requirement.get("statement"),
                "features": realizing,
                "acceptance_criteria": requirement.get("acceptance_criteria", []),
            }
        )
    features = []
    for feature_id in subject.get("feature_refs", []):
        feature = records.get(feature_id, {})
        tasks = [
            task_id
            for task_id in subject.get("work_item_refs", [])
            if feature_id in records.get(task_id, {}).get("feature_refs", [])
        ]
        features.append(
            {
                "id": feature_id,
                "title": feature.get("title"),
                "criteria": [
                    {
                        "id": criterion.get("id"),
                        "statement": criterion.get("statement"),
                        "profiles": criterion.get("required_profiles", []),
                    }
                    for criterion in feature.get("completion_criteria", [])
                ],
                "tasks": tasks,
            }
        )
    unresolved = [
        {
            "id": record.get("id"),
            "gate_level": record.get("gate_level"),
            "status": record.get("status"),
            "title": record.get("title"),
            "affects": record.get("affects", []),
            "blocks": record.get("blocks", []),
        }
        for record in records.values()
        if record.get("kind") == "open_item"
        and not _open_item_resolution_complete(record)
    ]
    authority_state, authority_detail = authority_status(root)
    plan_assurance = effective_approval_assurance(
        root, "PLAN", subject=plan
    )
    return {
        "plan_id": plan_id,
        "plan_version": plan.get("version"),
        "plan_fingerprint": subject_fingerprint_for_path(
            record_path(root, "plan", plan_id)
        ),
        "preflight": preflight.as_dict(),
        "requirements": requirements,
        "features": features,
        "workstreams": subject.get("workstreams", []),
        "verification_strategy": subject.get("verification_strategy", {}),
        "authorized_actions": subject.get("authorized_actions", []),
        "excluded_actions": subject.get("excluded_actions", []),
        "unresolved_items": sorted(
            unresolved, key=lambda item: (str(item.get("gate_level")), str(item.get("id")))
        ),
        "human_authority": {
            "state": authority_state,
            "detail": authority_detail,
        },
        "approval_assurance": {
            "required": plan_assurance,
            "procedural_confirmation_available": plan_assurance == "PROCEDURAL",
            "cryptographic_authority_required": plan_assurance
            == "CRYPTOGRAPHIC",
        },
        "decision_options": [
            "APPROVED",
            "APPROVED_WITH_CONDITIONS",
            "REVISION_REQUIRED",
            "DEFERRED",
            "REJECTED",
        ],
    }


def completion_report(root: Path) -> dict[str, Any]:
    from .gates import feature_completion_gate, project_completion_gate

    project = load_json(root / HARNESS_DIR / "project.json")
    context = EvaluationContext.load(root)
    features = {
        feature_id: feature_completion_gate(
            root, feature_id, context=context
        ).as_dict()
        for feature_id in project.get("required_features", [])
    }
    return {
        "project_id": project.get("id"),
        "features": features,
        "technical_closure_preflight": project_completion_gate(
            root, require_approval=False, context=context
        ).as_dict(),
        "authorized_closure": project_completion_gate(
            root, require_approval=True, context=context
        ).as_dict(),
    }


def pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
