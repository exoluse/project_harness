# Architecture

The harness separates three concerns that should not be confused:

```text
user request -> routine execution
concurrent writers -> claims / worktrees / handoffs
high-risk action -> protected cryptographic approval
```

## Policy modes

`.harness/project.json` selects:

- `execution_mode`: `USER_DIRECTED` or legacy `PLAN_GATED`;
- `claim_mode`: `WHEN_CONCURRENT` or legacy `REQUIRED`;
- `record_mode`: `ON_DEMAND` or legacy `REQUIRED`.

New projects use the first value in each pair. Missing fields retain legacy behavior so older repositories do not silently become less strict.

## Stores

- Canonical records live in `.harness/` and are versioned with the repository.
- Plans are references/baselines. `state.active_plan` names an active execution baseline only when a project intentionally uses one.
- Claims, mutexes, and mailboxes live under the Git common runtime so linked worktrees share concurrency state.
- Protected approval configuration, allowed signers, and decision ledgers live outside the repository.
- `HANDOFF.md` and reports are derived views, not authority.

## Mutation boundary

Evidence attachment and lifecycle transitions use one atomic mutation service. In `WHEN_CONCURRENT` mode they may run without a claim when no active claim overlaps their targets. If an overlapping claim exists, the unclaimed mutation fails closed. In legacy `REQUIRED` mode a current matching claim is mandatory.

Explicit record-producing commands may emit an event atomically. Ordinary filesystem development does not create audit events merely to obtain permission.

## Evaluation

An evaluation context caches records and validation for one command. Gates still enforce declared blockers, open-item scope, evidence freshness, high-risk approval currentness, and event integrity. `fast` and `full` verification tiers share those contracts while differing in test breadth.
