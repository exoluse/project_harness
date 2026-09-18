# Workflow

Follow [AGENTS.md](../AGENTS.md) for the current workflow and authority.
Identify applicable project-contract and protected-CI requirements.

For this harness's own policy, README and agent-guidance maintenance, use
[policy maintenance](../AGENTS.md#harness-policy-maintenance): edit current
files, use Git/diffs for history and report scope/decisions/checks in the
conversation. Do not create change notes, update a policy-work index or archive
copies merely to record those edits. The project-document workflow below
continues to apply to actual development and requested document deliverables.

## The path as it runs today

1. Identify the requested outcome, stage/stopping point, existing decisions and
   relevant project notes. Inspect dirty work before writing.
2. Establish the current input versions and preserve existing progress.
3. Produce the requested discovery, requirements, design or planning outputs.
   Maintain a project overview and separate independently scoped feature/work
   documents. For planning, follow the
   selected [planning depth](DEVELOPMENT_METHOD.md#choosing-planning-depth)
   and pass its applicable completion checks,
   including source coverage and executable detail. Check content and trace;
   stop there for a stage-only request.
4. For implementation, establish scope, feasibility, impact, risks, dependencies
   and verification at a useful level. A clear direct implementation request
   supplies its scope decision; record it or reference an applicable prior
   decision. Present alternatives and obtain a decision for unresolved material
   choices or uncovered scope under [Approvals](APPROVALS.md).
5. Apply [work-item readiness](#scope-decisions-and-work-item-readiness), reusing
   the owning assessment and recording changed facts and real blockers.
6. Execute covered work and verify the changed deliverables against the agreed
   criteria. Preserve observations, failures and limits.
7. Deliver the requested result. For releases or project closure, include all
   contributing work, acceptance and operational obligations as applicable.

When authoring stage outputs, use the
[document organization standard](DATA_MODEL.md#document-organization) to locate
the overview and owning documents. Apply the Information model's detailed
rules; create only the outputs needed for the requested stage.

## Existing project intake and reverse engineering

Keep the existing commit/snapshot, unknown changes and actual progress. Inventory
only the material needed for the requested scope. Recover requirements/design
with source/version references and distinguish observed behavior, inferred intent,
confirmed requirements and unresolved contradictions.

Describe current implementation separately from desired changes. A code review
does not establish test success or customer acceptance. Plan actual remaining
work; do not invent earlier approvals or force a lifecycle reset. See
[Development method](DEVELOPMENT_METHOD.md#existing-project-intake-and-reverse-engineering).

## Scope decisions and work-item readiness

[Approvals](APPROVALS.md#coverage-and-currentness) owns readiness criteria,
recording and reuse. When selecting or resuming work, use that assessment and
review the [open items](#open-item-lifecycle) affecting the selected scope,
including unresolved owner or provider responsibilities. Update the owning
assessment for changed facts; do not maintain another readiness checklist here
or require a new approval solely because the work item changes.

## Open-item lifecycle

Apply this procedure to unresolved items from discovery through maintenance.
Use the [open-item content and boundaries](DATA_MODEL.md#open-items) for where
to record them. The lifecycle is maintained in ordinary project documents or a
designated [external tracker](DATA_MODEL.md#external-work-trackers); it does
not require a tracker, background monitor or additional approval stage.

For a clarification answered, checked and incorporated in the same session
without remaining follow-up, use the short question/answer/evidence note under
[Open items](DATA_MODEL.md#open-items). The tracking steps below apply when
follow-up remains; do not manufacture a lifecycle for a completed clarification.

### Capture and classify

Record a concrete question or finding when it needs follow-up. Identify its
source/version, affected work, resolution criterion, accountable owner, next
action, needed-by point and next review trigger. Reuse unambiguous parent values
under the Information model instead of copying them. If ownership is not yet known,
state that it is unassigned and identify the assignment needed; do not pretend
that a named team or external provider has accepted responsibility. Resolve
accountability before starting dependent work that requires it.

Distinguish an unresolved scope/design choice from an execution prerequisite
and a bounded local implementation choice under the
[planning disposition rules](DEVELOPMENT_METHOD.md#planning-completion-checks).
State whether it blocks planning completion, work start, verification, delivery
or closure, and which dependents are affected. Do not block unrelated work or
downgrade a consequential unknown merely to finish a plan.

Investigate questions that can be answered from authorized sources. When a
human decision is needed, present the question, relevant evidence, alternatives,
recommendation and affected scope to the actual decision owner. Reuse valid
decisions; a clarification does not require approving the whole plan again.
Waiting, silence or a target date passing never supplies an answer or permission.

### States and transitions

Use the following meanings; equivalent project or local-language labels are
acceptable if their mapping is clear. State describes progress on the item;
blocking impact and deferral are recorded separately.

| State | Meaning and transition condition |
|---|---|
| OPEN | Follow-up is required and no resolution is established. Move to IN_PROGRESS when an identified action starts, or WAITING when a concrete outside input prevents progress. |
| IN_PROGRESS | Investigation or resolution work is actually underway with an owner and next action. Move to WAITING for a named dependency, or RESOLVED when evidence satisfies the recorded resolution criterion. |
| WAITING | A specific answer, dependency, assignment or permission is outstanding. Record who/what is awaited and when to revisit it. Return to IN_PROGRESS when useful resolution work resumes, or RESOLVED if the received evidence directly satisfies the criterion. |
| RESOLVED | The answer/result meets the item's resolution criterion with attributable evidence or a valid decision. Propagation and dependent-readiness checks may still remain; this state alone does not unblock work. |
| CLOSED | The resolution has been checked, affected definitions/statuses updated and the closure disposition recorded, or a justified non-resolution closure below has been completed. This does not establish product acceptance or project closure. |

An immediately answered item may go from OPEN to RESOLVED without invented
intermediate activity. Resolution review and closure may happen in the same
session, with their actual checks recorded. No separate reviewer or human
approval is required solely for these labels; actual decision and high-risk
boundaries still apply. Failed resolution checks return the item to OPEN,
IN_PROGRESS or WAITING as appropriate, preserving the failed evidence.

When resolution checking, propagation and dependent-readiness review finish
together, one dated/versioned entry may record the answer/evidence, affected
owner links, readiness outcome and final CLOSED disposition. That entry covers
both resolution and closure; do not copy the evidence into a separate entry for
each label. Inherit unambiguous parent values under
[Open items](DATA_MODEL.md#open-items). If propagation or a closure check remains,
retain RESOLVED with the remaining action; grouping the record does not waive
either condition. See the [worked example](EXAMPLE_WEB_PROJECT.md#open-item-lifecycle-example).

### Resolution, closure and dependent work

Check the proposed answer or result against the recorded criterion and input
version. An answer must come from an authoritative source when the question
requires one. A question about intended behavior can be resolved by the actual
owner's decision; a claim that behavior works needs the applicable verification.
A proposed fix, scheduled test or supplied credential/environment alone does
not prove the dependent work's success. Do not store protected values as evidence.

Before CLOSED with a resolved disposition:

1. Record the checked answer/result, method or decision source, version and limits.
2. Update or link the affected owning requirements, design, plan, tasks and checks.
   Apply [material-change rules](APPROVALS.md#material-changes) before performing
   work beyond existing authority; resolving a question is not implementation.
3. Assess each affected dependency. Record what is ready and what remains blocked
   by other items or permissions, with remaining actions and owners. Reuse
   applicable evidence; do not automatically resume canceled or paused work.
4. Record the closure reason/history and update relevant overview/handoff links
   under [summary ownership and updates](DATA_MODEL.md#summary-ownership-and-updates).

Deferral leaves the item unresolved. Record the rationale, impact, authorized
scope/timing decision when needed, accountable owner, next action and review
trigger; retain its actual state and blocking effect. Moving an item to another
plan, accepting a risk or moving a deadline does not by itself satisfy a required
criterion. A required unresolved item still prevents the affected completion
claim unless the actual authorized scope has changed.

Close without resolution only for an evidenced duplicate, a demonstrated
non-applicable item or an actual authorized cancellation/exclusion of the
obligation. Record that disposition explicitly rather than saying "resolved,"
link the surviving item or decision, and check effects on dependents and
retained obligations. A duplicate's dependents follow the surviving item;
deleting the duplicate reference cannot remove their blocker. An agent cannot
exclude a requirement to produce a clean report.

### Review, escalation and reopening

Review affected items before completing planning, starting/resuming dependent
work, handing off, or claiming the relevant verification, delivery or closure.
Also review when their needed-by point/review trigger is reached, an answer or
dependency arrives, or relevant scope, input, environment, evidence or ownership
changes. Reuse unchanged assessments; no fixed polling loop or repeated full
project scan is required.

When a needed-by point is missed or an item has no feasible next action, surface
the actual impact and needed decision/input to the user or authorized owner,
and update the action, responsibility and review trigger. Report unassigned
or unreachable owners explicitly. Do not invent a deadline extension, silently
defer the work, or contact external parties without applicable authorization.
Continue independent covered work while the affected work remains blocked.

Reopen a RESOLVED or CLOSED item when new evidence contradicts its answer, the
same failure recurs, a relied-on decision is withdrawn, or changed assumptions
invalidate its resolution/disposition. Retain its identity and prior closure;
record the new source/version, reason, current state (OPEN, IN_PROGRESS or
WAITING), owner, action and affected dependents. Reassess their readiness and
stop affected work as necessary. A genuinely different issue follows the normal
item-boundary rules and links the earlier one instead of overwriting its history.

## Changing an approved plan

Preserve the reviewed version, actual decision and observations. Refine tasks,
ordering and document structure within that scope without another decision.
For material changes, prepare the delta and its impact, obtain the applicable
owner decision once, then implement and reverify affected parts.

A sibling task edit or stale historical observation does not automatically
invalidate unrelated work. Explain actual dependency or scope impacts. Do not
copy an old PASS into new evidence without checking applicability.
Reassess affected open items and reopen invalidated resolutions under the
[lifecycle rules](#review-escalation-and-reopening).

For a cancellation, pause or withdrawn permission, follow
[cancellation and resumption](APPROVALS.md#cancellation-withdrawal-and-resumption).
Keep the actual stopping state and remaining work in the owning plan/work note;
use those facts when checking authority and readiness to resume.

## Switching to the next plan

Plans are an organizational choice, not a single active slot. Several plans
may share an owner decision or reference their own decisions. Switching or
splitting plans does not by itself require approval.

Carry forward unfinished work explicitly. Verify the next work item's coverage
and dependencies. Keep actual assignments and status accurate, and report
completion when the requested scope is complete.

## Verification and completion

Choose checks that establish the declared result. Document the subject version,
method/environment, expected and observed result, relevant artifacts and limits.
Name the actual command or check target and environment. Reference the
[project conventions](DATA_MODEL.md#suggested-information) recorded in the
overview where they exist; where none is recorded, record the command and
environment actually used in the verification record and state that the
convention is undecided. When a verification-level claim, dependent work or
handoff relies on an undecided convention, track it under the
[open-item lifecycle](#open-item-lifecycle) instead of inventing one.
Use distinct levels such as STATIC_VERIFIED and INTEGRATION_VERIFIED; a document
check does not establish either product integration or production success.

Before completion, release, handover or push, review the diff and relevant
verification. Apply [document validation](DATA_MODEL.md#document-validation)
for document deliverables at the requested stage. Reuse applicable baseline
results under [verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification);
a transition from completion to push alone does not require a fresh full scan.
Required project/CI checks remain required. Report a check failure accurately
even when unrelated authorized work can continue.
No test run means no test-pass claim.

## Status and trace reporting

A status request such as "how far is this project" or "how much of the
requirements are traced" is an analysis request. It authorizes reading the
project records and producing the report; it does not authorize document
edits, and it does not require the user to name IDs, paths or stages. Derive
every statement from the owning records at a stated version; never estimate
progress from titles, labels or file counts alone.

### Scope and basis

1. Identify the requested scope: the whole project, an area, one plan or one
   requirement. Default to the whole project as indexed by the root overview.
2. Inspect Git status and record the baseline commit/snapshot, dirty work and
   the date. Treat unknown dirty files as someone else's work.
3. Start from the [project overview](DATA_MODEL.md#document-organization) and
   applicable [area overviews](DATA_MODEL.md#area-overviews), then read the
   owning requirement, design, plan, task, verification and open-item records
   for the scope. Read designated
   [external tracker](DATA_MODEL.md#external-work-trackers) state where it
   owns work status; if the tracker is unreachable, report that state as
   unknown rather than reusing a Markdown copy.
4. Under [summary ownership](DATA_MODEL.md#summary-ownership-and-updates),
   owning records prevail over overview or plan summaries. Report the owning
   fact and list the disagreement as a discrepancy.

Mechanical scans (link resolution, ID and status collection) may be
delegated under [model selection](CONTEXT_EFFICIENCY.md#model-selection-and-delegation);
the accountable agent interprets the result and makes the stage and
coverage judgments.

### Report content

| Section | Content |
|---|---|
| Basis | Scope, overview version/commit, date, dirty work, records read and records not read or not resolvable. |
| Stage summary | Current stage per the overview, active plans, and the stage actually supported by the owning records where it differs. |
| Requirement trace | One row per in-scope requirement: covering design/contract, plan, tasks with their statuses, verification records with the highest evidence level and its subject version, acceptance, and blocking open items. Use the [evidence levels](../AGENTS.md#history-evidence-and-real-blockers); unrun, failed, partial or stale verification is reported as such, not as a lower pass. |
| Coverage | Counts derived from the trace with stated denominators: requirements in scope; with an owning design; with a plan; with all tasks complete; with evidence at each level; accepted. Requirements whose records could not be read count as unresolved, never as covered. |
| Gaps and discrepancies | Requirements without covering design or work; work, contracts or verification not linked to any requirement; unresolved links or IDs; summaries that contradict owning records; evidence whose subject version predates later changes to that subject; open items past their needed-by point. |
| Blockers and next action | Real blockers under the [open-item lifecycle](#open-item-lifecycle), affected scope, and the next action for each. |

Progress numbers describe record states, not effort or schedule. State what
each count measures; a task-completion ratio is not a requirement-level
completion ratio, and a plan marked complete does not establish verification
or acceptance. Do not report a percentage without its definition and
denominator.

### After the report

The report is conversation output. If the user asks to keep it, store it as
a dated snapshot with its baseline version, for example in the project note or
a handoff record; it is historical and not a parallel current status. Repairing
links, updating summaries or recording discrepancies as open items is separate
work that follows the usual [request authority](../AGENTS.md#authority-and-decisions);
propose it with the report and perform it when requested. Handoff notes reuse
the same basis under [progress and handoff notes](CONTEXT_EFFICIENCY.md#progress-and-handoff-notes).

## Closure preparation

Aggregate the declared release/project across all contributing plans. Review
required outcomes, work dispositions, decisions, applicable evidence, actual
customer acceptance, delivery status, handover and maintenance obligations.
Use a release inventory or existing project document.

Every required item must be complete or have an explicit disposition consistent
with the agreed scope. Do not omit unfinished work to obtain closure. Final
customer acceptance and production actions retain [external controls](SECURITY.md).
A documentation engagement closes at its agreed document scope.
Reconcile retained open items, deferrals and non-resolution closures under the
[open-item lifecycle](#open-item-lifecycle); handing them over does not itself
satisfy an outstanding required obligation.

## Collaboration and handoff

One writer needs no claim record. Concurrent writers agree owners and
non-overlapping paths/resources, using worktrees where practical. Treat unknown
dirty files as someone else's work until ownership is understood.

For a handoff, state baseline/output versions, changed paths, applicable
decisions, verification, failures, limits, unfinished work and next action.
Markdown is sufficient when accepted by the delivery contract. See
[Collaboration](COLLABORATION.md).

## Hotfixes and incidents

Record the incident, affected version, smallest feasible repair scope, risk and
verification. Reuse valid authority where it covers the repair; prepare a
material delta when it does not. Check actual dependencies and ownership, fix,
verify and report the outcome. Urgency does not create consent.

Production rollback/redeployment, data repair, destructive actions and credential
access retain their specific human and external controls. Keep failed attempts
and the actual recovery history.

## Starting over

Reset requires an explicit current user request. Prepare a dry run describing
the exact target paths, affected committed/uncommitted records, recoverable
copies and preserved decision history. Apply the applicable destructive-operation
human/external boundary. Never reset to silence diagnostics.

Verify recoverability, including uncommitted records, before destructive work.

## Former runtime records

This repository no longer ships a CLI, runtime, schemas or record store. There
is nothing to install, initialize or invoke, and no tool gate, claim, PLAN
fingerprint or runtime marker takes part in current work. Management records are
ordinary project documents under the [Information model](DATA_MODEL.md).

A project adopted from the earlier runtime-required process may still hold
`.harness/` records, signed payloads, baselines and snapshots. Preserve them:
they retain their original format, meaning and evidentiary value, and they are
historical input rather than current authority. Record mutation, migration,
conversion or deletion needs its own matching task authority under
[Security](SECURITY.md#classifying-development-actions); no such migration is
implied by this repository dropping its tooling. Never forge records, rewrite
signed payloads, install authority markers by hand or fabricate past attempts.

When continuing that work, identify the actual owner decision, baseline,
remaining scope and applicable evidence, and resolve missing authority or
material changes before dependent work. Stopping tool use or changing record
format alone needs no renewed decision. Required project/CI checks, human
decisions and external controls remain binding regardless of local tooling.

The former runtime's source, tests, schemas and design documents remain in Git
history, together with the findings that motivated its retirement. Consult that
history only when an adopted project's existing records need interpreting; none
of it states a requirement for current work.
