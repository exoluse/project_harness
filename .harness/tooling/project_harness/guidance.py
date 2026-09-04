from __future__ import annotations

from pathlib import Path
from typing import Any

from .authoring import RETIRED_PLAN_STATUSES, next_record_id
from .constants import HARNESS_DIR
from .core import load_json
from .evaluation import EvaluationContext
from .gates import task_start_gate
from .policy import execution_mode, user_directed

# Mirrors the startable set enforced by ``gates.task_start_gate``.
STARTABLE_TASK_STATUSES = {"READY", "APPROVED", "RUNNING"}
TERMINAL_TASK_STATUSES = {"INTEGRATED", "DONE", "CLOSED"}

HARNESS = "python scripts/harness.py"

# Validation codes this command can point at a repair command.
REPAIRABLE_CODES = {"UNBOUND_PLAN_DEPENDENCY"}


def _plan_tasks(plan: dict[str, Any]) -> list[str]:
    subject = plan.get("approval_subject")
    if not isinstance(subject, dict):
        return []
    refs = subject.get("work_item_refs")
    if not isinstance(refs, list):
        return []
    return [value for value in refs if isinstance(value, str)]


def _plan_id_from_path(value: str | None) -> str | None:
    if not value:
        return None
    stem = Path(value).stem
    return stem if stem.startswith("PLAN-") else None


def _repair_commands(errors: list[Any]) -> list[str]:
    commands: list[str] = []
    for issue in errors:
        if issue.code not in REPAIRABLE_CODES:
            return []
        plan_id = _plan_id_from_path(issue.path)
        if plan_id is None:
            return []
        command = f"{HARNESS} plan sync {plan_id}"
        if command not in commands:
            commands.append(command)
    return commands


def next_step(root: Path) -> dict[str, Any]:
    """Report the single next step that moves this project forward.

    ``status`` describes the project; this describes what to do about it. It is
    the orientation command for an agent working only from a user's prompt.
    """
    root = root.resolve()
    if not (root / HARNESS_DIR / "project.json").is_file():
        # A copied template: the runtime is here, the project identity is not.
        return {
            "project_id": None,
            "execution_mode": None,
            "lifecycle_state": None,
            "current_plan": None,
            "state": "NEEDS_PROJECT_IDENTITY",
            "summary": "this folder carries the harness but no project yet; name it",
            "commands": [f'{HARNESS} init . --project-id <PROJECT-ID> --name "<Project name>"'],
            "details": [],
            "warnings": [],
        }
    context = EvaluationContext.load(root)
    state = load_json(root / HARNESS_DIR / "state.json")
    project = load_json(root / HARNESS_DIR / "project.json")

    report: dict[str, Any] = {
        "project_id": project.get("id"),
        "execution_mode": execution_mode(root),
        "lifecycle_state": state.get("lifecycle_state"),
        "current_plan": state.get("current_plan"),
    }

    # `validate --strict` fails on warnings too, so they are part of what an
    # agent must see before it reports a task complete.
    warnings = [
        f"{issue.code}: {issue.message}"
        for issue in context.validation_issues
        if issue.severity == "WARNING"
    ]

    def step(
        name: str,
        summary: str,
        commands: list[str],
        details: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            **report,
            "state": name,
            "summary": summary,
            "commands": commands,
            "details": details or [],
            "warnings": warnings,
        }

    errors = [issue for issue in context.validation_issues if issue.severity == "ERROR"]
    if errors:
        repairs = _repair_commands(errors)
        return step(
            "PROJECT_INVALID",
            f"{len(errors)} validation error(s) block every gate; resolve them first",
            repairs or [f"{HARNESS} validate --strict"],
            [f"{issue.code}: {issue.message}" for issue in errors],
        )

    records = context.records
    plans = {
        record_id: record
        for record_id, record in records.items()
        if record.get("kind") == "plan"
    }
    if not plans:
        return step(
            "NEEDS_PLAN",
            "no PLAN exists; create one describing the requested change",
            [f'{HARNESS} new plan {next_record_id(root, "plan")} "<plan title>"'],
        )

    current_plan_id = state.get("current_plan")
    plan = plans.get(current_plan_id) if isinstance(current_plan_id, str) else None
    if plan is None:
        candidates = sorted(
            record_id
            for record_id, record in plans.items()
            if record.get("status") not in RETIRED_PLAN_STATUSES
        )
        if not candidates:
            return step(
                "NEEDS_PLAN",
                "every PLAN is retired; create one for the requested change",
                [f'{HARNESS} new plan {next_record_id(root, "plan")} "<plan title>"'],
            )
        target = candidates[-1]
        if not _plan_tasks(plans[target]):
            return step(
                "NEEDS_TASK",
                f"PLAN {target} lists no TASK; add one before activating it",
                [
                    f'{HARNESS} new task {next_record_id(root, "work_item")} '
                    f'"<task title>" --plan {target}'
                ],
                [f"candidate plans: {', '.join(candidates)}"],
            )
        if not user_directed(root):
            return step(
                "NEEDS_PLAN_APPROVAL",
                f"PLAN_GATED projects activate {target} through the approval workflow",
                [
                    f"{HARNESS} approval prepare --type PLAN --subject {target} ...",
                    f"{HARNESS} approval record --request <file> --signature <file>",
                    f"{HARNESS} plan apply-decision --approval <APR-ID>",
                ],
            )
        return step(
            "NEEDS_PLAN_ACTIVATION",
            f"no current PLAN is selected; activate {target}",
            [f"{HARNESS} plan activate {target}"],
            [f"candidate plans: {', '.join(candidates)}"],
        )

    linked = _plan_tasks(plan)
    if not linked:
        return step(
            "NEEDS_TASK",
            f"current PLAN {current_plan_id} lists no TASK",
            [
                f'{HARNESS} new task {next_record_id(root, "work_item")} '
                f'"<task title>" --plan {current_plan_id}'
            ],
        )

    ready: list[str] = []
    needs_ready: list[str] = []
    blocked: list[tuple[str, list[str]]] = []
    open_tasks = 0
    for task_id in linked:
        task = records.get(task_id)
        if task is None or task.get("kind") != "work_item":
            blocked.append((task_id, [f"task {task_id} is missing"]))
            open_tasks += 1
            continue
        status = task.get("status")
        if status in TERMINAL_TASK_STATUSES:
            continue
        open_tasks += 1
        gate = task_start_gate(root, task_id, context=context)
        if gate.passed:
            ready.append(task_id)
            continue
        status_blocker = f"task status {status} is not startable"
        remaining = [value for value in gate.blockers if value != status_blocker]
        if status not in STARTABLE_TASK_STATUSES and not remaining:
            needs_ready.append(task_id)
        else:
            blocked.append((task_id, gate.blockers))

    if ready:
        target = ready[0]
        return step(
            "READY",
            f"TASK {target} passes TASK_START; implement the user's request now",
            [f"{HARNESS} gate task {target}"],
            [f"startable tasks: {', '.join(ready)}"],
        )
    if needs_ready:
        target = needs_ready[0]
        return step(
            "NEEDS_TASK_READY",
            f"TASK {target} is otherwise startable but is not in a startable status",
            [
                f"{HARNESS} transition --kind work_item --id {target} --to READY "
                f'--agent <agent> --reason "<why>"'
            ],
        )
    if open_tasks == 0:
        return step(
            "NEEDS_TASK",
            f"every TASK in {current_plan_id} is complete; add one for the new change",
            [
                f'{HARNESS} new task {next_record_id(root, "work_item")} '
                f'"<task title>" --plan {current_plan_id}'
            ],
        )
    target, blockers = blocked[0]
    return step(
        "TASK_BLOCKED",
        f"TASK {target} cannot start yet",
        [f"{HARNESS} gate task {target}"],
        blockers,
    )
