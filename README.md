# Project Agent Harness

Project Agent Harness is a repository-native planning, coordination, and evidence layer for work performed by people and coding agents. A project may begin with discovery alone; before implementation, it selects a current PLAN and every change has a TASK in that PLAN. The user's explicit request authorizes routine execution of that structure.

## Default operating model

New projects use:

```json
{
  "execution_mode": "USER_DIRECTED",
  "claim_mode": "WHEN_CONCURRENT",
  "record_mode": "ON_DEMAND"
}
```

This means:

- a newly initialized project starts in `DISCOVERY` with `current_plan: null` and no invented PLAN/TASK placeholders;
- before implementation, the project selects a current `PLAN-*` and creates a `TASK-*` listed in it;
- PLAN and TASK are readable `.md` documents with strict machine-validated front matter; state and audit records remain JSON;
- every later change is represented by a TASK listed in its PLAN;
- ordinary development, tests, commits, fetch, conflict resolution, and a normal push to the configured upstream are allowed by an explicit user request for that TASK;
- PLAN approval is not a per-task permission token;
- a claim is needed only when multiple writers are active;
- results, events, and evidence are created automatically by commands that need them or explicitly when audit, review, release, acceptance, or completion proof requires them;
- cryptographic approval is reserved for production deployment, production data changes, destructive operations, secret access, and final customer acceptance.

The older `PLAN_GATED` / `REQUIRED` modes remain readable for existing repositories that intentionally need that workflow.

## Install and initialize

The generated project is self-contained and does not depend on this source checkout:

```powershell
python -m project_harness.cli init C:\work\my-project --project-id MYPROJECT --name "My Project"
cd C:\work\my-project
python scripts/harness.py doctor
python scripts/harness.py status
python scripts/harness.py validate --strict
```

`init --force` repairs distributed runtime files without overwriting canonical project records. It fails closed on unsafe or incompatible targets.

## Routine agent workflow

```powershell
git status --short
python scripts/harness.py status
python scripts/harness.py gate task TASK-0001
# implement the user's request
python scripts/check_repo.py fast
git add -- <explicit paths>
git commit -m "Describe the change"
git fetch --prune <configured-remote>
git push
```

Before push, inspect upstream divergence. Resolve conflicts without resetting or discarding either side. Force push, tag push, branch deletion, or another target requires separate explicit authorization.

## Concurrent writers

Claims are optional coordination leases, not execution permits. Use them only when agents or other writers overlap in time:

```powershell
python scripts/harness.py claim acquire --agent codex --task TASK-0001 --paths src tests
python scripts/harness.py mailbox list --box inbox --agent codex
```

Prefer separate Git worktrees and non-overlapping paths. Use a handoff when ownership of dirty in-progress work changes. See [Collaboration](docs/COLLABORATION.md).

## Plans and trace records

The trace model remains available:

```text
source -> requirement -> feature -> criterion -> work item
                                      -> evidence/result -> review
```

PLAN and TASK form the mandatory execution structure but are not generated as empty initialization placeholders. Discovery and specification may happen before they exist. Once implementation is ready, `state.current_plan` names the current planning reference, every TASK points to a PLAN, and every PLAN lists its TASKs. PLAN approval does not authorize routine execution in `USER_DIRECTED` mode; the explicit user request does. Evidence is required when a command asserts a governed verification, customer acceptance, production outcome, or project closure—not just because a developer edits a file.

PLAN and TASK files use strict YAML-style front matter followed by a normal Markdown body. The front matter is canonical for validation, fingerprints, and gates. The body is preserved across harness mutations for human notes, but it is non-authoritative. The parser uses a deliberately small dependency-free subset: two-space indentation, quoted JSON scalars, arrays, and objects. Malformed front matter fails closed. Legacy PLAN/TASK JSON remains readable for compatibility, while newly created records use Markdown.

## Verification tiers

```powershell
python scripts/check_repo.py fast
python scripts/check_repo.py full
# bare invocation is full
python scripts/check_repo.py
```

Both tiers compile and run strict harness validation. `fast` runs focused contract tests; `full` runs all tests. Commands stored in mutable records are never auto-executed.

## High-risk approval

These boundaries are always cryptographic and fail closed:

- `PRODUCTION_DEPLOYMENT`
- `PRODUCTION_DATA_CHANGE`
- `DESTRUCTIVE_ACTION`
- `SECRET_ACCESS`
- `CUSTOMER_ACCEPTANCE`

The protected authority configuration and ledger live outside the repository. Agents may prepare a request but cannot sign, install, infer, or self-grant approval. See [Human approval operations](docs/APPROVALS.md) and [Security](docs/SECURITY.md).

## Key paths

- `.harness/project.json`: project policy and completion contract
- `.harness/state.json`: current lifecycle, nullable discovery-time `current_plan`, and optional approval references
- `.harness/plans/PLAN-*.md`: human-readable execution plans
- `.harness/work-items/TASK-*.md`: human-readable executable work units
- `.harness/events/`, `results/`, `evidence/`: on-demand audit records
- `<git-common-dir>/project-harness-runtime/`: shared transient claims and mailboxes

Additional details: [Workflow](docs/WORKFLOW.md), [Architecture](docs/ARCHITECTURE.md), [Record model](docs/RECORD_MODEL.md).
