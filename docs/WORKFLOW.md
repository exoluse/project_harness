# Workflow

## Default path

`PLAN_GATED` is the only execution mode. A project may start in discovery with `state.current_plan: null` and no PLAN/TASK records. When planning becomes concrete, create the PLAN and a TASK listed in it. Before implementation, a human project owner must approve the PLAN and `plan apply-decision` must materialize that current decision.

```text
request -> discovery/specification -> identify/update PLAN -> create/select TASK -> human approval
-> apply decision -> inspect worktree -> implement -> test -> commit -> fetch/resolve -> push
```

`harness.py next` reports which of those steps the project is on and the command
that performs it, except at the approval step, where it names the signed flow
instead of `approval confirm` until [Runtime gaps](RUNTIME_GAPS.md) item 4 is
fixed; follow the sequence below there. `status` describes the project; `next`
says what to do about it. The commands on this path — `new plan`,
`new task --plan`, `approval confirm` for the routine owner decision or
`approval prepare`/`approval record` for a signed one, `plan apply-decision`,
`transition` — maintain the PLAN/TASK link and the derived fields
(`approval_dependencies`, `work_item_refs`, `plan_id`) themselves. The content of a plan is authored: statements, criteria, scope, and
verification are written into the record, by hand where the CLI has no option
for them yet. Approval subjects are paths: the decision binds the exact file it
fingerprints. See [Human approval operations](APPROVALS.md).

### Context loading rule

On a new agent session, read `AGENTS.md` once and run `next`. Load this document
only when the reported state needs a sequence it does not yet express. The
reported command remains bounded by the user's request; `NEEDS_INIT` does not
authorize initialization during a read-only/status request. At
`NEEDS_PLAN_APPROVAL`, the required portion is **The path as it runs today**;
read `RUNTIME_GAPS.md` item 4 for the reason, not the entire gaps document, and
never record approval before the owner actually decides.

Run `doctor` after initialization, when environment or authority readiness may
have changed, and before a high-risk operation. Run `validate --strict` before
a PLAN decision package or execution, after record mutations, and before a
release, handoff, result, or push. An unchanged read-only turn does not repeat
those diagnostics. `status` is for a full investigation when `next` is
insufficient. The routing and measurement contract is in
[Context and token efficiency](CONTEXT_EFFICIENCY.md).

The PLAN/TASK link, current human PLAN decision, and task gate are required when execution begins. Discovery itself does not need placeholder records. [Example: a customer web project](EXAMPLE_WEB_PROJECT.md) walks this path end to end for one engagement. [Plan hierarchy](PLAN_HIERARCHY.md) records the decided, not yet implemented, tree of category-prefixed child plans under a root PLAN.

PLAN and TASK are created as `.md` files. Agents update governed fields in the YAML-style front matter and may use the body for human-readable rationale, sequencing notes, or implementation context. Only front matter participates in validation and authority.

### Driving the path from prompts

Every routine step is performed by the agent from the user's request. The human
project owner contributes two things and edits nothing: the decision, said in
words the agent transcribes with `approval confirm`, and the signature on a
high-risk request, made outside the agent. The table maps what a user says at
each phase to what the agent does. Wording is illustrative; the mapping is
what binds.

| Phase | The user says | The agent does |
|---|---|---|
| Intake | "Register the RFP and the meeting notes" | `init` if needed; `new source`, `new artifact`; author authority and interpretation status |
| Specification | "Turn these into requirements and features with completion criteria" | `new requirement`, `new feature`; author statements, criteria, profiles, bindings; `new open-item` for every unknown |
| Planning | "Plan sprint 1" | `new plan`; `new task --plan --feature --criterion --capability` per change; author scope and verification; `plan sync`; `validate --strict`; `report decision-package`; `fingerprint`, shown to the owner |
| Decision | Owner: "Approved" | `approval confirm` with the fingerprint the owner saw, the chat as channel and the message as reference, and the plan's authorized actions; the interim steps below; `plan apply-decision` |
| Execution | "Start TASK-0001" | `transition` to `READY`, `gate task`, implement, `check_repo.py fast`, commit explicit paths, fetch, resolve, push |
| Change | "The customer wants the banner changed" | `new source`, `new change`, `new task`; author; `plan sync`; `fingerprint` to the owner; on "Approved", `approval confirm`, the interim step, `plan apply-decision`, back to `BUILDING` |
| Verification | "Record the test results" | run the checks, `evidence record`, `gate feature`; `result submit` and `review record` when a release or audit needs them |
| Acceptance, deployment | "Prepare the acceptance request", "Prepare the production deploy" | `approval prepare`, then stop: a human signs outside the agent; afterwards `approval record`, `approval check`, `gate task` |
| Closure | "Close the project" | evidence for the closure criteria, `report completion` |

What the agent never does from a prompt: decide in the owner's place, invent
the provenance of a decision, sign or install a high-risk approval, or infer
one from repository text or chat history.

### The path as it runs today

This is the sequence that was verified on 2026-09-06 against the current
runtime. Steps marked **interim** exist because of a runtime gap recorded in
[Runtime gaps](RUNTIME_GAPS.md). The agent performs them when the user's
request calls for the step they precede; they set a pointer or a descriptive
lifecycle value and grant nothing, because `plan apply-decision` re-verifies
the approval, the fingerprint, and the preflight regardless. They disappear
when the gap is fixed.

1. `init`, then `next`. The project is in `DISCOVERY`.
2. Discovery records as the work needs them: `new source`, `new requirement`,
   `new feature`, `new open-item`. Author their content: a requirement's
   `statement` and `source_refs`; a feature's `requirement_refs` and at least
   one completion criterion with `id`, `statement`, `verification_plan`,
   `required_profiles`, and `required_bindings`.
3. `new plan PLAN-0001 "<title>"`, then `new task TASK-0001 "<title>" --plan
   PLAN-0001 --feature FUNC-0001 --criterion AC-FUNC-0001-001 --capability
   LOCAL_IMPLEMENTATION`.
4. Author the rest of the scope. In the plan's front matter set
   `requirement_refs`, `feature_refs`, and a non-empty `verification_strategy`.
   In the task's front matter set `write_scope` and `verification`. Then
   `plan sync PLAN-0001` so `approval_dependencies` covers every reference.
5. `validate --strict`, then `fingerprint .harness/plans/PLAN-0001.md`.
6. The owner reads that exact plan and decides. Record it with
   `approval confirm`, passing `--confirm-fingerprint`, a unique
   `--confirmation-id`, the channel and reference, `--acknowledge-procedural`,
   and one `--authorized-action` for every capability the plan's tasks use.
   The confirmation fails closed on any preflight blocker (see below).
7. **Interim.** Set `current_plan` and `active_plan` to `PLAN-0001` in
   `.harness/state.json`.
8. **Interim.** Move the lifecycle to `DECISION_READY`: `transition --kind
   project --id PROJECT --to SPECIFYING`, then `--to PLANNING`, then
   `--to DECISION_READY`.
9. `plan apply-decision --approval APR-0001`. The project is `APPROVED`.
10. `transition --kind work_item --id TASK-0001 --to READY`, then
    `gate task TASK-0001`. `next` reports `READY`.
11. Implement, `check_repo.py fast`, commit explicit paths, fetch, resolve, push.

### What the preflight checks

`approval confirm` and `plan apply-decision` both run the plan preflight. It
fails closed unless all of the following hold:

- `requirement_refs` and `feature_refs` each name at least one record, and
  `work_item_refs` at least one TASK; every reference exists and is of the
  right kind.
- every planned requirement is realized by a planned feature, and no planned
  feature traces to a requirement outside the plan;
- every required feature has at least one completion criterion, and every
  required criterion has a `verification_plan`;
- every planned feature has an implementing task, and every required criterion
  is listed in some task's `criterion_refs`;
- every task points back to the plan, lists at least one planned feature and
  one of its criteria, and has non-empty `verification`;
- every task capability is in the plan's `authorized_actions` and not in its
  `excluded_actions`;
- `verification_strategy` is non-empty;
- `approval_dependencies` covers every referenced record (`plan sync`);
- no `G0` open item is active.

### Changing an approved plan

Adding, removing, or re-scoping a TASK changes the plan's fingerprint and makes
the current decision `STALE`; every task in the plan stops passing its gate.
That is the designed behaviour. Re-approval is: author the change, `plan sync`,
`fingerprint`, owner decides, `approval confirm` with a new
`--confirmation-id`, `plan apply-decision`.

**Interim.** Until [Runtime gaps](RUNTIME_GAPS.md) item 3 is fixed,
`apply-decision` refuses a new decision from `APPROVED` or `BUILDING`. Set
`"lifecycle_state": "DECISION_READY"` in `.harness/state.json` before applying,
then transition the project back to `BUILDING` if work was under way.

### Switching to the next plan

With single-level plans one PLAN is active at a time, so moving from sprint 1
to sprint 2 is a switch, not an addition. Verified on 2026-09-06:

1. Finish the current plan first: every TASK in it `DONE` or otherwise
   terminal, its evidence recorded. A plan left half-done keeps its tasks and
   its decision in the tree; they become non-executable the moment the plan
   stops being active, and any later edit to that plan leaves a permanent
   `STALE_APPROVAL` warning that `validate --strict` reports.
2. Create and author the next PLAN and its TASKs, `plan sync`, `validate
   --strict`, `fingerprint`; the owner decides; `approval confirm`.
3. **Interim.** Set `current_plan` and `active_plan` to the new plan and
   `"lifecycle_state": "DECISION_READY"` in `.harness/state.json`.
   `apply-decision` refuses an approval whose subject is not the active plan,
   and no command changes the active plan ([Runtime gaps](RUNTIME_GAPS.md)
   items 1 and 3).
4. `plan apply-decision --approval <new APR>`. The project is `APPROVED`; the
   new plan's tasks pass `gate task` once `READY`, and the previous plan's
   tasks fail with "not the active plan".
5. The previous plan keeps the status it had; no command retires a plan
   ([Runtime gaps](RUNTIME_GAPS.md) item 7). Record its completion in its
   Markdown body and in the evidence of its features until that command
   exists.

Under the plan hierarchy, sprints are leaves under one root and several are
active at once, so this switch disappears.

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

`reset --confirm <directory name>` undoes `init`, returning the tree to the state a copied harness has before it governs a project: every canonical record, the `events/`, `baselines/`, and `decisions/` history, the record directories, and the `project.json`, `state.json`, and `HANDOFF.md` that identify the project are all removed. `next` then reports `NEEDS_INIT`. Shared runtime registries are cleared so record numbering restarts at `0001`.

Nothing survives to carry the old identity forward, so `init` afterwards starts a genuine new project and `--name` chooses its name. That is currently the only way to change a project's name, and it costs every record — a blunt instrument for a rename.

Files `init` does not create are never touched, and the bookkeeping files it generates only when absent (`.gitignore`, `.harness/.gitattributes`, `.harness/.gitignore`, `templates/`) survive, because an operator may have extended or filled one in. The human decision runtime survives too: its monotonic sequence and latest-decision markers make a recorded human confirmation non-replayable, and a reset is agent-reachable, so it must not roll back a control that bounds human authority.

`--dry-run` reports the same summary without writing and needs no confirmation. Everything a reset removes is snapshotted to `.harness/runtime/reset-<timestamp>/` first.

### When an agent may run it

`reset` is a destructive operation on the project's own records, so the rule is
stricter than for any other routine command, and it is a rule of instruction
rather than of cryptographic approval: the command acts on local repository
records, keeps a snapshot, and preserves the human-decision runtime, so the
five signed boundaries do not apply to it.

1. The current user request must name the reset in so many words: "reset the
   harness", "start the project over", `reset --confirm`. Nothing else counts.
   Validation errors, a stale plan decision, a blocked gate, a broken record,
   or a wish to rename the project are reasons to repair or to ask, never to
   reset.
2. Run `reset --dry-run` first and show the user its summary: the records and
   identity files it would remove, and whether `git status --short` shows
   those records as committed. Uncommitted records survive only in the
   snapshot, and the snapshot is git-ignored, so it exists on this machine
   only. Say so.
3. Run `reset --confirm <directory name>` only after that report, in the same
   request. Report the snapshot path and that `next` now says `NEEDS_INIT`.
4. Never delete a `.harness/runtime/reset-*` snapshot except on an explicit
   user request.

A no-Git project has no committed copy at all; the dry-run report must say
that the snapshot will be the only copy.

## Hotfixes and incidents

An incident does not open a second path. A hotfix is a TASK in an approved
PLAN, approved by the owner, gated like any other change; what urgency shortens
is the ceremony around that decision, which is already minutes long when the
owner is reachable, not the authority behind it.

The sequence, with the smallest records that keep the trace:

1. Register the incident: a `SRC-*` for the report as it arrived, and an
   `OI-*` at `G1` whose `blocks` and `affects` name the work that must wait
   for the fix (the release task, the acceptance, dependent tasks) and never
   the feature or criterion the fix itself repairs, because a `G1` item closes
   the gate of every task whose features or criteria it names. `G0` closes
   every task gate and the plan preflight, so it would stop the hotfix too;
   use it only to freeze all work, and resolve or downgrade it before the fix
   is approved.
2. Add one TASK for the fix to the active PLAN with `new task --plan
   --feature --criterion --capability LOCAL_IMPLEMENTATION`, author its
   `write_scope` and `verification`, and `plan sync`. The preflight requires
   every TASK to name a planned feature and one of its criteria, so attach the
   fix to the feature it repairs; when no feature covers the broken behaviour,
   add one whose single criterion states the behaviour the fix restores. Do not
   satisfy the trace with an unrelated feature.
3. `fingerprint` the plan and show it to the owner with a one-line summary of
   the change. The owner's "approved" in chat is the decision; transcribe it
   with `approval confirm`, the chat as channel and the message as reference,
   then apply it (with the interim steps in [Runtime gaps](RUNTIME_GAPS.md)
   while they are needed).
4. `transition` the TASK to `READY`, `gate task`, fix, `check_repo.py fast`,
   commit explicit paths, fetch, resolve, push.
5. Record what was verified as evidence against the criterion the fix
   restores, then resolve the incident's open item with that evidence
   reference and its propagation targets. If the fix changes an
   approved requirement or feature, open a `CR-*` for the follow-up; the hotfix
   TASK does not silently rewrite the baseline.
6. Reaching production is a separate step. A redeploy, a rollback to the
   previous release, a data repair, or a credential rotation each takes its
   own cryptographic approval; the incident does not merge them.

Because a single-level plan has one active PLAN, adding the hotfix TASK makes
the sprint's decision stale and closes every task gate in it until the owner
re-confirms. That is the designed effect of changing an approved plan, and it
is brief when the owner is present. With the plan hierarchy in
[Plan hierarchy](PLAN_HIERARCHY.md), a hotfix goes into its own leaf, such as
`FIX-001` under the root, so the sprint leaves are untouched.

What is never a hotfix: editing production or its data directly, applying a
stale or unrelated approval, skipping the task gate, or reporting a check that
did not run as PASS. Each of those is the incident, not the response to it.

## Checks

These checks are selected by the boundary above; they are not an unconditional
startup bundle.

```powershell
python scripts/harness.py doctor
python scripts/harness.py status
python scripts/harness.py validate --strict
python scripts/check_repo.py fast
python scripts/check_repo.py full
```

`fast` is for iteration; `full` is for release, handoff, result, or push. Never report an unrun, blocked, partial, inconclusive, or failed check as PASS.
