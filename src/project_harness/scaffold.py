from __future__ import annotations

import re
from pathlib import Path

from .constants import HARNESS_DIR, RECORD_DIRECTORIES
from .core import HarnessError, atomic_write_json, atomic_write_text, load_json, utc_now


RUNTIME_DIRECTORIES = [
    "events",
    "baselines",
    "decisions",
    "templates",
    "runtime",
]


GENERATED_AGENTS = """# Shared Agent Policy\n\nRead `.harness/project.json`, `.harness/state.json`, `HANDOFF.md`, and inspect Git status. A newly initialized project may remain in discovery without a PLAN or TASK, and discovery/specification records may be created directly from the user's request. Before deliverable implementation, create or select a current PLAN and a TASK listed in it. An explicit user request authorizes ordinary execution of that TASK without PLAN approval. Use claims only for concurrent writers, and create results/events/evidence only when coordination, audit, release, or completion proof needs them. Cryptographic human approval is reserved for production, destructive operations, secret access, production data changes, and final customer acceptance. Preserve pre-existing work and report verification limits exactly.\n"""

GENERATED_CLAUDE = """# Claude Code Adapter\n\n`AGENTS.md` is canonical. Follow its user-directed execution model. Discovery may precede PLAN/TASK creation; both become mandatory before implementation. PLAN approval is not required. Claims and handoffs are for concurrent writers; audit records are created only when needed.\n"""

GENERATED_CODEX_PROMPT = """# Codex Start Prompt\n\nRead `AGENTS.md`, inspect current state and Git status, and determine whether the request is discovery/specification or execution. Discovery/specification records may precede PLAN/TASK; before deliverable implementation, create or select the current PLAN and its TASK. Perform the explicit user request without requiring PLAN approval. Use claims only for concurrent editing and audit records only when needed. Never infer high-risk human approval.\n"""

GENERATED_CLAUDE_PROMPT = """# Claude Code Start Prompt\n\nRead `AGENTS.md` and `CLAUDE.md`, inspect current state and Git status, and determine whether the request is discovery/specification or execution. Discovery/specification records may precede PLAN/TASK; before deliverable implementation, create or select the current PLAN and its TASK. Perform the explicit user request without requiring PLAN approval. Use claims only for concurrent editing and audit records only when needed. Never infer high-risk human approval.\n"""

GENERATED_HANDOFF = """# Current Handoff\n\nNo accepted handoff has been recorded yet. Canonical records live in `.harness/handoffs/`.\n"""

GENERATED_WRAPPER = """from pathlib import Path\nimport sys\n\nROOT = Path(__file__).resolve().parents[1]\nsys.path.insert(0, str(ROOT / \".harness\" / \"tooling\"))\n\nfrom project_harness.cli import main\n\nif __name__ == \"__main__\":\n    raise SystemExit(main())\n"""

GENERATED_CHECK_REPO = """from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str]) -> bool:
    print(f"[{label}] {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT, check=False)
    print(f"[{label}] exit={result.returncode}")
    return result.returncode == 0


def checks_for(tier: str) -> list[tuple[str, list[str]]]:
    checks = [("compile", [sys.executable, "-m", "compileall", "-q", ".harness/tooling", "scripts", "tests"])]
    if tier == "full":
        checks.append(("tests-full", [sys.executable, "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-v"]))
    checks.append(("harness-strict", [sys.executable, "scripts/harness.py", "validate", "--strict"]))
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run fixed project verification")
    parser.add_argument(
        "tier",
        nargs="?",
        choices=("fast", "full"),
        default="full",
        help="full is the default when the tier is omitted",
    )
    args = parser.parse_args(argv)
    print(f"[check-repo] tier={args.tier}")
    outcomes = [run(label, command) for label, command in checks_for(args.tier)]
    return 0 if all(outcomes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _install_runtime(harness: Path) -> None:
    source_package = Path(__file__).resolve().parent
    target_package = harness / "tooling" / "project_harness"
    target_package.mkdir(parents=True, exist_ok=True)
    for source in sorted(source_package.glob("*.py")):
        atomic_write_text(target_package / source.name, source.read_text(encoding="utf-8"))

    # Keep the generated project self-contained.  In this repository the
    # canonical schemas live at the repository root; in an already-vendored
    # runtime they live beside the vendored package.  Copy them both to the
    # operator-visible schema directory and back into the vendored runtime so
    # a generated project can itself initialize another project.
    schema_candidates = [
        source_package.parents[1] / "schemas",
        source_package.parent / "schemas",
    ]
    schema_source = next(
        (candidate for candidate in schema_candidates if candidate.is_dir()),
        None,
    )
    if schema_source is None:
        raise HarnessError("Harness schema assets are missing from the distribution")
    for source in sorted(schema_source.glob("*.json")):
        content = source.read_text(encoding="utf-8")
        atomic_write_text(harness.parent / "schemas" / source.name, content)
        atomic_write_text(harness / "tooling" / "schemas" / source.name, content)


def _install_guidance(root: Path) -> None:
    """Copy the complete generic policy/docs when the distribution has them."""
    source_package = Path(__file__).resolve().parent
    distribution_root = next(
        (
            candidate
            for candidate in source_package.parents
            if (candidate / "AGENTS.md").is_file()
            and (candidate / "docs").is_dir()
        ),
        None,
    )
    if distribution_root is None:
        return
    for relative in (
        "AGENTS.md",
        "CLAUDE.md",
        "CODEX_START_PROMPT.md",
        "CLAUDE_START_PROMPT.md",
    ):
        source = distribution_root / relative
        target = root / relative
        if source.is_file() and not target.exists():
            atomic_write_text(target, source.read_text(encoding="utf-8"))
    for source in sorted((distribution_root / "docs").glob("*.md")):
        target = root / "docs" / source.name
        if not target.exists():
            atomic_write_text(target, source.read_text(encoding="utf-8"))


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
        "AGENTS.md": GENERATED_AGENTS,
        "CLAUDE.md": GENERATED_CLAUDE,
        "CODEX_START_PROMPT.md": GENERATED_CODEX_PROMPT,
        "CLAUDE_START_PROMPT.md": GENERATED_CLAUDE_PROMPT,
        "HANDOFF.md": GENERATED_HANDOFF,
        "scripts/harness.py": GENERATED_WRAPPER,
        "scripts/check_repo.py": GENERATED_CHECK_REPO,
        ".harness/.gitattributes": "*.json text eol=lf\n",
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
                "authorized_actions": [],
                "excluded_actions": [],
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
