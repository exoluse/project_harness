from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import HARNESS_DIR
from .core import HarnessError, load_json


EXECUTION_MODES = {"USER_DIRECTED", "PLAN_GATED"}
CLAIM_MODES = {"WHEN_CONCURRENT", "REQUIRED"}
RECORD_MODES = {"ON_DEMAND", "REQUIRED"}


def project_policy(root: Path) -> dict[str, Any]:
    project = load_json(root / HARNESS_DIR / "project.json")
    policy = project.get("policy", {})
    if not isinstance(policy, dict):
        raise HarnessError("Project policy is malformed")
    return policy


def execution_mode(root: Path) -> str:
    """Return the execution model; old projects remain plan-gated by default."""
    value = project_policy(root).get("execution_mode", "PLAN_GATED")
    if value not in EXECUTION_MODES:
        raise HarnessError(f"Unsupported execution mode: {value}")
    return str(value)


def user_directed(root: Path) -> bool:
    return execution_mode(root) == "USER_DIRECTED"


def claim_mode(root: Path) -> str:
    value = project_policy(root).get("claim_mode", "REQUIRED")
    if value not in CLAIM_MODES:
        raise HarnessError(f"Unsupported claim mode: {value}")
    return str(value)


def record_mode(root: Path) -> str:
    value = project_policy(root).get("record_mode", "REQUIRED")
    if value not in RECORD_MODES:
        raise HarnessError(f"Unsupported record mode: {value}")
    return str(value)


def approval_required(root: Path, approval_type: str) -> bool:
    configured = project_policy(root).get("human_approval_required_for", [])
    if not isinstance(configured, list):
        raise HarnessError("human_approval_required_for must be a list")
    return approval_type in configured
