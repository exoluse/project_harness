# Development Method

This repository uses detailed waterfall stages with revision throughout.
[AGENTS.md](../AGENTS.md) is the governing policy. Stages describe work and
evidence; they are not mandatory CLI states. Existing projects can enter at
their actual stage without recreating an invented history.

## Stage contract

For each requested stage, identify the input versions, scope, deliverables,
dependencies, verification and exit criteria. Organize deliverables by feature
or work unit under a project overview, following the
[document boundaries](DATA_MODEL.md#document-organization). Sections suffice
within a small coherent unit; independent units need separate documents.
Sprints are optional.

| Stage | Inputs | Deliverables and exit criteria |
|---|---|---|
| Discovery | User objective, sources, current project | Problem, boundaries, stakeholders, constraints and unresolved questions are identified. |
| Requirements | Discovery and attributable evidence | Outcomes, acceptance criteria, priorities and trace are clear enough for the requested scope. |
| Design | Versioned requirements and constraints | Components, interfaces, data, alternatives, risks and requirement coverage are described. |
| Planning | Requirements, design and current progress | Feasible tasks, order, dependencies, verification and open items are authored and checked. |
| Implementation | Concrete scope decision, ready inputs and permissions | Covered work is implemented; changes and deviations are recorded. |
| Verification | Candidate version, criteria and check environment | Actual results, failures, applicability and limits are recorded for the declared verification level. |
| Acceptance | Candidate and applicable verification | The authorized customer gives attributable acceptance or feedback for the stated candidate. |
| Delivery | Release scope, operational prerequisites and permits | Delivery is performed within authority; deployed version and applicable post-delivery checks are recorded. |
| Closure | Contributions from all plans, evidence and obligations | Required work has an honest disposition; acceptance, delivery, handover and maintenance obligations are satisfied as applicable. |
| Maintenance | Released baseline and new requests/incidents | Authorized changes are traced, implemented and reverified; prior observations are preserved. |

A documentation-only engagement can close with its document deliverables;
it does not claim product implementation, production delivery or customer
acceptance. Stage readiness is a documented assessment, not another human
approval at every row.

## Stage-by-stage or continuous execution

Honor the user's stopping point. Requirements-only, design-only, planning-only
and verification-only requests end with those outputs and findings. The request
authorizes writing its document outputs and relevant document checks; no
placeholder project, PLAN or TASK record is needed.

Under a full-workflow request, continue across ready stages within the actual
decision and permissions. Prepare a concrete implementation proposal before
the owner decision when that decision has not already been given. Ask only for
essential missing input, material choices or genuinely required authority.
Do not add a separate approval of planning completion.

## Planning complete and execution ready

Planning is complete when the requested scope, work items, feasible order,
dependencies, risks, uncertainties and verification are authored and reviewed
against the inputs. Failed required planning checks mean the plan needs work;
clearly disclosed execution prerequisites may remain open.

Execution is ready when the owner has decided on the concrete implementation
scope, the selected work is covered and its real dependencies, ownership,
safety and external permissions are ready. A CLI fingerprint, applied decision,
lifecycle enum or machine gate is not a prerequisite under the current policy.
Tool output cannot create consent or turn missing evidence into a pass.

A useful plan includes:

- The intended result, acceptance criteria and explicit exclusions.
- Affected components, paths, actions and data effects.
- Tasks, ordering and actual technical dependencies.
- Feasibility, alternatives, material risks and unresolved assumptions.
- Verification methods, environments and delivery obligations.
- The actual scope decision, source and remaining prerequisites.

Before completing planning, check that independently scoped units have their
own documents, the overview indexes them, shared specifications have one
maintained source, and requirements/design/work ID links cover the requested
scope. Check item-ID coverage, uniqueness and references using the
[ID convention](DATA_MODEL.md#item-ids).
Identify planned verification without claiming evidence from an unrun stage.

## Existing project intake and reverse engineering

Preserve the intake commit or snapshot and identify dirty/unknown work before
editing. Record analysis boundaries, available sources, actual progress and
known verification/deployment status. Existing documents and tools remain
inputs; resolve conflicting project rules explicitly.

Recover requirements and design from code, configuration, tests, interfaces and
attributable product documents. Distinguish:

| Kind of statement | How to record it |
|---|---|
| Observed implementation | Source location, revision and observed behavior; state whether it was read or executed. |
| Inferred intent | Supporting evidence, uncertainty and any needed owner clarification. |
| Confirmed requirement | Actual decision or authoritative source and acceptance criterion. |
| Contradiction or unknown | Conflicting sources, missing information and affected conclusions. |
| Proposed target | Explicit desired change and its difference from the current implementation. |

Code is not proof of the original business intent, correctness or acceptance.
Tests found in the repository are not tests that have passed. Do not turn
existing code into a retrospectively approved plan or reset completed work.
Plan the remaining work from the actual baseline and report analysis coverage.
Running unfamiliar code requires a suitable environment and applicable scope;
static recovery does not require executing it.

## Requirements, tasks and execution order

Requirements state the intended outcomes and constraints. Plans organize work
to meet them. The agent may split, refine, reorder and move tasks within the
reviewed scope without another decision. Several plans may share a decision,
and ordinary documents use the project overview and feature/work boundaries.
Task refinement inside a unit can stay in its plan; a new independent feature
or change gets its own document and an overview entry.

Follow user priorities subject to real dependencies. Explain a material
tradeoff when priority and feasibility conflict. Keep dependencies visible;
do not infer a global stop from an unrelated draft or a tool's single-plan model.

## Baselines and review boundaries

Use commits, versioned documents or dated snapshots sufficient to identify
the basis for dependent work. Preserve the actual decision and its proposal.
Do not require hashes or a fixed record format solely for ceremony.

A changed version requires an applicability assessment of existing decisions
and evidence. Preserve past observations as history, including their original
limits. Reuse unaffected evidence only when it still supports the stated
criterion, subject and environment. Reverify changed outputs and affected
dependencies.

## Change classification

| Change | Treatment |
|---|---|
| Task detail, ordering or document formatting within scope | Record useful rationale and proceed under current authority. |
| Metadata or format migration with unchanged commitments | Preserve provenance and history; no decision solely for the format. |
| Changed outcome, criterion, data effect, risk or delivery commitment | Prepare the material delta and obtain the actual owner decision before affected implementation. |
| Defect or contradictory current evidence | Report honestly, assess impact and block the affected claim/work until resolved. |
| Production, destructive, credential or final acceptance action | Apply the specific human and external control in [Security](SECURITY.md). |

## Change cycle and propagation

1. Preserve the prior baseline and trace the request.
2. Assess feasibility, alternatives, uncertainty and effects on behavior, data,
   dependencies, effort/schedule, verification and delivery.
3. Update the necessary requirements, design and plan detail into a reviewable
   proposal. Identify affected and unaffected work.
4. Reuse current authority for covered refinements; obtain one actual owner
   decision for a material delta. Do not ask again for the same scope under
   different record labels.
5. Implement covered work when its real prerequisites are ready.
6. Verify changed outputs and affected dependencies; retain applicable evidence
   and document the applicability assessment.
7. Update progress, remaining obligations and handover information.

A change section or log may carry this trace. A separate CHANGE/CR record is
needed only when an agreed project or external process requires it.

## When to ask again

Ask again when a material commitment, assumption, impact, condition or authority
has changed beyond the reviewed proposal. Explain the delta. Missing essential
input also requires clarification; a simple task split does not.

Do not renew approval merely because a plan ID, file layout, optional tool
marker or lifecycle field differs. Do not widen an old decision to cover work
that was never reviewed. Continue independent covered work when safe.

## Current runtime compatibility

The bundled runtime remains unchanged and optional. Its strict validation,
state transitions, fingerprints and record constraints can reject a valid
document-based workflow. Diagnose that mismatch without claiming the CLI passed
or editing its history to satisfy it. Actual authority, integrity, dependencies
and externally mandated checks remain binding.

See [optional runtime](WORKFLOW.md#optional-runtime) and the
[legacy findings](RUNTIME_GAPS.md). Those findings are not prerequisites for
ordinary project progress under this policy.
