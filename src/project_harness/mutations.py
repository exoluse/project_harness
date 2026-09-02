from __future__ import annotations

import base64
import shutil
import uuid
from pathlib import Path
from typing import Any, Callable

from .approvals import find_current_approval
from .collaboration import ensure_claim_current, get_claim, runtime_root
from .constants import HARNESS_DIR
from .core import (
    HarnessError,
    allocate_record_id,
    atomic_write_json,
    is_path_within,
    load_json,
    normalize_agent_id,
    normalize_claim_path,
    record_path,
    sha256_path,
    subject_fingerprint,
    utc_now,
    filesystem_mutex,
)
from .evaluation import EvaluationContext
from .gates import (
    _latest_task_result_assessment,
    feature_completion_gate,
    plan_preflight_gate,
    project_completion_gate,
    task_start_gate,
)
from .schema_validation import SCHEMA_FILES, SchemaSet


MutationValidator = Callable[[], None]


class AtomicMutationService:
    """Apply a multi-file canonical mutation with rollback and crash recovery.

    Filesystems do not provide a portable multi-file rename transaction.  This
    service therefore journals every original byte sequence before replacing
    targets.  A caught failure rolls back immediately; the next mutation also
    rolls back any PREPARED transaction left by process or host interruption.
    """

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.runtime = runtime_root(self.root) / "mutations"
        self.lock = self.runtime / "record.lock"
        self.transactions = self.runtime / "transactions"

    def _transaction_directories(self) -> list[Path]:
        if not self.transactions.is_dir():
            return []
        return sorted(path for path in self.transactions.glob("TXN-*") if path.is_dir())

    def _restore(self, directory: Path, manifest: dict[str, Any]) -> None:
        for index, entry in enumerate(manifest.get("targets", [])):
            target = self.root / entry["path"]
            if entry.get("existed"):
                backup = directory / "backups" / f"{index:04d}.bin"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(backup.read_bytes())
            elif target.exists():
                target.unlink()
        manifest["state"] = "ROLLED_BACK"
        manifest["rolled_back_at"] = utc_now()
        atomic_write_json(directory / "manifest.json", manifest)

    def recover_incomplete(self) -> list[str]:
        recovered: list[str] = []
        for directory in self._transaction_directories():
            manifest_path = directory / "manifest.json"
            manifest = load_json(manifest_path)
            if manifest.get("state") == "PREPARED":
                self._restore(directory, manifest)
                recovered.append(str(manifest.get("id")))
            if manifest.get("state") in {"COMMITTED", "ROLLED_BACK"}:
                shutil.rmtree(directory, ignore_errors=True)
        return recovered

    def apply(
        self,
        *,
        writes: dict[str, dict[str, Any]],
        event_type: str,
        event_payload: dict[str, Any],
        validate_before_commit: MutationValidator | None = None,
        fail_after_writes: int | None = None,
    ) -> dict[str, Any]:
        if not writes:
            raise HarnessError("Atomic mutation requires at least one target")
        normalized_writes: dict[str, dict[str, Any]] = {}
        for value, record in writes.items():
            normalized = normalize_claim_path(self.root, value)
            if normalized == "**":
                raise HarnessError("Atomic mutation target must be one file")
            normalized_writes[normalized] = record

        with filesystem_mutex(
            self.lock,
            timeout_seconds=30,
            recovery_directory=self.runtime / "lock-recoveries",
            timeout_message="Timed out waiting for the canonical mutation lock",
        ):
            recovered = self.recover_incomplete()
            transaction_id = f"TXN-{uuid.uuid4().hex}"
            directory = self.transactions / transaction_id
            backups = directory / "backups"
            backups.mkdir(parents=True, exist_ok=False)

            events = self.root / HARNESS_DIR / "events"
            event_id = allocate_record_id(self.root, events, "EVT-")
            event_relative = f"{HARNESS_DIR}/events/{event_id}.json"
            normalized_writes[event_relative] = {
                "schema": "harness.event/v1",
                "id": event_id,
                "kind": "event",
                "event_type": event_type,
                "occurred_at": utc_now(),
                "payload": event_payload,
            }

            targets: list[dict[str, Any]] = []
            for index, relative in enumerate(sorted(normalized_writes)):
                target = self.root / relative
                existed = target.is_file()
                if existed:
                    (backups / f"{index:04d}.bin").write_bytes(target.read_bytes())
                targets.append({"path": relative, "existed": existed})
            manifest = {
                "schema": "harness.atomic-mutation/v1",
                "id": transaction_id,
                "kind": "atomic_mutation",
                "state": "PREPARED",
                "event_id": event_id,
                "targets": targets,
                "prepared_at": utc_now(),
            }
            atomic_write_json(directory / "manifest.json", manifest)

            try:
                if validate_before_commit is not None:
                    validate_before_commit()
                applied = 0
                for relative in sorted(normalized_writes):
                    atomic_write_json(self.root / relative, normalized_writes[relative])
                    applied += 1
                    if fail_after_writes is not None and applied >= fail_after_writes:
                        raise OSError("injected atomic mutation failure")
            except Exception:
                self._restore(directory, manifest)
                shutil.rmtree(directory, ignore_errors=True)
                raise

            manifest["state"] = "COMMITTED"
            manifest["committed_at"] = utc_now()
            atomic_write_json(directory / "manifest.json", manifest)
            shutil.rmtree(directory, ignore_errors=True)
            return {
                "transaction_id": transaction_id,
                "event_id": event_id,
                "changed_files": sorted(normalized_writes),
                "recovered_transactions": recovered,
            }


def _authorize_claim_targets(
    root: Path,
    *,
    claim_id: str,
    agent: str,
    targets: list[str],
) -> dict[str, Any]:
    normalized_agent = normalize_agent_id(agent)
    claim, _path = get_claim(root, claim_id)
    if claim.get("status") != "ACTIVE" or claim.get("agent") != normalized_agent:
        raise HarnessError("Canonical mutation requires the agent's active claim")
    ensure_claim_current(root, claim)
    normalized_targets = [normalize_claim_path(root, value) for value in targets]
    outside = [
        value
        for value in normalized_targets
        if not is_path_within(value, claim.get("paths", []))
    ]
    if outside:
        raise HarnessError(
            "Canonical mutation targets exceed the active claim: "
            + ", ".join(sorted(outside))
        )
    return claim


def _validate_records(root: Path, values: list[tuple[str, dict[str, Any]]]) -> None:
    schemas = SchemaSet(root / "schemas")
    errors: list[str] = []
    for kind, value in values:
        errors.extend(schemas.validate(value, SCHEMA_FILES[kind]))
    if errors:
        raise HarnessError("Mutation would write invalid records: " + "; ".join(errors))


def record_evidence(
    root: Path,
    *,
    claim_id: str,
    agent: str,
    claim_text: str,
    supports: list[str],
    profile: str,
    method: str,
    environment: str,
    expected: str,
    actual: str,
    result: str,
    ambiguity_level: str,
    ambiguity_reasons: list[str],
    binding_paths: list[str],
    limitations: list[str],
) -> dict[str, Any]:
    root = root.resolve()
    if not supports:
        raise HarnessError("Evidence requires at least one supported criterion")
    context = EvaluationContext.load(root)
    evidence_directory = root / HARNESS_DIR / "evidence"
    evidence_id = allocate_record_id(root, evidence_directory, "EVD-")
    evidence_relative = f"{HARNESS_DIR}/evidence/{evidence_id}.json"

    writes: dict[str, dict[str, Any]] = {}
    criterion_fingerprints: dict[str, str] = {}
    closure_fingerprints: dict[str, str] = {}
    owner_paths: set[str] = set()
    for supported_id in supports:
        supported = context.records.get(supported_id)
        if supported is None:
            raise HarnessError(f"Evidence supports missing criterion {supported_id}")
        kind = supported.get("kind")
        if kind == "completion_criterion":
            feature_id = str(supported.get("feature_id"))
            feature_path = record_path(root, "feature", feature_id)
            relative = feature_path.relative_to(root).as_posix()
            feature = writes.get(relative) or load_json(feature_path)
            criterion = next(
                item
                for item in feature.get("completion_criteria", [])
                if item.get("id") == supported_id
            )
            refs = criterion.setdefault("evidence_refs", [])
            if evidence_id not in refs:
                refs.append(evidence_id)
            writes[relative] = feature
            owner_paths.add(relative)
            criterion_fingerprints[supported_id] = subject_fingerprint(supported)
        elif kind == "closure_criterion":
            project_path = root / HARNESS_DIR / "project.json"
            relative = project_path.relative_to(root).as_posix()
            project = writes.get(relative) or load_json(project_path)
            criterion = next(
                item
                for item in project.get("closure_contract", [])
                if item.get("id") == supported_id
            )
            refs = criterion.setdefault("evidence_refs", [])
            if evidence_id not in refs:
                refs.append(evidence_id)
            writes[relative] = project
            owner_paths.add(relative)
            closure_fingerprints[supported_id] = subject_fingerprint(supported)
        else:
            raise HarnessError(
                f"Evidence support {supported_id} is not a completion or closure criterion"
            )

    bindings = []
    for value in binding_paths:
        normalized = normalize_claim_path(root, value)
        path = root / normalized
        if not path.exists():
            raise HarnessError(f"Evidence binding is missing: {normalized}")
        bindings.append({"path": normalized, "sha256": sha256_path(path)})

    evidence = {
        "schema": "harness.evidence/v1",
        "id": evidence_id,
        "kind": "evidence",
        "observed_at": utc_now(),
        "claim": claim_text,
        "supports": supports,
        "profile": profile,
        "method": method,
        "environment": environment,
        "subject": {
            "criterion_fingerprints": criterion_fingerprints,
            "closure_criterion_fingerprints": closure_fingerprints,
        },
        "expected": expected,
        "actual": actual,
        "result": result,
        "ambiguity": {
            "level": ambiguity_level,
            "reasons": ambiguity_reasons,
        },
        "bindings": bindings,
        "limitations": limitations,
    }
    writes[evidence_relative] = evidence
    _authorize_claim_targets(
        root,
        claim_id=claim_id,
        agent=agent,
        targets=[evidence_relative, *owner_paths],
    )
    _validate_records(
        root,
        [("evidence", evidence)]
        + [
            ("project" if relative.endswith("project.json") else "feature", value)
            for relative, value in writes.items()
            if relative != evidence_relative
        ],
    )
    transaction = AtomicMutationService(root).apply(
        writes=writes,
        event_type="EVIDENCE_RECORDED",
        event_payload={
            "evidence_id": evidence_id,
            "claim_id": claim_id,
            "agent": normalize_agent_id(agent),
            "supports": supports,
            "result": result,
        },
    )
    return {"evidence": evidence, "transaction": transaction}


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
    claim_id: str,
    agent: str,
    kind: str,
    record_id: str,
    target_status: str,
    reason: str,
    rework: bool = False,
) -> dict[str, Any]:
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
    _authorize_claim_targets(
        root,
        claim_id=claim_id,
        agent=agent,
        targets=[relative],
    )
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
    if kind == "work_item" and target_status in {"REVIEWED", "INTEGRATED", "DONE", "CLOSED"}:
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
                "Work item lacks a current independently reviewed PASS: "
                + "; ".join(reasons)
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
    _validate_records(root, [(kind, record)])
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
    claim_id: str,
    agent: str,
    target_state: str,
    reason: str,
    resume: bool = False,
) -> dict[str, Any]:
    state_path = root / HARNESS_DIR / "state.json"
    relative = state_path.relative_to(root).as_posix()
    _authorize_claim_targets(
        root,
        claim_id=claim_id,
        agent=agent,
        targets=[relative],
    )
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
        if not isinstance(active_plan, str):
            raise HarnessError("Project cannot enter BUILDING without an active plan")
        gate = plan_preflight_gate(
            root,
            active_plan,
            require_approval=True,
            context=context,
        )
        if not gate.passed:
            raise HarnessError("Project cannot enter BUILDING: " + "; ".join(gate.blockers))
    if target_state == "CUSTOMER_ACCEPTANCE":
        project = load_json(root / HARNESS_DIR / "project.json")
        feature_blockers: list[str] = []
        for feature_id in project.get("required_features", []):
            gate = feature_completion_gate(root, feature_id, context=context)
            feature_blockers.extend(
                f"{feature_id}: {value}" for value in gate.blockers
            )
        if feature_blockers:
            raise HarnessError(
                "Project cannot enter CUSTOMER_ACCEPTANCE: "
                + "; ".join(feature_blockers)
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
    _validate_records(root, [("state", state)])
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
