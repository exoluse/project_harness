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
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .constants import (
    APPROVAL_ASSURANCE_LEVELS,
    APPROVAL_DECISIONS,
    APPROVED_DECISIONS,
    CRYPTOGRAPHIC_APPROVAL_TYPES,
    HARNESS_DIR,
    PROCEDURAL_APPROVAL_TYPES,
    PROCEDURAL_PLAN_ACTIONS,
)
from .core import (
    HarnessError,
    allocate_record_id,
    atomic_write_json,
    atomic_write_text,
    canonical_json,
    filesystem_mutex,
    git_common_dir,
    load_json,
    normalize_claim_path,
    parse_utc,
    record_event,
    run_git,
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
    "DESTRUCTIVE_ACTION": "change",
    "SECRET_ACCESS": "change",
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


def required_approval_assurance(root: Path, approval_type: str) -> str:
    """Return the configured minimum assurance, defaulting legacy projects closed."""

    project = load_json(root / HARNESS_DIR / "project.json")
    policy = project.get("policy", {})
    if not isinstance(policy, dict):
        raise HarnessError("Project approval policy is malformed")
    assurance = policy.get("approval_assurance", {})
    if assurance is None:
        assurance = {}
    if not isinstance(assurance, dict):
        raise HarnessError("Project approval_assurance policy must be an object")
    default = assurance.get("default", "CRYPTOGRAPHIC")
    by_type = assurance.get("by_type", {})
    if not isinstance(default, str) or default not in APPROVAL_ASSURANCE_LEVELS:
        raise HarnessError("Project approval assurance default is invalid")
    if not isinstance(by_type, dict):
        raise HarnessError("Project approval assurance by_type must be an object")
    value = by_type.get(approval_type, default)
    if approval_type in CRYPTOGRAPHIC_APPROVAL_TYPES:
        value = "CRYPTOGRAPHIC"
    if not isinstance(value, str) or value not in APPROVAL_ASSURANCE_LEVELS:
        raise HarnessError(f"Approval assurance for {approval_type} is invalid")
    if value == "PROCEDURAL" and approval_type not in PROCEDURAL_APPROVAL_TYPES:
        raise HarnessError(
            f"PROCEDURAL assurance is not permitted for {approval_type}"
        )
    return value


def effective_approval_assurance(
    root: Path,
    approval_type: str,
    *,
    subject: dict[str, Any] | None = None,
) -> str:
    """Apply code-controlled risk escalation to the configured minimum."""

    required = required_approval_assurance(root, approval_type)
    if approval_type != "PLAN" or required != "PROCEDURAL" or subject is None:
        return required
    approval_subject = subject.get("approval_subject")
    actions = (
        approval_subject.get("authorized_actions", [])
        if isinstance(approval_subject, dict)
        else []
    )
    if not isinstance(actions, list) or any(not isinstance(item, str) for item in actions):
        raise HarnessError("PLAN authorized_actions must be a string list")
    return (
        "CRYPTOGRAPHIC"
        if set(actions) - PROCEDURAL_PLAN_ACTIONS
        else "PROCEDURAL"
    )


def _assurance_satisfies(actual: str, required: str) -> bool:
    rank = {"PROCEDURAL": 1, "CRYPTOGRAPHIC": 2}
    return actual in rank and required in rank and rank[actual] >= rank[required]


def _attestation_assurance(attestation: dict[str, Any] | None) -> str | None:
    if not isinstance(attestation, dict):
        return None
    mode = attestation.get("mode")
    if mode == "SSH_ALLOWED_SIGNERS":
        return "CRYPTOGRAPHIC"
    if mode == "PROCEDURAL_CONFIRMATION":
        return "PROCEDURAL"
    return None


def approval_assurance(approval: dict[str, Any]) -> str | None:
    """Return a declared assurance or infer the legacy SSH assurance."""

    declared = approval.get("assurance")
    if isinstance(declared, str):
        return declared
    return _attestation_assurance(approval.get("attestation"))


def _decision_mutex_paths(root: Path) -> tuple[Path, Path]:
    directory = _decision_runtime_directory(root)
    return directory / "record.lock", directory / "lock-recoveries"


def _decision_runtime_directory(root: Path) -> Path:
    common = git_common_dir(root)
    runtime = (
        common / "project-harness-runtime"
        if common is not None
        else root / HARNESS_DIR / "runtime"
    )
    return runtime / "human-decisions"


def _primary_git_worktree(root: Path) -> Path | None:
    if git_common_dir(root) is None:
        return None
    code, output = run_git(root, "worktree", "list", "--porcelain")
    if code != 0:
        raise HarnessError("Unable to identify the primary Git worktree")
    for line in output.splitlines():
        if line.startswith("worktree "):
            return Path(line.removeprefix("worktree ")).resolve()
    raise HarnessError("Git did not report a primary worktree")


def require_procedural_decision_writer(root: Path) -> None:
    """Keep repository procedural history authoritative in one worktree."""

    primary = _primary_git_worktree(root)
    if primary is None:
        return
    if os.path.normcase(str(primary)) != os.path.normcase(str(root.resolve())):
        raise HarnessError(
            "PROCEDURAL decisions may be recorded only in the primary integration "
            f"worktree: {primary}"
        )


def _procedural_marker_path(
    root: Path, *, approval_type: str, subject_id: str
) -> Path:
    key = sha256_bytes(f"{approval_type}\0{subject_id}".encode("utf-8"))
    return _decision_runtime_directory(root) / "latest-procedural" / f"{key}.json"


def _write_procedural_marker(
    root: Path,
    *,
    expected: dict[str, Any],
    attestation: dict[str, Any],
) -> None:
    atomic_write_json(
        _procedural_marker_path(
            root,
            approval_type=str(expected.get("approval_type", "")),
            subject_id=str(expected.get("subject_id", "")),
        ),
        {
            "schema": "harness.procedural-latest/v1",
            "project_id": expected.get("project_id"),
            "approval_type": expected.get("approval_type"),
            "subject_id": expected.get("subject_id"),
            "subject_fingerprint": expected.get("subject_fingerprint"),
            "decision_id": expected.get("decision_id"),
            "decision": expected.get("decision"),
            "authority_id": expected.get("authority_id"),
            "authority_sequence": expected.get("authority_sequence"),
            "confirmation_id": attestation.get("confirmation_id"),
            "recorded_at": expected.get("decision_at"),
        },
    )


def _verify_procedural_marker(
    root: Path,
    *,
    expected: dict[str, Any],
    attestation: dict[str, Any],
) -> tuple[bool, str]:
    path = _procedural_marker_path(
        root,
        approval_type=str(expected.get("approval_type", "")),
        subject_id=str(expected.get("subject_id", "")),
    )
    try:
        marker = load_json(path)
    except HarnessError as exc:
        return False, f"shared latest procedural decision marker is unavailable: {exc}"
    if marker.get("schema") != "harness.procedural-latest/v1":
        return False, "shared latest procedural decision marker is malformed"
    if marker.get("decision_id") != expected.get("decision_id"):
        return False, (
            "superseded by shared procedural decision "
            f"{marker.get('decision_id')}"
        )
    comparisons = {
        "project_id": expected.get("project_id"),
        "approval_type": expected.get("approval_type"),
        "subject_id": expected.get("subject_id"),
        "subject_fingerprint": expected.get("subject_fingerprint"),
        "decision": expected.get("decision"),
        "authority_id": expected.get("authority_id"),
        "authority_sequence": expected.get("authority_sequence"),
        "confirmation_id": attestation.get("confirmation_id"),
        "recorded_at": expected.get("decision_at"),
    }
    mismatches = [
        field for field, value in comparisons.items() if marker.get(field) != value
    ]
    if mismatches:
        return False, (
            "shared latest procedural decision marker conflicts on: "
            + ", ".join(sorted(mismatches))
        )
    return True, "shared latest procedural decision marker is current"


def _allocate_procedural_authority_sequence(
    root: Path, existing_records: list[dict[str, Any]]
) -> int:
    counter_path = _decision_runtime_directory(root) / "procedural-sequence.txt"
    counter = 0
    if counter_path.is_file():
        try:
            counter = int(counter_path.read_text(encoding="ascii").strip())
        except (OSError, ValueError) as exc:
            raise HarnessError(
                f"Invalid shared procedural decision sequence: {counter_path}"
            ) from exc
    local_sequences = [
        item.get("authority_sequence")
        for item in existing_records
        if item.get("authority_id") == "PROCEDURAL-LOCAL"
        and isinstance(item.get("authority_sequence"), int)
        and not isinstance(item.get("authority_sequence"), bool)
    ]
    value = max(counter, *local_sequences, 0) + 1
    atomic_write_text(counter_path, f"{value}\n")
    return value


def _ensure_procedural_authority_sequence(
    root: Path, authority_sequence: int
) -> None:
    """Advance the shared counter when repairing an already-recorded decision."""

    if authority_sequence <= 0:
        raise HarnessError("Procedural authority sequence must be positive")
    counter_path = _decision_runtime_directory(root) / "procedural-sequence.txt"
    counter = 0
    if counter_path.is_file():
        try:
            counter = int(counter_path.read_text(encoding="ascii").strip())
        except (OSError, ValueError) as exc:
            raise HarnessError(
                f"Invalid shared procedural decision sequence: {counter_path}"
            ) from exc
    if authority_sequence > counter:
        atomic_write_text(counter_path, f"{authority_sequence}\n")


@contextmanager
def decision_mutex(root: Path, *, operation: str = "processing a human decision"):
    """Serialize decision recording and application across shared worktrees."""

    lock, recovery = _decision_mutex_paths(root)
    with filesystem_mutex(
        lock,
        recovery_directory=recovery,
        timeout_message=f"Timed out {operation}",
    ):
        yield


def _procedural_payload(expected: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "project_id",
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
        "assurance",
    )
    return {field: expected.get(field) for field in fields}


def _procedural_provenance_payload(
    attestation: dict[str, Any], expected: dict[str, Any]
) -> dict[str, Any]:
    return {
        "mode": attestation.get("mode"),
        "confirmation_id": attestation.get("confirmation_id"),
        "confirmation_channel": attestation.get("confirmation_channel"),
        "confirmation_reference": attestation.get("confirmation_reference"),
        "confirmed_at": attestation.get("confirmed_at"),
        "confirmed_by": attestation.get("confirmed_by"),
        "confirmed_subject_fingerprint": attestation.get(
            "confirmed_subject_fingerprint"
        ),
        "decision_payload_sha256": attestation.get("decision_payload_sha256"),
        "authority_id": expected.get("authority_id"),
        "authority_sequence": expected.get("authority_sequence"),
        "decision_id": expected.get("decision_id"),
        "decision_at": expected.get("decision_at"),
    }


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
    assurance: str,
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
        "assurance": assurance,
    }


def _verify_attestation(
    root: Path,
    attestation: dict[str, Any] | None,
    expected: dict[str, Any],
    *,
    enforce_request_expiry: bool,
    require_current_ledger_decision: bool = True,
    verify_procedural_marker: bool = True,
) -> tuple[bool, str]:
    if not isinstance(attestation, dict):
        return False, "approval attestation is required"
    actual_assurance = expected.get("assurance") or _attestation_assurance(attestation)
    if not isinstance(actual_assurance, str) or actual_assurance not in APPROVAL_ASSURANCE_LEVELS:
        return False, "approval assurance is missing or invalid"
    try:
        approval_type = str(expected.get("approval_type", ""))
        subject: dict[str, Any] | None = None
        subject_path = expected.get("subject_path")
        if approval_type == "PLAN" and isinstance(subject_path, str):
            normalized_subject = normalize_claim_path(root, subject_path)
            candidate_path = root / normalized_subject
            if candidate_path.is_file():
                subject = load_json(candidate_path)
        required_assurance = effective_approval_assurance(
            root, approval_type, subject=subject
        )
    except HarnessError as exc:
        return False, str(exc)
    if not _assurance_satisfies(actual_assurance, required_assurance):
        return False, (
            f"approval assurance {actual_assurance} does not satisfy "
            f"required {required_assurance}"
        )

    if actual_assurance == "PROCEDURAL":
        if attestation.get("mode") != "PROCEDURAL_CONFIRMATION":
            return False, "procedural confirmation attestation is required"
        if expected.get("approval_type") not in PROCEDURAL_APPROVAL_TYPES:
            return False, "procedural assurance is not allowed for this approval type"
        if attestation.get("confirmed_subject_fingerprint") != expected.get(
            "subject_fingerprint"
        ):
            return False, "procedural confirmation fingerprint does not match"
        confirmation_id = attestation.get("confirmation_id")
        channel = attestation.get("confirmation_channel")
        reference = attestation.get("confirmation_reference")
        confirmed_by = attestation.get("confirmed_by")
        confirmed_at = attestation.get("confirmed_at")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                confirmation_id,
                channel,
                reference,
                confirmed_by,
                confirmed_at,
            )
        ):
            return False, "procedural confirmation provenance is incomplete"
        if not re.fullmatch(r"HCONF-[A-Za-z0-9_.-]{1,120}", str(confirmation_id)):
            return False, "procedural confirmation ID is invalid"
        if confirmed_by != expected.get("approved_by"):
            return False, "procedural confirmer does not match approved_by"
        try:
            parse_utc(str(confirmed_at))
        except (TypeError, ValueError):
            return False, "procedural confirmation time is invalid"
        if confirmed_at != expected.get("decision_at"):
            return False, "procedural confirmation time does not match decision_at"
        payload = _procedural_payload(expected)
        digest = sha256_bytes(canonical_json(payload).encode("utf-8"))
        if attestation.get("decision_payload_sha256") != digest:
            return False, "procedural decision payload hash does not match"
        provenance_digest = sha256_bytes(
            canonical_json(
                _procedural_provenance_payload(attestation, expected)
            ).encode("utf-8")
        )
        if attestation.get("confirmation_provenance_sha256") != provenance_digest:
            return False, "procedural confirmation provenance hash does not match"
        if verify_procedural_marker:
            marker_valid, marker_reason = _verify_procedural_marker(
                root, expected=expected, attestation=attestation
            )
            if not marker_valid:
                return False, marker_reason
        return True, (
            "procedural confirmation is current provenance only; "
            "human identity is not cryptographically authenticated"
        )

    if attestation.get("mode") != "SSH_ALLOWED_SIGNERS":
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
    if request.get("assurance", "CRYPTOGRAPHIC") != "CRYPTOGRAPHIC":
        return False, "signed approval request assurance is not CRYPTOGRAPHIC"
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


def _approval_snapshot_hash_matches(path: Path, expected: str) -> bool:
    """Accept Git's CRLF checkout transform for JSON approval snapshots only."""

    if sha256_file(path) == expected:
        return True
    if path.suffix.casefold() != ".json":
        return False
    try:
        raw = path.read_bytes()
        load_json(path)
    except (OSError, HarnessError):
        return False
    normalized = raw.replace(b"\r\n", b"\n")
    return normalized != raw and sha256_bytes(normalized) == expected


def _record_approval_unlocked(
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
    assurance: str | None = None,
    procedural_recording: bool = False,
) -> dict[str, Any]:
    if authority_role != "HUMAN_PROJECT_OWNER":
        raise HarnessError("Only HUMAN_PROJECT_OWNER decisions can be recorded as approvals")
    if decision not in APPROVAL_DECISIONS:
        raise HarnessError(f"Unsupported approval decision: {decision}")
    if approval_type not in APPROVAL_SUBJECT_KINDS:
        raise HarnessError(f"Unsupported approval type: {approval_type}")
    if not approver.strip() or not basis.strip():
        raise HarnessError("Approval requires an approver and an explicit decision basis")
    inferred_assurance = _attestation_assurance(attestation)
    assurance = assurance or inferred_assurance or required_approval_assurance(
        root, approval_type
    )
    if assurance not in APPROVAL_ASSURANCE_LEVELS:
        raise HarnessError(f"Unsupported approval assurance: {assurance}")
    required_assurance = required_approval_assurance(root, approval_type)
    if not _assurance_satisfies(assurance, required_assurance):
        raise HarnessError(
            f"Approval assurance {assurance} does not satisfy required "
            f"{required_assurance}"
        )
    if inferred_assurance and inferred_assurance != assurance:
        raise HarnessError("Approval assurance does not match its attestation mode")
    if assurance == "PROCEDURAL":
        require_procedural_decision_writer(root)
        if inferred_assurance == "PROCEDURAL" and not procedural_recording:
            raise HarnessError(
                "PROCEDURAL decisions must use record_procedural_approval"
            )
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
    if (
        approval_type == "PLAN"
        and decision in APPROVED_DECISIONS
        and not authorized_actions
    ):
        raise HarnessError("Approved PLAN decisions require explicit authorized_actions")
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
    existing_records: list[dict[str, Any]] = []
    for existing_path in (root / HARNESS_DIR / "approvals").glob("APR-*.json"):
        existing = load_json(existing_path)
        existing_records.append(existing)
        existing_sequence = existing.get("authority_sequence")
        if isinstance(existing_sequence, int) and not isinstance(existing_sequence, bool):
            existing_sequences.append(existing_sequence)
    authority_id = authority_id or "TEST-MOCK-AUTHORITY"
    authority_sequence = authority_sequence or (max(existing_sequences, default=0) + 1)
    decision_id = decision_id or f"DEC-{uuid.uuid4()}"
    decision_at = decision_at or utc_now()
    for existing in existing_records:
        integrity_conflict = _approval_integrity_conflict(root, existing)
        if integrity_conflict:
            raise HarnessError(
                "Existing approval decision history is inconsistent: "
                + integrity_conflict
            )
    proposed_confirmation_id = (
        attestation.get("confirmation_id")
        if isinstance(attestation, dict)
        and attestation.get("mode") == "PROCEDURAL_CONFIRMATION"
        else None
    )
    for existing in existing_records:
        if existing.get("decision_id") == decision_id:
            raise HarnessError(f"Approval decision_id already exists: {decision_id}")
        if (
            existing.get("authority_id") == authority_id
            and existing.get("authority_sequence") == authority_sequence
        ):
            raise HarnessError(
                "Approval authority sequence already exists for this authority: "
                f"{authority_id}#{authority_sequence}"
            )
        existing_attestation = existing.get("attestation")
        if (
            isinstance(proposed_confirmation_id, str)
            and proposed_confirmation_id
            and isinstance(existing_attestation, dict)
            and existing_attestation.get("mode") == "PROCEDURAL_CONFIRMATION"
            and existing_attestation.get("confirmation_id")
            == proposed_confirmation_id
        ):
            raise HarnessError(
                "Approval confirmation_id already exists: "
                f"{proposed_confirmation_id}"
            )
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
        assurance=assurance,
    )
    attestation_valid, attestation_reason = _verify_attestation(
        root,
        attestation,
        expected_attestation,
        enforce_request_expiry=True,
        verify_procedural_marker=not procedural_recording,
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
        "assurance": assurance,
        "record_sequence": int(approval_id.removeprefix("APR-")),
        "recorded_at": utc_now(),
    }
    atomic_write_json(directory / f"{approval_id}.json", value)
    if procedural_recording:
        if not isinstance(attestation, dict):
            raise HarnessError("Procedural decision attestation is missing")
        _write_procedural_marker(
            root, expected=expected_attestation, attestation=attestation
        )
    record_event(
        root,
        "HUMAN_DECISION_RECORDED",
        {
            "approval_id": approval_id,
            "approval_type": approval_type,
            "subject_id": subject.get("id"),
            "decision": decision,
            "assurance": assurance,
        },
    )
    return value


def record_approval(root: Path, **kwargs: Any) -> dict[str, Any]:
    """Serialize approval IDs, authority sequences, snapshots, and events."""

    with decision_mutex(root, operation="recording a human decision"):
        return _record_approval_unlocked(root, **kwargs)


def record_procedural_approval(
    root: Path,
    *,
    approval_type: str,
    subject_path: str,
    decision: str,
    approver: str,
    basis: str,
    confirm_fingerprint: str,
    confirmation_id: str,
    confirmation_channel: str,
    confirmation_reference: str,
    authorized_actions: list[str] | None = None,
    excluded_actions: list[str] | None = None,
    conditions: list[str] | None = None,
    condition_refs: list[str] | None = None,
    acknowledge_procedural: bool = False,
) -> dict[str, Any]:
    """Record an explicitly acknowledged, non-authenticating human decision."""

    if not acknowledge_procedural:
        raise HarnessError(
            "Procedural approval requires --acknowledge-procedural because it "
            "does not cryptographically authenticate the human"
        )
    require_procedural_decision_writer(root)
    if approval_type not in PROCEDURAL_APPROVAL_TYPES:
        raise HarnessError(
            f"PROCEDURAL assurance is not permitted for {approval_type}"
        )
    if required_approval_assurance(root, approval_type) != "PROCEDURAL":
        raise HarnessError(
            f"Project policy does not permit PROCEDURAL {approval_type} approval"
        )
    if not re.fullmatch(r"HCONF-[A-Za-z0-9_.-]{1,120}", confirmation_id):
        raise HarnessError("confirmation_id must match HCONF-[A-Za-z0-9_.-]+")
    if not confirmation_channel.strip() or not confirmation_reference.strip():
        raise HarnessError("Procedural approval requires channel and reference")

    relative = normalize_claim_path(root, subject_path)
    path = root / relative
    if not path.is_file():
        raise HarnessError(f"Approval subject does not exist: {subject_path}")
    subject = load_json(path)
    fingerprint = subject_fingerprint_for_path(path)
    if confirm_fingerprint != fingerprint:
        raise HarnessError(
            "Confirmed fingerprint does not match the current approval subject"
        )
    if authorized_actions is not None and (
        not isinstance(authorized_actions, list)
        or any(not isinstance(item, str) for item in authorized_actions)
    ):
        raise HarnessError("Procedural authorized_actions must be a string list")
    requested_actions = set(authorized_actions or [])
    plan_subject = subject.get("approval_subject")
    raw_plan_actions = (
        plan_subject.get("authorized_actions", [])
        if isinstance(plan_subject, dict)
        else []
    )
    if not isinstance(raw_plan_actions, list) or any(
        not isinstance(item, str) for item in raw_plan_actions
    ):
        raise HarnessError("PLAN authorized_actions must be a string list")
    plan_actions = set(raw_plan_actions)
    unsafe_actions = sorted(
        (requested_actions | plan_actions) - PROCEDURAL_PLAN_ACTIONS
    )
    if unsafe_actions:
        raise HarnessError(
            "PROCEDURAL PLAN approval is limited to local safe actions; "
            "CRYPTOGRAPHIC assurance is required for: "
            + ", ".join(unsafe_actions)
        )
    project_id = str(load_json(root / HARNESS_DIR / "project.json").get("id", ""))
    with decision_mutex(root, operation="recording a procedural human decision"):
        require_procedural_decision_writer(root)
        directory = root / HARNESS_DIR / "approvals"
        existing_records = [load_json(item) for item in directory.glob("APR-*.json")]
        authority_id = "PROCEDURAL-LOCAL"
        replay_expected = _attestation_expected(
            project_id=project_id,
            authority_id=authority_id,
            authority_sequence=0,
            decision_id="",
            decision_at="",
            approval_type=approval_type,
            decision=decision,
            authority_role="HUMAN_PROJECT_OWNER",
            approver=approver,
            basis=basis,
            subject=subject,
            relative=relative,
            fingerprint=fingerprint,
            conditions=conditions,
            condition_refs=condition_refs,
            authorized_actions=authorized_actions,
            excluded_actions=excluded_actions,
            assurance="PROCEDURAL",
        )
        payload_digest = sha256_bytes(
            canonical_json(_procedural_payload(replay_expected)).encode("utf-8")
        )
        for existing in existing_records:
            existing_attestation = existing.get("attestation")
            if not isinstance(existing_attestation, dict):
                continue
            if existing_attestation.get("confirmation_id") != confirmation_id:
                continue
            replay_provenance = {
                "mode": "PROCEDURAL_CONFIRMATION",
                "confirmation_channel": confirmation_channel.strip(),
                "confirmation_reference": confirmation_reference.strip(),
                "confirmed_by": approver,
                "confirmed_subject_fingerprint": fingerprint,
            }
            if (
                existing_attestation.get("decision_payload_sha256") == payload_digest
                and all(
                    existing_attestation.get(field) == value
                    for field, value in replay_provenance.items()
                )
            ):
                status, reason = approval_status(
                    root, existing, verify_procedural_marker=False
                )
                if status not in {"CURRENT", "NOT_APPROVED"}:
                    raise HarnessError(
                        f"Existing confirmation {confirmation_id} is {status}: {reason}"
                    )
                expected_existing = {
                    field: existing.get(field) for field in SIGNED_REQUEST_FIELDS
                }
                expected_existing["assurance"] = approval_assurance(existing)
                marker_path = _procedural_marker_path(
                    root,
                    approval_type=str(existing.get("approval_type", "")),
                    subject_id=str(existing.get("subject_id", "")),
                )
                if marker_path.is_file():
                    marker_valid, marker_reason = _verify_procedural_marker(
                        root,
                        expected=expected_existing,
                        attestation=existing_attestation,
                    )
                    if not marker_valid:
                        raise HarnessError(
                            f"Existing confirmation {confirmation_id} cannot repair "
                            f"the shared marker: {marker_reason}"
                        )
                else:
                    _write_procedural_marker(
                        root,
                        expected=expected_existing,
                        attestation=existing_attestation,
                    )
                existing_sequence = existing.get("authority_sequence")
                if not isinstance(existing_sequence, int) or isinstance(
                    existing_sequence, bool
                ):
                    raise HarnessError(
                        "Existing procedural authority sequence is invalid"
                    )
                _ensure_procedural_authority_sequence(root, existing_sequence)
                return existing
            raise HarnessError(
                f"confirmation_id {confirmation_id} was already used for another decision"
            )
        authority_sequence = _allocate_procedural_authority_sequence(
            root, existing_records
        )
        decision_id = f"DEC-{uuid.uuid4()}"
        decision_at = utc_now()
        expected = _attestation_expected(
            project_id=project_id,
            authority_id=authority_id,
            authority_sequence=authority_sequence,
            decision_id=decision_id,
            decision_at=decision_at,
            approval_type=approval_type,
            decision=decision,
            authority_role="HUMAN_PROJECT_OWNER",
            approver=approver,
            basis=basis,
            subject=subject,
            relative=relative,
            fingerprint=fingerprint,
            conditions=conditions,
            condition_refs=condition_refs,
            authorized_actions=authorized_actions,
            excluded_actions=excluded_actions,
            assurance="PROCEDURAL",
        )
        payload_digest = sha256_bytes(
            canonical_json(_procedural_payload(expected)).encode("utf-8")
        )
        attestation = {
            "mode": "PROCEDURAL_CONFIRMATION",
            "confirmation_id": confirmation_id,
            "confirmation_channel": confirmation_channel.strip(),
            "confirmation_reference": confirmation_reference.strip(),
            "confirmed_at": decision_at,
            "confirmed_by": approver,
            "confirmed_subject_fingerprint": fingerprint,
            "decision_payload_sha256": payload_digest,
            "limitation": (
                "Records procedural provenance only; it does not authenticate "
                "the human against a same-privilege process"
            ),
        }
        attestation["confirmation_provenance_sha256"] = sha256_bytes(
            canonical_json(
                _procedural_provenance_payload(attestation, expected)
            ).encode("utf-8")
        )
        return _record_approval_unlocked(
            root,
            approval_type=approval_type,
            subject_path=relative,
            decision=decision,
            approver=approver,
            authority_role="HUMAN_PROJECT_OWNER",
            basis=basis,
            conditions=conditions,
            condition_refs=condition_refs,
            authorized_actions=authorized_actions,
            excluded_actions=excluded_actions,
            attestation=attestation,
            authority_id=authority_id,
            authority_sequence=authority_sequence,
            decision_id=decision_id,
            decision_at=decision_at,
            assurance="PROCEDURAL",
            procedural_recording=True,
        )


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
    if (
        approval_type == "PLAN"
        and decision in APPROVED_DECISIONS
        and not authorized_actions
    ):
        raise HarnessError("Approved PLAN requests require explicit authorized_actions")
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
            assurance="CRYPTOGRAPHIC",
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
        assurance="CRYPTOGRAPHIC",
    )


def _approval_integrity_conflict(
    root: Path, approval: dict[str, Any]
) -> str | None:
    current_id = str(approval.get("id", ""))
    decision_id = approval.get("decision_id")
    authority_id = approval.get("authority_id")
    authority_sequence = approval.get("authority_sequence")
    attestation = approval.get("attestation")
    confirmation_id = (
        attestation.get("confirmation_id")
        if isinstance(attestation, dict)
        and attestation.get("mode") == "PROCEDURAL_CONFIRMATION"
        else None
    )
    for path in sorted((root / HARNESS_DIR / "approvals").glob("APR-*.json")):
        if path.stem == current_id:
            continue
        candidate = load_json(path)
        candidate_id = candidate.get("id", path.stem)
        if isinstance(decision_id, str) and decision_id and candidate.get(
            "decision_id"
        ) == decision_id:
            return f"decision_id is duplicated by {candidate_id}"
        if (
            isinstance(authority_id, str)
            and authority_id
            and isinstance(authority_sequence, int)
            and not isinstance(authority_sequence, bool)
            and candidate.get("authority_id") == authority_id
            and candidate.get("authority_sequence") == authority_sequence
        ):
            return (
                "authority sequence is duplicated by "
                f"{candidate_id}: {authority_id}#{authority_sequence}"
            )
        candidate_attestation = candidate.get("attestation")
        if (
            isinstance(confirmation_id, str)
            and confirmation_id
            and isinstance(candidate_attestation, dict)
            and candidate_attestation.get("mode") == "PROCEDURAL_CONFIRMATION"
            and candidate_attestation.get("confirmation_id") == confirmation_id
        ):
            return f"confirmation_id is duplicated by {candidate_id}"
    return None


def approval_status(
    root: Path,
    approval: dict[str, Any],
    *,
    verify_procedural_marker: bool = True,
) -> tuple[str, str]:
    approval_id_match = re.fullmatch(
        r"APR-([0-9]+)", str(approval.get("id", ""))
    )
    if approval_id_match is None:
        return "INVALID", "approval ID is invalid"
    record_sequence = approval.get("record_sequence")
    if record_sequence is not None and (
        not isinstance(record_sequence, int)
        or isinstance(record_sequence, bool)
        or record_sequence != int(approval_id_match.group(1))
    ):
        return "INVALID", "approval record_sequence does not match its ID"
    try:
        integrity_conflict = _approval_integrity_conflict(root, approval)
    except HarnessError as exc:
        return "INVALID", f"approval decision history is unreadable: {exc}"
    if integrity_conflict:
        return "INVALID", integrity_conflict
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
        if not snapshot_path.is_file() or not _approval_snapshot_hash_matches(
            snapshot_path, expected
        ):
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
    assurance = approval_assurance(approval)
    expected_attestation = {
        field: approval.get(field) for field in SIGNED_REQUEST_FIELDS
    }
    expected_attestation["assurance"] = assurance
    attestation_valid, attestation_reason = _verify_attestation(
        root,
        approval.get("attestation"),
        expected_attestation,
        enforce_request_expiry=False,
        verify_procedural_marker=verify_procedural_marker,
    )
    if not attestation_valid:
        if (
            "superseded by protected authority sequence" in attestation_reason
            or "superseded by shared procedural decision" in attestation_reason
        ):
            return "SUPERSEDED", attestation_reason
        return "INVALID", f"approval identity verification failed: {attestation_reason}"
    current_sequence = approval.get("record_sequence")
    if not isinstance(current_sequence, int) or isinstance(current_sequence, bool):
        match = re.fullmatch(r"APR-([0-9]+)", str(approval.get("id", "")))
        current_sequence = int(match.group(1)) if match else 0
    for candidate_path in (root / HARNESS_DIR / "approvals").glob("APR-*.json"):
        candidate = load_json(candidate_path)
        if candidate.get("subject_id") != approval.get("subject_id") or candidate.get(
            "approval_type"
        ) != approval.get("approval_type"):
            continue
        candidate_sequence = candidate.get("record_sequence")
        if not isinstance(candidate_sequence, int) or isinstance(candidate_sequence, bool):
            match = re.fullmatch(r"APR-([0-9]+)", str(candidate.get("id", "")))
            candidate_sequence = int(match.group(1)) if match else 0
        if candidate_sequence > current_sequence:
            return (
                "SUPERSEDED",
                f"superseded by later local decision {candidate.get('id')}",
            )
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
    # Local APR creation order is the common ordering domain across assurance
    # providers.  Provider-specific authority_sequence remains part of that
    # provider's own replay/fork verification.
    def record_order(item: dict[str, Any]) -> tuple[int, str]:
        sequence = item.get("record_sequence")
        if isinstance(sequence, int) and not isinstance(sequence, bool):
            return sequence, str(item.get("id", ""))
        match = re.fullmatch(r"APR-([0-9]+)", str(item.get("id", "")))
        return (int(match.group(1)) if match else 0), str(item.get("id", ""))

    latest = max(matches, key=record_order)
    status, reason = approval_status(root, latest)
    if status != "CURRENT":
        return None, f"latest decision {latest.get('id')} is {status}: {reason}"
    return latest, "latest decision is a current approval"
