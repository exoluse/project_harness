from __future__ import annotations

HARNESS_DIR = ".harness"

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
