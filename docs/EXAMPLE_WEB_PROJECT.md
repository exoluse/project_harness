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
`overview/DOC-00001.md`, `requirements/REQ-00001.md`,
`backend-plans/API-00001.md`, `tasks/TASK-API-00001.md` and
`changes/CHG-00001.md`. Each filename stem exactly matches its body document ID;
feature names and descriptions belong in the body and overview, not filenames.
For a consumer-required name such as `README.md`, apply the
[required-name exception](DATA_MODEL.md#required-name-exceptions): retain the
required path and indexed identity instead of creating an ID-named duplicate.

Illustrative item trace: requirement `REQ-00001` connects to design `DES-00001`,
backend plan `API-00001` and screen plan `SCR-00001`; their work items might be
`TASK-API-00001` and `TASK-SCR-00001`. Actual documents use resolvable links to
each item's anchor and record each task's real parent plan. A later search
requirement gets the next available `REQ` serial, not another `REQ-00001` in a
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
