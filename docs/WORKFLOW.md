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
   [detailed planning procedure](DEVELOPMENT_METHOD.md#detailed-planning-procedure)
   and pass its [completion checks](DEVELOPMENT_METHOD.md#planning-completion-checks),
   including source coverage and executable detail. Check content and trace;
   stop there for a stage-only request.
4. For implementation, establish scope, feasibility, impact, risks, dependencies
   and verification at a useful level. A clear direct implementation request
   supplies its scope decision; record it or reference an applicable prior
   decision. Present alternatives and obtain a decision for unresolved material
   choices or uncovered scope under [Approvals](APPROVALS.md).
5. Before each work item, assess decision coverage, input readiness, ownership,
   safety and required external permissions. Document real blockers and their
   affected scope.
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

The owner decides in ordinary prompt language through a clear direct request
or a response to a concrete proposal. Record the actual request/response, source
and applicable scope version; do not invent an
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

## Closure preparation

Aggregate the declared release/project across all contributing plans. Review
required outcomes, work dispositions, decisions, applicable evidence, actual
customer acceptance, delivery status, handover and maintenance obligations.
Use a release inventory or existing project document.

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
