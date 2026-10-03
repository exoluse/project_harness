# Example: Continuing an Existing Web Project

This illustrative workflow uses ordinary project documents under
[AGENTS.md](../AGENTS.md). The decisions and results below are examples, not
real approvals or verification evidence for this repository.

## 1. Recover the current specification

The user requests: “Review this existing web app and write requirements, design
and a plan for the remaining work.”

The agent identifies the intake revision, dirty work, analysis scope and existing
project rules. It reads the relevant routes, components, configuration, tests
and product documents, then writes:

| Output | Contents |
|---|---|
| Requirements | Confirmed outcomes/criteria, observed features, inferred intent and unanswered questions. |
| Design | Current components, interfaces, data flow and risks, with source/version references. |
| Remaining-work plan | Actual gaps, tasks, dependencies, alternatives, risk and verification. |

These are information types, not a limit of one file per type. Take a project
with sign-in and search features. An overview groups each feature's
requirements, designs, plans, tasks and verification links. Where the project
has no established layout, these documents are stored in the
[default folders](DATA_MODEL.md#folders-by-document-kind) under `project-docs/`.

Illustrative item trace: requirement `REQ-001` connects to design `DES-001`,
API contract `API-001`, screen specification `SCR-PC-001` and implementation
plan `PLAN-001`. Work items might be `TASK-API-001` and `TASK-PC-001`. The item
files might be stored as `requirements/REQ-001.md`, `contracts/API-001-sign-in.md`,
`tasks/TASK-API-001.md` and so on. A later search requirement gets the next
available `REQ` serial, not another `REQ-001` in a different file. Retain the
actual project's established IDs and meanings during intake. These syntax
examples do not allocate IDs or establish evidence.

At this planning-only stopping point, record intended checks in the plans;
actual verification reports are written when those checks are performed.

For example, finding pagination code supports “the current implementation has a
pagination path.” It does not establish that pagination is a confirmed business
requirement or that its tests pass. Keep proposed behavior separate.

### Compact planning example

A user requests: "Fix the search count showing one for zero results; preserve
the search API and check zero and nonzero results." This fictional example
illustrates the procedure; it is not an actual decision or test result.

Assume the inspected contract defines a required non-negative `total`.
The requirement says to display that total even when pagination returns fewer
rows. The formatter currently substitutes one for zero.
These inputs define a bounded display correction using established contracts.

Use the existing task and linked definitions. If its local approach or check
record has no owner yet, keep that content in the task under
[compact documentation](DATA_MODEL.md#minimum-documentation-for-a-small-change).
A short work note can contain:

| Content | Example |
|---|---|
| Basis and outcome | Link the actual request, source revision, requirement and API contract. Preserve valid zero; keep established loading/error behavior. |
| Steps and boundary | Identify formatter/caller paths, inspect affected consumers, remove the incorrect fallback and run the relevant component checks. The API and persistent data remain outside the change. |
| Planned checks | Name the actual runner and environment. Render totals 0, 1 and 17, including 17 with only ten returned rows; expect the displayed total to remain 0, 1 and 17. Reuse existing cases and add missing regression coverage only. |
| Results after execution | Record the tested candidate, commands, observed results and limits here or link the existing verification owner. |

Before editing, compare those steps and checks with the source contract and
affected consumers. A missing/null total outside that contract needs
investigation; do not invent a zero fallback.
Keep findings in this note without an eligibility report or separate review log.
Unchanged requirement, design and overview files need no edit.

A requested help-text addition with supplied wording can use the same compact
path. A new public export contract triggers detailed planning for that scope.
The distinction follows consequences and dependencies, not the number of files.

### Small correction without existing management documents

Consider the same count defect in a repository with code and tests but no
requirement, design or work documents. The user explicitly requests: "Fix the
search count showing one for zero results; preserve the existing search API
and verify zero and nonzero results." This fictional request supplies the
bounded correction's scope; it does not confirm every existing search behavior.

Inspect the relevant source revision, dirty work, API definition, formatter
callers and test setup. Establish the intended count behavior from the request
and attributable contract sources, distinguishing it from observed code. When
that resolves consequential unknowns, the correction qualifies for compact
planning under the [small-change rule](DATA_MODEL.md#minimum-documentation-for-a-small-change).
If the API's count semantics remain uncertain, resolve that uncertainty before
declaring the implementation plan complete.

Assume one writer owns this correction, the inspected sources establish its
expected behavior, and no shared definition or additional independently managed
output needs introducing. No project or delivery rule requires separate files.
Prepare one work document that also serves as the overview under
[compact documentation](DATA_MODEL.md#minimum-documentation-for-a-small-change).
Its ID and path below are illustrative, not an allocation:

| Owning section in `tasks/TASK-001.md` | Bounded content |
|---|---|
| Project context | Bounded objective, intake revision and analysis limits, document root, folder/ID conventions actually used, initial allocation basis/counter and observed check commands/environment. Other features remain outside this analysis. |
| Work and evidence | Current basis and writer, source/expected behavior, approach, steps and checks, findings and actual verification as described below. Keep each definition once; no separate overview or eligibility report is needed. |

Project entry links lead to this work document. It is the next session's entry point:

- **Current basis and expected behavior:** link the actual request, source
  revision and inspected API definition. State the bounded zero/nonzero count
  expectation and the existing loading/error behavior; do not claim confirmed
  requirements for all search behavior. Link the other sections and overview.
- **Approach:** identify the response-to-display flow and incorrect fallback;
  preserve valid zero while keeping the API contract. Reference the existing
  contract rather than copying it or creating another API record.
- **Plan and execution:** state the writer, affected formatter/caller paths,
  exclusions, impact/readiness assessment, ordered edit/check steps and status.
  Plan the compact example's zero, nonzero, paginated-total and applicable
  loading/error checks with the actual runner/environment found in the project.
- **Findings, when needed:** keep consequential findings and remaining prerequisites
  with the steps and checks. Compare those steps with the request and contract
  before implementation; no separate planning-review record is needed.
- **Actual verification:** add the candidate, actual commands/environment,
  expected/observed results, artifacts and limits only when checks run. Keep
  failures and unrun checks visible, separate from planned checks and old results.

This needs no additional DOC, REQ, DES, PLAN or VER file just to fill those roles.
Suppose scope expands to a new export requirement or to work assigned to
several writers. In that case, establish a separate overview under the
[expansion rule](DATA_MODEL.md#minimum-documentation-for-a-small-change) before
that work starts. This example demonstrates documentation scope, not product
success.

### Detailed planning example

If the requested work instead changes the public count contract and requires
independently assigned API and display changes, use the
[detailed procedure](DEVELOPMENT_METHOD.md#detailed-planning-procedure). Reuse the
inspected sources and existing decisions, then define the new contract,
compatibility requirements, provider/consumer work, integration order and checks.
Keep source-to-work/check coverage in the plan; link owning definitions rather
than copying them. An unresolved choice about missing totals blocks completion
of the affected implementation plan. A missing integration environment can
remain an execution prerequisite only with the required follow-up recorded.

The scope decision must cover the actual contract change. Expanding planning
detail alone neither grants that authority nor requires repeating an existing
valid decision. This variant illustrates when the compact path is insufficient;
it does not add work to the original display correction.

### Open-item lifecycle example

First consider a question answered by the inspected, authoritative contract
during the same session: "Is zero a valid total?" The owning note can record
"Yes; `total` is a non-negative integer, including zero," with the actual
contract/version link and the corresponding planned zero-result check. Once
checked and incorporated, no separate OI or state history is needed. The check
is still planned; a contract definition does not establish product success.

Consider a variant of the fictional count correction. Here the inspected
contract does not say whether a missing `total` means an empty result or an
invalid response. This changes the earlier example's known inputs; the agent cannot
assume zero. Keep the question in the owning work document unless investigation
or shared use needs a separate item under the normal boundary rules. The
following states and decisions are illustrative, not actual events.

| Event | State, impact and required record |
|---|---|
| Gap discovered | OPEN. Link the response contract/version and contradictory or missing definition. The planning agent owns follow-up; the product/API decision owner must settle intended behavior. The affected display plan cannot be completed. Resolution requires an authoritative contract or attributable owner decision defining the missing-total behavior. |
| Investigation starts | IN_PROGRESS. Inspect authorized contract sources and callers; record what they establish and any remaining ambiguity. Needed-by point: before finalizing the display/state design. Next review: after that inspection, or sooner if a relevant input changes. |
| Sources cannot settle intent | WAITING. Present the owner with alternatives, evidence and the affected scope. Record whose answer is needed and revisit on response or at the needed-by point. Independent work may continue; do not silently implement a zero fallback. |
| Owner supplies a decision | RESOLVED only after checking its source and scope. Suppose the actual answer in this fictional variant is that a missing total must use the existing invalid-response state. Link that answer and retain the former uncertainty; this settles intent, not proof of product behavior. |
| Answer incorporated | Update affected owning definitions, such as the contract, display design, work steps and planned missing-total check; retain applicable definitions unchanged. Assess implementation authority and other prerequisites. Once those propagation checks are recorded, close this question as resolved. Product implementation and testing remain separate work with their actual states. |
| Later contradictory input | If a revised contract invalidates the answer, reopen the same question as OPEN. On reopening, preserve the old decision and closure, record the new version and next action, and reassess the affected plan and dependent work. |

Checking and incorporating the answer may finish together. In that case, one
closure entry can link the checked owner response/version and the updated
contract, design, task and planned check. That entry can also state: "CLOSED:
missing total uses the invalid-response state; the planning gap is removed;
implementation and product verification remain pending." This is a fictional
record shape, not an actual decision or test result.

## 2. Prepare one concrete implementation decision

Consider a clear direct request: “Fix the empty search result count to show
zero and check non-empty results.” Such a request supplies the scope decision
under the [clear-request criteria](APPROVALS.md#clear-implementation-requests).
Record the request and derived scope, then proceed when prerequisites are
ready; no second proceed response is needed. A request may instead leave an
uncovered material choice. In that case, present the concrete proposal and
record the actual response, such as “Proceed with this scope,” with its source.
Do not copy these examples as real decisions.

## 3. Implement across several plans

Within a feature, one plan may group frontend and API task links in sections;
each separately managed task has its own file. A new production data migration
or changed acceptance criterion is a material delta with its own applicable
authority. Task splitting or reordering within scope is not.

When an API task finishes and its UI task comes next, the API task owns its
execution status and links the actual verification. The plan's resumption
record points to the UI task. The overview retains its plan link without copying
either task's status. Apply [current-state updates](WORKFLOW.md#updating-current-work-state)
so an old "awaiting implementation approval" instruction cannot survive as the
current basis after a covered implementation request. Keep the original
planning-only decision in dated history.

## 4. Verify and handle feedback

Schedule a task's changed API checks with that task and the combined browser
flow after API and UI integration. Run required release coverage at its required
checkpoint, reusing applicable evidence under [check scheduling](CONTEXT_EFFICIENCY.md#check-scope-and-scheduling).
For a shared dialog change, inspect one real product dialog in representative
states before migrating all dialogs. A narrow viewport and long error message
can expose clipping that an element-existence assertion misses. Record the
states actually examined; other dialogs still need their applicable checks.

For a claim that an error message is readable, an assertion that its element
exists can pass even when an overlay hides it. Inspect the rendered message
in the required state and use a check that observes visibility and clipping.
For a displayed total, use the contract's expected value rather than calling
the formatter under test to calculate the expectation. Both choices follow
[claim-based verification](WORKFLOW.md#verification-and-completion).

For feedback, preserve the previous candidate and observations. Obtain a
decision for a material delta when needed, then reverify the affected outputs.

## 5. Accept, deliver and close

Where the contract requires acceptance, the authorized customer accepts the
identified candidate. Production deployment uses its specific human decision
and an independently controlled deployment boundary. A development decision or
agent test report replaces neither. A release inventory aggregates the frontend/API work, actual
decisions, current evidence, delivery, handover and maintenance obligations
from every contributing plan.
