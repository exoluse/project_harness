from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from .approvals import approval_status
from .collaboration import RECOVERY_CHECK_NAMES, list_claims
from .constants import (
    APPROVAL_ASSURANCE_LEVELS,
    EVIDENCE_RESULTS,
    HARNESS_DIR,
    OPEN_ITEM_CLOSED_STATES,
    OPEN_ITEM_STATES,
    PROJECT_LIFECYCLE_STATES,
    PROCEDURAL_APPROVAL_TYPES,
    RECORD_DIRECTORIES,
)
from .core import (
    HarnessError,
    binding_status,
    git_changed_paths,
    iter_record_files,
    load_json,
    normalize_claim_path,
    parse_utc,
    paths_overlap,
    record_path,
    subject_fingerprint,
    subject_fingerprint_for_path,
    sha256_bytes,
    sha256_file,
)
from .schema_validation import SCHEMA_FILES, SchemaSet


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    path: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


def _issue(severity: str, code: str, message: str, path: Path | None = None) -> Issue:
    return Issue(severity, code, message, str(path) if path else None)


def _refs(value: Any) -> Iterable[str]:
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                yield item


def _record_number(value: dict[str, Any]) -> int:
    record_id = str(value.get("id", ""))
    try:
        return int(record_id.rsplit("-", 1)[1])
    except (IndexError, ValueError):
        return -1


def _check_secret_fields(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            lowered = key.casefold()
            if lowered in {"password", "secret", "token", "private_key", "connection_string"}:
                if isinstance(child, str) and child and not (
                    child.startswith("${") or child in {"REDACTED", "SECRET_REFERENCE"}
                ):
                    found.append(child_path)
            found.extend(_check_secret_fields(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_check_secret_fields(child, f"{path}[{index}]"))
    return found


SHAPE_FIELDS: dict[str, dict[str, type]] = {
    "source": {},
    "artifact": {},
    "requirement": {"source_refs": list, "acceptance_criteria": list},
    "feature": {"requirement_refs": list, "completion_criteria": list},
    "plan": {"approval_dependencies": list, "approval_subject": dict},
    "work_item": {
        "feature_refs": list,
        "criterion_refs": list,
        "dependencies": list,
        "blocked_by": list,
        "write_scope": list,
        "preexisting_dirty_paths": list,
        "logical_locks": list,
        "verification": list,
        "capabilities": list,
        "forbidden_actions": list,
    },
    "open_item": {"affects": list, "blocks": list},
    "evidence": {
        "observed_at": str,
        "supports": list,
        "subject": dict,
        "ambiguity": dict,
        "bindings": list,
        "limitations": list,
    },
    "approval": {
        "project_id": str,
        "authority_id": str,
        "authority_sequence": int,
        "decision_id": str,
        "decision_at": str,
        "attestation": dict,
        "snapshot_manifest": list,
        "conditions": list,
        "condition_refs": list,
        "authorized_actions": list,
        "excluded_actions": list,
    },
    "change": {"source_refs": list, "affects": list, "impact": dict},
    "result": {
        "changed_files": list,
        "changed_file_states": dict,
        "verification": list,
        "verification_state": str,
        "build_fingerprint": str,
        "evidence_refs": list,
        "evidence_fingerprints": dict,
        "limitations": list,
    },
    "review": {"checks": list, "result_build_fingerprint": str},
    "handoff": {
        "owned_paths": list,
        "changed_files": list,
        "changed_file_states": dict,
        "verification": list,
        "verification_state": str,
        "unverified": list,
        "decisions": list,
        "risks": list,
    },
}

OBJECT_LIST_FIELDS = {
    ("feature", "completion_criteria"),
    ("evidence", "bindings"),
    ("approval", "snapshot_manifest"),
    ("result", "verification"),
    ("handoff", "verification"),
}


def _shape_errors(record: dict[str, Any], kind: str) -> list[str]:
    errors: list[str] = []
    for field, expected_type in SHAPE_FIELDS.get(kind, {}).items():
        if field not in record:
            errors.append(f"missing required field {field}")
        elif not isinstance(record[field], expected_type):
            errors.append(f"{field} must be {expected_type.__name__}")
        elif expected_type is list:
            item_type = dict if (kind, field) in OBJECT_LIST_FIELDS else str
            if any(not isinstance(item, item_type) for item in record[field]):
                errors.append(f"{field} items must be {item_type.__name__}")
    if kind == "feature" and isinstance(record.get("completion_criteria"), list):
        for index, criterion in enumerate(record["completion_criteria"]):
            if not isinstance(criterion, dict):
                errors.append(f"completion_criteria[{index}] must be object")
                continue
            for field in (
                "verification_plan",
                "required_profiles",
                "required_bindings",
                "evidence_refs",
            ):
                if field not in criterion or not isinstance(criterion[field], list):
                    errors.append(f"completion_criteria[{index}].{field} must be list")
                elif any(not isinstance(item, str) for item in criterion[field]):
                    errors.append(
                        f"completion_criteria[{index}].{field} items must be string"
                    )
    if kind == "plan" and isinstance(record.get("approval_subject"), dict):
        subject = record["approval_subject"]
        for field in (
            "requirement_refs",
            "feature_refs",
            "work_item_refs",
            "workstreams",
            "authorized_actions",
            "excluded_actions",
            "invalidation_triggers",
        ):
            if field not in subject or not isinstance(subject[field], list):
                errors.append(f"approval_subject.{field} must be list")
            elif field == "workstreams":
                if any(not isinstance(item, dict) for item in subject[field]):
                    errors.append("approval_subject.workstreams items must be object")
            elif any(not isinstance(item, str) for item in subject[field]):
                errors.append(f"approval_subject.{field} items must be string")
        if not isinstance(subject.get("verification_strategy"), dict):
            errors.append("approval_subject.verification_strategy must be object")
    if kind == "evidence" and isinstance(record.get("ambiguity"), dict):
        if not isinstance(record["ambiguity"].get("reasons"), list):
            errors.append("ambiguity.reasons must be list")
    if kind in {"result", "handoff"} and isinstance(record.get("verification"), list):
        for index, check in enumerate(record["verification"]):
            if not isinstance(check, dict):
                continue
            if not isinstance(check.get("command"), str) or not check.get("command", "").strip():
                errors.append(f"verification[{index}].command must be nonempty string")
            if check.get("outcome") not in {
                "PASS",
                "FAIL",
                "BLOCKED",
                "NOT_RUN",
                "PARTIAL",
                "INCONCLUSIVE",
            }:
                errors.append(f"verification[{index}].outcome is invalid")
    return errors


def validate_project(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    harness = root / HARNESS_DIR
    required_files = [
        root / "AGENTS.md",
        root / "CLAUDE.md",
        root / "HANDOFF.md",
        harness / "project.json",
        harness / "state.json",
        *(root / "schemas" / name for name in sorted(set(SCHEMA_FILES.values()))),
    ]
    for path in required_files:
        if not path.is_file():
            issues.append(_issue("ERROR", "MISSING_STRUCTURE", f"required file is missing: {path.name}", path))
    for directory, _prefix in RECORD_DIRECTORIES.values():
        path = harness / directory
        if not path.is_dir():
            issues.append(_issue("ERROR", "MISSING_STRUCTURE", f"record directory is missing: {directory}", path))
    if issues:
        return issues

    try:
        project = load_json(harness / "project.json")
        state = load_json(harness / "state.json")
    except HarnessError as exc:
        return [_issue("ERROR", "INVALID_JSON", str(exc))]
    schema_set = SchemaSet(root / "schemas")
    for value, schema_kind, path in (
        (project, "project", harness / "project.json"),
        (state, "state", harness / "state.json"),
    ):
        issues.extend(
            _issue("ERROR", "SCHEMA_VIOLATION", message, path)
            for message in schema_set.validate(value, SCHEMA_FILES[schema_kind])
        )
    if state.get("project_id") != project.get("id"):
        issues.append(_issue("ERROR", "STATE_PROJECT_MISMATCH", "state project_id does not match project id"))
    event_ids: set[str] = set()
    for event_path in sorted((harness / "events").glob("EVT-*.json")):
        try:
            event = load_json(event_path)
        except HarnessError as exc:
            issues.append(_issue("ERROR", "INVALID_EVENT", str(exc), event_path))
            continue
        for message in schema_set.validate(event, SCHEMA_FILES["event"]):
            issues.append(_issue("ERROR", "INVALID_EVENT", message, event_path))
        event_id = event.get("id")
        if event_path.stem != event_id:
            issues.append(
                _issue(
                    "ERROR",
                    "INVALID_EVENT",
                    f"filename {event_path.stem} does not match id {event_id}",
                    event_path,
                )
            )
        if isinstance(event_id, str):
            if event_id in event_ids:
                issues.append(
                    _issue("ERROR", "DUPLICATE_ID", f"duplicate event id {event_id}", event_path)
                )
            event_ids.add(event_id)
    if state.get("lifecycle_state") not in PROJECT_LIFECYCLE_STATES:
        issues.append(_issue("ERROR", "INVALID_LIFECYCLE", f"invalid lifecycle state {state.get('lifecycle_state')}"))
    if not isinstance(project.get("required_features"), list) or any(
        not isinstance(item, str) for item in project.get("required_features", [])
    ):
        issues.append(
            _issue("ERROR", "MALFORMED_PROJECT", "project required_features must be a string list")
        )
    if not isinstance(project.get("policy"), dict):
        issues.append(_issue("ERROR", "MALFORMED_PROJECT", "project policy must be an object"))
    else:
        assurance = project["policy"].get("approval_assurance")
        if assurance is not None:
            if not isinstance(assurance, dict):
                issues.append(
                    _issue(
                        "ERROR",
                        "INVALID_APPROVAL_ASSURANCE_POLICY",
                        "approval_assurance must be an object",
                    )
                )
            else:
                default = assurance.get("default")
                by_type = assurance.get("by_type")
                if default not in APPROVAL_ASSURANCE_LEVELS or not isinstance(
                    by_type, dict
                ):
                    issues.append(
                        _issue(
                            "ERROR",
                            "INVALID_APPROVAL_ASSURANCE_POLICY",
                            "approval_assurance requires a valid default and by_type map",
                        )
                    )
                elif any(
                    value not in APPROVAL_ASSURANCE_LEVELS
                    for value in by_type.values()
                ):
                    issues.append(
                        _issue(
                            "ERROR",
                            "INVALID_APPROVAL_ASSURANCE_POLICY",
                            "approval_assurance by_type contains an invalid level",
                        )
                    )
                else:
                    forbidden = sorted(
                        approval_type
                        for approval_type, value in by_type.items()
                        if value == "PROCEDURAL"
                        and approval_type not in PROCEDURAL_APPROVAL_TYPES
                    )
                    if default == "PROCEDURAL" or forbidden:
                        issues.append(
                            _issue(
                                "ERROR",
                                "UNSAFE_PROCEDURAL_APPROVAL_POLICY",
                                "PROCEDURAL assurance is permitted only by explicit PLAN override",
                            )
                        )
    project_dependencies = project.get("approval_dependencies")
    if not isinstance(project_dependencies, list) or any(
        not isinstance(item, str) for item in (project_dependencies or [])
    ):
        issues.append(
            _issue(
                "ERROR",
                "MALFORMED_PROJECT",
                "project approval_dependencies must be a string list",
            )
        )
    closure_criteria: dict[str, dict[str, Any]] = {}
    closure_contract = project.get("closure_contract")
    if not isinstance(closure_contract, list):
        issues.append(
            _issue("ERROR", "MALFORMED_PROJECT", "project closure_contract must be a list")
        )
    else:
        for index, criterion in enumerate(closure_contract):
            if not isinstance(criterion, dict) or not isinstance(criterion.get("id"), str):
                issues.append(
                    _issue(
                        "ERROR",
                        "MALFORMED_PROJECT",
                        f"closure_contract[{index}] requires a string id",
                    )
                )
                continue
            criterion_id = criterion["id"]
            for field in ("required_profiles", "evidence_refs"):
                if not isinstance(criterion.get(field), list) or any(
                    not isinstance(item, str) for item in criterion.get(field, [])
                ):
                    issues.append(
                        _issue(
                            "ERROR",
                            "MALFORMED_PROJECT",
                            f"closure criterion {criterion_id} {field} must be a string list",
                        )
                    )
            if criterion_id in closure_criteria:
                issues.append(
                    _issue(
                        "ERROR",
                        "DUPLICATE_ID",
                        f"duplicate closure criterion id {criterion_id}",
                    )
                )
            closure_criteria[criterion_id] = criterion
    if not isinstance(state.get("active_baselines"), dict):
        issues.append(
            _issue("ERROR", "MALFORMED_STATE", "state active_baselines must be an object")
        )

    records: dict[str, dict[str, Any]] = {}
    record_paths: dict[str, Path] = {}
    criteria: dict[str, dict[str, Any]] = {}
    criterion_owners: dict[str, str] = {}
    malformed_records: set[str] = set()
    for expected_kind, path in iter_record_files(root):
        try:
            record = load_json(path)
        except HarnessError as exc:
            issues.append(_issue("ERROR", "INVALID_JSON", str(exc), path))
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            issues.append(_issue("ERROR", "MISSING_ID", "record id is required", path))
            continue
        if path.stem != record_id:
            issues.append(_issue("ERROR", "ID_FILENAME_MISMATCH", f"filename {path.stem} does not match id {record_id}", path))
        if record_id in records:
            issues.append(_issue("ERROR", "DUPLICATE_ID", f"duplicate record id {record_id}", path))
        records[record_id] = record
        record_paths[record_id] = path
        schema_errors = schema_set.validate(record, SCHEMA_FILES[expected_kind])
        if schema_errors:
            malformed_records.add(record_id)
            issues.extend(
                _issue("ERROR", "SCHEMA_VIOLATION", message, path)
                for message in schema_errors
            )
        if record.get("kind") != expected_kind:
            issues.append(_issue("ERROR", "KIND_DIRECTORY_MISMATCH", f"expected kind {expected_kind}, found {record.get('kind')}", path))
        _directory, prefix = RECORD_DIRECTORIES[expected_kind]
        if not record_id.startswith(prefix):
            issues.append(_issue("ERROR", "ID_PREFIX", f"{record_id} must start with {prefix}", path))
        for secret_path in _check_secret_fields(record):
            issues.append(_issue("ERROR", "SECRET_VALUE", f"possible secret value at {secret_path}", path))
        shape_errors = _shape_errors(record, expected_kind)
        if shape_errors:
            malformed_records.add(record_id)
            issues.extend(
                _issue("ERROR", "MALFORMED_RECORD", message, path)
                for message in shape_errors
            )
        if expected_kind == "feature" and not shape_errors:
            for criterion in record.get("completion_criteria", []):
                if not isinstance(criterion, dict) or not isinstance(criterion.get("id"), str):
                    issues.append(_issue("ERROR", "INVALID_CRITERION", "feature criterion requires an id", path))
                    continue
                criterion_id = criterion["id"]
                if criterion_id in criteria or criterion_id in records:
                    issues.append(_issue("ERROR", "DUPLICATE_ID", f"duplicate criterion id {criterion_id}", path))
                criteria[criterion_id] = criterion
                criterion_owners[criterion_id] = record_id

    for criterion_id in closure_criteria:
        if criterion_id in records or criterion_id in criteria:
            issues.append(
                _issue("ERROR", "DUPLICATE_ID", f"duplicate closure criterion id {criterion_id}")
            )
    known_ids = set(records) | set(criteria) | set(closure_criteria)
    latest_result_ids: set[str] = set()
    latest_results: dict[str, dict[str, Any]] = {}
    result_groups: dict[str, list[dict[str, Any]]] = {}
    for candidate in records.values():
        if candidate.get("kind") == "result" and isinstance(
            candidate.get("task_id"), str
        ):
            result_groups.setdefault(candidate["task_id"], []).append(candidate)
    for task_id, group in result_groups.items():
        latest = max(group, key=_record_number)
        if isinstance(latest.get("id"), str):
            latest_result_ids.add(latest["id"])
            latest_results[task_id] = latest

    latest_reviews: dict[str, dict[str, Any]] = {}
    review_groups: dict[str, list[dict[str, Any]]] = {}
    for candidate in records.values():
        if candidate.get("kind") == "review" and isinstance(
            candidate.get("result_id"), str
        ):
            review_groups.setdefault(candidate["result_id"], []).append(candidate)
    for result_id, group in review_groups.items():
        latest_reviews[result_id] = max(group, key=_record_number)

    for record_id, record in records.items():
        path = record_paths[record_id]
        kind = record.get("kind")
        if record_id in malformed_records:
            continue
        if kind == "source":
            if record.get("authority") not in {
                "RAW_INPUT", "REFERENCE", "REVIEW_CANDIDATE", "APPROVED_BASELINE", "CONTRACT_AUTHORITY"
            }:
                issues.append(_issue("ERROR", "SOURCE_AUTHORITY", "source authority is invalid or missing", path))
            if record.get("interpretation_status") not in {
                "EXPLICIT", "INFERRED", "UNKNOWN", "CONFLICTING", "CONFIRMED"
            }:
                issues.append(_issue("ERROR", "INTERPRETATION_STATUS", "source interpretation status is invalid", path))
        elif kind == "artifact":
            artifact_path = record.get("path")
            if artifact_path:
                try:
                    normalized_artifact = normalize_claim_path(root, artifact_path)
                except HarnessError as exc:
                    issues.append(_issue("ERROR", "UNSAFE_PATH", str(exc), path))
                else:
                    actual_path = root / normalized_artifact
                    if not actual_path.is_file():
                        issues.append(
                            _issue(
                                "ERROR",
                                "MISSING_ARTIFACT_FILE",
                                f"artifact file is missing: {artifact_path}",
                                path,
                            )
                        )
                    elif record.get("sha256") != sha256_file(actual_path):
                        issues.append(
                            _issue(
                                "ERROR",
                                "STALE_ARTIFACT_HASH",
                                f"artifact hash is missing or stale: {artifact_path}",
                                path,
                            )
                        )
            else:
                issues.append(_issue("ERROR", "MISSING_ARTIFACT_PATH", "artifact path is required", path))
            source_ref = record.get("source_ref")
            if source_ref not in records or records.get(source_ref, {}).get("kind") != "source":
                issues.append(
                    _issue("ERROR", "DANGLING_REFERENCE", f"artifact source is missing: {source_ref}", path)
                )
            if record.get("safe_to_execute") and record.get("execution_trust") == "UNTRUSTED":
                issues.append(_issue("ERROR", "UNTRUSTED_EXECUTION", "untrusted artifact cannot be marked safe to execute", path))
        elif kind == "requirement":
            for reference in _refs(record.get("source_refs")):
                if reference not in known_ids:
                    issues.append(_issue("ERROR", "DANGLING_REFERENCE", f"missing source {reference}", path))
            if record.get("required", True) and record.get("status") in {"APPROVED", "PLANNED", "IMPLEMENTED", "VERIFIED", "ACCEPTED"}:
                if not record.get("acceptance_criteria"):
                    issues.append(_issue("ERROR", "MISSING_ACCEPTANCE_CRITERIA", f"required requirement {record_id} has no acceptance criteria", path))
            for criterion_id in _refs(record.get("acceptance_criteria")):
                if criterion_id not in criteria:
                    issues.append(
                        _issue(
                            "ERROR",
                            "DANGLING_REFERENCE",
                            f"requirement acceptance criterion is missing: {criterion_id}",
                            path,
                        )
                    )
                else:
                    owner_id = criterion_owners.get(criterion_id)
                    owner = records.get(owner_id, {})
                    if record_id not in owner.get("requirement_refs", []):
                        issues.append(
                            _issue(
                                "ERROR",
                                "CROSSED_ACCEPTANCE_TRACE",
                                f"criterion {criterion_id} belongs to {owner_id}, which does not trace to {record_id}",
                                path,
                            )
                        )
        elif kind == "feature":
            for reference in _refs(record.get("requirement_refs")):
                if reference not in records:
                    issues.append(_issue("ERROR", "DANGLING_REFERENCE", f"missing requirement {reference}", path))
            if record.get("required", True) and not record.get("completion_criteria"):
                issues.append(_issue("ERROR", "MISSING_COMPLETION_CONTRACT", f"required feature {record_id} has no completion criteria", path))
            for criterion in record.get("completion_criteria", []):
                if criterion.get("required", True) and not criterion.get("verification_plan"):
                    issues.append(_issue("ERROR", "MISSING_VERIFICATION_PLAN", f"criterion {criterion.get('id')} has no verification plan", path))
                if criterion.get("required", True) and not criterion.get("required_bindings"):
                    issues.append(
                        _issue(
                            "ERROR",
                            "MISSING_SUBJECT_BINDING_PLAN",
                            f"criterion {criterion.get('id')} has no required subject bindings",
                            path,
                        )
                    )
                evidence_refs = set(_refs(criterion.get("evidence_refs")))
                for evidence_id in evidence_refs:
                    evidence = records.get(evidence_id)
                    if not evidence or evidence.get("kind") != "evidence":
                        issues.append(
                            _issue(
                                "ERROR",
                                "DANGLING_REFERENCE",
                                f"criterion {criterion.get('id')} references missing evidence {evidence_id}",
                                path,
                            )
                        )

                if (
                    record.get("status") not in {"VERIFIED", "ACCEPTED"}
                    or not criterion.get("required", True)
                ):
                    continue
                required_profiles = criterion.get("required_profiles", []) or [None]
                for required_profile in required_profiles:
                    candidates = [
                        candidate
                        for candidate in records.values()
                        if candidate.get("kind") == "evidence"
                        and isinstance(candidate.get("supports"), list)
                        and criterion.get("id") in candidate["supports"]
                        and (
                            required_profile is None
                            or candidate.get("profile") == required_profile
                        )
                    ]
                    reasons: list[str] = []
                    if not candidates:
                        reasons.append("no evidence record supports this criterion/profile")
                    else:
                        latest = max(candidates, key=_record_number)
                        latest_id = latest.get("id")
                        if latest_id not in evidence_refs:
                            reasons.append(
                                f"latest evidence {latest_id} is omitted from the completion contract"
                            )
                        from .gates import _evidence_is_eligible

                        eligible, eligibility_reasons = _evidence_is_eligible(
                            root,
                            latest,
                            criterion=criterion,
                            feature_id=record_id,
                            required_profile=required_profile,
                        )
                        if not eligible:
                            reasons.extend(eligibility_reasons)
                    if reasons:
                        issues.append(
                            _issue(
                                "ERROR",
                                "FEATURE_STATUS_EVIDENCE_MISMATCH",
                                f"feature {record_id} status {record.get('status')} is unsupported for "
                                f"criterion {criterion.get('id')} profile {required_profile or 'ANY'}: "
                                + "; ".join(reasons),
                                path,
                            )
                        )
        elif kind == "plan":
            subject = record.get("approval_subject")
            if not isinstance(subject, dict):
                issues.append(_issue("ERROR", "MISSING_APPROVAL_SUBJECT", "plan requires approval_subject", path))
            else:
                for field in ("requirement_refs", "feature_refs", "work_item_refs"):
                    for reference in _refs(subject.get(field)):
                        if reference not in known_ids:
                            issues.append(_issue("ERROR", "DANGLING_REFERENCE", f"plan {field} references missing {reference}", path))
                planned_requirements = set(_refs(subject.get("requirement_refs")))
                planned_features = set(_refs(subject.get("feature_refs")))
                planned_tasks = set(_refs(subject.get("work_item_refs")))
                for requirement_id in planned_requirements:
                    if not any(
                        requirement_id in records.get(feature_id, {}).get("requirement_refs", [])
                        for feature_id in planned_features
                    ):
                        issues.append(
                            _issue(
                                "ERROR",
                                "UNREALIZED_REQUIREMENT",
                                f"plan requirement {requirement_id} has no feature",
                                path,
                            )
                        )
                for feature_id in planned_features:
                    if not any(
                        feature_id in records.get(task_id, {}).get("feature_refs", [])
                        for task_id in planned_tasks
                    ):
                        issues.append(
                            _issue(
                                "ERROR",
                                "UNIMPLEMENTED_FEATURE_PLAN",
                                f"plan feature {feature_id} has no task",
                                path,
                            )
                        )
                    feature = records.get(feature_id, {})
                    for criterion in feature.get("completion_criteria", []):
                        if not criterion.get("required", True):
                            continue
                        criterion_id = criterion.get("id")
                        if not any(
                            criterion_id
                            in records.get(task_id, {}).get("criterion_refs", [])
                            for task_id in planned_tasks
                        ):
                            issues.append(
                                _issue(
                                    "ERROR",
                                    "UNPLANNED_COMPLETION_CRITERION",
                                    f"required criterion {criterion_id} has no planned task",
                                    path,
                                )
                            )
                expected_dependencies: set[str] = set()
                kind_for_field = {
                    "requirement_refs": "requirement",
                    "feature_refs": "feature",
                    "work_item_refs": "work_item",
                }
                for field, dependency_kind in kind_for_field.items():
                    for reference in _refs(subject.get(field)):
                        dependency = record_paths.get(reference)
                        if dependency:
                            expected_dependencies.add(dependency.relative_to(root).as_posix())
                actual_dependencies = set(record.get("approval_dependencies", []))
                missing_dependencies = expected_dependencies - actual_dependencies
                if missing_dependencies:
                    issues.append(
                        _issue(
                            "ERROR",
                            "UNBOUND_PLAN_DEPENDENCY",
                            "plan approval is not fingerprint-bound to: "
                            + ", ".join(sorted(missing_dependencies)),
                            path,
                        )
                    )
                for dependency_value in actual_dependencies:
                    try:
                        normalized = normalize_claim_path(root, dependency_value)
                    except HarnessError as exc:
                        issues.append(_issue("ERROR", "UNSAFE_PATH", str(exc), path))
                        continue
                    if not (root / normalized).is_file():
                        issues.append(_issue("ERROR", "MISSING_APPROVAL_DEPENDENCY", f"missing approval dependency {dependency_value}", path))
        elif kind == "work_item":
            plan_id = record.get("plan_id")
            if plan_id and plan_id not in records:
                issues.append(_issue("ERROR", "DANGLING_REFERENCE", f"missing plan {plan_id}", path))
            for reference in [*_refs(record.get("feature_refs")), *_refs(record.get("dependencies")), *_refs(record.get("blocked_by"))]:
                if reference not in known_ids:
                    issues.append(_issue("ERROR", "DANGLING_REFERENCE", f"task references missing {reference}", path))
            task_features = set(_refs(record.get("feature_refs")))
            for criterion_id in _refs(record.get("criterion_refs")):
                if criterion_id not in criteria:
                    issues.append(
                        _issue(
                            "ERROR",
                            "DANGLING_REFERENCE",
                            f"task references missing criterion {criterion_id}",
                            path,
                        )
                    )
                elif criterion_owners.get(criterion_id) not in task_features:
                    issues.append(
                        _issue(
                            "ERROR",
                            "CROSSED_TASK_CRITERION",
                            f"task criterion {criterion_id} is outside its feature scope",
                            path,
                        )
                    )
            for value in record.get("write_scope", []):
                try:
                    normalize_claim_path(root, value)
                except HarnessError as exc:
                    issues.append(_issue("ERROR", "UNSAFE_PATH", str(exc), path))
            if not record.get("feature_refs"):
                issues.append(_issue("WARNING", "ORPHAN_TASK", f"task {record_id} has no feature basis", path))
            status = record.get("status")
            result_required_statuses = {
                "SUBMITTED",
                "REVIEWED",
                "INTEGRATED",
                "DONE",
                "CLOSED",
            }
            reviewed_statuses = {"REVIEWED", "INTEGRATED", "DONE", "CLOSED"}
            integrated_statuses = {"INTEGRATED", "DONE", "CLOSED"}
            if status in result_required_statuses:
                latest_result = latest_results.get(record_id)
                if latest_result is None:
                    issues.append(
                        _issue(
                            "ERROR",
                            "TASK_STATUS_INCONSISTENT",
                            f"task {record_id} status {status} requires a submitted result",
                            path,
                        )
                    )
                else:
                    result_id = str(latest_result.get("id"))
                    latest_review = latest_reviews.get(result_id)
                    reasons: list[str] = []
                    if status in reviewed_statuses:
                        if latest_review is None:
                            reasons.append(f"latest result {result_id} has no review")
                        else:
                            if latest_review.get("result_fingerprint") != subject_fingerprint(
                                latest_result
                            ):
                                reasons.append("latest review result fingerprint is stale")
                            if latest_review.get("result_build_fingerprint") != latest_result.get(
                                "build_fingerprint"
                            ):
                                reasons.append("latest review build fingerprint is stale")
                            if str(latest_review.get("reviewer", "")).casefold() == str(
                                latest_result.get("agent", "")
                            ).casefold():
                                reasons.append("latest result was self-reviewed")
                            if (
                                status in integrated_statuses
                                and latest_review.get("decision") != "PASS"
                            ):
                                reasons.append(
                                    f"latest review decision is {latest_review.get('decision')}"
                                )
                    if status in integrated_statuses:
                        if latest_result.get("verification_state") != "PASS":
                            reasons.append(
                                "latest result verification_state is "
                                f"{latest_result.get('verification_state')}"
                            )
                        from .collaboration import result_currentness

                        try:
                            current, currentness_reasons = result_currentness(
                                root, latest_result
                            )
                        except (HarnessError, TypeError, ValueError) as exc:
                            current = False
                            currentness_reasons = [str(exc)]
                        if not current:
                            reasons.extend(currentness_reasons)
                        if not latest_result.get("base_commit") or not latest_result.get(
                            "head_commit"
                        ):
                            reasons.append("latest result lacks a committed Git baseline")
                        else:
                            dirty = git_changed_paths(root)
                            if dirty is None:
                                reasons.append("latest result is not in a Git worktree")
                            else:
                                unintegrated = set(
                                    latest_result.get("changed_files", [])
                                ).intersection(dirty)
                                if unintegrated:
                                    reasons.append(
                                        "latest result files are not committed/integrated: "
                                        + ", ".join(sorted(unintegrated))
                                    )
                    if reasons:
                        issues.append(
                            _issue(
                                "ERROR",
                                "TASK_STATUS_INCONSISTENT",
                                f"task {record_id} status {status} is unsupported by latest result "
                                f"{result_id}: "
                                + "; ".join(dict.fromkeys(reasons)),
                                path,
                            )
                        )
        elif kind == "open_item":
            if record.get("gate_level") not in {"G0", "G1", "G2", "G3"}:
                issues.append(_issue("ERROR", "INVALID_GATE_LEVEL", f"invalid gate level {record.get('gate_level')}", path))
            if record.get("status") not in OPEN_ITEM_STATES:
                issues.append(
                    _issue(
                        "ERROR",
                        "INVALID_OPEN_ITEM_STATUS",
                        f"invalid or missing open-item status {record.get('status')}",
                        path,
                    )
                )
            for reference in [*_refs(record.get("affects")), *_refs(record.get("blocks"))]:
                if reference not in known_ids:
                    issues.append(_issue("WARNING", "DANGLING_OPEN_ITEM_REFERENCE", f"open item references unknown {reference}", path))
            if record.get("status") in OPEN_ITEM_CLOSED_STATES:
                resolution = record.get("resolution")
                if not isinstance(resolution, dict):
                    issues.append(
                        _issue(
                            "ERROR",
                            "UNPROPAGATED_RESOLUTION",
                            "resolved open item requires a resolution object",
                            path,
                        )
                    )
                else:
                    for field in (
                        "summary",
                        "decided_by",
                        "decision_authority",
                        "resolved_at",
                        "propagated_to",
                        "evidence_refs",
                        "baseline_refs",
                    ):
                        value = resolution.get(field)
                        valid = (
                            isinstance(value, list)
                            and bool(value)
                            and all(isinstance(item, str) and item.strip() for item in value)
                            if field in {"propagated_to", "evidence_refs", "baseline_refs"}
                            else isinstance(value, str) and bool(value.strip())
                        )
                        if not valid:
                            issues.append(
                                _issue(
                                    "ERROR",
                                    "UNPROPAGATED_RESOLUTION",
                                    f"resolved open item lacks {field}",
                                    path,
                                )
                            )
                    if isinstance(resolution.get("resolved_at"), str):
                        try:
                            parse_utc(resolution["resolved_at"])
                        except (TypeError, ValueError):
                            issues.append(
                                _issue(
                                    "ERROR",
                                    "UNPROPAGATED_RESOLUTION",
                                    "resolved open item has invalid resolved_at",
                                    path,
                                )
                            )
                    if (
                        isinstance(record.get("decision_authority"), str)
                        and resolution.get("decision_authority")
                        != record.get("decision_authority")
                    ):
                        issues.append(
                            _issue(
                                "ERROR",
                                "UNPROPAGATED_RESOLUTION",
                                "resolution decision_authority does not match the open item",
                                path,
                            )
                        )
                    for reference in _refs(resolution.get("propagated_to")):
                        if reference not in known_ids:
                            issues.append(
                                _issue(
                                    "ERROR",
                                    "UNPROPAGATED_RESOLUTION",
                                    f"resolution propagation target is missing: {reference}",
                                    path,
                                )
                            )
                    for reference in _refs(resolution.get("evidence_refs")):
                        if records.get(reference, {}).get("kind") != "evidence":
                            issues.append(
                                _issue(
                                    "ERROR",
                                    "UNPROPAGATED_RESOLUTION",
                                    f"resolution evidence is missing: {reference}",
                                    path,
                                )
                            )
                    for baseline in _refs(resolution.get("baseline_refs")):
                        try:
                            normalized = normalize_claim_path(root, baseline)
                        except HarnessError as exc:
                            issues.append(_issue("ERROR", "UNSAFE_PATH", str(exc), path))
                        else:
                            if not (root / normalized).is_file():
                                issues.append(
                                    _issue(
                                        "ERROR",
                                        "UNPROPAGATED_RESOLUTION",
                                        f"resolution baseline is missing: {baseline}",
                                        path,
                                    )
                                )
        elif kind == "evidence":
            try:
                parse_utc(str(record.get("observed_at", "")))
            except (TypeError, ValueError):
                issues.append(
                    _issue(
                        "ERROR",
                        "INVALID_EVIDENCE_TIME",
                        "evidence observed_at is missing or invalid",
                        path,
                    )
                )
            if record.get("result") not in EVIDENCE_RESULTS:
                issues.append(_issue("ERROR", "INVALID_EVIDENCE_RESULT", f"invalid evidence result {record.get('result')}", path))
            for reference in _refs(record.get("supports")):
                if reference not in known_ids:
                    issues.append(_issue("ERROR", "DANGLING_REFERENCE", f"evidence supports missing {reference}", path))
            if record.get("result") == "VERIFIED":
                for field in ("claim", "method", "environment", "expected", "actual"):
                    if not record.get(field):
                        issues.append(_issue("ERROR", "INCOMPLETE_EVIDENCE", f"verified evidence lacks {field}", path))
                if record.get("ambiguity", {}).get("level") not in {"NONE", "LOW"}:
                    issues.append(_issue("ERROR", "AMBIGUOUS_VERIFIED_EVIDENCE", "verified evidence has excessive ambiguity", path))
                if not record.get("bindings"):
                    issues.append(
                        _issue(
                            "ERROR",
                            "UNBOUND_VERIFIED_EVIDENCE",
                            "verified evidence requires at least one immutable file binding",
                            path,
                        )
                    )
                subject = record.get("subject", {})
                criterion_fingerprints = subject.get("criterion_fingerprints", {})
                closure_fingerprints = subject.get(
                    "closure_criterion_fingerprints", {}
                )
                for supported_id in _refs(record.get("supports")):
                    if supported_id in criteria:
                        criterion = criteria[supported_id]
                        feature_id = next(
                            (
                                candidate_id
                                for candidate_id, candidate in records.items()
                                if candidate.get("kind") == "feature"
                                and any(
                                    item.get("id") == supported_id
                                    for item in candidate.get("completion_criteria", [])
                                )
                            ),
                            None,
                        )
                        expected = subject_fingerprint(
                            {
                                **criterion,
                                "kind": "completion_criterion",
                                "feature_id": feature_id,
                            }
                        )
                        if criterion_fingerprints.get(supported_id) != expected:
                            issues.append(
                                _issue(
                                    "ERROR",
                                    "STALE_EVIDENCE_SUBJECT",
                                    f"evidence lacks current fingerprint for {supported_id}",
                                    path,
                                )
                            )
                    elif supported_id in closure_criteria:
                        expected = subject_fingerprint(
                            {
                                **closure_criteria[supported_id],
                                "kind": "closure_criterion",
                                "project_id": project.get("id"),
                            }
                        )
                        if closure_fingerprints.get(supported_id) != expected:
                            issues.append(
                                _issue(
                                    "ERROR",
                                    "STALE_EVIDENCE_SUBJECT",
                                    f"evidence lacks current fingerprint for {supported_id}",
                                    path,
                                )
                            )
            for binding in record.get("bindings", []):
                current, reason = binding_status(root, binding)
                if not current:
                    issues.append(_issue("WARNING", "STALE_EVIDENCE_BINDING", reason, path))
        elif kind == "approval":
            if record.get("authority_role") != "HUMAN_PROJECT_OWNER":
                issues.append(_issue("ERROR", "INVALID_APPROVAL_AUTHORITY", "approval is not from HUMAN_PROJECT_OWNER", path))
            if record.get("decision") == "APPROVED_WITH_CONDITIONS":
                if not record.get("conditions") or not record.get("condition_refs"):
                    issues.append(
                        _issue(
                            "ERROR",
                            "UNENFORCEABLE_APPROVAL_CONDITION",
                            "conditional approval needs conditions and open-item references",
                            path,
                        )
                    )
                for condition_ref in _refs(record.get("condition_refs")):
                    if records.get(condition_ref, {}).get("kind") != "open_item":
                        issues.append(
                            _issue(
                                "ERROR",
                                "DANGLING_REFERENCE",
                                f"approval condition references missing open item {condition_ref}",
                                path,
                            )
                        )
            status, reason = approval_status(root, record)
            if status == "STALE":
                issues.append(_issue("WARNING", "STALE_APPROVAL", reason, path))
            elif status == "SUPERSEDED":
                issues.append(_issue("WARNING", "SUPERSEDED_APPROVAL", reason, path))
            elif status == "INVALID":
                issues.append(_issue("ERROR", "INVALID_APPROVAL", reason, path))
        elif kind == "change":
            for reference in [*_refs(record.get("source_refs")), *_refs(record.get("affects"))]:
                if reference not in known_ids:
                    issues.append(_issue("WARNING", "DANGLING_CHANGE_REFERENCE", f"change references unknown {reference}", path))
            if record.get("status") in {"DECISION_READY", "APPROVED", "IMPLEMENTING", "VERIFIED", "CLOSED"}:
                if record.get("classification") == "UNCLASSIFIED":
                    issues.append(_issue("ERROR", "UNASSESSED_CHANGE", "change is still unclassified", path))
                if not record.get("affects") or not record.get("impact"):
                    issues.append(_issue("ERROR", "UNASSESSED_CHANGE", "change lacks affected scope or impact", path))
            decision_ref = record.get("decision_ref")
            if record.get("status") in {"APPROVED", "IMPLEMENTING", "VERIFIED", "CLOSED"}:
                if not decision_ref or records.get(decision_ref, {}).get("kind") != "approval":
                    issues.append(_issue("ERROR", "CHANGE_NO_DECISION", "approved change lacks an approval decision", path))
                else:
                    decision = records[decision_ref]
                    status, reason = approval_status(root, decision)
                    if (
                        decision.get("approval_type") != "CHANGE"
                        or decision.get("subject_id") != record_id
                        or status != "CURRENT"
                    ):
                        issues.append(
                            _issue(
                                "ERROR",
                                "CHANGE_DECISION_INVALID",
                                f"change decision is not current: {reason}",
                                path,
                            )
                        )
        elif kind == "recovery":
            checks = record.get("checks", [])
            names = [
                check.get("name")
                for check in checks
                if isinstance(check, dict)
            ]
            if (
                len(names) != len(RECOVERY_CHECK_NAMES)
                or set(names) != RECOVERY_CHECK_NAMES
            ):
                issues.append(
                    _issue(
                        "ERROR",
                        "RECOVERY_AUDIT_TAMPER",
                        "recovery record does not contain each required check exactly once",
                        path,
                    )
                )
            for check in checks:
                if not isinstance(check, dict):
                    continue
                name = str(check.get("name", "UNKNOWN"))
                detail = check.get("detail")
                expected_detail_hash = check.get("detail_sha256")
                actual_detail_hash = (
                    sha256_bytes(detail.encode("utf-8"))
                    if isinstance(detail, str)
                    else None
                )
                if actual_detail_hash != expected_detail_hash:
                    issues.append(
                        _issue(
                            "ERROR",
                            "RECOVERY_AUDIT_TAMPER",
                            f"recovery check {name} detail hash is stale",
                            path,
                        )
                    )
                if name != "external_side_effects":
                    continue
                reconciliation = check.get("reconciliation")
                receipts = check.get("receipts", [])
                idempotency_keys = check.get("idempotency_keys", [])
                if reconciliation == "RECONCILED" and (
                    not receipts or not idempotency_keys
                ):
                    issues.append(
                        _issue(
                            "ERROR",
                            "RECOVERY_AUDIT_TAMPER",
                            "reconciled external side effects lack receipt or idempotency evidence",
                            path,
                        )
                    )
                if reconciliation == "NONE" and (receipts or idempotency_keys):
                    issues.append(
                        _issue(
                            "ERROR",
                            "RECOVERY_AUDIT_TAMPER",
                            "NONE external side effects unexpectedly contain receipts or idempotency keys",
                            path,
                        )
                    )
                for receipt in receipts:
                    current, reason = binding_status(root, receipt)
                    if not current:
                        issues.append(
                            _issue(
                                "ERROR",
                                "RECOVERY_AUDIT_TAMPER",
                                f"recovery receipt is stale: {reason}",
                                path,
                            )
                        )
        elif kind == "result":
            task_id = record.get("task_id")
            if task_id not in records:
                issues.append(_issue("ERROR", "DANGLING_REFERENCE", f"result references missing task {task_id}", path))
            else:
                if (
                    record_id in latest_result_ids
                    and record.get("task_fingerprint")
                    != subject_fingerprint(records[task_id])
                ):
                    issues.append(_issue("WARNING", "STALE_RESULT", "result task fingerprint is stale", path))
                task_plan = records[task_id].get("plan_id")
                plan_path = record_paths.get(task_plan)
                if plan_path:
                    if (
                        record_id in latest_result_ids
                        and record.get("plan_fingerprint")
                        != subject_fingerprint_for_path(plan_path)
                    ):
                        issues.append(_issue("WARNING", "STALE_RESULT", "result plan fingerprint is stale", path))
            if not record.get("verification"):
                issues.append(_issue("ERROR", "RESULT_NO_VERIFICATION", "result requires verification", path))
            else:
                from .collaboration import verification_state

                task = records.get(task_id, {})
                expected_state = verification_state(
                    record.get("verification", []), task.get("verification", [])
                )
                if record.get("verification_state") != expected_state:
                    issues.append(
                        _issue(
                            "ERROR",
                            "RESULT_VERIFICATION_STATE",
                            f"result verification_state must be {expected_state}",
                            path,
                        )
                    )
            for evidence_id in _refs(record.get("evidence_refs")):
                if evidence_id not in records:
                    issues.append(_issue("ERROR", "DANGLING_REFERENCE", f"result references missing evidence {evidence_id}", path))
            from .collaboration import result_currentness

            current, reasons = result_currentness(root, record)
            if record_id in latest_result_ids and not current:
                issues.append(
                    _issue(
                        "WARNING",
                        "STALE_RESULT_BUILD",
                        "; ".join(reasons),
                        path,
                    )
                )
        elif kind == "review":
            result_id = record.get("result_id")
            result = records.get(result_id)
            if not result or result.get("kind") != "result":
                issues.append(_issue("ERROR", "DANGLING_REFERENCE", f"review references missing result {result_id}", path))
            else:
                if record.get("result_fingerprint") != subject_fingerprint(result):
                    issues.append(_issue("WARNING", "STALE_REVIEW", "reviewed result fingerprint changed", path))
                if record.get("result_build_fingerprint") != result.get("build_fingerprint"):
                    issues.append(
                        _issue(
                            "WARNING",
                            "STALE_REVIEW_BUILD",
                            "reviewed result build fingerprint changed",
                            path,
                        )
                    )
                if record.get("reviewer") == result.get("agent"):
                    issues.append(_issue("ERROR", "SELF_REVIEW", "result author cannot be the reviewer", path))
                if record.get("decision") == "PASS" and result.get("verification_state") != "PASS":
                    issues.append(
                        _issue(
                            "ERROR",
                            "PASS_REVIEW_ON_FAILED_RESULT",
                            "review cannot pass an incompletely verified result",
                            path,
                        )
                    )
        elif kind == "handoff":
            if not record.get("verification"):
                issues.append(_issue("ERROR", "HANDOFF_NO_VERIFICATION", "handoff requires exact verification", path))
            if not record.get("next_action"):
                issues.append(_issue("ERROR", "HANDOFF_NO_NEXT_ACTION", "handoff requires a next action", path))

    active_plan = state.get("active_plan")
    if active_plan and active_plan not in records:
        issues.append(_issue("ERROR", "MISSING_ACTIVE_PLAN", f"active plan {active_plan} does not exist"))
    required_features = project.get("required_features", [])
    if not isinstance(required_features, list):
        required_features = []
    for feature_id in required_features:
        if feature_id not in records:
            issues.append(_issue("ERROR", "MISSING_REQUIRED_FEATURE", f"required feature {feature_id} does not exist"))
    for criterion_id, criterion in closure_criteria.items():
        for evidence_id in _refs(criterion.get("evidence_refs")):
            evidence = records.get(evidence_id)
            if not evidence or evidence.get("kind") != "evidence":
                issues.append(
                    _issue(
                        "ERROR",
                        "DANGLING_REFERENCE",
                        f"closure criterion {criterion_id} references missing evidence {evidence_id}",
                    )
                )

    claims = list_claims(root, active_only=True)
    for claim in claims:
        try:
            expires_at = parse_utc(str(claim.get("expires_at", "")))
        except (TypeError, ValueError):
            issues.append(
                _issue(
                    "ERROR",
                    "INVALID_CLAIM_EXPIRY",
                    f"claim {claim.get('id')} has an invalid expires_at",
                )
            )
        else:
            if expires_at <= datetime.now(UTC):
                issues.append(
                    _issue(
                        "ERROR",
                        "EXPIRED_ACTIVE_CLAIM",
                        f"claim {claim.get('id')} is expired and requires recovery",
                    )
                )
        try:
            same_worktree = Path(str(claim.get("worktree", ""))).resolve() == root.resolve()
        except (OSError, RuntimeError):
            same_worktree = False
        if not same_worktree:
            continue
        if not isinstance(claim.get("worktree_snapshot"), dict):
            issues.append(
                _issue(
                    "ERROR",
                    "CLAIM_NO_WORKTREE_SNAPSHOT",
                    f"claim {claim.get('id')} lacks an acquisition snapshot",
                )
            )
        task_id = claim.get("task_id")
        task = records.get(task_id)
        if not task or task.get("kind") != "work_item":
            issues.append(
                _issue("ERROR", "CLAIM_MISSING_TASK", f"claim references missing task {task_id}")
            )
            continue
        if claim.get("task_fingerprint") != subject_fingerprint(task):
            issues.append(
                _issue("ERROR", "STALE_ACTIVE_CLAIM", f"claim {claim.get('id')} task changed")
            )
        plan_id = task.get("plan_id")
        try:
            plan_fingerprint = subject_fingerprint_for_path(
                record_path(root, "plan", plan_id)
            )
        except HarnessError as exc:
            issues.append(_issue("ERROR", "STALE_ACTIVE_CLAIM", str(exc)))
        else:
            if claim.get("plan_fingerprint") != plan_fingerprint:
                issues.append(
                    _issue("ERROR", "STALE_ACTIVE_CLAIM", f"claim {claim.get('id')} plan changed")
                )
    for index, left in enumerate(claims):
        for right in claims[index + 1 :]:
            path_conflict = any(
                paths_overlap(a, b) for a in left.get("paths", []) for b in right.get("paths", [])
            )
            lock_conflict = bool(set(left.get("logical_locks", [])).intersection(right.get("logical_locks", [])))
            if path_conflict or lock_conflict:
                issues.append(
                    _issue(
                        "ERROR",
                        "OVERLAPPING_ACTIVE_CLAIMS",
                        f"{left.get('id')} and {right.get('id')} overlap",
                    )
                )
    return issues


def issue_counts(issues: list[Issue]) -> dict[str, int]:
    return {
        "errors": sum(issue.severity == "ERROR" for issue in issues),
        "warnings": sum(issue.severity == "WARNING" for issue in issues),
    }
