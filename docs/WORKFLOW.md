# Workflow

## Default path

`USER_DIRECTED` is the default execution mode. A project may start in discovery with `state.current_plan: null` and no PLAN/TASK records. When planning becomes concrete, create the PLAN; before implementation, select it as `state.current_plan` and create a TASK listed in that PLAN. The explicit user request authorizes ordinary execution of the TASK without PLAN approval.

```text
request -> discovery/specification -> identify/update PLAN -> create/select TASK -> inspect worktree
-> implement -> test -> commit -> fetch/resolve -> push
```

The PLAN/TASK link and task gate are required when execution begins. Discovery itself does not need placeholder records. A routine task does not need PLAN approval, a claim, result, event, or evidence record.

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

In `USER_DIRECTED` mode, `current_plan` may be null during discovery but is mandatory before `BUILDING`. `active_plan`, `active_decision`, and PLAN approval are not required for routine execution. Entering production or final customer acceptance still uses the high-risk boundary. Project closure may require evidence when the project actually claims its closure contract.

## Checks

```powershell
python scripts/harness.py doctor
python scripts/harness.py status
python scripts/harness.py validate --strict
python scripts/check_repo.py fast
python scripts/check_repo.py full
```

`fast` is for iteration; `full` is for release, handoff, result, or push. Never report an unrun, blocked, partial, inconclusive, or failed check as PASS.
