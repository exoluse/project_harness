# Development Method

This repository uses waterfall stages with planning depth matched to the work.
[AGENTS.md](../AGENTS.md) is the governing policy. Stages describe work and
evidence. Existing projects enter at their actual stage without recreating
an invented history.

## Stage contract

For each requested stage, identify the input versions, scope, deliverables,
dependencies, verification and exit criteria. Organize deliverables under the
[document boundaries](DATA_MODEL.md#document-organization), with
[compact documentation](DATA_MODEL.md#minimum-documentation-for-a-small-change)
for bounded work. Sprints are optional.

| Stage | Inputs | Deliverables and exit criteria |
|---|---|---|
| Discovery | User objective, sources, current project | Problem, boundaries, stakeholders, constraints and unresolved questions are identified. |
| Requirements | Discovery and attributable evidence | Outcomes, acceptance criteria, priorities and trace are clear enough for the requested scope. |
| Design | Versioned requirements and constraints | Components, interfaces, data, alternatives, risks and requirement coverage are described. |
| Planning | Original scope sources, requirements, design and current progress | Source coverage, detailed work, integration order and verification pass the planning completion checks; unresolved prerequisites have an explicit disposition. |
| Implementation | Concrete scope decision, ready inputs and permissions | Covered work is implemented; the plan shows what remains, and the commit message states what was done. |
| Verification | Candidate version, criteria and check environment | Actual results, applicability and limits are stated for the declared [verification kinds](WORKFLOW.md#verification-and-completion); failures that still stand stay in their owning documents. |
| Acceptance | Candidate and applicable verification | The authorized customer gives attributable acceptance or feedback for the stated candidate. |
| Delivery | Release scope, operational prerequisites and permits | Delivery is performed within authority; the release inventory records the deployed version and applicable post-delivery checks. |
| Closure | Contributions from all plans, evidence and obligations | Required work has an honest disposition; acceptance, delivery, handover and maintenance obligations are satisfied as applicable. |
| Maintenance | Released baseline and new requests/incidents | Authorized changes are traced, implemented and reverified. |

A documentation-only engagement can close with its document deliverables;
it does not claim product implementation, production delivery or customer
acceptance. Stage readiness is an assessment, not another human approval at
every row.

## Stage-by-stage or continuous execution

Honor the user's stopping point. Requirements-only, design-only, planning-only
and verification-only requests end with those outputs and findings. The request
authorizes writing its document outputs and relevant document checks; no
placeholder project, PLAN or TASK record is needed.

Under a full-workflow request, continue across ready stages within the actual
decision and permissions under [Approvals](APPROVALS.md). Do not add a separate
approval of planning completion.

## Planning complete and execution ready

The development plan and its linked specifications/tasks are the primary basis
for implementation. Planning must make the intended work executable and
checkable, resolving details that affect the outcome. Select the planning depth
below and apply its completion checks; compact planning is the default for
bounded low-risk work.
Failed required planning checks mean the plan needs work; classify remaining
unknowns by their actual effect rather than treating their disclosure as a pass.

Execution readiness is governed by
[coverage and currentness](APPROVALS.md#coverage-and-currentness). Planning
completion alone cannot create consent or turn missing evidence into a pass.

### Choosing planning depth

Use compact planning by default for bounded, reversible work with a clear
outcome and no consequential scope/design unknown. This includes corrections
and small additions using established contracts. File count and a new requirement
alone do not require detailed planning. Nor does a project rule that each unit
needs an approved plan; a compact plan can be the plan presented for approval.

Use the detailed procedure for the affected scope when it introduces:

- New or changed public contracts, data lifecycle or access policies.
- Independently managed outputs needing coordinated delivery or ownership.
- High-risk external effects or an applicable contract requiring detailed planning.

For compact work, use the existing work document and linked definitions under
[compact documentation](DATA_MODEL.md#minimum-documentation-for-a-small-change):

1. Before editing, state the expected result and affected paths. Describe the
   chosen approach and ordered edit/check steps. Name actual check commands or
   targets and their environment; reference existing details.
2. Compare that short plan with the governing inputs and affected consumers.
   Confirm that the checks can detect the relevant wrong result under
   [claim-based verification](WORKFLOW.md#verification-and-completion).
   Fix the gaps found; keep unresolved prerequisites in the same work note.
3. Perform covered work when ready. Report actual results and limits, and put
   them in the commit message; a failure that still stands stays in the work
   note. A planning-only request stops before execution.

Use existing authority and readiness under [Approvals](APPROVALS.md#coverage-and-currentness).
Do not add an eligibility report, separate planning-review log, coverage matrix
or another proceed request. Unchanged linked definitions need no ceremonial edit.
The first two steps establish compact planning completion; product checks remain
planned until run. The [unknown dispositions](#planning-completion-checks) still apply.

If a detailed trigger appears, expand only affected planning before that work
starts. Preserve useful analysis and evidence. Changing depth alone needs no approval.

### Detailed planning procedure

For work requiring detailed planning, use this order. Reuse current
inputs and applicable checks; update affected parts when later work reveals
a gap. Keep the requested stopping point and actual implementation authority.

1. **Establish the inputs.** Identify the requested outcome, stopping point,
   source versions, actual decisions, existing progress and analysis boundaries.
   Read the relevant original requests, specifications and constraints. Extract
   each obligation and its supporting conditions into a source-linked inventory
   in the owning documents. Conversational requests need their resulting obligations,
   not a prompt reference. Separate confirmed requirements, observed behavior,
   inferred needs, proposals and unknowns. Record observed behavior only where
   it affects a requirement, gap or check, and link its source instead of
   describing the code. Include exclusions and unresolved
   contradictions; do not infer that uninspected inputs are covered.
2. **Define observable outcomes.** For each requirement, specify acceptance
   details, normal behavior, applicable boundary/failure cases and constraints.
   Walk through the affected user or system flow from trigger to final result.
   Use the detail checklist below to find necessary supporting work that was
   not explicitly named in the request. Record its rationale; newly proposed
   commitments remain proposals until covered by an actual scope decision.
   Plan [product-assumption checks](#testing-product-assumptions) where the
   intended outcome depends on use that has not yet been observed.
3. **Resolve the approach.** Locate the affected components and existing
   contracts. Specify behavior, interfaces, data changes and integration points
   at the detail below, including feasibility, relevant alternatives and why
   the selected approach fits. Investigate technical unknowns within current
   authority. Do not invent file paths, API contracts, limits or owner decisions
   to make the plan appear complete; label proposed elements and unresolved ones.
4. **Define executable work.** For each work item, record its source/requirement
   links, concrete output, accountable writer or unassigned status, affected
   paths/logical resources, inputs and prerequisites. Describe ordered actions,
   the applicable implementation details and completion checks. Include setup,
   wiring, configuration, compatibility, documentation and delivery work when
   needed by the scope. Titles such as "implement API" or "add tests" alone
   do not define executable work. Use existing document boundaries; steps and
   checklist entries do not automatically become separate tasks or files.
5. **Order and connect the work.** Identify what each dependency supplies, its
   provider and consumer, required version/contract and readiness condition.
   Include shared changes and integration work across task boundaries. Check
   for cycles, missing providers and incompatible assumptions. Separate work
   that can proceed from work blocked on a specific input or decision.
6. **Plan verification with the work.** Cover every acceptance detail and
   material failure/risk. For each, specify the scenario or input, expected
   observable result, check method, environment/fixtures and responsible work
   item. Include integration and affected regression checks. Apply
   [claim-based verification](WORKFLOW.md#verification-and-completion) to ensure
   the checks can distinguish a correct result from the relevant failure. Use the
   [recorded check commands](DATA_MODEL.md#suggested-information) or known
   commands/targets where available; otherwise specify the check to create and
   how it will run. State unrun checks as planned, including any unavailable
   environment or permission. Apply [check scheduling](CONTEXT_EFFICIENCY.md#check-scope-and-scheduling)
   to separate task, integration and release checks, including resource limits
   for costly runs. For shared UI patterns or repeated assets, schedule the
   [representative product inspection](WORKFLOW.md#verification-and-completion)
   before extending the treatment to the remaining instances.
7. **Audit from the sources and hand off.** Apply all completion checks below
   against the original inputs, linked definitions and candidate plan. Repair
   omissions and check their effects. Keep unresolved findings and remaining
   execution prerequisites in the plan as open questions. Put the reviewed
   versions and coverage result in the commit message. Report completion only
   for the scope that passed; a narrower completed subset does not complete the
   original request.

### Required implementation detail

Use these areas to find omissions in the affected scope. Record applicable
details in their owning sections; do not copy them into an applicability table
or write N/A for unrelated rows. Explain an exclusion when it could otherwise
hide a source obligation or material risk. State another exclusion only where
a reader would otherwise assume it is in scope. Write each exclusion once, in
the scope section; other sections link there. This checklist grants no
authority to add features. Domain-specific obligations from the inputs remain
required even when this checklist does not name them.

| Area | Details to resolve in the plan or linked owning specification/task |
|---|---|
| Behavior and flow | Actors/triggers, preconditions, ordered flow, states/transitions, success result, alternate paths, cancellation and repeated actions where relevant. |
| Inputs, outputs and interfaces | Producers/consumers, actual or proposed interface locations, fields/types, required/optional values, defaults, validation, bounds, response/error behavior and compatibility. |
| Data and lifecycle | Reads/writes, relationships, invariants, transaction boundaries, ordering, concurrent updates, persistence and applicable migration, retention or cleanup effects. |
| User-facing behavior | Loading, empty, success, validation and failure states; navigation, input preservation, accessibility and supported layouts/locales when applicable. |
| Failure and recovery | Invalid or missing input, missing resources, dependency errors, timeouts, partial success, retry/duplicate behavior and recovery without inconsistent state. |
| Access and protection | Relevant identity, permission and ownership checks; sensitive-data handling, trust boundaries and applicable abuse controls. Reference protected configuration without exposing values. |
| Integration and environment | Callers, consumers and shared contracts; configuration/defaults, dependencies/versions, setup, feature activation and compatibility with existing behavior. |
| Quality and operations | Applicable performance/resource budgets with sources, observability, diagnostics and operational failure handling; identify unknown targets instead of inventing numbers. |
| Delivery and maintenance | Applicable build/package, rollout order, migration/recovery, documentation and handover work, with specific external permissions kept separate from planning. |
| Verification | Normal, boundary, failure, access and regression scenarios as applicable; concrete inputs, expected results, method, environment and task coverage, including integrated behavior. |

Detail is sufficient when another implementer can follow the linked plan
without inventing required behavior, public contracts, data effects or material
verification criteria. Resolve consequential algorithms and ordering rules;
routine local coding choices may remain with the implementer. Do not prescribe
every line of code or copy specifications into every task. Compact work uses
the short procedure above and linked definitions under
[minimum documentation](DATA_MODEL.md#minimum-documentation-for-a-small-change).

### Coverage and working structure

For detailed planning, keep a coverage table or equivalent linked checklist in
the existing plan/owning work document. Start from the source inventory, not from the tasks
already written. Each input obligation and supporting acceptance detail must
reach the applicable requirement, design, work and planned verification, or
have a justified disposition. Use owning paths and stable section anchors;
retain existing IDs where present. Supporting conditions need no separate item.
Links point to authoritative definitions rather than duplicate them. Shared work may cover multiple rows.

| Source/requirement and condition | Design/behavior definition | Work and dependencies | Verification scenario and expected result | Disposition/open item |
|---|---|---|---|---|
| Link to original input and owning requirement/condition | Link to the relevant contract or decision | Link to the implementing and integrating work | Link to the planned check details | Covered, existing with evidence, proposed, deferred, excluded or unresolved; include reason and authority where required |

"Covered" here means planning coverage, not successful product verification.
Existing implementation requires a baseline and applicable evidence; where
evidence is missing, plan the needed verification. A deferred/excluded label
cannot silently remove required scope. Preserve the requested boundary and
identify any decision needed to change it.

For a new detailed plan, use this working order unless the project's existing
layout already presents the same information clearly:

1. Objective, scope/exclusions, baseline and source/decision links.
2. Input inventory and requirement/acceptance coverage.
3. Linked design and resolved implementation details, rationale and alternatives.
4. Ordered work links or owned work steps, dependencies and integration.
5. Verification scenarios, expected results, environment and coverage links.
6. Risks/unknowns, resolution work, owner and readiness impact.
7. Unresolved findings, remaining prerequisites and next action.

This is a writing aid, not a mandatory set of documents. The
[Information model](DATA_MODEL.md#plans-and-tasks) governs ownership and file
boundaries. See the [worked example](EXAMPLE_WEB_PROJECT.md#detailed-planning-example).

### Planning completion checks

For detailed planning, perform these distinct checks; compact plans use the
review under [choosing planning depth](#choosing-planning-depth). Rereading only
the plan or asking generally whether anything is missing is insufficient.
These checks may be done by one writer
and do not require repeated approval or a fixed number of review rounds.

| Check | Passing condition |
|---|---|
| Original inputs to inventory | Each relevant request, requirement, supporting condition, constraint and decision in the inspected sources is represented. Check the originals independently of the drafted inventory; report any unavailable source and its impact. |
| Inventory to implementation and verification | Every included obligation/acceptance detail has concrete design, work and check coverage. Each work item traces back to scope or a justified supporting need; exclusions/deferments respect actual authority. No unexplained empty cells or umbrella task titles stand in for detail. |
| Scenario walkthrough | Follow normal, alternate, boundary and failure flows through the affected components and task handoffs. Applicable checklist details have definitions, compatible contracts and expected results; include interactions between requirements. |
| Executability and order | Each task states outputs, edit boundaries, actions, inputs, prerequisites and completion checks. Dependencies have providers and readiness conditions; order is feasible and integration work is assigned or explicitly unassigned pending execution. Check scheduling identifies where task, integration and release evidence is obtained, with resource limits for costly checks and representative product inspection where applicable. |
| Unknowns and decisions | Apply the disposition rules below; consequential scope/design unknowns are resolved for any scope claimed complete. Remaining prerequisites have resolution actions, owners, timing and affected dependents. |
| Document consistency | Apply [document validation](DATA_MODEL.md#document-validation), including links to owning definitions and consistency with source versions. Planning coverage is not reported as passed product testing. |

Classify remaining unknowns explicitly:

- An unknown that can change required behavior, acceptance, public contracts,
  data effects, the chosen approach or task feasibility blocks completion of
  the affected implementation plan. Record an investigation/decision action,
  responsible owner (or needed assignment), expected output and affected work.
  An investigation plan may be complete for its own requested scope; it does
  not complete the dependent implementation plan. Do not hide this gap as
  "TBD during implementation."
- A later execution prerequisite, such as an environment becoming available
  or a specific deployment permission, may remain open when two conditions
  hold. First, its required state, resolution owner/action, needed-by point and
  dependent work are clear. Second, it does not conceal an unresolved
  scope/design choice. Planning completion does not mark that work
  execution-ready.
- A routine local implementation choice may remain open when its constraints
  and observable result are fixed and it cannot change the reviewed commitments.

Track follow-up under the [open-item lifecycle](WORKFLOW.md#open-item-lifecycle).
These planning dispositions describe impact, not lifecycle states. An OPEN or
WAITING execution prerequisite can be compatible with a complete plan. An
unresolved consequential design choice cannot. Check resolution evidence
and its propagation into the affected plan before removing that planning gap.
Deferral or a status label alone does not satisfy a planning completion check.

Fix the actual gaps these checks find, and recheck affected coverage and
dependencies. Keep only unresolved findings, as open questions in the plan.
Reuse unaffected review evidence. Do not:

- restart the entire plan for wording preferences;
- stop after an arbitrary retry count;
- declare completion because a checklist was filled without checking its
  linked content.

If essential input is unavailable, report the incomplete scope and needed input
honestly. Subsequent source/scope changes
reopen the affected coverage checks under the existing change rules.

### Testing product assumptions

Separate specified behavior from assumptions about its usefulness, usability
or balance. Implementing the specified values does not establish the intended
experience. Keep each consequential assumption with its owning requirement,
design or open item; no separate hypothesis register is required.

Plan the smallest authorized experiment or representative flow that can inform
the affected decision. Record the following in the owning plan or task:

- The assumption and the decision or dependent work it affects.
- The method, representative inputs or participants, and observations needed.
- The decision criteria and their source, or the unresolved criteria and owner.
- The responsible work and when the evidence is needed.

Schedule the check before expanding work that depends on the unconfirmed
assumption. An actual decision may defer it; record that decision, the risk
and the later checkpoint. Do not present an estimate or agent preference as
observed user experience.

Apply the [unknown dispositions](#planning-completion-checks) when the assumption
can change required behavior, acceptance or the approach. Calling it a hypothesis
does not make an incomplete implementation plan complete. Bounded investigation
may proceed within its own authority. Record what the experiment establishes
and its limits; [verification](WORKFLOW.md#verification-and-completion) still
distinguishes agent review, observed use and customer acceptance.

## Existing project intake and reverse engineering

Record the intake commit, or keep a versioned copy without Git, and identify
dirty/unknown work before editing. Record analysis boundaries, available
sources, actual progress, known verification/deployment status and the
observed stack and build, test and check commands under the
[project entry and conventions](DATA_MODEL.md#suggested-information).
Existing documents and tools remain inputs; resolve conflicting project rules
explicitly. Some material is kept for communication, superseded by a later
decision or scheduled for replacement. Such material is designated under
[non-authoritative inputs](#non-authoritative-inputs) rather than treated as a
source of requirements.

Recover requirements and design from code, configuration, tests, interfaces and
attributable product documents. Distinguish:

| Kind of statement | How to record it |
|---|---|
| Observed implementation | Source location, revision and observed behavior; state whether it was read or executed. |
| Inferred intent | Supporting evidence, uncertainty and any needed owner clarification. |
| Confirmed requirement | Actual decision or authoritative source and acceptance criterion. |
| Contradiction or unknown | Conflicting sources, missing information and affected conclusions. |
| Proposed target | Explicit desired change and its difference from the current implementation. |

This recording recovers definitions that no owner holds. Later planning links
those definitions and records only gaps against them; it does not survey the
code again into its plan.

Code is not proof of the original business intent, correctness or acceptance.
Tests found in the repository are not tests that have passed. Do not turn
existing code into a retrospectively approved plan or reset completed work.
Plan the remaining work from the actual baseline and report analysis coverage.
Running unfamiliar code requires a suitable environment and applicable scope;
static recovery does not require executing it.

## Execution order

Follow user priorities subject to real dependencies. Explain a material
tradeoff when priority and feasibility conflict. Refine plan-level grouping,
ordering and dependencies in the plan. Refine a separately managed task in its
owning task file. The plan updates its links rather than holding a second
definition.

## Baselines and review boundaries

Use commits or versioned copies sufficient to identify the basis for
dependent work. Keep the decided scope in its owner under
[Approvals](APPROVALS.md#preparing-and-recording-one-decision).
Do not require hashes or a fixed record format solely for ceremony.

A changed version requires an applicability assessment of existing decisions
and evidence. Replace or remove evidence that no longer applies; version
history keeps the earlier observation. Keep a failure that still stands, under
[current state only](#current-state-only). Reuse unaffected evidence only when
it still supports the stated criterion, subject and environment. Reverify
changed outputs and affected dependencies.

### Current state only

Project documents hold only what later work needs and cannot recover from the
code or version history:

- decisions in force, with any reason that still governs current work;
- open questions that block work;
- failures that still stand;
- the current position of work that spans sessions.

Requirements, designs, contracts, plans and tasks are decisions.
State their decided outcome, scope and constraints directly.
Keep rationale concise and limited to what later work needs.
Link necessary sources instead of reproducing discussions or a decision's history.
Update the owning document in place when a decision changes.
Version history, in Git or the designated tracker, carries the past;
link the commit or version where current work depends on it.

| Content | Handling |
|---|---|
| Checks run and their results, the starting state and handoff notes | Put them in the commit message when the work is committed, and report them until then. Where work stays uncommitted past a session, keep the starting state and handoff notes with the [current position](DATA_MODEL.md#resumption-state) until the commit. Without Git, keep all of them there instead. |
| History | Write none: no change notes or dated entries; no reopening, withdrawal or amendment notes; no session diaries, history files or archive snapshots. |
| A decision overturned by a later one | Delete it and record the decision in force in its place. Where no new decision replaces it, record the owner's cancellation or withdrawal as the decision in force. Update what relied on it under the [change cycle](#change-cycle-and-propagation). |
| A superseded instruction or contract | Replace it with the current one. |
| A finished or cancelled task | Delete it once its completion checks pass, or once its plan, or the overview for a standalone task, records its cancellation. Before deleting it, move any decision later work still needs to its owner. A work document that also serves as the overview keeps its project context. |
| Finished work in a plan | Delete finished work steps, and planned checks that passed for the current version, unless a check must run again at a named later point. Once the plan's completion criteria pass or its cancellation is recorded, move lasting decisions to their owner and delete the plan. The overview then links those owners. |
| Investigation, survey and review results | Put them in the commit message or the report. Keep only what they produce: a decision, work for a gap, an open question or a failure that still stands. Keep no reading lists. Describe current code only where no design owns that behavior yet, as at [intake](#existing-project-intake-and-reverse-engineering). |
| An answered open question | Put the answer in its owning definitions, then delete the question under the [open-item lifecycle](WORKFLOW.md#open-item-lifecycle). |
| A failure | Keep it while it still stands or a decision in force rests on it. A failed check stands until a later check of its scope passes, or until an actual owner decision removes its subject from scope. The same holds for a finding that overturned a pass and for an incident not yet repaired. |
| A record an external process requires | Keep that process's format and retention rules. Examples are approval records, issued reports and delivered verification evidence. |

Without version history, the versioned copy kept at
[startup](../AGENTS.md#startup-and-context) is the only earlier version.

## Input precedence

Work inputs conflict routinely. A current instruction, a received
specification, an approved contract, the code as it runs, provisional material
and the agent's own proposal rarely agree. Where the owning project records no
precedence of its own, rank them:

1. The user's current instruction and the scope and constraints it records.
2. Received specifications and the approved changes to them.
3. Approved requirements, design decisions and interface contracts.
4. Current code, configuration and tests, as evidence of present behavior.
5. Provisional material such as mock-ups, samples and drafts, as reference for
   what nothing above specifies.
6. The agent's own proposal, which is the weakest basis and stays marked as
   proposed until it is decided.

The ladder decides which input to follow so bounded work continues; it does not
hide the conflict. Record the divergence where the losing input is owned, and
apply the [change cycle](#change-cycle-and-propagation) when the correct
reading changes a commitment. A lower rank does not overtake a higher one by
being newer, more detailed or easier to implement. Detail found only in
provisional material does not become a requirement. Current behavior that
contradicts an approved contract is a defect to report, not a specification to
preserve.

The ladder ranks inputs, not authority, and it ranks what to follow rather than
what is true. It does not settle a
[material change](APPROVALS.md#material-changes), a high-risk action, a missing
required input, or contradictory evidence about whether something actually
works. Those remain [real blockers](../AGENTS.md#current-state-evidence-and-real-blockers)
for the scope they affect. Where applying the ladder would decide one of them,
stop and resolve it as an [open item](WORKFLOW.md#open-item-lifecycle) instead.

## Non-authoritative inputs

A project can designate an input as non-authoritative for development:

- material kept for communication, reporting or reference;
- a source that a later decision has superseded; or
- an implementation the current work replaces.

Record the designation, the material it covers and its owner once in the owning
overview or plan, and keep the material itself in place.

A non-authoritative input is not a requirement, scope boundary, acceptance
criterion or verification evidence. Do not derive work from it, synchronize
project documents to it, or raise its divergence from the product as a defect,
conflict or blocker. It becomes a work subject only when the user explicitly
requests work on that material, in its own context.

The designation is bounded. It does not apply to an input the project still
depends on. A contract, an external control, an authorized customer statement
and a current owning instruction stay binding wherever they are kept. An
earlier version that dependent work still names as its
[baseline](#baselines-and-review-boundaries) stays identifiable in version
history. Where actual reliance is unclear, resolve it as an
[open item](WORKFLOW.md#open-item-lifecycle) instead of assuming either reading.

## Change cycle and propagation

Apply the [material-change criteria](APPROVALS.md#material-changes) against the
actual authorized scope. Record the impact assessment once in the owning
plan/work document and reference it from affected items. Identify the change and baseline, affected owning paths and
reasons, required updates/work/checks, and the basis for reusing existing content
or evidence. Follow consumers, shared contracts and dependencies across
requirements, designs, plans, tasks and verification, including effects on
acceptance, data, authority, blockers and delivery commitments. An unchanged file
is not proof of no impact. Broaden investigation when links, baseline coverage
or effects are uncertain. Group unaffected content with a common reuse basis;
do not require a separate impact report or an N/A row for every project document.
Assign required corrections under [fixes across work-item boundaries](WORKFLOW.md#fixes-across-work-item-boundaries).

1. Identify the prior baseline and the applicable decided scope.
2. Assess feasibility, alternatives, uncertainty and effects on behavior, data,
   dependencies, effort/schedule, verification and delivery.
3. Update affected owning definitions into a reviewable current version. Keep
   requirements, design, plans, tasks and verification in their owning files
   or the sections allowed by compact documentation.
   Implementers must not have to reconstruct current instructions from a chain
   of change notes. Mark uncovered commitments as proposed until an actual
   decision covers them. Identify affected and reusable work; version history
   keeps the prior version.
4. Reuse current authority for covered refinements; obtain one actual owner
   decision for a material delta. Do not ask again for the same scope under
   different record labels.
5. Implement covered work when its real prerequisites are ready.
6. Verify changed outputs and affected dependencies. Reuse applicable evidence,
   and state the applicability assessment in the commit message.
7. Update remaining obligations and the current position under the
   [summary update rules](DATA_MODEL.md#summary-ownership-and-updates).
   Reassess affected [open items](WORKFLOW.md#open-item-lifecycle), propagate
   answers and reopen items whose basis no longer holds.

Propagation is complete when all of these hold:

- affected definitions, references and summaries are current;
- required checks for the requested stage are accounted for;
- remaining blockers/obligations have owners and next actions.

Review actual results before claiming implementation complete; planned or
failed checks are not passes.
Do not revisit unaffected documents without a new impact, contradictory evidence
or a required project check. Reuse follows
[verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification).

Keep this trace in the owning plan or work document while the change is in
progress. Delete it once propagation is complete; the current definitions and
the commit message carry it under [current state only](#current-state-only).
A separate CHANGE/CR record is needed only when an agreed project or external
process requires it.

### Conversation decisions and current instructions

When the owner settles a question or changes a prior decision in conversation,
record the decision and its covered scope in its owner under
[Approvals](APPROVALS.md#preparing-and-recording-one-decision).
Replace the superseded instruction in its owner; version history keeps it. Update the affected owning
definitions and the work item's current basis before the next action that
relies on the decision, and before handoff or completion.
A commit message cannot replace the current owning instructions. Unaccepted suggestions remain proposals.

Update only affected owners and summaries, following their ownership and the
actual editing scope. In a report-only request, describe the needed amendments
and current discrepancy without editing files. If another writer must apply an
update, record the pending change and follow
[coordination waits](COLLABORATION.md#coordination-waits). In that case, do not
present the old definition as current or claim propagation complete.

### Discoveries during implementation

Implementation can reveal that a planned approach or assumption is wrong. Apply
the change cycle to the affected work, record the observation and reopen its
planning/readiness assessment when needed. Use the
[unknown dispositions](#planning-completion-checks) to distinguish these cases:

| Discovery | Next action |
|---|---|
| A library or existing component may behave differently from the plan | Inspect the relevant version or perform an authorized, suitably isolated experiment with a stated question, boundaries and expected evidence. A bounded investigation may proceed while the dependent implementation plan remains incomplete. Record observations, then revise the approach and affected checks before resuming that implementation. |
| Observed behavior leaves a material outcome undecided, such as whether a missing API total means zero or an error | Show the source conflict, alternatives and affected work to the decision owner. Do not invent the contract to finish the plan. Continue independent covered work. |
| A local coding choice changes while behavior, contracts and checks remain valid | Choose within the established constraints without another approval. Update instructions only where the choice changes their facts or dependent work. |

Plan only the experiment needed to answer the question; it does not require a
finished design for the dependent feature. Its execution still needs matching
authority and applicable security controls. An experiment's result establishes
only what it exercised, not product acceptance. Reuse unaffected planning and
verification instead of restarting the whole project for a local discovery.
