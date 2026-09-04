# Workflow

## Default path

`PLAN_GATED` is the only execution mode. A project may start in discovery with `state.current_plan: null` and no PLAN/TASK records. When planning becomes concrete, create the PLAN and a TASK listed in it. Before implementation, a human project owner must approve the PLAN and `plan apply-decision` must materialize that current decision.

```text
request -> discovery/specification -> identify/update PLAN -> create/select TASK -> human approval
-> apply decision -> inspect worktree -> implement -> test -> commit -> fetch/resolve -> push
```

`harness.py next` reports which of those steps the project is on and the command
that performs it. `status` describes the project; `next` says what to do about
it. The commands it names — `new plan`, `new task --plan`, `approval confirm`
for the routine owner decision or `approval prepare`/`approval record` for a
signed one, `plan apply-decision`, `transition` — maintain the PLAN/TASK link
and every derived field themselves, so this path never requires hand-editing
front matter. Approval subjects are paths: the decision binds the exact file it
fingerprints. See [Human approval operations](APPROVALS.md).

The PLAN/TASK link, current human PLAN decision, and task gate are required when execution begins. Discovery itself does not need placeholder records.

PLAN and TASK are created as `.md` files. Agents update governed fields in the YAML-style front matter and may use the body for human-readable rationale, sequencing notes, or implementation context. Only front matter participates in validation and authority.

## When the harness becomes strict

The harness adds a gate only where the consequence needs one:

1. Concurrent writers use claims and non-overlapping worktrees/paths.
2. `blocked_by` and active `G0/G1` items block the affected governed command.
3. A verification/completion assertion needs current eligible evidence.
4. Production, production-data, destructive, secret-access, and final-customer-acceptance actions need cryptographic approval.

Unknown state, invalid events, stale evidence, unsafe paths, and malformed high-risk approvals fail closed.

## Required work trace and optional audit trace

```text
source -> requirement -> feature -> completion criterion -> work item
                                                        -> evidence/result -> review
```

PLAN and TASK are present once execution is prepared, providing sequencing, scope, dependencies, and accountability. Source, requirement, feature, result, review, and evidence records are added according to the project's specification, audit, release, and completion needs.

## Lifecycle

The lifecycle remains descriptive:

```text
OPPORTUNITY -> DISCOVERY -> CONTRACTED -> SPECIFYING -> PLANNING
-> DECISION_READY -> APPROVED -> BUILDING -> VERIFYING
-> CUSTOMER_ACCEPTANCE -> DEPLOYING -> CLOSED -> MAINTAINING
```

During discovery, `current_plan` may be null. Before `BUILDING`, `active_plan` and `active_decision` must materialize a current human PLAN approval. Entering production or final customer acceptance still uses the high-risk boundary. Project closure may require evidence when the project actually claims its closure contract.

## Starting over

`reset --confirm <directory name>` returns the harness to the shape `init` produces: every canonical record, plus `events/`, `baselines/`, and `decisions/`, is cleared, and `project.json`, `state.json`, and `HANDOFF.md` are regenerated from the same builders `init` uses. Shared runtime registries are cleared so record numbering restarts at `0001`.

Files `init` does not create are never touched. The project name and policy survive, because a reset restarts the work rather than the project. The human decision runtime survives too: its monotonic sequence and latest-decision markers make a recorded human confirmation non-replayable, and a reset is agent-reachable, so it must not roll back a control that bounds human authority.

`--dry-run` reports the same summary without writing and needs no confirmation. Everything a reset removes is snapshotted to `.harness/runtime/reset-<timestamp>/` first.

## Checks

```powershell
python scripts/harness.py doctor
python scripts/harness.py status
python scripts/harness.py validate --strict
python scripts/check_repo.py fast
python scripts/check_repo.py full
```

`fast` is for iteration; `full` is for release, handoff, result, or push. Never report an unrun, blocked, partial, inconclusive, or failed check as PASS.
