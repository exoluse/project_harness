# Workflow

## Default path

`USER_DIRECTED` is the default execution mode. An explicit user request is sufficient for ordinary implementation, tests, documentation, commits, fetch, conflict resolution, and a normal push to the configured upstream.

```text
request -> inspect worktree -> implement -> test -> commit -> fetch/resolve -> push
```

Plans and work items can organize the work, but they do not gate this path. A routine task does not need a claim, result, event, or evidence record.

## When the harness becomes strict

The harness adds a gate only where the consequence needs one:

1. Concurrent writers use claims and non-overlapping worktrees/paths.
2. `blocked_by` and active `G0/G1` items block the affected governed command.
3. A verification/completion assertion needs current eligible evidence.
4. Production, production-data, destructive, secret-access, and final-customer-acceptance actions need cryptographic approval.

Unknown state, invalid events, stale evidence, unsafe paths, and malformed high-risk approvals fail closed.

## Optional trace

```text
source -> requirement -> feature -> completion criterion -> work item
                                                        -> evidence/result -> review
```

Create only the records the project needs. A plan remains useful for sequencing and impact analysis. A result is useful for independent review or release lineage. Evidence is useful for an asserted criterion, acceptance, or closure state. None is paperwork required merely to start editing.

## Lifecycle

The lifecycle remains descriptive:

```text
OPPORTUNITY -> DISCOVERY -> CONTRACTED -> SPECIFYING -> PLANNING
-> DECISION_READY -> APPROVED -> BUILDING -> VERIFYING
-> CUSTOMER_ACCEPTANCE -> DEPLOYING -> CLOSED -> MAINTAINING
```

In `USER_DIRECTED` mode, entering `BUILDING` does not require an active plan. Entering production or final customer acceptance still uses the high-risk boundary. Project closure may require evidence when the project actually claims its closure contract.

## Checks

```powershell
python scripts/harness.py doctor
python scripts/harness.py status
python scripts/harness.py validate --strict
python scripts/check_repo.py fast
python scripts/check_repo.py full
```

`fast` is for iteration; `full` is for release, handoff, result, or push. Never report an unrun, blocked, partial, inconclusive, or failed check as PASS.
