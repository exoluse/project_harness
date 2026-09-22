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

These are information types, not a limit of one file per type. For a project
with sign-in and search features, maintain an overview grouping each feature's
requirements, designs, plans, tasks and verification links. Store the actual
documents in suitable classification folders, for example under `project-docs/`.
The root, folder names and hierarchy are chosen for the project, not mandated
by this example. A small search empty-state correction reuses its requirement's
separate design, plan, task and verification files, updating affected content.
Record the boundaries and
link dependencies. See
the [illustrative layout](DATA_MODEL.md#document-organization).

Use requirements as the primary scope boundaries under the
[requirement criteria](DATA_MODEL.md#requirement-boundaries). Search and export
are distinct requirements; displaying zero for an empty search result is a
condition of search. A correction or regression test for that count references
the existing search REQ. Separate frontend/backend tasks may cover the same
REQ, and a shared design or verification item may cover several REQs without
duplicating them. Preserve those document roles, create their files when needed
for the requested stage, and split further for actual separate work boundaries.

Project deliverables normally use `<document-type>/<ID>.md` under that root,
including the overview and shared specifications: for example
`overview/DOC-001.md`, `requirements/REQ-001.md`,
`plans/PLAN-001.md`, `contracts/API-001.md`, `tasks/TASK-API-001.md` and
`changes/CHG-001.md`. A short optional description can follow the ID, for example
`contracts/API-001-sign-in.md`; the body ID remains `API-001`. Keep one owning
file per ID and link its actual filename. Full titles and context belong in
the body and overview; apply [document paths](DATA_MODEL.md#document-paths)
for slug syntax and renames.
For a consumer-required name such as `README.md`, apply the
[required-name exception](DATA_MODEL.md#required-name-exceptions): retain the
required path and indexed identity instead of creating an ID-named duplicate.

Illustrative item trace: requirement `REQ-001` connects to design `DES-001`,
API contract `API-001`, screen specification `SCR-PC-001` and implementation
plan `PLAN-001`; work items might be `TASK-API-001` and `TASK-PC-001`.
This example selects three-digit formats from the [ID dictionary](ID_DICTIONARY.md);
retain the actual project's established IDs and meanings during intake.
Actual documents use resolvable links to
each item's anchor and record each task's real parent plan. A later search
requirement gets the next available `REQ` serial, not another `REQ-001` in a
different file. These syntax examples do not allocate IDs or establish evidence.

At this planning-only stopping point, record intended checks in the plans;
actual verification reports are written when those checks are performed.

For example, finding pagination code supports “the current implementation has a
pagination path.” It does not establish that pagination is a confirmed business
requirement or that its tests pass. Keep proposed behavior separate.

The document request authorizes those files and their relevant checks;
unrelated implementation or product-code execution is outside this scope.
Report document coverage and open items at this stopping point.

### Compact planning example

For the empty search count correction, a useful plan goes beyond "fix count;
add tests." The following is a fictional, bounded example, not a claim about
code, requirements, decisions or test results in this repository. In a real
project, replace the described source locations with versioned file/anchor
links and preserve the owning requirement's actual behavior.

Assume the inspected requirement specifies that a successful search displays
the API's total matching count, including zero; pagination does not change that
total. Its existing states distinguish loading, success and failure. Assume
the inspected API contract defines `total` as a required non-negative integer,
and the display currently substitutes `1` when `total` is zero. These example
inputs establish a display correction, with no API or persistent-data change.

These established inputs qualify for
[compact planning](DEVELOPMENT_METHOD.md#choosing-planning-depth). Reuse the
linked owning files and their existing IDs; the following rows identify content
ownership, not new documents to allocate for every correction:

| Owning content | Concrete example detail |
|---|---|
| Existing requirement and contract | Reference their inspected versions and the actual request. Reuse the total-count, loading and failure definitions after confirming applicability. |
| Display design | Update the formatter approach if necessary: preserve valid zero instead of substituting one. Reference the contract and retain the existing state definitions. |
| Plan and impact assessment | Record the baseline, affected display/callers and linked work/checks, the reuse basis and any unavailable prerequisite. Check shared formatter consumers before limiting impact to search. Reference existing readiness and define the correction order. |
| Task | Identify actual display/formatter and check paths, inspect callers, replace the incorrect fallback and run affected checks. Link design and check definitions, and record execution status. |
| Planned checks | In the plan/task or linked check definition, specify the actual component runner/environment. Render successful responses with total 0 and no rows, total 1 and one row, and total 17 with ten rows; expect counts 0, 1 and 17. Exercise existing loading/error states and affected response-to-display integration. |
| Planning review | In the plan, compare affected definitions with the original request/requirement and contract, walk affected states, and record findings and remaining prerequisites. A missing/null total outside the established contract requires investigation, not an invented zero fallback. |
| Verification after execution | Record the actual candidate, checks, expected/observed results and limits in the owning verification file; link it from the task and plan. Retain prior results with their original versions. |

The linked definitions provide detailed executable instructions without another
coverage matrix or unrelated-area N/A table. They retain their current content;
the implementer need not reconstruct it from change notes. Product checks remain
planned until performed; this example supplies no real approval or passing result.

If the display task completes while other API work in the wider search plan
remains, its task status changes.
Reassess dependent work in the plan. An overview saying "search implementation
in progress" can remain valid, while an exact completed-task count must be
updated. If a shared formatter change also affects export, extend the impact
assessment to that requirement's design, work and verification. A newly blocking
failure must reach affected summaries; apply the
[summary update rules](DATA_MODEL.md#summary-ownership-and-updates).

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
Prepare an overview and one work document using the chosen folders and checked
IDs. The names below are illustrative, not allocations:

| Owning file | Bounded content |
|---|---|
| `overview/DOC-001.md` | Intake revision and analysis limits, objective, folder/ID conventions and initial allocation basis/counters, observed check commands/environment, and a link to the correction. Other features remain outside this analysis. |
| `tasks/TASK-001.md` | Current basis and writer, source/expected behavior, approach, plan/execution and actual verification sections as described below. Record why the small-change exception applies; no other document owns these definitions. |

The work document is the next session's entry point:

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
- **Planning review:** compare the plan with the actual request and contract,
  walk affected states and record findings and remaining prerequisites before
  implementation. A missing/null total calls for investigation, not an invented
  fallback to make the plan appear complete.
- **Actual verification:** add the candidate, actual commands/environment,
  expected/observed results, artifacts and limits only when checks run. Keep
  failures and unrun checks visible, separate from planned checks and old results.

If a later conversation changes a governing decision, preserve its source and
update the affected current section before dependent work continues. A change
note alone must not leave conflicting instructions for the next session.

This needs no additional REQ, DES, PLAN or VER file just to fill those roles.
Where any such owner already exists, reuse it instead of moving or copying its
definition here. If scope expands to a new export requirement or work assigned
to several writers, create the necessary independent owning items before that
work starts and retain the correction's ID and history. No whole-application
reconstruction or invented historical approval is needed. This example
demonstrates documentation scope, not product success.

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

Consider a variant of the fictional count correction: the inspected contract
does not say whether a missing `total` means an empty result or an invalid
response. This changes the earlier example's known inputs; the agent cannot
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
| Later contradictory input | If a revised contract invalidates the answer, reopen the same question as OPEN, preserve the old decision and closure, record the new version and next action, and reassess the affected plan and dependent work. |

When checking and incorporating the answer finish together, one closure entry
can link the checked owner response/version, the updated contract, design, task
and planned check, and state: "CLOSED: missing total uses the invalid-response
state; the planning gap is removed; implementation and product verification
remain pending." Record the actual actor and date/version. The follow-up owner,
scope and review trigger may be inherited from the parent when unambiguous;
only differing values need local fields. Preserve earlier question/response
history without repeating the same evidence for RESOLVED and CLOSED. If the
contract update is still pending, keep RESOLVED and its next action instead.
This is a fictional record shape, not an actual decision or test result.

If the owner instead defers the question, retain the unresolved state and
blocking effect, with the next action and review trigger. A delayed answer does
not complete the display plan. If the question duplicates a shared issue,
reference that issue and its owner; the display work keeps that dependency even
if the duplicate entry is closed. A handoff carries the surviving item and its
current resolution criterion, owner, needed-by point and next action.

## 2. Prepare one concrete implementation decision

For a clear direct request such as “Fix the empty search result count to show
zero and check non-empty results,” record the actual request/source and derived
scope. Establish the outcome and acceptance criteria, affected components/data,
exclusions, dependencies, feasible approach, risks and checks, then proceed
when prerequisites are ready under the [clear-request criteria](APPROVALS.md#clear-implementation-requests).
The request supplies the scope decision; no second proceed response is needed.

When the request leaves a material choice or uncovered scope, present the
concrete proposal and its version for the owner's decision. Record the actual
response, such as “Proceed with this scope,” and its source. Do not copy these
examples as real decisions. Reuse applicable decisions across plans/tasks;
high-risk actions retain their specific authority and external controls.

## 3. Implement across several plans

Within a feature, one plan may group frontend and API task links in sections.
Each separately managed task has its own file; separate plans are appropriate
when their scope, ownership or verification needs independent tracking. The
overview indexes the documents, and each work item identifies dependencies
and verification. A small shared scope does not merge separate task definitions.
Before starting, the agent checks coverage, input readiness, ownership and
external permissions.

Task splitting or order changes within scope do not require another decision.
A new production data migration or changed acceptance criterion is a material
delta with its own applicable authority. Concurrent writers agree non-overlapping
ownership; a single writer needs no claim record.

## 4. Verify and handle feedback

Run the agreed relevant checks on the candidate and report the actual version,
environment and result. Static review, integration tests and browser verification
are distinct. An unavailable environment is a limit, not a pass.

For feedback, preserve the previous candidate and observations. Assess the
change, obtain a decision for a material delta when needed, and reverify affected
outputs. Unrelated historical evidence stays visible without automatically
stopping independent work.

## 5. Accept, deliver and close

The authorized customer supplies final acceptance for the identified candidate
when the contract requires it. Production deployment uses the specific human
decision and an independently controlled deployment boundary; a development
decision or agent test report cannot replace either.

Aggregate frontend/API work, actual decisions, current evidence, delivery,
handover and maintenance obligations into a release inventory. Several plans
can contribute. A Markdown handoff is
sufficient if the delivery contract accepts it.
