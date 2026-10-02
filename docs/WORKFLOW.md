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
   relevant project notes. Resolve a request stated in plain words to its
   owning items through the overview and plans and state that resolution. Start
   from the selected item's [current basis](DATA_MODEL.md#plans-and-tasks)
   when its owning document is already known;
   present candidates before editing when several items could match, and do
   not create a new item merely because no description matched. Inspect dirty
   work before writing.
2. Establish the current input versions and preserve existing progress.
3. Produce the requested discovery, requirements, design or planning outputs.
   Maintain a project overview and separate independently scoped feature/work
   documents, with an eligible work document serving as the overview under
   [compact documentation](DATA_MODEL.md#minimum-documentation-for-a-small-change).
   For planning, follow the
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
6. Apply [starting execution in a working tree](#starting-execution-in-a-working-tree)
   before the first edit. Execute covered work and verify the changed
   deliverables against the agreed criteria. Preserve observations, failures
   and limits.
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
including unresolved owner or provider responsibilities. Where the work records
a [resumption state](DATA_MODEL.md#resumption-state), enter from it. It names
the position and links to checkpoint evidence, blockers and the first documents
to read. Confirm it against the owning records before
relying on it, and correct it where it has fallen behind. Update the owning
assessment for changed facts; do not maintain another readiness checklist here
or require a new approval solely because the work item changes.
Use [current-state updates](#updating-current-work-state) to reconcile the
selected item's instructions and navigation.

## Starting execution in a working tree

Before the first edit of a work item, establish the actual state of the
checkout you are about to write in.

1. Confirm the checkout contains the governing instructions this work must
   follow, including the policy, adapter and owning-document changes decided
   for it. Work started from an earlier revision follows superseded
   instructions; update the checkout or state the gap before editing.
2. Inspect uncommitted and staged changes and record what was already there,
   so your own diff stays separable from work you did not do.
3. Compare that existing work against the item's declared write scope under
   [plans and tasks](DATA_MODEL.md#plans-and-tasks). Where they overlap, do not
   edit the overlapping paths: identify the owner and resolve the overlap, or
   hand the item back with it recorded. Existing work outside the declared
   scope does not block the item.

Record what the inspection established where the work is owned: the revision
the work starts from, the uncommitted paths that were already there, and the
outcome for any overlap with the declared write scope. Without it, a later
session cannot separate this item's diff from work it inherited, and the next
writer re-derives those facts from a tree that has since moved. A few lines in
the item or its progress note are enough; this needs no separate document. A
[direct change](DEVELOPMENT_METHOD.md#direct-changes) states them in its report.

This establishes the starting state and its limits. It grants no authority and
does not replace [work-item readiness](#scope-decisions-and-work-item-readiness)
or the [collaboration basis](COLLABORATION.md#collaboration-basis).

## Task states

Record a task's current state with these meanings. Equivalent project or
tracker labels are acceptable once the overview states their mapping. The state
describes the task's own progress; its execution mode, blockers and evidence
stay with their owners and are linked.

| State | Meaning |
|---|---|
| PLANNED | Defined and not started. |
| IN_PROGRESS | Work is underway, including rework after a failed completion check. |
| BLOCKED | Work cannot start or continue until a named prerequisite arrives. Link the open item that owns it instead of restating the reason. |
| IMPLEMENTED | The changes are complete, but the task's completion checks have not all passed yet. Link any open item that keeps a check from running. |
| DONE | The task's declared completion checks passed on an identified version, with linked evidence. |
| CANCELLED | An authorized decision cancelled the task or excluded it from scope. Link that decision. |

DONE covers only the task's own checks. It does not establish another
verification kind, a plan's outcome, acceptance or closure. A failed completion
check returns the task to IN_PROGRESS. A later check that overturns DONE follows
[pass withdrawal](#verification-and-completion), and the task returns to the
state the evidence supports.

A state change alone requires no parent update under
[current-state updates](#updating-current-work-state).
[Direct changes](DEVELOPMENT_METHOD.md#direct-changes) have no task and no
state.

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
Apply [conversation decisions](DEVELOPMENT_METHOD.md#conversation-decisions-and-current-instructions)
to current owning instructions before dependent work uses them. For unexpected
implementation behavior, follow
[discoveries during implementation](DEVELOPMENT_METHOD.md#discoveries-during-implementation)
to investigate, revise the affected plan or obtain the missing outcome decision.

A sibling task edit or stale historical observation does not automatically
invalidate unrelated work. Explain actual dependency or scope impacts. Do not
copy an old PASS into new evidence without checking applicability.
Reassess affected open items and reopen invalidated resolutions under the
[lifecycle rules](#review-escalation-and-reopening).

For a cancellation, pause or withdrawn permission, follow
[cancellation and resumption](APPROVALS.md#cancellation-withdrawal-and-resumption).
Keep the actual stopping state and remaining work in the owning plan/work note;
use those facts when checking authority and readiness to resume.

## Updating current work state

When advancing to another task or plan, resuming work, or handing it off, align
the current instructions before the next action relies on them.

1. Read the selected work item's actual state, execution mode, prerequisites,
   next action and evidence. Resolve superseded instructions in their owner under
   [conversation decisions](DEVELOPMENT_METHOD.md#conversation-decisions-and-current-instructions).
   Keep unresolved discrepancies visible; a navigation pointer cannot settle them.
2. Record a changed result or next action once in its owner. If work moves,
   move the [resumption position](DATA_MODEL.md#resumption-state) and its reading
   links. Reference blockers and evidence instead of copying their current state.
3. Change parent or entry documents only when their own scope, dependencies or
   navigation change. Replace affected duplicate current claims with owner links
   under [summary ownership](DATA_MODEL.md#summary-ownership-and-updates).

A task status change alone requires no parent update or separate status report.
Preserve history through versions or dated records. Follow owning records before
dependent work; reducing duplicate text does not remove a prerequisite.

## Fixes across work-item boundaries

When changing a shared contract, data format or component, check its affected
consumers, tests and fixtures. Follow the [change cycle](DEVELOPMENT_METHOD.md#change-cycle-and-propagation)
and identify the owning work for each required correction.

Keep corrections in their owning tasks. A single writer responsible for the
affected tasks may revise their allocations within already authorized scope.
Declare changed write paths before editing; task boundaries alone require no
new owner approval. This does not override explicit exclusions or another
writer's assignment. Coordinate shared writes under the
[collaboration basis](COLLABORATION.md#collaboration-basis).

If a required correction is deferred, record the following in its owning item
or an existing [open item](#open-item-lifecycle):

- The defect, affected consumers and observed failure or missing evidence.
- The responsible task and writer, or the assignment that is still missing.
- The next action and the checkpoint before which the correction is needed.

"Outside this task" identifies a boundary but does not dispose of the defect.
Keep dependent work blocked where the correction is a prerequisite; independent
covered work can continue. Report missing assignments under the open-item
lifecycle. Extend closed records under [verification and completion](#verification-and-completion)
and preserve their original scope and results.

## Switching to the next plan

Plans are an organizational choice, not a single active slot. Several plans
may share an owner decision or reference their own decisions. Switching or
splitting plans does not by itself require approval.

Carry forward unfinished work explicitly. Verify the next work item's coverage
and dependencies, then apply [current-state updates](#updating-current-work-state).
Keep actual assignments accurate and report completion when the requested scope
is complete.

## Verification and completion

Choose checks that establish the declared result. Record the subject version,
the method and environment, the expected and observed result, the relevant
artifacts and the limits. Apply [check scheduling](CONTEXT_EFFICIENCY.md#check-scope-and-scheduling)
to their execution scope, timing and resource use.

**Start from the claim.** For each material outcome, identify the observable
result and a plausible failure the check must distinguish. Keep this reasoning
with the existing planned check; no separate matrix or verification document is required.

- Ground expected results in requirements, contracts or independently derived
  examples. Calling the implementation again to produce its own expected answer
  cannot establish that the answer is correct.
- Inspect what the check actually observes. An element's existence, a generated
  capture or a successful command supports only that property, not usability,
  visibility or a completed user flow.
- If the check could pass with the relevant defect still present, improve the
  observation or narrow the claim. Use assertions, known failures or representative
  cases to assess this; deliberately introducing defects is not a routine requirement.

Narrowing a check's claim does not remove required acceptance coverage.
Supply another suitable check or report the remaining outcome as unverified.

Reuse checks that already establish the result. Add a check when a missing
outcome or material regression risk needs coverage; do not add tests merely
to mirror an implementation or increase counts. Required project/CI checks remain.

**Name the check concretely.** Give the actual command or check target and the
environment it runs in. Reference the
[check commands](DATA_MODEL.md#suggested-information) in the project's entry
file and the project conventions in the overview where they exist.

Where no convention is recorded, record the command and environment actually
used, and state that the convention is undecided. Track it under the
[open-item lifecycle](#open-item-lifecycle) once a verification-level claim,
dependent work or handoff relies on it. Do not invent one.

**Keep completion evidence reproducible.** Identify the actual tested output,
including uncommitted changes. Without Git, reference a preserved tested snapshot
or equivalent versioned artifact; a pre-edit backup identifies only the earlier baseline.

For automated checks, retain or link the command, custom check code and relevant
inputs/configuration. Include random seeds when they determine the case sequence.
Use existing test files or retained evidence; no duplicate management copy is needed.
For human or exploratory observation, retain the method, conditions, sample and
results so another reviewer can assess the claim. Exact replay of human behavior
is not required.

An unavailable one-off script or unidentified tested output limits what later
work can establish. Preserve the observation, state the missing evidence and
obtain the required check before relying on it for completion or reuse.

**Verification kinds.** Record which kind each check establishes. The kinds are
distinct, not steps on one scale: a browser check need not establish
integration, nor the reverse.

| Kind | Established by | Does not establish |
|---|---|---|
| STATIC_VERIFIED | Checks that do not run the product, such as compilation, static analysis and document or link checks. | Behavior, integration or production success. |
| INTEGRATION_VERIFIED | Running the connected components together in a test environment. | Behavior in a real user interface, or in production. |
| BROWSER_VERIFIED | Exercising the product through a real browser or user interface. | Production data, configuration or load. |
| LIVE_ENV_VERIFIED | Checking in production or an environment declared equivalent. | Customer acceptance. |

Each kind holds only for its subject, version and environment. IMPLEMENTED is a
[task state](#task-states). CUSTOMER_ACCEPTED is the authorized customer's
acceptance, and CLOSED is the closure of a named subject: an open item, a
release or a project. None of them is a verification kind. Name the subject
whenever CLOSED is reported, since an open item's closure is not a release's.

**Before completion, release, handover or push.** Review the diff and the
relevant verification.

- Apply [document validation](DATA_MODEL.md#document-validation) for document
  deliverables at the requested stage.
- Reuse applicable baseline results under
  [verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification). Moving
  from completion to push alone needs no fresh full scan.
- Required project and CI checks remain required.
- Report a check failure accurately, even when unrelated authorized work can
  continue.

No test run means no test-pass claim.

**Check the actual subject of the claim.** A stand-in — a synthetic fixture, a
copied sample, a mock of the component under test, a hand-built approximation —
is evidence about that stand-in. It says nothing about the route, build, data
or environment the claim names.

Where the claim is about real behavior, run the check against the real artifact
and record which one. State what the check covered. Where a subject has
repeated or multiple instances, name the instances actually examined; a spot
check is not a whole-subject result.

**Check visible and interactive results early.** For product changes affecting
appearance or interaction, inspect the actual product rendering and exercise
the affected interaction against its requirements.

During implementation, check a representative result before extending a shared
UI pattern or repeated asset treatment to the remaining instances. Select
representative normal and edge states for the changed mechanism, such as
layering, small viewports or long labels. Check applicable visibility, clipping,
readability, content meaning and interaction criteria.

Inspect the rendered result; element existence or capture generation alone
does not establish its visual quality. Record the artifact version, states and
instances examined, findings and limits in the owning verification record.
An agent's visual review remains distinct from required human review or customer
acceptance. Use the dispositions below when a required check cannot run.

**Inspection is not a pass.** Reading, rendering or capturing a subject
establishes a pass only against the stated criteria, and only with no
unresolved item left in its scope.

Where a whole-item or acceptance-level pass carries high consequence, confirm it
through a check separate from the writer who produced the work. Run that check
against identified artifact versions, and keep the writer's own results as their
own evidence. The separation and the identified subject are what matter, not a
particular record format; apply
[baselines](DEVELOPMENT_METHOD.md#baselines-and-review-boundaries).

**Give a subject that did not pass its own disposition.** An absent or
optimistic disposition hides it. Distinguish at least:

- examined, with evidence recorded, but not passed;
- failing the stated criteria and needing rework;
- not checkable because a required input is missing — name which one: an actor,
  permission state, data set, environment, policy state or source version;
- not applicable, with the reason it does not apply.

Equivalent project labels are fine where their mapping is stated. None of these
is a pass. Keep them out of pass counts and totals, and report each subject
under its own disposition. Raise a missing required input as an open item so it
is owned rather than carried as a silent gap. A disposition records the
subject's current standing. It neither grants nor withholds the authority to
continue.

**A later check can overturn an earlier pass.** Withdraw it explicitly once an
independent check, an audit or a discovered defect shows that a granted pass or
acceptance did not hold.

- Name the subjects whose pass is withdrawn.
- Keep both the original evidence and the finding that overturned it.
- Correct every record and summary that still reports the withdrawn result.
- Return work that was allowed to start or close on that basis to its state
  before it, under
  [cancellation and resumption](APPROVALS.md#cancellation-withdrawal-and-resumption)
  where a decision rested on it.
- Record what would restore it: which check, at what scope, by whom.

Dependent work waits behind that condition, and the condition is a real blocker
rather than a preference. A withdrawal is not an erasure. The original
observation stays as history with its limits, and unaffected evidence keeps its
standing under
[verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification).

**A closed record is extended, not rewritten.** Work already recorded as
complete sometimes must take in something it did not cover — a dependent path
the frozen scope missed, a file the check turned out to require. Append a dated
amendment stating:

- what is added;
- why it belongs to the closed work;
- what did not change, naming the subject, criteria and evidence already
  recorded.

Editing the original body instead leaves a record that no longer describes what
was done and checked at the time. It also hides the extension from the review
that would have examined it. An amendment that moves the subject, the criteria
or the result is not an amendment. It is a new check, or a withdrawal under the
paragraph above.

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
| Stage summary | Derive the current stage and active work from owning records reached through the overview. Identify stale copied summaries as discrepancies. |
| Requirement trace | One row per in-scope requirement: covering design/contract, plan, tasks with their [states](#task-states), verification records with each [verification kind](#verification-and-completion) reached and its subject version, acceptance, and blocking open items. Unrun, failed, partial or stale verification is reported as such, not as a weaker pass. |
| Coverage | Counts derived from the trace with stated denominators: requirements in scope; with an owning design; with a plan; with all non-cancelled tasks DONE; with evidence of each verification kind; accepted. Requirements whose records could not be read count as unresolved, never as covered. Subjects examined without a pass, blocked on a missing input, needing rework or not applicable are reported under their [own disposition](#verification-and-completion) and never added to a pass count; a withdrawn pass is reported as withdrawn, with the condition for restoring it. |
| Gaps and discrepancies | Requirements without covering design or work; work, contracts or verification missing their requirement/source trace under the item-boundary rules; unresolved links or IDs; summaries that contradict owning records; evidence whose subject version predates later changes to that subject; open items past their needed-by point. |
| Blockers and next action | Real blockers under the [open-item lifecycle](#open-item-lifecycle), affected scope, and the next action for each. |

For a [compact work document](DATA_MODEL.md#minimum-documentation-for-a-small-change),
trace its owning sections and linked sources. Missing separate role files are
not a gap under those rules. If no independent REQ was established,
report the bounded outcome and its evidence without counting it as full
feature/requirement coverage or inventing a requirement to fill the report.

[Direct changes](DEVELOPMENT_METHOD.md#direct-changes) leave no work record.
Where the scope covers them, take the commits since the baseline that no work
item links from Git history. Report them as unlinked changes, and do not count
them toward requirement coverage.

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

### Recurring reports

Some projects owe a report on a schedule rather than on request — weekly to a
customer, at each milestone or before a gate. That report is a deliverable. It
has an owner, a cadence, a storage location and a form its readers expect;
record those where the obligation is owned. Its basis is the one above: owning
records at a stated version, never titles or estimates. Two things differ.

**It is written at one moment and delivered at another,** and its reader acts
on it.

- Report what the writing point actually established as established.
- Report work expected between writing and delivery as expected.
- Report what could not be confirmed as unconfirmed, naming what would confirm
  it.

Closing that gap with an estimate misinforms the reader who acts on it.

**Its numbers reach people who cannot check them.** Name one source for each
progress figure, and take every issue from that same source at its current
version. That source is a designated
[external tracker](DATA_MODEL.md#external-work-trackers) where one owns work
status, and otherwise the owning records. Where nothing owns a figure, say so
instead of deriving one for the occasion.

Track the report's own state, such as drafted, ready and delivered. An
unfinished issue is then not submitted, and a delivered one is not quietly
changed; a correction after delivery is a new statement to its reader.

Keep each issue as a dated record with its basis version, and leave it as
history. A past issue is not rewritten to match later facts. The current
position stays in the owning records and the
[resumption state](DATA_MODEL.md#resumption-state), not in the latest report.
Where readers expect a fixed form, keep one template with those records; the
form serves the reader and does not change what counts as established.

A report prepared for people outside the work is communication. It is not a
source of requirements, scope or status for the work itself; apply
[non-authoritative inputs](DEVELOPMENT_METHOD.md#non-authoritative-inputs). A
figure does not become a commitment by appearing in it. Where an issued report
and the owning records disagree, the records settle it and the next issue
carries the correction. Outstanding report obligations are part of
[closure preparation](#closure-preparation).

## Closure preparation

Aggregate the declared release/project across all contributing plans. Review
required outcomes, work dispositions, decisions, applicable evidence, actual
customer acceptance, delivery status, outstanding
[reporting obligations](#recurring-reports), handover and maintenance
obligations.
Use a release inventory or existing project document.

Every required item must be complete or have an explicit disposition consistent
with the agreed scope. Deployment alone is not closure. Do not omit unfinished
work to obtain closure. Final
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
Apply [current-state updates](#updating-current-work-state) before the receiver
relies on the entry pointers. Markdown is sufficient when accepted by the delivery
contract. See [Collaboration](COLLABORATION.md).

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
