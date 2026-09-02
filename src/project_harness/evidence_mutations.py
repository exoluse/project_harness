from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import HARNESS_DIR
from .core import (
    HarnessError,
    allocate_record_id,
    load_json,
    normalize_agent_id,
    normalize_claim_path,
    record_path,
    sha256_path,
    subject_fingerprint,
    utc_now,
)
from .evaluation import EvaluationContext
from .mutation_service import (
    AtomicMutationService,
    authorize_claim_targets,
    validate_records,
)


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
    """Record evidence and attach it to every supported criterion atomically."""
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
        "ambiguity": {"level": ambiguity_level, "reasons": ambiguity_reasons},
        "bindings": bindings,
        "limitations": limitations,
    }
    writes[evidence_relative] = evidence
    authorize_claim_targets(
        root,
        claim_id=claim_id,
        agent=agent,
        targets=[evidence_relative, *owner_paths],
    )
    validate_records(
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
