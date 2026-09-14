# Workflow

This is the current policy-first workflow. Follow [AGENTS.md](../AGENTS.md).
Project initialization, schema records and bundled CLI gates are not required.
A project contract or protected CI can impose separate requirements; identify
those rather than assuming this policy removes them.

## The path as it runs today

1. Identify the requested outcome, stage/stopping point, existing decisions and
   relevant project notes. Inspect dirty work before writing.
2. Establish the current input versions and preserve existing progress.
3. Produce the requested discovery, requirements, design or planning outputs.
   Maintain a project overview and separate independently scoped feature/work
   documents. Check their content and trace; stop there for a stage-only request.
4. For implementation, prepare the concrete scope, feasibility, impact, risks,
   alternatives, dependencies and verification. Record the owner's actual
   response to that proposal, or reference an applicable decision already given.
5. Before each work item, assess decision coverage, input readiness, ownership,
   safety and required external permissions. Document real blockers and their
   affected scope. No mandatory CLI command is part of this assessment.
6. Execute covered work and verify the changed deliverables against the agreed
   criteria. Preserve observations, failures and limits.
7. Deliver the requested result. For releases or project closure, include all
   contributing work, acceptance and operational obligations as applicable.

A concise Markdown (`.md`) project overview holds shared context, status and
links to feature/work documents. Each unit holds its own stage, baseline,
decision reference, tasks, prerequisites, results and next action. A small
coherent unit may combine these in sections; independent units use separate
documents under the [organization guidance](DATA_MODEL.md#document-organization).
New harness management documents must use `.md` and stable item IDs following the
[ID convention](DATA_MODEL.md#item-ids). New project Markdown uses
`<document-root>/<classification-path>/<ID>.md`: the filename is exactly the
document ID plus `.md`, without a descriptive suffix. Independently managed items have
their own files; feature groups are maintained through overview/item links.
The agent chooses folder names and hierarchy for the project and records the
mapping; example paths such as `project-docs/requirements` are not fixed names.
Use [independent-item boundaries](DATA_MODEL.md#independent-items-and-supporting-detail)
for file separation. Tool/contract/repository-required names keep their actual
paths under the [required-name exception](DATA_MODEL.md#required-name-exceptions),
with document identity and the reason recorded in the overview.
Do not create parallel JSON management records. Preserve existing records and
tool-required formats as described in the
[format policy](../AGENTS.md#management-document-format).
Do not create empty PLAN/TASK records simply to begin documenting a project.

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

The owner decides in ordinary prompt language on a concrete presented scope.
Record the actual response, source and proposal version; do not invent an
approval quote, signer or timestamp. The decision may cover several plans and
their implementation/verification within the stated bounds.

Before starting affected implementation, confirm:

- The outcome, paths/actions, data effects and checks are covered.
- Required input versions and technical dependencies are ready.
- There is no applicable ownership conflict or unresolved safety issue.
- Necessary human decisions and external permissions are present.

This is a review of facts, not a new approval ceremony. Record changes and open
items at a useful level; do not repeat unchanged checks for every small edit.
See [Approvals](APPROVALS.md).

## Changing an approved plan

Preserve the reviewed version, actual decision and observations. Refine tasks,
ordering and document structure within that scope without another decision.
For material changes, prepare the delta and its impact, obtain the applicable
owner decision once, then implement and reverify affected parts.

A sibling task edit or stale historical observation does not automatically
invalidate unrelated work. Explain actual dependency or scope impacts. Do not
copy an old PASS into new evidence without checking applicability.

## Switching to the next plan

Plans are an organizational choice, not a single active slot. Several plans
may share an owner decision or reference their own decisions. Switching or
splitting plans does not by itself require approval.

Carry forward unfinished work explicitly. Verify the next work item's coverage
and dependencies; do not retire or reassign past work solely to satisfy a
legacy state field. Report completion when the requested scope is complete.

## Verification and completion

Choose checks that establish the declared result. Document the subject version,
method/environment, expected and observed result, relevant artifacts and limits.
Use distinct levels such as STATIC_VERIFIED and INTEGRATION_VERIFIED; a document
check does not establish either product integration or production success.

Before completion, release, handover or push, review the diff and relevant
verification. For document work, also check unit boundaries, overview entries,
local file/anchor links, type-folder mapping, exact filename/body document-ID
agreement or the documented required-name mapping, item-ID coverage/uniqueness
and the requirements-to-design-to-work-to-verification trace for the requested
stage. Required project/CI checks remain required. Optional tool failure must
be reported accurately even when unrelated authorized work can continue.
No test run means no test-pass claim.

## Closure preparation

Aggregate the declared release/project across all contributing plans. Review
required outcomes, work dispositions, decisions, applicable evidence, actual
customer acceptance, delivery status, handover and maintenance obligations.
Use a release inventory or existing project document; no project schema field
or single-active-PLAN membership is required.

Every required item must be complete or have an explicit disposition consistent
with the agreed scope. Do not omit unfinished work to obtain closure. Final
customer acceptance and production actions retain [external controls](SECURITY.md).
A documentation engagement closes at its agreed document scope.

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

If the optional legacy reset command is selected, inspect its actual dry-run
output and snapshot behavior before executing it. Do not assume Git contains
uncommitted records. Do not remove snapshots, authority material or runtime code
as a side effect of policy adoption.

## Optional runtime

The existing `scripts/harness.py`, `scripts/check_repo.py`, schemas and
`.harness/tooling/` remain available and unchanged. Using them is optional
under this policy; installing Python or running `init` is not a startup step.

Use existing help/report commands when their output is useful. Record-changing
commands need matching task scope and must preserve history. Do not initialize
records for a policy-only request. A chosen legacy command still enforces its
own format, signatures, markers and state rules; this policy does not make
unsupported commands or transitions work.

Classify a diagnostic before deciding what stops:

| Finding | Handling |
|---|---|
| Missing real decision, unsafe action, required dependency or ownership conflict | Stop affected work and resolve the underlying issue. |
| Tampered authority or contradictory current evidence | Preserve evidence, investigate impact and block dependent claims/work. |
| Historical evidence no longer applicable | Retain it as history; obtain current evidence where needed. |
| Unrelated incomplete draft or bundled lifecycle/format limitation | Record the limitation; continue independently authorized document-based work. |
| Contractually required tool/CI check fails | Resolve it or obtain an authorized process change; do not bypass it. |

Never relabel a failed CLI run as PASS, fabricate a claim, edit a signature or
install an authority marker by hand. The legacy limitations in
[Runtime gaps](RUNTIME_GAPS.md) remain unimplemented unless separately verified.

## Transition from the old workflow

Preserve legacy records and approval snapshots. Map the actual owner decision,
reviewed baseline, remaining scope, current evidence and limitations into the
team's project documents. Respect the decision's original bounds and resolve
unclear provenance before affected execution.

Stopping optional CLI use or changing document format alone does not require
another decision. A project contract, protected CI or independently required
signature remains binding until changed by its authorized owner.
The [pre-transition archive](archive/runtime-required-policy/README.md) is
historical reference, not current operating instructions.
