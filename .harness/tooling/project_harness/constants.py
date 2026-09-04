from __future__ import annotations

HARNESS_DIR = ".harness"

# A harness governs exactly one project: the repository it lives in.  The
# project record therefore carries a fixed marker rather than a chosen
# identity, so nothing addresses the project by name.
PROJECT_RECORD_ID = "PROJECT"

RECORD_DIRECTORIES = {
    "source": ("sources", "SRC-"),
    "artifact": ("artifacts", "ART-"),
    "requirement": ("requirements", "REQ-"),
    "feature": ("features", "FUNC-"),
    "plan": ("plans", "PLAN-"),
    "work_item": ("work-items", "TASK-"),
    "open_item": ("open-items", "OI-"),
    "evidence": ("evidence", "EVD-"),
    "approval": ("approvals", "APR-"),
    "change": ("changes", "CR-"),
    "result": ("results", "RES-"),
    "review": ("reviews", "VRD-"),
    "handoff": ("handoffs", "HOF-"),
    "recovery": ("recoveries", "RCV-"),
}

RECORD_EXTENSIONS = {
    kind: ".md" if kind in {"plan", "work_item"} else ".json"
    for kind in RECORD_DIRECTORIES
}

RECORD_KIND_ALIASES = {
    "task": "work_item",
    "work-item": "work_item",
    "open-item": "open_item",
}

PROJECT_LIFECYCLE_STATES = {
    "OPPORTUNITY",
    "DISCOVERY",
    "CONTRACTED",
    "SPECIFYING",
    "PLANNING",
    "DECISION_READY",
    "APPROVED",
    "BUILDING",
    "VERIFYING",
    "CUSTOMER_ACCEPTANCE",
    "DEPLOYING",
    "CLOSED",
    "MAINTAINING",
    "ON_HOLD",
    "CANCELLED",
}

OPEN_ITEM_ACTIVE_STATES = {
    "OPEN",
    "ANALYZING",
    "WAITING_DECISION",
    "WAITING_EXTERNAL",
    "DECISION_READY",
    "BLOCKED",
    "DEFERRED",
    "REOPENED",
}

OPEN_ITEM_CLOSED_STATES = {"RESOLVED", "CANCELLED"}
OPEN_ITEM_STATES = OPEN_ITEM_ACTIVE_STATES | OPEN_ITEM_CLOSED_STATES

APPROVED_DECISIONS = {"APPROVED", "APPROVED_WITH_CONDITIONS"}

APPROVAL_DECISIONS = {
    *APPROVED_DECISIONS,
    "REVISION_REQUIRED",
    "DEFERRED",
    "REJECTED",
    "REVOKED",
}

APPROVAL_ASSURANCE_LEVELS = {
    "PROCEDURAL",
    "CRYPTOGRAPHIC",
}

# Routine decisions can be recorded procedurally when a project chooses to
# retain them. The high-impact set below is code-forced to cryptographic
# assurance and cannot be weakened by project configuration.
CRYPTOGRAPHIC_APPROVAL_TYPES = {
    "PRODUCTION_DEPLOYMENT",
    "PRODUCTION_DATA_CHANGE",
    "DESTRUCTIVE_ACTION",
    "SECRET_ACCESS",
    "CUSTOMER_ACCEPTANCE",
}

PROCEDURAL_APPROVAL_TYPES = {
    "PLAN",
    "PROJECT_CLOSURE",
    "CHANGE",
    "EXCEPTION",
}

PROCEDURAL_PLAN_ACTIONS = {
    "LOCAL_IMPLEMENTATION",
    "LOCAL_TESTS",
    "DOCUMENTATION",
}

CAPABILITY_APPROVAL_TYPES = {
    "PRODUCTION_DEPLOYMENT": "PRODUCTION_DEPLOYMENT",
    "PRODUCTION_DATA_CHANGE": "PRODUCTION_DATA_CHANGE",
    "DESTRUCTIVE_CLEANUP": "DESTRUCTIVE_ACTION",
    "SECRET_ACCESS": "SECRET_ACCESS",
}

NEVER_AGENT_CAPABILITIES = {"HUMAN_PRIVATE_KEY_ACCESS"}

EVIDENCE_RESULTS = {
    "NOT_TESTED",
    "COLLECTED",
    "PARTIAL",
    "INCONCLUSIVE",
    "FAILED",
    "VERIFIED",
    "STALE",
    "REVOKED",
}

EXIT_PASS = 0
EXIT_INVALID = 1
EXIT_BLOCKED = 2
EXIT_STALE = 3
EXIT_USAGE = 4
