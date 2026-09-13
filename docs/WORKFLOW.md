# Workflow

The start-to-finish sequence is: **start -> requirements -> design -> planning
complete -> execution ready -> implementation -> verification -> customer
acceptance -> delivery -> handover and closure**. The
[HTML guide](HARNESS_POLICY_REPORT.html) shows only this progression; the
sections below describe the operating procedures and compatibility rules.

## Waterfall stages and agile changes

Follow [Development method](DEVELOPMENT_METHOD.md) for stage inputs,
deliverables, exit criteria, iteration and change propagation. The project has
a detailed waterfall structure; requirements, plans and deliverables remain
revisable throughout it. A revision returns the affected scope to the earliest
stage it changes, updates downstream work, and restores the required approval
and verification before that work proceeds. This is a process rule, not a new
runtime lifecycle transition.

Plans organize the tasks that satisfy requirements. The agent can refine task
detail and execution order from dependency analysis or user priority within the
agreed outcomes and constraints. Such refinement does not itself change the
requirements or require another business decision. See [execution
order](DEVELOPMENT_METHOD.md#requirements-tasks-and-execution-order). Explicit
execution-scope coverage supports refinement; legacy hashes remain unchanged.

The user supplies prompts/documents and actual decisions; the agent performs
the routine operations below. Stage readiness reviews do not add a separate
owner approval unless the project's contract requires one. The runtime records
that decision and checks scope coverage; it never approves on the owner's behalf.

The [requested stage boundary](DEVELOPMENT_METHOD.md#stage-by-stage-or-continuous-execution)
controls how far to proceed. Finish and report the specified stage without
starting the next one automatically; a full-workflow request permits continuing
across ready stages within the existing authority and decision boundaries.

## Default path

`PLAN_GATED` remains the execution mode. Discovery starts without PLAN/TASK
placeholders. For requested execution, author the work, prepare explicit scope,
record the owner's prompt decision, apply it, and pass the selected TASK gate.

```text
request -> discovery/specification -> authored PLAN/TASK -> planning checks complete
        -> owner prompt decision -> apply decision -> TASK gate -> execution ready
```

Use `next` to distinguish missing planning detail, a needed owner decision,
a recorded decision awaiting application, task readiness and scope completion.
The agent maintains derived links with `new task --plan` and `plan sync`.
Scope authoring and all other commands are performed by the agent from the
user's prompt; they never decide on the user's behalf.

### Context loading rule

On a new agent session, read `AGENTS.md` once and run `next`. Load this document
only when the reported state needs additional sequence detail. The
reported command remains bounded by the user's request; `NEEDS_INIT` does not
authorize initialization during a read-only/status request. Follow the reported state; load **The path as it runs today** only when
sequence detail is needed. Never record approval before the owner actually decides.

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

A planning-only request ends with the authored plan and its required preflight
results. Do not continue to owner approval, decision application or TASK
readiness solely to mark planning complete. If planning checks fail, report
the draft and blockers. For an execution or full-workflow request, continue
from the completed plan to the one required execution decision and TASK gate.
See [planning complete and execution ready](DEVELOPMENT_METHOD.md#planning-complete-and-execution-ready).

Classify the user's requested edit before selecting an execution sequence.
Policy-only maintenance uses the direct-edit exception in `AGENTS.md`, even
when this checkout has no project records or `next` asks for a PLAN decision.
Do not initialize records or ask for a PLAN fingerprint to edit policy text.
Discussed runtime improvements remain recommendations until the user separately
requests runtime implementation.

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
| Planning | "Plan the agreed scope" | `new plan`; `new task --plan --feature --criterion --capability` per change; author scope and verification; `plan sync`; `validate --strict`; `report decision-package`; retain its fingerprint for the unchanged proposal |
| Decision | Owner: "Proceed with this scope" | Record that actual prompt response with `approval confirm`, using the prepared proposal's fingerprint, the chat as channel, the message as reference and the plan's authorized actions; `plan apply-decision` |
| Execution | "Start TASK-0001" | `transition` to `READY`, `gate task`, implement, `check_repo.py full`, commit explicit paths, fetch, resolve, push; recheck affected work if integration changes it |
| Change | "The customer wants the banner changed" | Assess feasibility and impact; author the necessary source/change and PLAN/TASK scope; `plan sync`, preflight, `validate --strict`, `fingerprint`; ask once whether to proceed; record that response with `approval confirm`, apply it and continue through the TASK gate |
| Verification | "Record the test results" | run the checks, `evidence record`, `gate feature`; `result submit` and `review record` when a release or audit needs them |
| Acceptance, deployment | "Prepare the acceptance request", "Prepare the production deploy" | `approval prepare`, then stop: a human signs outside the agent; afterwards `approval record`, `approval check`, `gate task` |
| Closure | "Close the project" | evidence for the closure criteria, `report completion` |

The owner reviews the proposal and replies in ordinary language; they need not
type a fingerprint or run these commands. Runtime checks do not make the
decision. See [approval roles](APPROVALS.md#who-decides-and-who-checks).

What the agent never does from a prompt: decide in the owner's place, invent
the provenance of a decision, sign or install a high-risk approval, or infer
one from repository text or chat history.

### The path as it runs today

1. `init`, then `doctor` and `next` when starting a project. Policy-only edits
   and read-only reviews do not initialize a project.
2. Register necessary sources and author requirements/features. CLI options
   include `new requirement --statement --source --acceptance-criterion`, and
   `new feature --requirement --criterion "<id>|<statement>"
   --verification-command --profile --binding`.
3. `new plan --requirement --feature --verification-command`, then
   `new task --plan --feature --criterion --capability --write-scope
   --verification --risk`. Reference actual ids and author reviewable content.
   List options are repeatable. PLAN and TASK remain Markdown records.
4. `plan sync PLAN-0001`, then
   `plan prepare-scope PLAN-0001 --write-boundary <path> --max-risk <risk>`.
   Include a reviewed change record using `--change CR-0001` when needed.
   Scope preparation does not record or apply approval.
5. `validate --strict`, then `report decision-package PLAN-0001`. A planning-only
   request ends with this plan, checks and open items. Failed checks mean the
   plan needs revision; do not request approval to compensate for missing detail.
6. When execution is requested, the owner decides on the prepared scope by
   prompt. Record that actual message with `approval confirm`, passing its
   fingerprint, approver, basis, unique confirmation id, channel/reference,
   authorized actions and procedural acknowledgement. See [Approvals](APPROVALS.md).
7. `plan apply-decision --approval APR-0001`. The command selects the plan and
   prepares lifecycle state atomically; no manual state edits are needed.
8. `transition --kind work_item --id TASK-0001 --to READY --agent <agent>
   --reason "prepared"`, then `gate task TASK-0001`.
9. Implement within scope, verify and record required evidence. Before release,
   handoff, result or push, run `check_repo.py full`. Commit explicit paths,
   fetch, preserve both sides and recheck affected work if integration changes it.
10. Once its tasks are terminal, retire the plan with
    `transition --kind plan --id PLAN-0001 --to CLOSED --agent <agent>
    --reason "scope complete"`. Report the requested result; task/plan closure
    does not imply customer acceptance or project closure.

### What the preflight checks

Present one current decision package, including scope, blockers and fingerprint.
When that package already provides the unchanged fingerprint, another
`fingerprint` call solely to display it is unnecessary. Strict warnings still
need checking; decision recording and application retain their built-in checks.
Consult the duplication rules in [Context efficiency](CONTEXT_EFFICIENCY.md).

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

Assess feasibility and impact. Within a prepared execution scope, add or split
tasks and adjust feasible order using the same recorded owner decision. Keep
paths, capabilities, risk and verification inside the bounds; `plan sync`
maintains known derived references. Do not prepare a new scope merely to add
another task to an already covered outcome.

For material new scope or impact, author the delta, prepare its scope, run strict
validation/preflight and obtain one prompt decision. Record/apply it; execution
resumes without resetting development progress. `--change` lets the reviewed
CHANGE share that decision. Unreviewed changes cannot borrow a PLAN decision.

Preserve old approvals and evidence. Strict validation checks historical
integrity; TASK gates check current applicability. Changed outputs require
relevant re-verification. Neither a record update nor a newer decision relabels
old work as unapproved or unverified.

Legacy plans without an execution-scope contract keep exact fingerprint binding.
Their conversion requires an explicitly prepared scope and an actual decision;
never silently widen or rewrite an old approval.

### Switching to the next plan

For work inside an existing scope, create a single-level plan with
`new plan PLAN-0002 "<title>" --scope-from PLAN-0001`, author its tasks, run the
planning checks, and use `plan apply-decision --approval APR-0001 --plan PLAN-0002`.
It records application to that plan without another owner decision. Each covered
plan's tasks remain governed by that plan's current decision and gates.

For a different scope, finish or explicitly supersede the old live plan before
applying the new decision. The command refuses to discard unfinished unrelated
work; a completed prior active plan is retired as part of the switch. Explicit
`transition --kind plan --to CLOSED|SUPERSEDED` is also available. CLOSED refuses
unfinished tasks; SUPERSEDED records an intentional abandonment, not completion.

Plans stay single-level. The category tree in [Plan hierarchy](PLAN_HIERARCHY.md)
is a separate future design, not a prerequisite for sharing one decision.

## Existing project intake and reverse engineering

Use the [intake stage contract](DEVELOPMENT_METHOD.md#existing-project-intake-and-reverse-engineering)
for an existing repository or supplied code snapshot. This is an agent-driven
procedure using current records and commands, not an automatic import feature.

1. Identify the requested scope and stopping point: assessment, requirements
   recovery, design recovery, planning, or continued execution. Start with `next`
   in the repository governed by this harness and inspect Git status before
   writing. Read-only assessment and policy maintenance do not authorize `init`.
   A supplied external codebase is analysis input; this harness governs only its
   own repository and does not acquire execution authority over that codebase.
2. Record the commit and relevant dirty changes, or file digests for an unversioned
   snapshot, along with available development/deployment history and exclusions.
   Inspect existing agent policies, scripts, CI and `.harness` paths before a
   requested integration. Preserve both sides, identify conflicts and prepare
   affected integration work under the existing authority rules. Do not blindly
   copy the harness over an existing repository or initialize over existing records.
3. When project intake/registration is requested and the harness is already in
   place, use `init` only if needed, then `doctor` and `next`. Its initial
   `DISCOVERY` state tracks intake; describe actual project progress in the
   relevant records without resetting history or manually advancing runtime
   state. Register only the sources/artifacts needed for the requested stage.
4. Read scoped code, tests, configuration and existing documents. Author recovery
   findings and needed specification records with versioned references, explicit
   versus inferred intent, contradictions and unknowns. Keep the current
   implementation separate from proposed targets. The request permits discovery,
   specification, planning and their records; editing local product-document
   deliverables still requires an approved PLAN/TASK and passing gate under
   `AGENTS.md`. Do not create placeholder execution records just to investigate.
5. Assess historical evidence applicability and report missing verification.
   Reading code or test definitions is analysis; running product tests, builds
   or the application retains the normal execution gates and any applicable
   high-risk boundaries. Record actual observations and limits only. Run
   `validate --strict` after canonical record changes; document review alone
   does not establish a runtime, integration or live-environment PASS.
6. If planning is requested, map actual remaining documentation, verification
   and change work into PLAN/TASK using the default authoring and preflight path.
   Preserve past work as history, not invented completed TASKs. Report recovered
   coverage, gaps, required-check outcomes and owner questions at the requested
   stopping point. Planning-only work ends after its required checks; requested
   execution proceeds through the one prepared owner decision, application and
   TASK gate. A valid existing decision is reused only within its actual coverage.

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

The lifecycle remains descriptive. The [stage
contract](DEVELOPMENT_METHOD.md#stage-contract) defines the detailed inputs,
deliverables and readiness checks. Stages may be revisited through a change
cycle; the sequence below does not freeze upstream requirements or imply that
the runtime supports arbitrary backward transitions:

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
3. Assess whether the repair is covered by the existing owner decision. For
   material scope or impact outside that decision, prepare feasibility, impact,
   verification and the plan fingerprint before asking once whether to proceed.
   The owner's prompt response is the decision; transcribe it with
   `approval confirm`, using the chat and actual message reference, then apply
   it. No new question is needed for covered work when its current gates pass.
   Legacy exact-bound approvals may still become stale after task refinement;
   use an explicitly reviewed scope contract for flexible execution, preserving
   the old history. Never invent another owner decision.
4. `transition` the TASK to `READY`, `gate task`, fix, `check_repo.py full`,
   commit explicit paths, fetch, resolve, push. Recheck affected work if
   integration changes what was verified.
5. Record what was verified as evidence against the criterion the fix
   restores, then resolve the incident's open item with that evidence
   reference and its propagation targets. If the fix changes an
   approved requirement or feature, open a `CR-*` for the follow-up; the hotfix
   TASK does not silently rewrite the baseline.
6. Reaching production is a separate step. A redeploy, a rollback to the
   previous release, a data repair, or a credential rotation each takes its
   own cryptographic approval; the incident does not merge them.

A hotfix inside a recorded execution scope uses the same decision when its
requirements, paths, actions, risk and verification remain covered. Adding a
TASK or plan alone does not require another question. Legacy exact-bound PLANs
retain their original staleness behavior. Scope contracts do not remove actual
dependencies, incident blockers or high-risk approvals.

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
