# Runtime Gaps on the Routine Path

Status: **items 1-7 verified on 2026-09-06, fixes decided, not yet implemented;
item 8 records the later task-refinement policy mismatch.** The
routine path in `docs/WORKFLOW.md` was run end to end on a fresh copy of the
harness with the CLI alone. It cannot be completed that way. The gaps below are
what stopped it, where each one lives, the interim step taken until the fix
lands, and the fix that is decided. The policy in `AGENTS.md`
does not change; the runtime is to be brought up to it.

This is a routed troubleshooting document, not routine startup context. Read
item 4 at `NEEDS_PLAN_APPROVAL`; read another item only when its named failure
occurs. The implementation priority is items 1 through 5 and 7 as one runtime
change plus the end-to-end CLI test described below. Until that approved runtime
work lands, context routing reduces repeated reading but does not remove the
interim commands.

The interim steps are performed by the agent when the user's request calls
for the step they precede, so the whole path stays drivable from prompts. None
of them grants execution authority: they set a pointer or a descriptive
lifecycle value, and `plan apply-decision` still verifies the approval, the
plan fingerprint, and the preflight before anything becomes executable. The
agent names each interim edit in its report so the audit trail is not silent.

## 1. Nothing sets the active plan

**What happens.** `plan apply-decision` refuses with "Project state has no
active plan". `plan activate` refuses with a message that points back at the
approval flow. No command writes `state.active_plan`; only `init` writes it, as
`null`.

**Where.** `lifecycle.apply_plan_decision` requires
`state.active_plan == approval.subject_id`. `authoring.activate_plan` raises on
its first line; the code beneath it never runs.

**Interim.** After the owner's confirmation is recorded and before
`plan apply-decision`, set both pointers in `.harness/state.json`:

```json
"current_plan": "PLAN-0001",
"active_plan": "PLAN-0001"
```

**Decided fix.** `plan apply-decision` sets `current_plan` and `active_plan`
from the approval's subject when the state has no active plan or the active
plan is retired (`CLOSED`, `SUPERSEDED`, `STALE`), and refuses when a different
live plan is active. The dead body of `activate_plan` is removed; the command
stays as an error that names `approval confirm`.

## 2. The decision can be applied only from `DECISION_READY`

**What happens.** With the active plan set, `plan apply-decision` refuses with
"A new PLAN decision can be applied only from DECISION_READY; current lifecycle
state is DISCOVERY". `next` never mentions a lifecycle transition.

**Where.** `lifecycle.apply_plan_decision` and
`lifecycle_mutations.PROJECT_TRANSITIONS`. A fresh project is in `DISCOVERY`;
reaching `DECISION_READY` takes `SPECIFYING`, `PLANNING`, `DECISION_READY` in
turn.

**Interim.** Before `plan apply-decision`:

```powershell
python scripts/harness.py transition --kind project --id PROJECT --to SPECIFYING --agent <agent> --reason "plan drafted"
python scripts/harness.py transition --kind project --id PROJECT --to PLANNING --agent <agent> --reason "plan drafted"
python scripts/harness.py transition --kind project --id PROJECT --to DECISION_READY --agent <agent> --reason "owner decision recorded"
```

From `CONTRACTED` the first step is `PLANNING`. An agent may run these; they
are descriptive lifecycle moves, not approvals.

**Decided fix.** `plan apply-decision` moves any pre-decision lifecycle state
(`DISCOVERY`, `CONTRACTED`, `SPECIFYING`, `PLANNING`, `DECISION_READY`) to
`APPROVED` itself and records the before and after states in its event.

## 3. A changed plan cannot be re-applied

**What happens.** Adding a TASK to an approved plan makes the decision `STALE`,
as intended. The owner re-confirms against the new fingerprint, and
`plan apply-decision` then refuses: "can be applied only from DECISION_READY;
current lifecycle state is APPROVED". No project transition leads back to
`DECISION_READY` from `APPROVED`, `BUILDING`, `VERIFYING`, or `MAINTAINING`.
Every mid-project change to a plan is a dead end.

**Where.** `lifecycle._replaces_superseded_active_decision` lets a new decision
replace the active one only when the previous decision's status is
`SUPERSEDED`. After the plan was edited, `approval_status` reports the previous
decision as `STALE` first, so the replacement path never fires.

**Interim.** After the owner re-confirms and before `plan apply-decision`, set
`"lifecycle_state": "DECISION_READY"` in `.harness/state.json`. `apply-decision`
then applies the new decision and moves the project to `APPROVED`; transition
it back to `BUILDING` if work was under way. Verified: after this, tasks in the
re-approved plan pass `gate task`.

**Decided fix.** The replacement check accepts a previous decision that is
`STALE` or `SUPERSEDED` when a newer current decision exists for the same
subject, and `apply-decision` preserves the lifecycle state in
`RESUMABLE_LIFECYCLE_STATES` instead of demanding `DECISION_READY`.

## 4. `next` gives the wrong instructions at the approval step

**What happens.** At `NEEDS_PLAN_APPROVAL`, `next` names `approval prepare` and
`approval record`, the signed flow reserved for the five cryptographic
boundaries. It does not name `approval confirm`, does not list the preflight
blockers that will make the confirmation fail, does not mention the lifecycle
transitions or the active plan pointer, and keeps saying the same thing after
a decision has been recorded.

**Where.** `guidance.next_step`, the `NEEDS_PLAN_APPROVAL` branch.

**Interim.** At that step follow `docs/WORKFLOW.md`, not `next`.

**Decided fix.** The branch names `approval confirm` with the plan's
`authorized_actions` filled in, lists `plan_preflight_gate` blockers in
`details`, reports a recorded but unapplied decision as
`NEEDS_DECISION_APPLIED` with the `apply-decision` command, and, until gaps 1
and 2 are fixed, lists their interim steps.

## 5. Drafts are empty and the preflight needs content the CLI cannot write

**What happens.** `new plan` and `new task` create records whose scope fields
are empty. The confirmation then fails preflight: requirement and feature
references empty, task without feature or criterion scope, task without
verification commands, plan without a verification strategy. `new task` accepts
`--feature` and `--criterion` but nothing else; `new requirement` and
`new feature` accept only a title.

**Where.** `scaffold.new_record`, `authoring.create_work_item`, `cli.cmd_new`.

**Interim.** Author the content directly. This is authoring, which the policy
allows: PLAN and TASK front matter and the JSON of REQ and FUNC are edited to
carry statements, criteria, references, scope, and verification. Only derived
fields (`approval_dependencies`, `work_item_refs`, `plan_id`) are left to the
commands; run `plan sync` after editing. `docs/WORKFLOW.md` lists exactly what
the preflight checks.

**Decided fix.** `new requirement --statement`, `new feature --criterion
"<id>|<statement>" --profile --binding`, `new plan --requirement --feature
--verification-command`, and `new task --write-scope --verification`, each
repeatable, so a plan that passes preflight can be reached from the CLI. The
scaffold gives a new plan the default verification strategy that names the
`check_repo.py` tiers.

## 6. The examples omitted `--authorized-action`

**What happens.** `approval confirm` refuses an `APPROVED` decision that names
no `--authorized-action`. The examples in `README.md`, `docs/APPROVALS.md`, and
`docs/EXAMPLE_WEB_PROJECT.md` did not pass it.

**Status.** Fixed in the documents on 2026-09-06. The confirmation must
authorize every capability of every TASK in the plan; a routine plan passes
`LOCAL_IMPLEMENTATION`, `LOCAL_TESTS`, and `DOCUMENTATION`.

## 7. No command changes a plan's status

**What happens.** `transition --kind` accepts `project`, `requirement`,
`feature`, and `work_item`, not `plan`. A plan's status is written only by
`plan apply-decision`. A finished or abandoned plan therefore stays `APPROVED`
or `ACTIVE` forever, `next` keeps counting it as a candidate when no plan is
current, and switching to the next plan leaves the previous one in the tree in
its last status.

**Where.** `lifecycle_mutations.SIMPLE_TRANSITIONS` and the `transition`
argument parser in `cli.py`.

**Interim.** Finish a plan's tasks before switching away from it, note its
completion in the plan's Markdown body, and let the switch make its tasks
non-executable; see "Switching to the next plan" in `docs/WORKFLOW.md`.

**Decided fix.** `transition --kind plan --to CLOSED|SUPERSEDED` with the
normal claim and reason handling, refusing `CLOSED` while a task in the plan is
not terminal. `plan apply-decision` on a different plan than the active one
marks the previous active plan `SUPERSEDED` when all its tasks are terminal and
refuses otherwise, so the switch in `docs/WORKFLOW.md` becomes one command.

## 8. PLAN approval also binds routine task refinement

**What happens.** The development policy distinguishes agreed requirements,
acceptance criteria and constraints from the task breakdown used to satisfy
them. Adding or splitting a task, or changing its order within those boundaries,
does not itself call for a new business decision. The current runtime includes
TASK membership and bound task fields in approval currentness, so such a
refinement can still make the PLAN stale and stop all its tasks.

**Where.** `core.subject_fingerprint` includes the PLAN approval subject and
TASK dependency/scope fields; PLAN dependency snapshots and current-approval
checks bind that structure to the owner's recorded decision.

**Interim.** Classify and explain the change accurately. Keep the task trace
complete and obey the existing fingerprint gate. If it requires confirmation,
present the refined plan and its fingerprint once and record only the owner's
actual decision. Do not disguise refinement as a new requirement, hide a task,
or fabricate fresh provenance for an old decision.

**Policy direction; runtime design pending.** Separate routine task refinement
from changes to agreed outcomes, acceptance criteria, authorized capabilities,
and material constraints. A future implementation must allow refinement only
within those boundaries while preserving scope validation, dependency checks,
evidence freshness and all high-risk approvals. No new schema, command or
approval mechanism is implemented or authorized by this policy update.

## Why the self-tests did not catch the original CLI gaps

The runtime's tests pass (126 on 2026-09-06). Their fixtures write
`state.json` directly with `active_plan` and `lifecycle_state` already set and
call `apply_plan_decision` as a function, so the CLI path from `init` to a
passing task gate is never exercised.

**Decided fix.** One end-to-end test drives the CLI from `init` through
`new plan`, `new task`, `approval confirm`, `plan apply-decision`, `transition`,
and `gate task`, then adds a task, re-confirms, re-applies, and checks both
gates, then finishes the plan and switches to a second one. It is the
acceptance test for gaps 1 to 5 and 7.

## Order of work

The fixes are one runtime change. They come before the plan hierarchy
(`docs/PLAN_HIERARCHY.md`) and the record format change
(`docs/RECORD_FORMAT.md`), because both build on the path these gaps break.
Item 8 needs a separately scoped runtime design; it is not silently included
in the previously decided fixes for items 1-5 and 7.
