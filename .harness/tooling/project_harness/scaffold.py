from __future__ import annotations

from pathlib import Path

from .constants import (
    CAPABILITY_APPROVAL_TYPES,
    HARNESS_DIR,
    HISTORY_DIRECTORIES,
    PROCEDURAL_PLAN_ACTIONS,
    PROJECT_RECORD_ID,
    RECORD_DIRECTORIES,
)
from .core import HarnessError, atomic_write_json, atomic_write_text, load_json, utc_now


RUNTIME_DIRECTORIES = [
    *HISTORY_DIRECTORIES,
    "templates",
    "runtime",
]


GENERATED_HANDOFF = (
    "# Current Handoff\n\nNo accepted handoff has been recorded yet. "
    "Canonical records live in `.harness/handoffs/`.\n"
)

# Files a harness owns but a project may extend.  They are written only when
# absent, so re-running init never overwrites an operator's version.
GENERATED_FILES = {
    ".gitignore": "__pycache__/\n*.py[cod]\n.venv/\n.harness/runtime/\n",
    "HANDOFF.md": GENERATED_HANDOFF,
    ".harness/.gitattributes": (
        "*.json text eol=lf\n"
        "plans/*.md text eol=lf\n"
        "work-items/*.md text eol=lf\n"
    ),
    ".harness/.gitignore": "/runtime/\n",
    ".harness/templates/allowed_signers.example": (
        "# Documentation only. Never use a repository file as the approval trust root.\n"
    ),
}


def project_directories(harness: Path) -> list[Path]:
    """The record and history directories ``init`` creates, in stable order.

    They hold the project rather than the harness: what it specified, planned,
    decided, and observed.  ``init`` creates them empty; a reset removes them.
    """

    names = {value[0] for value in RECORD_DIRECTORIES.values()}
    names.update(HISTORY_DIRECTORIES)
    return [harness / name for name in sorted(names)]


def _carries_records(harness: Path) -> bool:
    """Whether records are present without the project record that governs them.

    Only the record and history directories count.  A filled-in authority
    template and the snapshots a reset leaves under ``runtime/`` are not
    records, and both outlive a reset on purpose, so a wider scan would make an
    already-reset tree impossible to initialize again.
    """

    for directory in project_directories(harness):
        if not directory.is_dir():
            continue
        for candidate in directory.rglob("*"):
            if candidate.is_file() and candidate.name != ".gitkeep":
                return True
    return False


def init_project(path: Path, name: str | None = None, *, force: bool = False) -> Path:
    """Initialize the harness records of the repository at ``path``.

    A harness governs one project, and that project is the repository it sits
    in, so this creates records rather than generating a project somewhere else.
    The runtime, guidance, and scripts are already part of the tree; ``init``
    adds the canonical project record, lifecycle state, and the record
    directories.  Repair never rewrites canonical identity, state, or records.
    """
    root = path.resolve()
    root.mkdir(parents=True, exist_ok=True)
    harness = root / HARNESS_DIR
    project_path = harness / "project.json"
    repairing = project_path.exists()
    existing_name: str | None = None
    if repairing:
        if not force:
            raise HarnessError(f"Project harness already exists at {root}")
        existing = load_json(project_path)
        existing_name = existing.get("name") if isinstance(existing, dict) else None
        if name is not None and name.strip() != existing_name:
            raise HarnessError(
                "init --force is repair-only: --name must match the existing "
                "canonical project record, or be omitted"
            )
    elif harness.exists() and _carries_records(harness):
        raise HarnessError(
            "Cannot initialize over harness records without a canonical "
            "project.json; recover or remove the ambiguous records explicitly"
        )

    # The directory the harness lives in names the project when nobody says
    # otherwise; the name is a human label, never an addressing key.
    project_name = (name or "").strip() or existing_name or root.name
    if not project_name:
        raise HarnessError("project name must not be empty")

    for directory in sorted({value[0] for value in RECORD_DIRECTORIES.values()}):
        record_directory = harness / directory
        record_directory.mkdir(parents=True, exist_ok=True)
        placeholder = record_directory / ".gitkeep"
        if not placeholder.exists():
            atomic_write_text(placeholder, "")
    for directory in RUNTIME_DIRECTORIES:
        (harness / directory).mkdir(parents=True, exist_ok=True)

    if not repairing:
        created = utc_now()
        atomic_write_json(project_path, fresh_project_record(project_name, created))
        atomic_write_json(harness / "state.json", fresh_state_record(created))

    for relative, content in GENERATED_FILES.items():
        target = root / relative
        if not target.exists():
            atomic_write_text(target, content)
    authority_example = harness / "templates" / "authority-config.example.json"
    if not authority_example.exists():
        atomic_write_json(authority_example, authority_config_example(root))
    return root


def authority_config_example(root: Path) -> dict:
    """The external authority configuration this harness expects.

    It is bound to the repository root rather than to a project name: the
    verifier locates the file by that root and refuses a configuration that
    declares a different one.  ``doctor`` reports the exact path it must be
    installed at.
    """

    return {
        "schema": "harness.authority/v1",
        "authority_id": "REPLACE_WITH_PROTECTED_AUTHORITY_ID",
        "repository_root": str(root),
        "protection": "OS_ACL_OR_EXTERNAL_BROKER",
        "signature_namespace": "project-harness",
        "allowed_signers_path": "REPLACE_WITH_ABSOLUTE_EXTERNAL_PATH",
        "allowed_signers_sha256": "REPLACE_WITH_SHA256",
        "decision_ledger_path": "REPLACE_WITH_ABSOLUTE_EXTERNAL_PATH",
        "approval_types": [
            "PRODUCTION_DEPLOYMENT",
            "PRODUCTION_DATA_CHANGE",
            "DESTRUCTIVE_ACTION",
            "SECRET_ACCESS",
            "CUSTOMER_ACCEPTANCE",
        ],
    }


def fresh_project_record(name: str, created: str) -> dict:
    """The canonical project record a newly initialized harness carries."""

    return {
        "schema": "harness.project/v1",
        "id": PROJECT_RECORD_ID,
        "kind": "project",
        "name": name,
        "schema_version": 1,
        "created_at": created,
        "required_features": [],
        "approval_dependencies": [],
        "closure_contract": [
            {
                "id": "DELIVERY",
                "required": True,
                "required_profiles": ["DELIVERY"],
                "evidence_refs": [],
            },
            {
                "id": "HANDOVER",
                "required": True,
                "required_profiles": ["HANDOVER"],
                "evidence_refs": [],
            },
            {
                "id": "MAINTENANCE_READINESS",
                "required": True,
                "required_profiles": ["MAINTENANCE_READINESS"],
                "evidence_refs": [],
            },
        ],
        "policy": {
            "execution_mode": "PLAN_GATED",
            "claim_mode": "WHEN_CONCURRENT",
            "record_mode": "ON_DEMAND",
            "human_approval_required_for": [
                "PLAN",
                "PRODUCTION_DEPLOYMENT",
                "PRODUCTION_DATA_CHANGE",
                "DESTRUCTIVE_ACTION",
                "SECRET_ACCESS",
                "CUSTOMER_ACCEPTANCE",
            ],
            "approval_assurance": {
                "default": "PROCEDURAL",
                "by_type": {
                    "PLAN": "PROCEDURAL",
                    "PRODUCTION_DEPLOYMENT": "CRYPTOGRAPHIC",
                    "PRODUCTION_DATA_CHANGE": "CRYPTOGRAPHIC",
                    "DESTRUCTIVE_ACTION": "CRYPTOGRAPHIC",
                    "SECRET_ACCESS": "CRYPTOGRAPHIC",
                    "CUSTOMER_ACCEPTANCE": "CRYPTOGRAPHIC",
                },
            },
            "default_claim_ttl_minutes": 120,
        },
    }


def fresh_state_record(created: str) -> dict:
    """The canonical state record a newly initialized harness carries."""

    return {
        "schema": "harness.state/v1",
        "lifecycle_state": "DISCOVERY",
        "current_plan": None,
        "active_plan": None,
        "active_baselines": {},
        "active_release": None,
        "updated_at": created,
    }


def new_record(kind: str, record_id: str, title: str) -> dict:
    now = utc_now()
    common = {
        "schema": f"harness.{kind}/v1",
        "id": record_id,
        "kind": kind,
        "title": title,
        "created_at": now,
        "updated_at": now,
    }
    if kind == "source":
        return {
            **common,
            "authority": "RAW_INPUT",
            "artifact_role": "REFERENCE",
            "interpretation_status": "EXPLICIT",
            "origin": "",
            "summary": "",
        }
    if kind == "requirement":
        return {
            **common,
            "version": "0.1.0",
            "status": "CANDIDATE",
            "required": True,
            "priority": "MUST",
            "statement": "",
            "source_refs": [],
            "acceptance_criteria": [],
        }
    if kind == "feature":
        return {
            **common,
            "version": "0.1.0",
            "status": "CANDIDATE",
            "required": True,
            "requirement_refs": [],
            "completion_criteria": [],
            "customer_acceptance_required": False,
        }
    if kind == "plan":
        return {
            **common,
            "version": "0.1.0",
            "status": "DRAFT",
            "approval_dependencies": [],
            "approval_subject": {
                "requirement_refs": [],
                "feature_refs": [],
                "work_item_refs": [],
                "workstreams": [],
                "verification_strategy": {"commands": ["python scripts/check_repo.py full"]},
                # Routine local work is authorized by default so a new plan can
                # carry a task immediately; every capability that needs a human
                # decision stays excluded until an author widens the subject.
                "authorized_actions": sorted(PROCEDURAL_PLAN_ACTIONS),
                "excluded_actions": sorted(CAPABILITY_APPROVAL_TYPES),
                "invalidation_triggers": [],
            },
        }
    if kind == "work_item":
        return {
            **common,
            "status": "DRAFT",
            "plan_id": "",
            "feature_refs": [],
            "criterion_refs": [],
            "dependencies": [],
            "blocked_by": [],
            "write_scope": [],
            "preexisting_dirty_paths": [],
            "logical_locks": [],
            "verification": [],
            "risk": "LOW",
            "capabilities": [],
            "capability_approval_refs": {},
            "forbidden_actions": [],
        }
    if kind == "open_item":
        return {
            **common,
            "category": "QUESTION",
            "gate_level": "G2",
            "status": "OPEN",
            "owner": "",
            "decision_authority": "",
            "affects": [],
            "blocks": [],
            "if_unresolved": "",
            "resolution": None,
        }
    if kind == "evidence":
        return {
            **common,
            "observed_at": now,
            "claim": "",
            "supports": [],
            "profile": "STATIC",
            "method": "",
            "environment": "",
            "subject": {},
            "expected": "",
            "actual": "",
            "result": "NOT_TESTED",
            "ambiguity": {"level": "NONE", "reasons": []},
            "bindings": [],
            "limitations": [],
        }
    if kind == "change":
        return {
            **common,
            "status": "RECEIVED",
            "classification": "UNCLASSIFIED",
            "source_refs": [],
            "affects": [],
            "impact": {},
            "decision_ref": None,
        }
    if kind == "artifact":
        return {
            **common,
            "source_ref": "",
            "path": "",
            "media_type": "application/octet-stream",
            "sha256": "",
            "execution_trust": "UNTRUSTED",
            "safe_to_execute": False,
        }
    raise HarnessError(f"Use a dedicated command to create {kind!r} records")
