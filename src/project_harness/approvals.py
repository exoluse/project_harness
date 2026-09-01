from __future__ import annotations

import base64
import binascii
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

from .constants import APPROVAL_DECISIONS, APPROVED_DECISIONS, HARNESS_DIR
from .core import (
    HarnessError,
    allocate_record_id,
    atomic_write_json,
    load_json,
    normalize_claim_path,
    parse_utc,
    record_event,
    sha256_bytes,
    sha256_file,
    subject_fingerprint_for_path,
    utc_after,
    utc_now,
)


APPROVAL_SUBJECT_KINDS = {
    "PLAN": "plan",
    "CUSTOMER_ACCEPTANCE": "feature",
    "PROJECT_CLOSURE": "project",
    "CHANGE": "change",
    "PRODUCTION_DEPLOYMENT": "project",
    "PRODUCTION_DATA_CHANGE": "change",
    "EXCEPTION": "change",
}

SIGNED_REQUEST_FIELDS = (
    "project_id",
    "authority_id",
    "authority_sequence",
    "decision_id",
    "decision_at",
    "approval_type",
    "decision",
    "authority_role",
    "approved_by",
    "basis",
    "subject_id",
    "subject_path",
    "subject_fingerprint",
    "conditions",
    "condition_refs",
    "authorized_actions",
    "excluded_actions",
)


def authority_config_path(root: Path) -> Path:
    """Return the non-overridable machine trust configuration path.

    Environment variables and repository policy are deliberately not consulted:
    both are writable by an ordinary coding-agent process.  Deployments that need
    a different location must wrap this verifier in a protected approval broker.
    """

    project = load_json(root / HARNESS_DIR / "project.json")
    project_id = str(project.get("id", ""))
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", project_id):
        raise HarnessError("Project ID is unsafe for the external authority path")
    if os.name == "nt":
        base = Path("C:/ProgramData/ProjectHarness/authorities")
    else:
        base = Path("/etc/project-harness/authorities")
    return base / f"{project_id}.json"


def _outside_repository(root: Path, path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return resolved
    raise HarnessError(f"{label} must be outside the project repository")


def _load_authority_config(root: Path) -> dict[str, Any]:
    config_path = _outside_repository(root, authority_config_path(root), "authority config")
    config = load_json(config_path)
    project = load_json(root / HARNESS_DIR / "project.json")
    required = {
        "schema": "harness.authority/v1",
        "project_id": project.get("id"),
        "protection": "OS_ACL_OR_EXTERNAL_BROKER",
    }
    for field, expected in required.items():
        if config.get(field) != expected:
            raise HarnessError(
                f"External authority config {field} must be {expected!r}"
            )
    authority_id = config.get("authority_id")
    if not isinstance(authority_id, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", authority_id
    ):
        raise HarnessError("External authority config has an invalid authority_id")
    configured_root = config.get("repository_root")
    if not isinstance(configured_root, str) or Path(configured_root).resolve() != root.resolve():
        raise HarnessError("External authority config is bound to a different repository")
    namespace = config.get("signature_namespace")
    if not isinstance(namespace, str) or not namespace.strip():
        raise HarnessError("External authority config lacks signature_namespace")
    approval_types = config.get("approval_types")
    if not isinstance(approval_types, list) or any(
        not isinstance(value, str) for value in approval_types
    ):
        raise HarnessError("External authority config approval_types must be a string list")

    signers_value = config.get("allowed_signers_path")
    ledger_value = config.get("decision_ledger_path")
    if not isinstance(signers_value, str) or not isinstance(ledger_value, str):
        raise HarnessError("External authority config lacks signer or ledger paths")
    signers = _outside_repository(root, Path(signers_value), "allowed-signers file")
    ledger = _outside_repository(root, Path(ledger_value), "decision ledger")
    if not signers.is_file():
        raise HarnessError("External allowed-signers file is missing")
    expected_digest = config.get("allowed_signers_sha256")
    if not isinstance(expected_digest, str) or sha256_file(signers) != expected_digest:
        raise HarnessError("External allowed-signers digest is missing or mismatched")
    if not ledger.is_dir():
        raise HarnessError("External decision ledger directory is missing")
    return {
        **config,
        "_config_path": str(config_path),
        "_allowed_signers_path": str(signers),
        "_decision_ledger_path": str(ledger),
    }


def authority_status(root: Path) -> tuple[str, str]:
    try:
        config = _load_authority_config(root)
    except HarnessError as exc:
        return "UNAVAILABLE", str(exc)
    return "READY", (
        f"protected authority {config['authority_id']} at {config['_config_path']}"
    )


def _verify_ssh_signature(
    config: dict[str, Any], raw_request: bytes, request: dict[str, Any], signature: str
) -> tuple[bool, str]:
    executable = shutil.which("ssh-keygen")
    if not executable:
        return False, "ssh-keygen is unavailable for approval verification"
    with tempfile.TemporaryDirectory(prefix="harness-approval-") as temp:
        signature_path = Path(temp) / "request.sig"
        signature_path.write_text(signature, encoding="utf-8")
        process = subprocess.run(
            [
                executable,
                "-Y",
                "verify",
                "-f",
                str(config["_allowed_signers_path"]),
                "-I",
                str(request.get("approved_by", "")),
                "-n",
                str(config["signature_namespace"]),
                "-s",
                str(signature_path),
            ],
            input=raw_request,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if process.returncode != 0:
        return False, "SSH approval signature verification failed"
    return True, "SSH approval signature is valid"


def _validated_ledger_entries(
    root: Path, config: dict[str, Any]
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    sequences: dict[int, str] = {}
    decision_ids: dict[str, str] = {}
    ledger = Path(config["_decision_ledger_path"])
    for request_path in sorted(ledger.glob("*.request.json")):
        try:
            raw = request_path.read_bytes()
            request = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HarnessError(f"Invalid authority ledger request {request_path}: {exc}") from exc
        if not isinstance(request, dict) or request.get("schema") != "harness.approval-request/v1":
            raise HarnessError(f"Invalid authority ledger request schema: {request_path}")
        if request.get("project_id") != config.get("project_id"):
            raise HarnessError(f"Authority ledger request has wrong project: {request_path}")
        if request.get("authority_id") != config.get("authority_id"):
            raise HarnessError(f"Authority ledger request has wrong authority: {request_path}")
        sequence = request.get("authority_sequence")
        decision_id = request.get("decision_id")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence <= 0:
            raise HarnessError(f"Authority ledger request has invalid sequence: {request_path}")
        if not isinstance(decision_id, str) or not decision_id.strip():
            raise HarnessError(f"Authority ledger request has invalid decision_id: {request_path}")
        digest = sha256_bytes(raw)
        if sequence in sequences and sequences[sequence] != digest:
            raise HarnessError(f"Authority ledger sequence fork detected at {sequence}")
        if decision_id in decision_ids and decision_ids[decision_id] != digest:
            raise HarnessError(f"Authority ledger decision_id fork detected: {decision_id}")
        signature_path = Path(str(request_path) + ".sig")
        try:
            signature = signature_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise HarnessError(f"Authority ledger signature is missing: {signature_path}") from exc
        valid, reason = _verify_ssh_signature(config, raw, request, signature)
        if not valid:
            raise HarnessError(f"Invalid authority ledger signature for {request_path}: {reason}")
        sequences[sequence] = digest
        decision_ids[decision_id] = digest
        entries.append(
            {
                "request": request,
                "request_sha256": digest,
                "signature": signature,
                "path": str(request_path),
            }
        )
    return entries


def _attestation_expected(
    *,
    project_id: str,
    authority_id: str,
    authority_sequence: int,
    decision_id: str,
    decision_at: str,
    approval_type: str,
    decision: str,
    authority_role: str,
    approver: str,
    basis: str,
    subject: dict[str, Any],
    relative: str,
    fingerprint: str,
    conditions: list[str] | None,
    condition_refs: list[str] | None,
    authorized_actions: list[str] | None,
    excluded_actions: list[str] | None,
) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "authority_id": authority_id,
        "authority_sequence": authority_sequence,
        "decision_id": decision_id,
        "decision_at": decision_at,
        "approval_type": approval_type,
        "decision": decision,
        "authority_role": authority_role,
        "approved_by": approver,
        "basis": basis,
        "subject_id": subject.get("id"),
        "subject_path": relative,
        "subject_fingerprint": fingerprint,
        "conditions": conditions or [],
        "condition_refs": condition_refs or [],
        "authorized_actions": authorized_actions or [],
        "excluded_actions": excluded_actions or [],
    }


def _verify_attestation(
    root: Path,
    attestation: dict[str, Any] | None,
    expected: dict[str, Any],
    *,
    enforce_request_expiry: bool,
    require_current_ledger_decision: bool = True,
) -> tuple[bool, str]:
    if not isinstance(attestation, dict) or attestation.get("mode") != "SSH_ALLOWED_SIGNERS":
        return False, "SSH approval attestation is required"
    encoded_request = attestation.get("request_base64")
    signature = attestation.get("signature")
    if not isinstance(encoded_request, str) or not isinstance(signature, str):
        return False, "approval attestation lacks request or signature"
    try:
        raw_request = base64.b64decode(encoded_request, validate=True)
        request = json.loads(raw_request.decode("utf-8"))
    except (ValueError, binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return False, f"invalid signed approval request: {exc}"
    if not isinstance(request, dict) or request.get("schema") != "harness.approval-request/v1":
        return False, "signed approval request schema is invalid"
    if attestation.get("request_sha256") != sha256_bytes(raw_request):
        return False, "signed approval request hash does not match"
    for field in SIGNED_REQUEST_FIELDS:
        if request.get(field) != expected.get(field):
            return False, f"signed approval field does not match: {field}"
    sequence = request.get("authority_sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence <= 0:
        return False, "signed approval authority_sequence is invalid"
    try:
        parse_utc(str(request.get("decision_at", "")))
    except (TypeError, ValueError):
        return False, "signed approval decision_at is invalid"
    if enforce_request_expiry:
        try:
            from datetime import UTC, datetime

            if parse_utc(str(request.get("expires_at", ""))) <= datetime.now(UTC):
                return False, "signed approval request has expired"
        except (TypeError, ValueError):
            return False, "signed approval request expiry is invalid"
    try:
        config = _load_authority_config(root)
        if request.get("approval_type") not in config.get("approval_types", []):
            return False, "approval type is not allowed by the external authority"
        valid, reason = _verify_ssh_signature(config, raw_request, request, signature)
        if not valid:
            return False, reason
        entries = _validated_ledger_entries(root, config)
    except HarnessError as exc:
        return False, str(exc)
    request_hash = sha256_bytes(raw_request)
    matching = [
        entry
        for entry in entries
        if entry["request_sha256"] == request_hash and entry["signature"] == signature
    ]
    if not matching:
        return False, "signed approval is not present in the protected authority ledger"
    same_subject = [
        entry
        for entry in entries
        if entry["request"].get("approval_type") == request.get("approval_type")
        and entry["request"].get("subject_id") == request.get("subject_id")
    ]
    if not same_subject:
        return False, "protected authority ledger has no decision for the subject"
    latest = max(
        same_subject,
        key=lambda entry: int(entry["request"].get("authority_sequence", 0)),
    )
    if require_current_ledger_decision and latest["request_sha256"] != request_hash:
        return False, (
            "signed approval is superseded by protected authority sequence "
            f"{latest['request'].get('authority_sequence')}"
        )
    return True, "SSH signature and protected authority ledger entry are valid"


def _canonical_subject_path(root: Path, subject: dict[str, Any]) -> str | None:
    kind = subject.get("kind")
    subject_id = subject.get("id")
    if kind == "project":
        return f"{HARNESS_DIR}/project.json"
    if isinstance(kind, str) and isinstance(subject_id, str):
        from .constants import RECORD_DIRECTORIES

        if kind in RECORD_DIRECTORIES:
            directory, _prefix = RECORD_DIRECTORIES[kind]
            return f"{HARNESS_DIR}/{directory}/{subject_id}.json"
    return None


def record_approval(
    root: Path,
    *,
    approval_type: str,
    subject_path: str,
    decision: str,
    approver: str,
    authority_role: str,
    basis: str,
    conditions: list[str] | None = None,
    condition_refs: list[str] | None = None,
    authorized_actions: list[str] | None = None,
    excluded_actions: list[str] | None = None,
    attestation: dict[str, Any] | None = None,
    authority_id: str | None = None,
    authority_sequence: int | None = None,
    decision_id: str | None = None,
    decision_at: str | None = None,
) -> dict[str, Any]:
    if authority_role != "HUMAN_PROJECT_OWNER":
        raise HarnessError("Only HUMAN_PROJECT_OWNER decisions can be recorded as approvals")
    if decision not in APPROVAL_DECISIONS:
        raise HarnessError(f"Unsupported approval decision: {decision}")
    if approval_type not in APPROVAL_SUBJECT_KINDS:
        raise HarnessError(f"Unsupported approval type: {approval_type}")
    if not approver.strip() or not basis.strip():
        raise HarnessError("Approval requires an approver and an explicit decision basis")
    if decision == "APPROVED_WITH_CONDITIONS" and (
        not conditions or not condition_refs
    ):
        raise HarnessError(
            "APPROVED_WITH_CONDITIONS requires human-readable conditions and open-item condition_refs"
        )
    relative = normalize_claim_path(root, subject_path)
    path = root / relative
    if not path.is_file():
        raise HarnessError(f"Approval subject does not exist: {subject_path}")
    subject = load_json(path)
    expected_kind = APPROVAL_SUBJECT_KINDS.get(approval_type)
    if expected_kind and subject.get("kind") != expected_kind:
        raise HarnessError(
            f"{approval_type} approval requires a {expected_kind} subject, "
            f"not {subject.get('kind')}"
        )
    canonical_path = _canonical_subject_path(root, subject)
    if canonical_path != relative:
        raise HarnessError(
            f"Approval subject must use its canonical path {canonical_path}, not {relative}"
        )
    if decision in APPROVED_DECISIONS:
        gate = None
        if approval_type == "PLAN":
            from .gates import plan_preflight_gate

            gate = plan_preflight_gate(root, str(subject.get("id")), require_approval=False)
        elif approval_type == "CUSTOMER_ACCEPTANCE":
            from .gates import feature_completion_gate

            gate = feature_completion_gate(
                root, str(subject.get("id")), require_customer_approval=False
            )
        elif approval_type == "PROJECT_CLOSURE":
            from .gates import project_completion_gate

            gate = project_completion_gate(root, require_approval=False)
        if gate is not None and not gate.passed:
            raise HarnessError(
                f"Cannot record {approval_type} approval before its preflight passes: "
                + "; ".join(gate.blockers)
            )
    fingerprint = subject_fingerprint_for_path(path)
    project_id = str(load_json(root / HARNESS_DIR / "project.json").get("id", ""))
    existing_sequences = []
    for existing_path in (root / HARNESS_DIR / "approvals").glob("APR-*.json"):
        existing_sequence = load_json(existing_path).get("authority_sequence")
        if isinstance(existing_sequence, int) and not isinstance(existing_sequence, bool):
            existing_sequences.append(existing_sequence)
    authority_id = authority_id or "TEST-MOCK-AUTHORITY"
    authority_sequence = authority_sequence or (max(existing_sequences, default=0) + 1)
    decision_id = decision_id or f"DEC-{uuid.uuid4()}"
    decision_at = decision_at or utc_now()
    expected_attestation = _attestation_expected(
        project_id=project_id,
        authority_id=authority_id,
        authority_sequence=authority_sequence,
        decision_id=decision_id,
        decision_at=decision_at,
        approval_type=approval_type,
        decision=decision,
        authority_role=authority_role,
        approver=approver,
        basis=basis,
        subject=subject,
        relative=relative,
        fingerprint=fingerprint,
        conditions=conditions,
        condition_refs=condition_refs,
        authorized_actions=authorized_actions,
        excluded_actions=excluded_actions,
    )
    attestation_valid, attestation_reason = _verify_attestation(
        root,
        attestation,
        expected_attestation,
        enforce_request_expiry=True,
    )
    if not attestation_valid:
        raise HarnessError(f"Approval identity verification failed: {attestation_reason}")

    directory = root / HARNESS_DIR / "approvals"
    approval_id = allocate_record_id(root, directory, "APR-")
    snapshot_paths = [relative]
    for dependency in subject.get("approval_dependencies", []):
        snapshot_paths.append(normalize_claim_path(root, dependency))
    snapshot_manifest: list[dict[str, str]] = []
    for snapshot_relative in sorted(set(snapshot_paths), key=str.casefold):
        source_path = root / snapshot_relative
        if not source_path.is_file():
            raise HarnessError(f"Approval snapshot input does not exist: {snapshot_relative}")
        snapshot_path = (
            root / HARNESS_DIR / "baselines" / approval_id / snapshot_relative
        )
        atomic_write_json(snapshot_path, load_json(source_path))
        snapshot_manifest.append(
            {
                "path": snapshot_relative,
                "snapshot_path": snapshot_path.relative_to(root).as_posix(),
                "sha256": sha256_file(snapshot_path),
            }
        )
    value = {
        "schema": "harness.approval/v1",
        "id": approval_id,
        "kind": "approval",
        "approval_type": approval_type,
        "decision": decision,
        "project_id": project_id,
        "authority_id": authority_id,
        "authority_sequence": authority_sequence,
        "decision_id": decision_id,
        "decision_at": decision_at,
        "authority_role": authority_role,
        "approved_by": approver,
        "basis": basis,
        "subject_id": subject.get("id"),
        "subject_path": relative,
        "subject_fingerprint": fingerprint,
        "snapshot_manifest": snapshot_manifest,
        "conditions": conditions or [],
        "condition_refs": condition_refs or [],
        "authorized_actions": authorized_actions or [],
        "excluded_actions": excluded_actions or [],
        "attestation": attestation,
        "recorded_at": utc_now(),
    }
    atomic_write_json(directory / f"{approval_id}.json", value)
    record_event(
        root,
        "HUMAN_DECISION_RECORDED",
        {
            "approval_id": approval_id,
            "approval_type": approval_type,
            "subject_id": subject.get("id"),
            "decision": decision,
        },
    )
    return value


def prepare_approval_request(
    root: Path,
    *,
    output_path: str,
    approval_type: str,
    subject_path: str,
    decision: str,
    approver: str,
    authority_role: str,
    basis: str,
    conditions: list[str] | None = None,
    condition_refs: list[str] | None = None,
    authorized_actions: list[str] | None = None,
    excluded_actions: list[str] | None = None,
    ttl_minutes: int = 60,
) -> dict[str, Any]:
    if ttl_minutes <= 0 or ttl_minutes > 1440:
        raise HarnessError("Approval request TTL must be between 1 and 1440 minutes")
    if authority_role != "HUMAN_PROJECT_OWNER":
        raise HarnessError("Only HUMAN_PROJECT_OWNER decisions can be prepared")
    if approval_type not in APPROVAL_SUBJECT_KINDS:
        raise HarnessError(f"Unsupported approval type: {approval_type}")
    if decision not in APPROVAL_DECISIONS:
        raise HarnessError(f"Unsupported approval decision: {decision}")
    if not approver.strip() or not basis.strip():
        raise HarnessError("Approval request requires approver and basis")
    if decision == "APPROVED_WITH_CONDITIONS" and (
        not conditions or not condition_refs
    ):
        raise HarnessError(
            "APPROVED_WITH_CONDITIONS requires conditions and open-item condition_refs"
        )
    relative = normalize_claim_path(root, subject_path)
    path = root / relative
    subject = load_json(path)
    expected_kind = APPROVAL_SUBJECT_KINDS[approval_type]
    if subject.get("kind") != expected_kind:
        raise HarnessError(f"{approval_type} requires a {expected_kind} subject")
    if _canonical_subject_path(root, subject) != relative:
        raise HarnessError("Approval request subject is not at its canonical path")
    if decision in APPROVED_DECISIONS:
        gate = None
        if approval_type == "PLAN":
            from .gates import plan_preflight_gate

            gate = plan_preflight_gate(root, str(subject.get("id")), require_approval=False)
        elif approval_type == "CUSTOMER_ACCEPTANCE":
            from .gates import feature_completion_gate

            gate = feature_completion_gate(
                root, str(subject.get("id")), require_customer_approval=False
            )
        elif approval_type == "PROJECT_CLOSURE":
            from .gates import project_completion_gate

            gate = project_completion_gate(root, require_approval=False)
        if gate is not None and not gate.passed:
            raise HarnessError("Approval preflight blocked: " + "; ".join(gate.blockers))
    fingerprint = subject_fingerprint_for_path(path)
    config = _load_authority_config(root)
    if approval_type not in config.get("approval_types", []):
        raise HarnessError(
            f"Approval type {approval_type} is not allowed by the external authority"
        )
    entries = _validated_ledger_entries(root, config)
    authority_sequence = max(
        (
            int(entry["request"].get("authority_sequence", 0))
            for entry in entries
        ),
        default=0,
    ) + 1
    project_id = str(load_json(root / HARNESS_DIR / "project.json").get("id", ""))
    request = {
        "schema": "harness.approval-request/v1",
        **_attestation_expected(
            project_id=project_id,
            authority_id=str(config["authority_id"]),
            authority_sequence=authority_sequence,
            decision_id=f"DEC-{uuid.uuid4()}",
            decision_at=utc_now(),
            approval_type=approval_type,
            decision=decision,
            authority_role=authority_role,
            approver=approver,
            basis=basis,
            subject=subject,
            relative=relative,
            fingerprint=fingerprint,
            conditions=conditions,
            condition_refs=condition_refs,
            authorized_actions=authorized_actions,
            excluded_actions=excluded_actions,
        ),
        "prepared_at": utc_now(),
        "expires_at": utc_after(ttl_minutes),
    }
    normalized_output = normalize_claim_path(root, output_path)
    target = root / normalized_output
    if target.exists():
        raise HarnessError(f"Approval request already exists: {output_path}")
    atomic_write_json(target, request)
    return request


def record_signed_approval(
    root: Path, *, request_path: str, signature_path: str
) -> dict[str, Any]:
    normalized_request = normalize_claim_path(root, request_path)
    normalized_signature = normalize_claim_path(root, signature_path)
    request_file = root / normalized_request
    signature_file = root / normalized_signature
    try:
        raw_request = request_file.read_bytes()
        signature = signature_file.read_text(encoding="utf-8")
        request = json.loads(raw_request.decode("utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError(f"Signed approval input is missing: {exc.filename}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HarnessError(f"Invalid signed approval request: {exc}") from exc
    if not isinstance(request, dict) or request.get("schema") != "harness.approval-request/v1":
        raise HarnessError("Invalid approval request schema")
    attestation = {
        "mode": "SSH_ALLOWED_SIGNERS",
        "request_path": normalized_request,
        "request_sha256": sha256_bytes(raw_request),
        "request_base64": base64.b64encode(raw_request).decode("ascii"),
        "signature": signature,
    }
    directory = root / HARNESS_DIR / "approvals"
    for path in directory.glob("APR-*.json"):
        existing = load_json(path)
        existing_attestation = existing.get("attestation")
        if (
            isinstance(existing_attestation, dict)
            and existing_attestation.get("request_sha256")
            == attestation["request_sha256"]
        ):
            raise HarnessError(f"Signed approval request was already recorded as {existing.get('id')}")
    return record_approval(
        root,
        approval_type=str(request.get("approval_type", "")),
        subject_path=str(request.get("subject_path", "")),
        decision=str(request.get("decision", "")),
        approver=str(request.get("approved_by", "")),
        authority_role=str(request.get("authority_role", "")),
        basis=str(request.get("basis", "")),
        conditions=request.get("conditions"),
        condition_refs=request.get("condition_refs"),
        authorized_actions=request.get("authorized_actions"),
        excluded_actions=request.get("excluded_actions"),
        attestation=attestation,
        authority_id=str(request.get("authority_id", "")),
        authority_sequence=request.get("authority_sequence"),
        decision_id=str(request.get("decision_id", "")),
        decision_at=str(request.get("decision_at", "")),
    )


def approval_status(root: Path, approval: dict[str, Any]) -> tuple[str, str]:
    if approval.get("authority_role") != "HUMAN_PROJECT_OWNER":
        return "INVALID", "approval authority is not HUMAN_PROJECT_OWNER"
    if not str(approval.get("approved_by", "")).strip() or not str(
        approval.get("basis", "")
    ).strip():
        return "INVALID", "approval lacks approver or decision basis"
    manifest = approval.get("snapshot_manifest")
    if not isinstance(manifest, list) or not manifest:
        return "INVALID", "approval baseline snapshot is missing"
    for entry in manifest:
        if not isinstance(entry, dict):
            return "INVALID", "approval baseline snapshot entry is invalid"
        snapshot_value = entry.get("snapshot_path")
        expected = entry.get("sha256")
        if not isinstance(snapshot_value, str) or not isinstance(expected, str):
            return "INVALID", "approval baseline snapshot entry is incomplete"
        try:
            normalized_snapshot = normalize_claim_path(root, snapshot_value)
        except HarnessError as exc:
            return "INVALID", str(exc)
        snapshot_path = root / normalized_snapshot
        if not snapshot_path.is_file() or sha256_file(snapshot_path) != expected:
            return "INVALID", f"approval baseline snapshot is missing or changed: {snapshot_value}"
    subject_path = approval.get("subject_path")
    if not isinstance(subject_path, str):
        return "INVALID", "approval subject_path is missing"
    try:
        normalized_subject_path = normalize_claim_path(root, subject_path)
    except HarnessError as exc:
        return "INVALID", str(exc)
    path = root / normalized_subject_path
    if not path.is_file():
        return "STALE", "approval subject is missing"
    try:
        subject = load_json(path)
    except HarnessError as exc:
        return "INVALID", str(exc)
    if approval.get("subject_id") != subject.get("id"):
        return "INVALID", "approval subject ID does not match the canonical subject"
    expected_kind = APPROVAL_SUBJECT_KINDS.get(str(approval.get("approval_type")))
    if expected_kind and subject.get("kind") != expected_kind:
        return "INVALID", f"approval type requires subject kind {expected_kind}"
    if _canonical_subject_path(root, subject) != normalized_subject_path:
        return "INVALID", "approval subject_path is not the canonical record path"
    try:
        current = subject_fingerprint_for_path(path)
    except HarnessError as exc:
        return "INVALID", str(exc)
    if current != approval.get("subject_fingerprint"):
        return "STALE", "approval subject fingerprint changed"
    expected_attestation = {
        field: approval.get(field) for field in SIGNED_REQUEST_FIELDS
    }
    attestation_valid, attestation_reason = _verify_attestation(
        root,
        approval.get("attestation"),
        expected_attestation,
        enforce_request_expiry=False,
    )
    if not attestation_valid:
        if "superseded by protected authority sequence" in attestation_reason:
            return "SUPERSEDED", attestation_reason
        return "INVALID", f"approval identity verification failed: {attestation_reason}"
    if approval.get("decision") not in APPROVED_DECISIONS:
        return "NOT_APPROVED", f"decision is {approval.get('decision')}"
    return "CURRENT", "approval fingerprint and decision are current"


def find_current_approval(
    root: Path,
    *,
    subject_id: str,
    approval_type: str | None = None,
) -> tuple[dict[str, Any] | None, str]:
    directory = root / HARNESS_DIR / "approvals"
    matches: list[dict[str, Any]] = []
    for path in sorted(directory.glob("APR-*.json")):
        approval = load_json(path)
        if approval.get("subject_id") != subject_id:
            continue
        if approval_type and approval.get("approval_type") != approval_type:
            continue
        matches.append(approval)
    if not matches:
        return None, f"no {approval_type or ''} decision for {subject_id}".strip()
    latest = max(
        matches,
        key=lambda item: (
            int(item.get("authority_sequence", 0))
            if isinstance(item.get("authority_sequence"), int)
            and not isinstance(item.get("authority_sequence"), bool)
            else 0,
            str(item.get("id", "")),
        ),
    )
    status, reason = approval_status(root, latest)
    if status != "CURRENT":
        return None, f"latest decision {latest.get('id')} is {status}: {reason}"
    return latest, "latest decision is a current approval"
