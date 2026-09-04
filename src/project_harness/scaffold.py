from __future__ import annotations

import re
from pathlib import Path

from .constants import (
    CAPABILITY_APPROVAL_TYPES,
    HARNESS_DIR,
    PROCEDURAL_PLAN_ACTIONS,
    RECORD_DIRECTORIES,
)
from .core import HarnessError, atomic_write_json, atomic_write_text, load_json, utc_now


RUNTIME_DIRECTORIES = [
    "events",
    "baselines",
    "decisions",
    "templates",
    "runtime",
]


ASSETS = Path(__file__).resolve().parent / "assets"

# Every file the distribution hands to a project lives under ``assets`` and is
# packaged with the runtime, so a generated project receives the same policy,
# schemas, and scripts whether ``init`` ran from a source checkout, a vendored
# runtime, or an installed package.  Guidance and scripts are written only when
# absent; a project may extend its own copies.
GUIDANCE_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "CODEX_START_PROMPT.md",
    "CLAUDE_START_PROMPT.md",
)
SCRIPT_FILES = ("harness.py", "check_repo.py")

GENERATED_HANDOFF = """# Current Handoff\n\nNo accepted handoff has been recorded yet. Canonical records live in `.harness/handoffs/`.\n"""


def asset_text(relative: str) -> str:
    path = ASSETS / relative
    if not path.is_file():
        raise HarnessError(f"Harness distribution asset is missing: {relative}")
    return path.read_text(encoding="utf-8")


def _install_runtime(harness: Path) -> None:
    source_package = Path(__file__).resolve().parent
    target_package = harness / "tooling" / "project_harness"
    target_package.mkdir(parents=True, exist_ok=True)
    for source in sorted(source_package.glob("*.py")):
        atomic_write_text(target_package / source.name, source.read_text(encoding="utf-8"))
    if not (ASSETS / "schemas").is_dir():
        raise HarnessError("Harness schema assets are missing from the distribution")
    for source in sorted(ASSETS.rglob("*")):
        if not source.is_file() or "__pycache__" in source.parts:
            continue
        relative = source.relative_to(source_package)
        atomic_write_text(target_package / relative, source.read_text(encoding="utf-8"))
    # Operator-visible copy; the vendored runtime carries the canonical set.
    for source in sorted((ASSETS / "schemas").glob("*.json")):
        atomic_write_text(
            harness.parent / "schemas" / source.name, source.read_text(encoding="utf-8")
        )


def _install_guidance(root: Path) -> None:
    for relative in GUIDANCE_FILES:
        target = root / relative
        if not target.exists():
            atomic_write_text(target, asset_text(f"guidance/{relative}"))
    for source in sorted((ASSETS / "guidance" / "docs").glob("*.md")):
        target = root / "docs" / source.name
        if not target.exists():
            atomic_write_text(target, source.read_text(encoding="utf-8"))
    for relative in SCRIPT_FILES:
        target = root / "scripts" / relative
        if not target.exists():
            atomic_write_text(target, asset_text(f"scripts/{relative}"))


def init_project(path: Path, project_id: str, name: str, *, force: bool = False) -> Path:
    """Create a harness, or safely repair its distribution when forced.

    Repair never rewrites canonical project identity, lifecycle state, or records.
    """
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", project_id):
        raise HarnessError(
            "project_id must start with a letter or number and contain only "
            "letters, numbers, dot, underscore, or hyphen"
        )
    if not name.strip():
        raise HarnessError("project name must not be empty")
    root = path.resolve()
    root.mkdir(parents=True, exist_ok=True)
    harness = root / HARNESS_DIR
    project_path = harness / "project.json"
    repairing = project_path.exists()
    if repairing:
        if not force:
            raise HarnessError(f"Project harness already exists at {root}")
        existing = load_json(project_path)
        existing_id = existing.get("id") if isinstance(existing, dict) else None
        existing_name = existing.get("name") if isinstance(existing, dict) else None
        if existing_id != project_id or existing_name != name:
            raise HarnessError(
                "init --force is repair-only: project id and name must exactly "
                "match the existing canonical project record"
            )
    elif harness.exists() and any(
        candidate.is_file()
        for candidate in harness.rglob("*.json")
        if "tooling" not in candidate.relative_to(harness).parts
    ):
        raise HarnessError(
            "Cannot initialize over harness records without a canonical "
            "project.json; recover or remove the ambiguous records explicitly"
        )

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
        project = {
            "schema": "harness.project/v1",
            "id": project_id,
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
                "execution_mode": "USER_DIRECTED",
                "claim_mode": "WHEN_CONCURRENT",
                "record_mode": "ON_DEMAND",
                "human_approval_required_for": [
                    "PRODUCTION_DEPLOYMENT",
                    "PRODUCTION_DATA_CHANGE",
                    "DESTRUCTIVE_ACTION",
                    "SECRET_ACCESS",
                    "CUSTOMER_ACCEPTANCE",
                ],
                "approval_assurance": {
                    "default": "PROCEDURAL",
                    "by_type": {
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
        state = {
            "schema": "harness.state/v1",
            "project_id": project_id,
            "lifecycle_state": "DISCOVERY",
            "current_plan": None,
            "active_plan": None,
            "active_baselines": {},
            "active_release": None,
            "updated_at": created,
        }
        atomic_write_json(project_path, project)
        atomic_write_json(harness / "state.json", state)

    _install_guidance(root)

    root_files = {
        ".gitignore": "__pycache__/\n*.py[cod]\n.venv/\n.harness/runtime/\n",
        "HANDOFF.md": GENERATED_HANDOFF,
        ".harness/.gitattributes": (
            "*.json text eol=lf\n"
            "plans/*.md text eol=lf\n"
            "work-items/*.md text eol=lf\n"
        ),
        ".harness/.gitignore": "/runtime/\n",
        ".harness/templates/allowed_signers.example": "# Documentation only. Never use a repository file as the approval trust root.\n",
    }
    for relative, content in root_files.items():
        target = root / relative
        if not target.exists():
            atomic_write_text(target, content)
    authority_example = harness / "templates" / "authority-config.example.json"
    if not authority_example.exists():
        atomic_write_json(
            authority_example,
            {
                "schema": "harness.authority/v1",
                "project_id": project_id,
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
            },
        )
    _install_runtime(harness)
    return root


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
                "verification_strategy": {},
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
