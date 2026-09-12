# Architecture

The harness separates three concerns that should not be confused:

```text
discovery / requirements / design -> authored PLAN and TASKs -> planning complete
owner prompt decision -> agent records/applies decision -> runtime TASK gate -> execution ready -> implementation
concurrent writers -> claims / worktrees / handoffs
high-risk action -> protected cryptographic approval
```

Planning-only work ends after authoring and required planning checks, without
requesting execution approval. Execution readiness is a separate boundary;
it does not add a second decision for the same concrete change. These are
policy milestones, not new runtime states. The full project sequence through
verification, acceptance, delivery and closure is in the
[HTML guide](HARNESS_POLICY_REPORT.html); [Development method](DEVELOPMENT_METHOD.md#planning-complete-and-execution-ready)
defines the criteria.

The owner approves the reviewed scope through a prompt. The agent maintains
the decision's source and binds it to the prepared proposal; the runtime checks
the record and execution prerequisites. A gate is not an approval authority:
PASS creates no consent, and failure does not erase a prior decision. See
[approval roles](APPROVALS.md#who-decides-and-who-checks).

## Policy modes

`.harness/project.json` selects:

- `execution_mode`: always `PLAN_GATED`; it is not repository-configurable as an execution bypass;
- `claim_mode`: `WHEN_CONCURRENT` or legacy `REQUIRED`;
- `record_mode`: `ON_DEMAND` or legacy `REQUIRED`.

New projects use the first value in each pair. Missing fields retain legacy behavior so older repositories do not silently become less strict.

## Stores

- A harness governs one project: the repository it lives in. `project.json` carries a fixed `PROJECT` marker and a human `name`, so no record, command, or approval addresses the project by an identity string.
- Canonical records live in `.harness/` in the working tree. The harness reads, validates, fingerprints, and gates them there; whether a project commits them to Git is the project's own choice, and no gate depends on a record's Git history.
- The runtime and the record schemas it validates against live in `.harness/tooling/project_harness/`; the project tree holds no second copy.
- Human-authored PLAN/TASK records use Markdown with strict YAML-style front matter; machine state and audit records use JSON. `docs/RECORD_FORMAT.md` specifies the decided move of every record to Markdown.
- `state.current_plan` may be null during initial discovery. It becomes mandatory execution context before implementation; every TASK points to that PLAN and is listed by it.
- `state.active_plan` and `active_decision` materialize the current human PLAN decision and are required before routine implementation. Today no command sets `active_plan`; `docs/RUNTIME_GAPS.md` item 1 records the interim step and the decided fix.
- Claims, mutexes, and mailboxes live under the Git common runtime so linked worktrees share concurrency state.
- Protected approval configuration, allowed signers, and decision ledgers live outside the repository.
- `HANDOFF.md` and reports are derived views, not authority.

## Mutation boundary

Evidence attachment and lifecycle transitions use one atomic mutation service. In `WHEN_CONCURRENT` mode they may run without a claim when no active claim overlaps their targets. If an overlapping claim exists, the unclaimed mutation fails closed. In legacy `REQUIRED` mode a current matching claim is mandatory.

Explicit record-producing commands may emit an event atomically. Ordinary filesystem development does not create audit events merely to obtain permission.

When a PLAN or TASK mutation is written, the mutation service rewrites only its canonical front matter and preserves the Markdown body. Parsing, schema validation, and atomic commit all complete before the record becomes visible. Invalid front matter, duplicate keys, mixed container types, odd indentation, and unquoted invalid scalars fail closed.

## Evaluation

An evaluation context caches records and validation for one command. Gates still enforce declared blockers, open-item scope, evidence freshness, high-risk approval currentness, and event integrity. `fast` and `full` verification tiers share those contracts while differing in test breadth.
