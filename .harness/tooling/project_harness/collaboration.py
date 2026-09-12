from __future__ import annotations

import os
import re
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from .constants import HARNESS_DIR
from .core import (
    HarnessError,
    allocate_record_id,
    atomic_write_json,
    atomic_write_text,
    canonical_json,
    filesystem_mutex,
    git_changed_paths,
    git_common_dir,
    git_head,
    git_status,
    is_path_within,
    load_json,
    next_id,
    normalize_agent_id,
    normalize_claim_path,
    paths_overlap,
    parse_utc,
    record_event,
    record_path,
    sha256_file,
    sha256_bytes,
    subject_fingerprint,
    subject_fingerprint_for_path,
    utc_after,
    utc_now,
)


SYSTEM_MANAGED_VIEW_PATHS = {"HANDOFF.md"}
RECOVERY_CHECK_NAMES = {
    "process",
    "worktree",
    "diff",
    "outbox",
    "external_side_effects",
}


def runtime_root(root: Path) -> Path:
    common = git_common_dir(root)
    if common is not None:
        location = common / "project-harness-runtime"
    else:
        location = root / HARNESS_DIR / "runtime"
    location.mkdir(parents=True, exist_ok=True)
    return location


def mailbox_directory(root: Path, box: str, agent: str) -> Path:
    if box not in {"inbox", "outbox"}:
        raise HarnessError("Mailbox must be inbox or outbox")
    agent = normalize_agent_id(agent)
    path = runtime_root(root) / "mailboxes" / box / agent
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_mailbox(
    root: Path, *, box: str, agent: str, include_acknowledged: bool = False
) -> list[dict[str, Any]]:
    agent = normalize_agent_id(agent)
    directory = mailbox_directory(root, box, agent)
    acknowledgements = runtime_root(root) / "mailboxes" / "acks" / agent
    values: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        value = load_json(path)
        item_id = str(value.get("id", path.stem))
        if not include_acknowledged and (acknowledgements / f"{item_id}.json").is_file():
            continue
        values.append(value)
    return values


def acknowledge_mailbox(
    root: Path, *, box: str, agent: str, item_id: str
) -> dict[str, Any]:
    agent = normalize_agent_id(agent)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", item_id):
        raise HarnessError("Invalid mailbox item ID")
    directory = mailbox_directory(root, box, agent)
    matching = [
        load_json(path)
        for path in directory.glob("*.json")
        if load_json(path).get("id") == item_id
    ]
    if not matching:
        raise HarnessError(f"Mailbox item not found: {item_id}")
    value = {
        "schema": "harness.mailbox-ack/v1",
        "id": item_id,
        "kind": "mailbox_ack",
        "box": box,
        "agent": agent,
        "acknowledged_at": utc_now(),
    }
    ack_path = runtime_root(root) / "mailboxes" / "acks" / agent / f"{item_id}.json"
    atomic_write_json(ack_path, value)
    return value


@contextmanager
def _runtime_mutex(
    root: Path, timeout_seconds: float = 5.0, lease_seconds: float = 300.0
):
    lock = runtime_root(root) / "claim-mutex"
    with filesystem_mutex(
        lock,
        timeout_seconds=timeout_seconds,
        lease_seconds=lease_seconds,
        recovery_directory=runtime_root(root) / "lock-recoveries",
        timeout_message=(
            "Timed out waiting for the runtime registry lock; inspect its owner metadata"
        ),
    ):
        yield


def _same_resolved_worktree(left: Path, right: Any) -> bool:
    if not isinstance(right, str) or not right.strip():
        return True
    try:
        return os.path.normcase(str(left.resolve())) == os.path.normcase(
            str(Path(right).resolve())
        )
    except (OSError, RuntimeError, TypeError, ValueError):
        # An old or malformed active claim must fail closed rather than permit a
        # second writer in an ownership domain that cannot be established.
        return True


def _reject_system_managed_claim_paths(paths: Iterable[str]) -> None:
    protected = [
        managed
        for managed in sorted(SYSTEM_MANAGED_VIEW_PATHS)
        if is_path_within(managed, paths)
    ]
    if protected:
        raise HarnessError(
            "Claim paths include system-managed generated views: "
            + ", ".join(protected)
        )


def lease_directory(root: Path) -> Path:
    path = runtime_root(root) / "leases"
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_claims(root: Path, *, active_only: bool = False) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for path in sorted(lease_directory(root).glob("CLM-*.json")):
        claim = load_json(path)
        if active_only and claim.get("status") != "ACTIVE":
            continue
        claims.append(claim)
    return claims


def get_claim(root: Path, claim_id: str) -> tuple[dict[str, Any], Path]:
    if not re.fullmatch(r"CLM-\d{4,}", claim_id):
        raise HarnessError(f"Invalid claim ID: {claim_id!r}")
    path = lease_directory(root) / f"{claim_id}.json"
    return load_json(path), path


def ensure_claim_current(root: Path, claim: dict[str, Any]) -> None:
    from .gates import task_start_gate

    task_id = claim.get("task_id")
    if not isinstance(task_id, str):
        raise HarnessError("Claim has no task ID")
    if Path(str(claim.get("worktree", ""))).resolve() != root.resolve():
        raise HarnessError("Claim belongs to a different Git worktree")
    try:
        expired = parse_utc(str(claim.get("expires_at", ""))) <= datetime.now(UTC)
    except (TypeError, ValueError) as exc:
        raise HarnessError("Claim has an invalid expiry timestamp") from exc
    if expired:
        raise HarnessError("Claim has expired; recover it and acquire a new claim")
    gate = task_start_gate(root, task_id)
    if not gate.passed:
        raise HarnessError("Claim context is no longer executable: " + "; ".join(gate.blockers))
    task = gate.subject
    plan_path = record_path(root, "plan", task["plan_id"])
    if claim.get("task_fingerprint") != subject_fingerprint(task):
        raise HarnessError("Claim task fingerprint is stale; release and reacquire the task")
    if claim.get("plan_fingerprint") != subject_fingerprint_for_path(plan_path):
        raise HarnessError("Claim plan fingerprint is stale; release and reacquire the task")


CONTROL_CHANGE_PREFIXES = {
    ".harness/runtime",
}

IMMUTABLE_CONTROL_PREFIXES = {
    ".harness/project.json",
    ".harness/state.json",
    ".harness/plans",
    ".harness/requirements",
    ".harness/features",
    ".harness/work-items",
    ".harness/open-items",
    ".harness/evidence",
    ".harness/approvals",
    ".harness/baselines",
    ".harness/results",
    ".harness/reviews",
    ".harness/handoffs",
    ".harness/recoveries",
    ".harness/events",
}


def _tracked_control_changes(root: Path) -> list[str]:
    changes: list[str] = []
    for line in git_status(root):
        status = line[:2] if len(line) >= 2 else ""
        if status == "??":
            continue
        payload = line[3:].strip() if len(line) > 3 else ""
        for value in payload.split(" -> ") if " -> " in payload else [payload]:
            value = value.strip('"')
            if not value:
                continue
            try:
                normalized = normalize_claim_path(root, value)
            except HarnessError:
                continue
            if any(
                paths_overlap(normalized, protected)
                for protected in IMMUTABLE_CONTROL_PREFIXES
            ):
                changes.append(normalized)
    return sorted(set(changes))


def _path_state(root: Path, value: str) -> str:
    path = root / value
    if path.is_file():
        return f"FILE:{sha256_file(path)}"
    if path.exists():
        return "EXISTS"
    return "MISSING"


RESULT_BUILD_FIELDS = (
    "task_id",
    "claim_id",
    "task_fingerprint",
    "plan_fingerprint",
    "base_commit",
    "head_commit",
    "changed_file_states",
    "evidence_fingerprints",
)


def result_build_fingerprint(result: dict[str, Any]) -> str:
    subject = {field: result.get(field) for field in RESULT_BUILD_FIELDS}
    return sha256_bytes(canonical_json(subject).encode("utf-8"))


def result_currentness(root: Path, result: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    task_id = result.get("task_id")
    if not isinstance(task_id, str):
        return False, ["result task_id is missing"]
    try:
        task = load_json(record_path(root, "work_item", task_id))
    except HarnessError as exc:
        return False, [str(exc)]
    if result.get("task_fingerprint") != subject_fingerprint(task):
        reasons.append("task fingerprint is stale")
    plan_id = task.get("plan_id")
    if not isinstance(plan_id, str):
        reasons.append("task plan_id is missing")
    else:
        try:
            plan_path = record_path(root, "plan", plan_id)
            if result.get("plan_fingerprint") != subject_fingerprint_for_path(plan_path):
                reasons.append("plan fingerprint is stale")
            from .decision_scope import coverage_blockers, plan_scope
            plan = load_json(plan_path)
            scope = plan_scope(plan)
            if scope:
                reasons.extend(coverage_blockers(root, plan, scope, task_id=task_id))
        except HarnessError as exc:
            reasons.append(str(exc))
    changed_files = result.get("changed_files")
    states = result.get("changed_file_states")
    if not isinstance(changed_files, list) or not isinstance(states, dict):
        reasons.append("changed-file state manifest is malformed")
    else:
        normalized: list[str] = []
        for value in changed_files:
            if not isinstance(value, str):
                reasons.append("changed-file manifest contains a non-string path")
                continue
            try:
                normalized.append(normalize_claim_path(root, value))
            except HarnessError as exc:
                reasons.append(str(exc))
        if set(normalized) != set(states):
            reasons.append("changed-file paths and state manifest differ")
        for value in normalized:
            if states.get(value) != _path_state(root, value):
                reasons.append(f"changed file is no longer current: {value}")
    expected_build = result_build_fingerprint(result)
    if result.get("build_fingerprint") != expected_build:
        reasons.append("result build fingerprint is missing or changed")
    evidence_fingerprints = result.get("evidence_fingerprints")
    evidence_refs = result.get("evidence_refs")
    if not isinstance(evidence_fingerprints, dict) or not isinstance(evidence_refs, list):
        reasons.append("result evidence fingerprint manifest is malformed")
    elif set(evidence_fingerprints) != set(evidence_refs):
        reasons.append("result evidence references and fingerprints differ")
    else:
        for evidence_id in evidence_refs:
            try:
                evidence = load_json(record_path(root, "evidence", evidence_id))
            except HarnessError as exc:
                reasons.append(str(exc))
                continue
            if evidence_fingerprints.get(evidence_id) != subject_fingerprint(evidence):
                reasons.append(f"result evidence changed after submission: {evidence_id}")
    return not reasons, reasons


def _change_snapshot(root: Path, base_commit: str | None) -> dict[str, str] | None:
    changed = git_changed_paths(root, base_commit)
    if changed is None:
        return None
    return {
        value: _path_state(root, value)
        for value in sorted(changed)
        if not any(paths_overlap(value, ignored) for ignored in CONTROL_CHANGE_PREFIXES)
    }


def _full_worktree_snapshot(root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        value = path.relative_to(root).as_posix()
        if any(paths_overlap(value, ignored) for ignored in CONTROL_CHANGE_PREFIXES):
            continue
        snapshot[value] = _path_state(root, value)
    return dict(sorted(snapshot.items()))


def validate_changed_files(
    root: Path, claim: dict[str, Any], changed_files: list[str]
) -> list[str]:
    normalized = [normalize_claim_path(root, value) for value in changed_files]
    if len(set(normalized)) != len(normalized):
        raise HarnessError("Changed files must not contain duplicates")
    outside = [value for value in normalized if not is_path_within(value, claim.get("paths", []))]
    if outside:
        raise HarnessError("Changed files exceed the active claim: " + ", ".join(outside))
    actual = git_changed_paths(root, claim.get("base_commit"))
    if actual is None:
        baseline_snapshot = claim.get("worktree_snapshot")
        if not isinstance(baseline_snapshot, dict):
            raise HarnessError("Claim lacks its acquisition worktree snapshot")
        current_snapshot = _full_worktree_snapshot(root)
        baseline_outside = {
            value: state
            for value, state in baseline_snapshot.items()
            if not is_path_within(value, claim.get("paths", []))
        }
        current_outside = {
            value: state
            for value, state in current_snapshot.items()
            if not is_path_within(value, claim.get("paths", []))
        }
        if current_outside != baseline_outside:
            changed_outside = sorted(
                value
                for value in set(current_outside) | set(baseline_outside)
                if current_outside.get(value) != baseline_outside.get(value)
            )
            raise HarnessError(
                "Worktree changed outside the active claim after acquisition: "
                + ", ".join(changed_outside)
            )
        inside_changes = {
            value
            for value in set(current_snapshot) | set(baseline_snapshot)
            if is_path_within(value, claim.get("paths", []))
            and current_snapshot.get(value) != baseline_snapshot.get(value)
        }
        declared = set(normalized)
        if inside_changes != declared:
            omitted = inside_changes - declared
            unsupported = declared - inside_changes
            details = []
            if omitted:
                details.append("omitted " + ", ".join(sorted(omitted)))
            if unsupported:
                details.append("unchanged " + ", ".join(sorted(unsupported)))
            raise HarnessError("Changed-file manifest does not match actual changes: " + "; ".join(details))
        return normalized
    baseline_snapshot = claim.get("worktree_snapshot")
    if not isinstance(baseline_snapshot, dict):
        raise HarnessError("Claim lacks its acquisition worktree snapshot")
    current_snapshot = {
        value: _path_state(root, value)
        for value in actual
        if not any(paths_overlap(value, ignored) for ignored in CONTROL_CHANGE_PREFIXES)
    }
    baseline_outside = {
        value: state
        for value, state in baseline_snapshot.items()
        if not is_path_within(value, claim.get("paths", []))
    }
    current_outside = {
        value: state
        for value, state in current_snapshot.items()
        if not is_path_within(value, claim.get("paths", []))
    }
    if current_outside != baseline_outside:
        changed_outside = sorted(
            value
            for value in set(current_outside) | set(baseline_outside)
            if current_outside.get(value) != baseline_outside.get(value)
        )
        raise HarnessError(
            "Worktree changed outside the active claim after acquisition: "
            + ", ".join(changed_outside)
        )
    relevant = {
        value
        for value in actual
        if is_path_within(value, claim.get("paths", []))
        and not any(paths_overlap(value, ignored) for ignored in CONTROL_CHANGE_PREFIXES)
    }
    declared = set(normalized)
    omitted = relevant - declared
    unsupported = declared - actual
    if omitted:
        raise HarnessError(
            "Changed-file manifest omits actual changes inside the claim: "
            + ", ".join(sorted(omitted))
        )
    if unsupported:
        raise HarnessError(
            "Changed-file manifest includes paths not changed from the claim base: "
            + ", ".join(sorted(unsupported))
        )
    return normalized


def _validate_scope_subset(requested: Iterable[str], allowed: Iterable[str]) -> None:
    allow = list(allowed)
    outside = [value for value in requested if not is_path_within(value, allow)]
    if outside:
        raise HarnessError(
            "Claim paths exceed the task write scope: " + ", ".join(outside)
        )


def acquire_claim(
    root: Path,
    *,
    agent: str,
    task_id: str,
    paths: list[str] | None = None,
    logical_locks: list[str] | None = None,
    ttl_minutes: int = 120,
    handoff_id: str | None = None,
) -> dict[str, Any]:
    from .gates import task_start_gate

    agent = normalize_agent_id(agent)
    if ttl_minutes <= 0:
        raise HarnessError("Claim TTL must be greater than zero minutes")
    gate = task_start_gate(root, task_id)
    if not gate.passed:
        raise HarnessError("Task start gate blocked: " + "; ".join(gate.blockers))

    task = gate.subject
    protected_changes = _tracked_control_changes(root)
    if protected_changes and "HARNESS_CONTROL_CHANGE" not in set(
        task.get("capabilities", [])
    ):
        raise HarnessError(
            "Tracked control-plane records changed outside an authorized change task: "
            + ", ".join(protected_changes)
        )
    plan_path = record_path(root, "plan", task["plan_id"])
    normalized_allowed = [
        normalize_claim_path(root, value) for value in task.get("write_scope", [])
    ]
    requested = paths if paths is not None else task.get("write_scope", [])
    normalized_paths = [normalize_claim_path(root, value) for value in requested]
    if not normalized_paths:
        raise HarnessError("A write claim requires at least one path")
    _reject_system_managed_claim_paths(normalized_paths)
    _validate_scope_subset(normalized_paths, normalized_allowed)

    acknowledged_dirty = [
        normalize_claim_path(root, value)
        for value in task.get("preexisting_dirty_paths", [])
    ]
    handoff_acknowledged_dirty: set[str] = set()
    accepted_handoff: dict[str, Any] | None = None
    if handoff_id:
        handoff_path = record_path(root, "handoff", handoff_id)
        if handoff_path.is_file():
            accepted_handoff = load_json(handoff_path)
        else:
            shared_handoff = mailbox_directory(root, "inbox", agent) / f"{handoff_id}.json"
            if shared_handoff.is_file():
                accepted_handoff = load_json(shared_handoff)
        if accepted_handoff is None:
            raise HarnessError(f"Handoff does not exist for {agent}: {handoff_id}")
        if (
            accepted_handoff.get("to_agent") != agent
            or accepted_handoff.get("task_id") != task_id
        ):
            raise HarnessError("Handoff recipient or task does not match the new claim")
        if accepted_handoff.get("task_fingerprint") != subject_fingerprint(task):
            raise HarnessError("Handoff task fingerprint is stale")
        if accepted_handoff.get("plan_fingerprint") != subject_fingerprint_for_path(plan_path):
            raise HarnessError("Handoff plan fingerprint is stale")
        handoff_changes = accepted_handoff.get("changed_files")
        handoff_states = accepted_handoff.get("changed_file_states")
        if not isinstance(handoff_changes, list) or not isinstance(handoff_states, dict):
            raise HarnessError("Handoff lacks a verifiable changed-file manifest")
        normalized_handoff_changes = [
            normalize_claim_path(root, value) for value in handoff_changes
        ]
        _validate_scope_subset(normalized_handoff_changes, normalized_paths)
        for value in normalized_handoff_changes:
            if handoff_states.get(value) != _path_state(root, value):
                raise HarnessError(f"Handoff file state changed before acceptance: {value}")
        handoff_acknowledged_dirty.update(normalized_handoff_changes)
    dirty_conflicts: list[str] = []
    for line in git_status(root):
        payload = line[3:].strip() if len(line) > 3 else ""
        dirty_values = payload.split(" -> ") if " -> " in payload else [payload]
        for value in dirty_values:
            value = value.strip('"')
            if not value:
                continue
            try:
                dirty_path = normalize_claim_path(root, value)
            except HarnessError:
                continue
            overlaps_request = any(paths_overlap(dirty_path, claimed) for claimed in normalized_paths)
            acknowledged = any(
                paths_overlap(dirty_path, allowed) for allowed in acknowledged_dirty
            ) or dirty_path.casefold() in {
                value.casefold() for value in handoff_acknowledged_dirty
            }
            if overlaps_request and not acknowledged:
                dirty_conflicts.append(dirty_path)
    if dirty_conflicts:
        raise HarnessError(
            "Claim overlaps pre-existing dirty paths without explicit task acknowledgement: "
            + ", ".join(sorted(set(dirty_conflicts)))
        )

    task_locks = {str(value).casefold() for value in task.get("logical_locks", [])}
    requested_locks = {
        str(value).strip().casefold() for value in (logical_locks or task.get("logical_locks", []))
    }
    if not requested_locks.issubset(task_locks):
        raise HarnessError("Claim requests logical locks not authorized by the task")

    with _runtime_mutex(root):
        acceptance_path: Path | None = None
        if accepted_handoff is not None:
            acceptance_path = runtime_root(root) / "handoff-acceptances" / f"{handoff_id}.json"
            if acceptance_path.is_file():
                raise HarnessError(f"Handoff {handoff_id} has already been accepted")
        active = list_claims(root, active_only=True)
        conflicts: list[str] = []
        if git_common_dir(root) is None and active:
            conflicts.append("parallel write claims require a Git repository and isolated worktrees")
        for existing in active:
            if existing.get("task_id") == task_id:
                conflicts.append(
                    f"{existing.get('id')} already owns the same task {task_id}; "
                    "parallel attempts require separate work items"
                )
                continue
            if _same_resolved_worktree(root, existing.get("worktree")):
                conflicts.append(
                    f"{existing.get('id')} already writes this resolved worktree; "
                    "use an isolated Git worktree for parallel work"
                )
                continue
            path_conflict = any(
                paths_overlap(left, right)
                for left in normalized_paths
                for right in existing.get("paths", [])
            )
            lock_conflict = bool(requested_locks.intersection(existing.get("logical_locks", [])))
            if path_conflict or lock_conflict:
                conflicts.append(
                    f"{existing.get('id')} owned by {existing.get('agent')} for {existing.get('task_id')}"
                )
        if conflicts:
            raise HarnessError("Claim conflicts with active ownership: " + "; ".join(conflicts))

        claim_id = next_id(lease_directory(root), "CLM-")
        base_commit = git_head(root)
        record_event(
            root,
            "CLAIM_ACQUIRED",
            {"claim_id": claim_id, "agent": agent, "task_id": task_id},
        )
        git_snapshot = _change_snapshot(root, base_commit)
        worktree_snapshot = (
            git_snapshot if git_snapshot is not None else _full_worktree_snapshot(root)
        )
        claim = {
            "schema": "harness.claim/v1",
            "id": claim_id,
            "kind": "claim",
            "status": "ACTIVE",
            "agent": agent,
            "task_id": task_id,
            "task_fingerprint": subject_fingerprint(task),
            "plan_id": task["plan_id"],
            "plan_fingerprint": subject_fingerprint_for_path(plan_path),
            "paths": normalized_paths,
            "logical_locks": sorted(requested_locks),
            "base_commit": base_commit,
            "worktree": str(root),
            "snapshot_mode": "GIT" if git_snapshot is not None else "NO_GIT",
            "worktree_snapshot": worktree_snapshot,
            "acquired_at": utc_now(),
            "expires_at": utc_after(ttl_minutes),
            "accepted_handoff_id": handoff_id,
            "verification": task.get("verification", []),
        }
        atomic_write_json(lease_directory(root) / f"{claim_id}.json", claim)
        if acceptance_path is not None:
            atomic_write_json(
                acceptance_path,
                {
                    "schema": "harness.handoff-acceptance/v1",
                    "id": handoff_id,
                    "kind": "handoff_acceptance",
                    "agent": agent,
                    "task_id": task_id,
                    "claim_id": claim_id,
                    "accepted_at": utc_now(),
                },
            )
    return claim


def refresh_claim(root: Path, *, claim_id: str, agent: str, ttl_minutes: int) -> dict[str, Any]:
    agent = normalize_agent_id(agent)
    if ttl_minutes <= 0:
        raise HarnessError("Claim TTL must be greater than zero minutes")
    with _runtime_mutex(root):
        claim, path = get_claim(root, claim_id)
        if claim.get("status") != "ACTIVE":
            raise HarnessError(f"Claim {claim_id} is not active")
        if claim.get("agent") != agent:
            raise HarnessError(f"Claim {claim_id} belongs to {claim.get('agent')}")
        ensure_claim_current(root, claim)
        claim["expires_at"] = utc_after(ttl_minutes)
        claim["refreshed_at"] = utc_now()
        atomic_write_json(path, claim)
    return claim


def release_claim(
    root: Path,
    *,
    claim_id: str,
    agent: str,
    disposition: str = "RELEASED",
    reason: str | None = None,
    validate_clean: bool = True,
) -> dict[str, Any]:
    agent = normalize_agent_id(agent)
    with _runtime_mutex(root):
        claim, path = get_claim(root, claim_id)
        if claim.get("status") != "ACTIVE":
            raise HarnessError(f"Claim {claim_id} is not active")
        if claim.get("agent") != agent:
            raise HarnessError(f"Claim {claim_id} belongs to {claim.get('agent')}")
        if validate_clean:
            baseline = claim.get("worktree_snapshot")
            if not isinstance(baseline, dict):
                raise HarnessError("Claim lacks its acquisition worktree snapshot")
            current = (
                _change_snapshot(root, claim.get("base_commit"))
                if claim.get("snapshot_mode") == "GIT"
                else _full_worktree_snapshot(root)
            )
            if current is None:
                raise HarnessError("Claim Git worktree is no longer available")
            drift = sorted(
                value
                for value in set(baseline) | set(current)
                if baseline.get(value) != current.get(value)
            )
            if drift:
                raise HarnessError(
                    "Claim has unrecorded workspace changes; submit a result or "
                    "create a handoff before release: " + ", ".join(drift)
                )
        claim["status"] = disposition
        claim["released_at"] = utc_now()
        claim["release_reason"] = reason
        atomic_write_json(path, claim)
    record_event(root, "CLAIM_RELEASED", {"claim_id": claim_id, "agent": agent, "disposition": disposition})
    return claim


def _recovery_manifest_source(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise HarnessError("Recovery requires --recovery-manifest with a repository-relative JSON path")
    normalized = normalize_claim_path(root, value)
    if normalized == "**":
        raise HarnessError("Recovery manifest must name one JSON file")
    source = root / normalized
    if not source.is_file() or source.suffix.casefold() != ".json":
        raise HarnessError(f"Recovery manifest is not a JSON file: {normalized}")
    return source


def _validate_recovery_receipts(
    root: Path, receipts: Any, *, required: bool
) -> list[dict[str, str]]:
    if not isinstance(receipts, list):
        raise HarnessError("external_side_effects receipts must be a list")
    if required and not receipts:
        raise HarnessError(
            "RECONCILED external side effects require at least one bound receipt"
        )
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, binding in enumerate(receipts):
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise HarnessError(
                f"external_side_effects receipts[{index}] requires only path and sha256"
            )
        value = binding.get("path")
        expected = binding.get("sha256")
        if not isinstance(value, str) or not isinstance(expected, str):
            raise HarnessError(
                f"external_side_effects receipts[{index}] path and sha256 must be strings"
            )
        path_value = normalize_claim_path(root, value)
        if path_value == "**" or path_value.casefold() in seen:
            raise HarnessError(
                f"external_side_effects receipts[{index}] has an invalid or duplicate path"
            )
        seen.add(path_value.casefold())
        path = root / path_value
        if not path.is_file():
            raise HarnessError(f"Recovery receipt is missing: {path_value}")
        actual = sha256_file(path)
        if expected != actual:
            raise HarnessError(f"Recovery receipt hash is stale: {path_value}")
        normalized.append({"path": path_value, "sha256": expected})
    return normalized


def _validate_recovery_manifest(
    root: Path,
    manifest: dict[str, Any],
    *,
    claim_id: str,
    agent: str,
    claim_expires_at: datetime,
) -> dict[str, Any]:
    allowed_fields = {
        "schema",
        "id",
        "kind",
        "claim_id",
        "recovered_by",
        "observed_at",
        "checks",
        "decision",
        "reason",
    }
    if set(manifest) != allowed_fields:
        missing = sorted(allowed_fields - set(manifest))
        extra = sorted(set(manifest) - allowed_fields)
        details: list[str] = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("unexpected " + ", ".join(extra))
        raise HarnessError("Recovery manifest fields are invalid: " + "; ".join(details))
    if manifest.get("schema") != "harness.recovery/v1" or manifest.get("kind") != "recovery":
        raise HarnessError("Recovery manifest schema/kind must be harness.recovery/v1 and recovery")
    recovery_id = manifest.get("id")
    if not isinstance(recovery_id, str) or not re.fullmatch(r"RCV-\d{4,}", recovery_id):
        raise HarnessError("Recovery manifest id must use RCV-<digits>")
    if manifest.get("claim_id") != claim_id:
        raise HarnessError("Recovery manifest claim_id does not match the expired claim")
    if manifest.get("recovered_by") != agent:
        raise HarnessError("Recovery manifest recovered_by does not match --agent")
    if manifest.get("decision") != "ABANDON_AND_RECLAIM":
        raise HarnessError("Recovery decision must be ABANDON_AND_RECLAIM")
    manifest_reason = manifest.get("reason")
    if not isinstance(manifest_reason, str) or not manifest_reason.strip():
        raise HarnessError("Recovery manifest reason must be nonempty")
    try:
        observed_at = parse_utc(str(manifest.get("observed_at", "")))
    except (TypeError, ValueError) as exc:
        raise HarnessError("Recovery manifest observed_at is invalid") from exc
    if observed_at.tzinfo is None:
        raise HarnessError("Recovery manifest observed_at must include a timezone")
    if observed_at < claim_expires_at:
        raise HarnessError("Recovery inspection must be observed after the claim expired")
    if observed_at > datetime.now(UTC):
        raise HarnessError("Recovery manifest observed_at cannot be in the future")

    checks = manifest.get("checks")
    if not isinstance(checks, list):
        raise HarnessError("Recovery manifest checks must be a list")
    normalized_checks: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    common_fields = {"name", "outcome", "detail", "detail_sha256"}
    external_fields = common_fields | {
        "reconciliation",
        "idempotency_keys",
        "receipts",
    }
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise HarnessError(f"Recovery checks[{index}] must be an object")
        name = check.get("name")
        if not isinstance(name, str) or name not in RECOVERY_CHECK_NAMES:
            raise HarnessError(f"Recovery checks[{index}] has an unsupported name")
        if name in seen_names:
            raise HarnessError(f"Recovery check is duplicated: {name}")
        seen_names.add(name)
        allowed = external_fields if name == "external_side_effects" else common_fields
        if set(check) != allowed:
            raise HarnessError(
                f"Recovery check {name} fields are invalid; expected {', '.join(sorted(allowed))}"
            )
        if check.get("outcome") != "PASS":
            raise HarnessError(f"Recovery check {name} must have outcome PASS")
        detail = check.get("detail")
        detail_hash = check.get("detail_sha256")
        if not isinstance(detail, str) or not detail.strip():
            raise HarnessError(f"Recovery check {name} detail must be nonempty")
        expected_hash = sha256_bytes(detail.encode("utf-8"))
        if detail_hash != expected_hash:
            raise HarnessError(f"Recovery check {name} detail_sha256 does not match detail")
        normalized_check: dict[str, Any] = {
            "name": name,
            "outcome": "PASS",
            "detail": detail,
            "detail_sha256": detail_hash,
        }
        if name == "external_side_effects":
            reconciliation = check.get("reconciliation")
            if reconciliation not in {"NONE", "RECONCILED"}:
                raise HarnessError(
                    "external_side_effects reconciliation must be NONE or RECONCILED"
                )
            keys = check.get("idempotency_keys")
            if not isinstance(keys, list) or any(
                not isinstance(value, str) or not value.strip() for value in keys
            ):
                raise HarnessError(
                    "external_side_effects idempotency_keys must be nonempty strings"
                )
            if len(set(keys)) != len(keys):
                raise HarnessError("external_side_effects idempotency_keys must be unique")
            receipts = _validate_recovery_receipts(
                root, check.get("receipts"), required=reconciliation == "RECONCILED"
            )
            if reconciliation == "RECONCILED" and not keys:
                raise HarnessError(
                    "RECONCILED external side effects require an idempotency key"
                )
            if reconciliation == "NONE" and (keys or receipts):
                raise HarnessError(
                    "NONE external side effects cannot declare idempotency keys or receipts"
                )
            normalized_check.update(
                {
                    "reconciliation": reconciliation,
                    "idempotency_keys": keys,
                    "receipts": receipts,
                }
            )
        normalized_checks.append(normalized_check)
    missing_checks = RECOVERY_CHECK_NAMES - seen_names
    if missing_checks:
        raise HarnessError(
            "Recovery manifest is missing required checks: "
            + ", ".join(sorted(missing_checks))
        )
    if len(normalized_checks) != len(RECOVERY_CHECK_NAMES):
        raise HarnessError("Recovery manifest must contain exactly the required checks")
    return {**manifest, "checks": normalized_checks}


def recover_claim(
    root: Path,
    *,
    claim_id: str,
    agent: str,
    reason: str,
    recovery_manifest: str | None = None,
) -> dict[str, Any]:
    agent = normalize_agent_id(agent)
    if not isinstance(reason, str) or not reason.strip():
        raise HarnessError("Recovery requires a nonempty operator reason")
    source_path = _recovery_manifest_source(root, recovery_manifest or "")
    source_manifest = load_json(source_path)
    source_hash = sha256_file(source_path)

    with _runtime_mutex(root):
        claim, claim_path = get_claim(root, claim_id)
        if claim.get("status") != "ACTIVE":
            raise HarnessError(f"Claim {claim_id} is not active")
        try:
            expires_at = parse_utc(str(claim.get("expires_at", "")))
        except (TypeError, ValueError) as exc:
            raise HarnessError(f"Claim {claim_id} has an invalid expiry timestamp") from exc
        if expires_at.tzinfo is None:
            raise HarnessError(f"Claim {claim_id} expiry timestamp lacks a timezone")
        if expires_at > datetime.now(UTC):
            raise HarnessError(f"Claim {claim_id} has not expired; obtain a normal handoff")

        # Re-run every observation and receipt hash check while ownership state
        # is serialized; the preloaded manifest alone is not authority.
        manifest = _validate_recovery_manifest(
            root,
            source_manifest,
            claim_id=claim_id,
            agent=agent,
            claim_expires_at=expires_at,
        )
        if sha256_file(source_path) != source_hash:
            raise HarnessError("Recovery manifest changed during inspection")
        recovery_path = record_path(root, "recovery", manifest["id"])
        if recovery_path.is_file():
            existing = load_json(recovery_path)
            if canonical_json(existing) != canonical_json(manifest):
                raise HarnessError(f"Recovery ID already exists: {manifest['id']}")
        else:
            atomic_write_json(recovery_path, manifest)
        canonical_hash = sha256_file(recovery_path)
        recovery_event = record_event(
            root,
            "CLAIM_RECOVERY",
            {
                "claim_id": claim_id,
                "previous_agent": claim.get("agent"),
                "recovered_by": agent,
                "operator_reason": reason,
                "recovery_id": manifest["id"],
                "recovery_manifest": recovery_path.relative_to(root).as_posix(),
                "recovery_manifest_sha256": canonical_hash,
                "source_manifest_sha256": source_hash,
                "observed_at": manifest["observed_at"],
                "decision": manifest["decision"],
                "checks": manifest["checks"],
            },
        )
        claim["status"] = "ABANDONED_AFTER_RECOVERY"
        claim["released_at"] = utc_now()
        claim["release_reason"] = reason
        claim["recovered_by"] = agent
        claim["recovery_id"] = manifest["id"]
        claim["recovery_manifest_sha256"] = canonical_hash
        claim["recovery_event"] = recovery_event.relative_to(root).as_posix()
        atomic_write_json(claim_path, claim)
    return claim


def _parse_verification(values: list[str]) -> list[dict[str, str]]:
    parsed: list[dict[str, str]] = []
    for value in values:
        if "::" not in value:
            raise HarnessError(
                "Verification must use `command::outcome`, for example `python -m unittest::passed`"
            )
        command, outcome = value.split("::", 1)
        command = command.strip()
        outcome = outcome.strip().upper()
        aliases = {"PASSED": "PASS", "FAILED": "FAIL"}
        outcome = aliases.get(outcome, outcome)
        if not command:
            raise HarnessError("Verification command cannot be empty")
        if outcome not in {
            "PASS",
            "FAIL",
            "BLOCKED",
            "NOT_RUN",
            "PARTIAL",
            "INCONCLUSIVE",
        }:
            raise HarnessError(f"Unsupported verification outcome: {outcome}")
        parsed.append({"command": command, "outcome": outcome})
    return parsed


def verification_state(
    checks: list[dict[str, str]], required_commands: list[str]
) -> str:
    outcomes = {item.get("command"): item.get("outcome") for item in checks}
    if any(item.get("outcome") == "FAIL" for item in checks):
        return "FAIL"
    if any(
        item.get("outcome")
        in {"BLOCKED", "NOT_RUN", "PARTIAL", "INCONCLUSIVE"}
        for item in checks
    ):
        return "INCOMPLETE"
    if any(outcomes.get(command) != "PASS" for command in required_commands):
        return "INCOMPLETE"
    return "PASS"


def create_handoff(
    root: Path,
    *,
    claim_id: str,
    from_agent: str,
    to_agent: str,
    task_id: str,
    summary: str,
    changed_files: list[str],
    verifications: list[str],
    next_action: str,
    decisions: list[str] | None = None,
    risks: list[str] | None = None,
    unverified: list[str] | None = None,
) -> dict[str, Any]:
    from_agent = normalize_agent_id(from_agent)
    to_agent = normalize_agent_id(to_agent)
    claim, _path = get_claim(root, claim_id)
    if claim.get("status") != "ACTIVE":
        raise HarnessError(f"Claim {claim_id} is not active")
    if claim.get("agent") != from_agent or claim.get("task_id") != task_id:
        raise HarnessError("Handoff agent or task does not match the active claim")
    ensure_claim_current(root, claim)
    normalized_changes = validate_changed_files(root, claim, changed_files)
    verification_records = _parse_verification(verifications)
    if not verification_records:
        raise HarnessError("Handoff requires at least one exact verification command and outcome")
    if not next_action.strip():
        raise HarnessError("Handoff requires one concrete next action")

    directory = root / HARNESS_DIR / "handoffs"
    handoff_id = allocate_record_id(root, directory, "HOF-")
    value = {
        "schema": "harness.handoff/v1",
        "id": handoff_id,
        "kind": "handoff",
        "status": "READY",
        "task_id": task_id,
        "claim_id": claim_id,
        "task_fingerprint": claim.get("task_fingerprint"),
        "plan_id": claim.get("plan_id"),
        "plan_fingerprint": claim.get("plan_fingerprint"),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "base_commit": claim.get("base_commit"),
        "head_commit": git_head(root),
        "owned_paths": claim.get("paths", []),
        "changed_files": normalized_changes,
        "changed_file_states": {
            value: _path_state(root, value) for value in normalized_changes
        },
        "summary": summary,
        "verification": verification_records,
        "verification_state": verification_state(
            verification_records, claim.get("verification", [])
        ),
        "unverified": unverified or [],
        "decisions": decisions or [],
        "risks": risks or [],
        "next_action": next_action,
        "created_at": utc_now(),
    }
    atomic_write_json(directory / f"{handoff_id}.json", value)
    atomic_write_json(
        mailbox_directory(root, "inbox", to_agent) / f"{handoff_id}.json", value
    )
    render_handoff(root)
    release_claim(
        root,
        claim_id=claim_id,
        agent=from_agent,
        reason=f"handoff {handoff_id}",
        validate_clean=False,
    )
    record_event(root, "HANDOFF_CREATED", {"handoff_id": handoff_id, "task_id": task_id})
    return value


def render_handoff(
    root: Path, handoff: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Render only the newest canonical HOF record under the shared mutex."""
    with _runtime_mutex(root):
        directory = root / HARNESS_DIR / "handoffs"
        candidates: list[tuple[int, Path]] = []
        for path in directory.glob("HOF-*.json"):
            match = re.fullmatch(r"HOF-(\d+)", path.stem)
            if match:
                candidates.append((int(match.group(1)), path))
        if not candidates:
            raise HarnessError("No canonical handoff record exists to render")
        _sequence, latest_path = max(candidates, key=lambda item: item[0])
        canonical_handoff = load_json(latest_path)
        if (
            canonical_handoff.get("schema") != "harness.handoff/v1"
            or canonical_handoff.get("kind") != "handoff"
            or canonical_handoff.get("id") != latest_path.stem
        ):
            raise HarnessError(f"Latest canonical handoff is malformed: {latest_path.name}")
        _render_handoff_view(root, canonical_handoff)
    return canonical_handoff


def _render_handoff_view(root: Path, handoff: dict[str, Any]) -> None:
    def bullets(values: list[Any]) -> str:
        return "\n".join(f"- {value}" for value in values) if values else "- None recorded"

    checks = [f"`{item['command']}` — {item['outcome']}" for item in handoff["verification"]]
    content = f"""# Current Handoff

Canonical record: `.harness/handoffs/{handoff['id']}.json`

## Ownership

- Task: `{handoff['task_id']}`
- From: `{handoff['from_agent']}`
- To: `{handoff['to_agent']}`
- Base commit: `{handoff.get('base_commit') or 'UNBORN'}`
- Head commit: `{handoff.get('head_commit') or 'UNBORN'}`

## Summary

{handoff['summary']}

## Changed files

{bullets(handoff['changed_files'])}

## Verification

{bullets(checks)}

## Unverified

{bullets(handoff['unverified'])}

## Decisions

{bullets(handoff['decisions'])}

## Risks

{bullets(handoff['risks'])}

## Next action

{handoff['next_action']}

This Markdown file is a view. The JSON record and referenced evidence are canonical.
"""
    atomic_write_text(root / "HANDOFF.md", content)
