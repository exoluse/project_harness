# Project Agent Harness

Project Agent Harness is a repository-native planning, coordination, and evidence layer for work performed by people and coding agents. A project may begin with discovery alone; before implementation, it needs a current human PLAN approval and every change has a TASK in that PLAN. A user request never substitutes for that approval.

## Default operating model

New projects use:

```json
{
  "execution_mode": "PLAN_GATED",
  "claim_mode": "WHEN_CONCURRENT",
  "record_mode": "ON_DEMAND"
}
```

This means:

- a newly initialized project starts in `DISCOVERY` with `current_plan: null` and no invented PLAN/TASK placeholders;
- before implementation, the project creates a `PLAN-*` and a `TASK-*` listed in it, obtains the human PLAN signature, and applies its current decision;
- PLAN and TASK are readable `.md` documents with strict machine-validated front matter; state and audit records remain JSON;
- every later change is represented by a TASK listed in its PLAN;
- ordinary development, tests, commits, fetch, conflict resolution, and a normal push to the configured upstream are allowed only after the current human PLAN decision has been applied;
- PLAN approval is an execution permission bound to the exact plan fingerprint and declared TASKs;
- a claim is needed only when multiple writers are active;
- results, events, and evidence are created automatically by commands that need them or explicitly when audit, review, release, acceptance, or completion proof requires them;
- Approval for production deployment, production data changes, destructive operations, secret access, and final customer acceptance is cryptographically verified; routine PLAN approval records a direct human confirmation.

`USER_DIRECTED` is not supported: a repository policy cannot disable the human approval gate.

## Use it: copy the folder

This folder is the harness. Copy it (or clone it, or use it as a GitHub
template) to where the project lives, name the project, and start:

```powershell
git clone <this-repository> C:\work\my-project     # or copy the folder into an existing repo
cd C:\work\my-project
python scripts/harness.py next                      # → NEEDS_PROJECT_IDENTITY, with the command below
python scripts/harness.py init . --project-id MYPROJECT --name "My Project"
python scripts/harness.py next                      # → NEEDS_PLAN
```

`init .` writes the project identity (`.harness/project.json`, `state.json`),
the empty record directories, and any root file that is missing; it never
overwrites a file you already have. The runtime lives in `.harness/tooling/`,
so the project depends on nothing outside its own tree. Dropping the same
files into an existing repository works the same way.

Everything a project receives — the agent policy, schemas, verification
script, and runtime — comes from `.harness/tooling/project_harness/assets/`;
the root `AGENTS.md`, `docs/`, `schemas/`, and `scripts/` are copies of it.
`init --force` repairs the runtime without touching canonical records.

The package can also be installed (`pip install <this-folder>`) and used as
`project-harness init <path> ...` to generate a project elsewhere.

## Routine agent workflow

`next` reports the single step that moves the project forward, and every step it
names is a command. Reaching a startable TASK from a fresh `init` never requires
editing a record by hand:

```powershell
git status --short
python scripts/harness.py next
python scripts/harness.py new plan PLAN-0001 "Describe the change"
python scripts/harness.py new task TASK-0001 "Describe the work" --plan PLAN-0001 --capability LOCAL_IMPLEMENTATION
python scripts/harness.py approval prepare --type PLAN --subject PLAN-0001 ...
# Human owner signs the prepared request outside the repository.
python scripts/harness.py approval record --request <file> --signature <file>
python scripts/harness.py plan apply-decision --approval APR-0001
python scripts/harness.py transition --kind work_item --id TASK-0001 --to READY --agent codex --reason "approved plan"
python scripts/harness.py gate task TASK-0001
# implement the user's request
python scripts/check_repo.py fast
git add -- <explicit paths>
git commit -m "Describe the change"
git fetch --prune <configured-remote>
git push
```

`new task` requires `--plan` and maintains both sides of the relationship: the
TASK's `plan_id`, the PLAN's `work_item_refs`, and the derived
`approval_dependencies`, in one atomic mutation. `plan apply-decision` alone
sets the approved plan and `state.current_plan` together after the human
signature is verified. `plan sync` rebuilds derived dependencies if a record
was edited by hand.

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

PLAN and TASK form the mandatory execution structure but are not generated as empty initialization placeholders. Discovery and specification may happen before they exist. Once implementation is ready, `state.current_plan` and `active_decision` must identify the current human-approved PLAN, every TASK points to a PLAN, and every PLAN lists its TASKs. Evidence is required when a command asserts a governed verification, customer acceptance, production outcome, or project closure—not just because a developer edits a file.

PLAN and TASK files use strict YAML-style front matter followed by a normal Markdown body. The front matter is canonical for validation, fingerprints, and gates. The body is preserved across harness mutations for human notes, but it is non-authoritative. The parser uses a deliberately small dependency-free subset: two-space indentation, quoted JSON scalars, arrays, and objects. Malformed front matter fails closed. Legacy PLAN/TASK JSON remains readable for compatibility, while newly created records use Markdown.

## Verification tiers

```powershell
python scripts/check_repo.py fast
python scripts/check_repo.py full
# bare invocation is full
python scripts/check_repo.py
```

Both tiers compile the project and run strict harness validation. `full` also runs the project's own `tests/` and reports `SKIPPED` when there are none yet, so a freshly named project passes its own verification before the first test is written. Commands stored in mutable records are never auto-executed.

`--self-test` additionally runs the harness runtime's own tests under `.harness/tooling/tests/`; a project's verification is otherwise about the project, not the harness.

## Developing the harness

The runtime is edited in place at `.harness/tooling/project_harness/`; its tests sit beside it. This repository carries no project identity of its own, so `next` on a fresh checkout reports `NEEDS_PROJECT_IDENTITY` — that is the state a copied folder starts in.

```powershell
python scripts/check_repo.py full --self-test          # runtime tests on the bare template
python scripts/harness.py init . --project-id DEV --name "Dev"   # then exercise it as a project
```

A drift test fails when a root copy (`AGENTS.md`, `docs/`, `schemas/`, `scripts/`) no longer matches its asset.

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
- `.harness/state.json`: current lifecycle, nullable discovery-time `current_plan`, and the active human PLAN decision before implementation
- `.harness/plans/PLAN-*.md`: human-readable execution plans
- `.harness/work-items/TASK-*.md`: human-readable executable work units
- `.harness/events/`, `results/`, `evidence/`: on-demand audit records
- `.harness/tooling/project_harness/`: the runtime and its `assets/` (policy, schemas, scripts)
- `<git-common-dir>/project-harness-runtime/`: shared transient claims and mailboxes

Additional details: [Workflow](docs/WORKFLOW.md), [Architecture](docs/ARCHITECTURE.md), [Data model](docs/DATA_MODEL.md).
