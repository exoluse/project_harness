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
by this example. A small search empty-state
change can keep tightly coupled stage notes in its change document; independently
managed requirements and tasks have their own files. Record the boundaries and
link dependencies. See
the [illustrative layout](DATA_MODEL.md#document-organization).

Use requirements as the primary scope boundaries under the
[requirement criteria](DATA_MODEL.md#requirement-boundaries). Search and export
are distinct requirements; displaying zero for an empty search result is a
condition of search. A correction or regression test for that count references
the existing search REQ. Separate frontend/backend tasks may cover the same
REQ, and a shared design or verification item may cover several REQs without
duplicating them. Create those work files only for actual separate management
needs; stages alone do not require a file per requirement.

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

### Detailed planning example

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

The owning change document can contain:

| Planning content | Concrete example detail |
|---|---|
| Scope and sources | Link the actual request, existing search requirement and count/state conditions, intake revision, response contract, display component and relevant tests. Preserve the distinction between inspected code and executed checks. |
| Intended change | On successful responses, render `total` including zero. Preserve the existing loading/error states and formatting. Use total matches rather than the current page's row count. |
| Edit boundaries and approach | Identify the real component/formatter and test paths. Replace the fallback that converts zero to one; inspect other callers if the formatter is shared. Keep API, storage and unrelated UI behavior outside this correction. |
| Ordered work and dependencies | The assigned writer first checks the contract and display/state callers, then changes the count handling, adds the targeted regression cases and runs component plus relevant integration checks. Record any shared-caller effect before choosing verification scope. These are steps of this one correction, not necessarily independent tasks. |
| Interface and state detail | Successful input is a required non-negative integer `total`; zero is valid. Loading and failure are separate states, not successful empty results. If the real contract permits missing/null totals, resolve the expected display before completing this plan instead of silently choosing zero. |
| Applicability | Behavior, response contract, UI states, shared callers and regression checks apply. Under these fictional inputs, the correction changes no writes, concurrency, permissions, service dependencies, resource targets or rollout behavior; refer to existing definitions for those unchanged areas. Confirm that assessment against the real diff. |
| Verification environment | Use the project's identified component runner and mocked search responses; identify the actual integration target for the search response-to-display path. Record concrete runner commands from project configuration. If unavailable, state the setup action, owner and blocked checks. |

The coverage section connects each source condition to its work and check;
the following rows are supporting detail of the same correction:

| Source condition | Planned work/check | Expected result |
|---|---|---|
| Successful empty search | Remove the zero fallback; render a success response with `total: 0` and no rows. | Count shows `0` and the existing empty state. |
| Successful non-empty search | Preserve normal rendering; check `total: 1` with one row. | Count shows `1`. |
| Total independent of page size | Check `total: 17` with only ten rows on the current page. | Count shows `17`, not `10`. |
| Existing loading and failure behavior | Exercise those states through the existing component/state path. | Existing loading/error presentation remains; neither is presented as a successful zero-result response. |

To review this plan, compare the original request and requirement with the
coverage rows, inspect the actual contract/callers and walk the response through
the display states. A plan that only tests zero misses the non-empty/pagination
conditions; a plan that fills missing totals with zero invents unspecified
behavior. Record which document checks actually ran and what remains unknown.
All product checks above remain planned until executed. No new implementation
permission follows from this example or from completing its planning checks.

### Open-item lifecycle example

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
| Answer incorporated | Update the owning contract/requirement, display design, work steps and planned missing-total check. Assess implementation authority and other prerequisites. Once those propagation checks are recorded, close this question as resolved. Product implementation and testing remain separate work with their actual states. |
| Later contradictory input | If a revised contract invalidates the answer, reopen the same question as OPEN, preserve the old decision and closure, record the new version and next action, and reassess the affected plan and dependent work. |

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
