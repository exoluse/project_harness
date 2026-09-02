# Project Agent Harness

Project Agent Harness is a repository-native coordination and evidence layer for work performed by people and coding agents. Its default model is deliberately lightweight: the user's explicit request drives ordinary execution, while the harness becomes strict only at concurrency, high-risk action, and claimed-completion boundaries.

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

- ordinary development, tests, commits, fetch, conflict resolution, and a normal push to the configured upstream are allowed by an explicit user request;
- `PLAN-*` is planning/reference material, not a per-task permission token;
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

Plans help organize that trace but do not authorize routine execution in `USER_DIRECTED` mode. Evidence is required when a command asserts a governed verification, customer acceptance, production outcome, or project closure—not just because a developer edits a file.

## Verification tiers

```powershell
python scripts/check_repo.py fast
python scripts/check_repo.py full
# bare invocation is full
python scripts/check_repo.py
```

Both tiers compile and run strict harness validation. `fast` runs focused contract tests; `full` runs all tests. Commands stored in mutable JSON are never auto-executed.

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
- `.harness/state.json`: current lifecycle and active references
- `.harness/plans/`: optional planning and historical baselines
- `.harness/work-items/`: optional decomposed work
- `.harness/events/`, `results/`, `evidence/`: on-demand audit records
- `<git-common-dir>/project-harness-runtime/`: shared transient claims and mailboxes

Additional details: [Workflow](docs/WORKFLOW.md), [Architecture](docs/ARCHITECTURE.md), [Record model](docs/RECORD_MODEL.md).
