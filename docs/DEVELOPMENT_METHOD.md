# Development Method

This is the operating policy for a detailed waterfall lifecycle with agile
revision throughout the project. Waterfall stages define what must be understood,
produced, and verified. Agile iterations allow requirements, plans, and
deliverables to evolve as feedback and evidence arrive. A completed stage is a
versioned basis for dependent work and may be reopened through the change process.

`AGENTS.md` remains canonical for authority. This document specifies agent
behavior using existing records and gates. It introduces no schema fields,
runtime states, commands, automatic transitions, or new approval types. The
current CLI operations are described in [Workflow](WORKFLOW.md).

## User and agent responsibilities

The user supplies documents, prompts, priorities, corrections, and decisions.
The agent preserves the input, distinguishes explicit requirements from its
interpretation, authors the necessary records, and advances authorized work.
The user is not expected to write record front matter, operate the CLI, or edit
state files. Added documents are input to interpret, not automatic approval.

Ask for essential missing information when it cannot be resolved from the
available material. For a proposed change, assess feasibility and impact and
prepare the concrete implementation/verification scope before asking once
whether to proceed. The owner's explicit proceed response to that proposal is
the change approval. Record and apply that same response through the PLAN flow;
do not then ask for separate PLAN or TASK approval of the same proposal. Prepare
the exact fingerprint before asking so the current runtime can bind the response
to the reviewed scope. Batch related decisions where practical and continue
within the decision without asking again at every stage or iteration.
The owner approves by an ordinary prompt response to that proposal; the agent
handles fingerprint binding and recording. No user-run approval command or
typed fingerprint is required. Runtime checks establish execution readiness,
not a decision on the owner's behalf. See [approval roles](APPROVALS.md#who-decides-and-who-checks).
High-risk signatures remain outside the agent and the prompt-only routine path.

## Stage-by-stage or continuous execution

The user can request one stage, several stages, or the full workflow. For
"requirements only", "design this", "prepare the work plan" or "verify only",
perform the requested stage and its necessary checks, report outputs and open
items, and stop. Do not begin downstream implementation or fix product defects
discovered during verification unless that work is also authorized. Completing
a stage establishes readiness, not permission to expand the user's request.

For a request to continue through the full workflow, advance across ready stages
under current authority. Ask only for essential missing information, required
decisions or material new impact; do not add a permission question at every
stage. An explicit stopping point remains in force until the user extends it.

Sequential waterfall execution is a complete supported path. Use iterations
when useful or requested; this policy does not mandate sprints or repeated
delivery cycles when the agreed work can proceed stage by stage.

### Planning complete and execution ready

These are distinct milestones, not new runtime statuses or approval types.

| Milestone | Required basis | Agent action |
|---|---|---|
| Planning complete | Requested scope, PLAN/TASK breakdown, ordering, dependencies, write scope, verification, risks and uncertainties are authored; required planning preflight and strict validation pass | Report the plan, check results and open items. For a planning-only request, stop without requesting execution approval, applying a decision or requiring a TASK gate to pass. |
| Execution ready | The current scope has an actual owner prompt decision recorded against the prepared fingerprint; the decision is applied; the selected TASK and its prerequisites pass the execution gate | Begin implementation only within the user's requested scope. Planning completion alone grants no execution authority. |

If required planning checks fail, report a draft or a plan needing revision and
the exact blockers; do not label the checks as passed. Unresolved assumptions
and implementation prerequisites must remain visible even when the planning
deliverable itself is complete.

For a full-workflow request, finish planning and present the necessary execution
decision package once, or apply the already valid decision when appropriate.
Do not add a separate owner sign-off for "planning complete". A later request
to execute a previously prepared plan first checks its currentness and any
changed inputs before the same execution decision boundary.

## Stage contract

For the current release or increment, identify its stage, scope, input versions,
deliverables, dependencies, responsible party, exit criteria, and unresolved
items. Maintain these details in the relevant specification, PLAN/TASK body,
and existing records rather than creating an empty document for every stage.
Governed scope, criteria, references, capabilities, and verification must also
be represented in the canonical fields that the current runtime understands.
Prose and a stage review cannot override a gate.

The following table defines the normal order and minimum content. Scale detail
to the project and risk. Mark an inapplicable output with a reason; do not waive
an approval boundary, a required completion criterion, or a contract obligation.
Independent investigation and preparation may overlap stages. Dependent
implementation starts only after its upstream scope is ready and authorized.

| Stage | Entry basis | Required content and deliverables | Exit criteria for dependent work |
|---|---|---|---|
| Discovery and feasibility | Owner intent and available source documents | Problem, users, business outcome, scope boundaries, constraints, feasibility, stakeholders, assumptions and unanswered questions; preserved source references | Intended outcome and exclusions are understandable; feasibility risks and missing decisions have owners and an explicit impact |
| Requirements | Discovery scope and attributable input | Functional behavior, non-functional requirements such as performance/security/accessibility, data and operational needs, priorities, observable acceptance criteria, source trace, conflicts and dependencies | Requirements in the proposed increment are testable and internally consistent; blocking ambiguities are resolved; deferred scope is explicit |
| Design | Current requirements and constraints for the increment | Architecture and component responsibilities, interfaces, data model, user flows where applicable, error behavior, security boundaries, technical choices and tradeoffs, integration and verification approach | Design covers the scoped requirements; interfaces and risky assumptions are sufficiently resolved for dependent work; decisions and residual risks are traceable |
| Planning and proposed baseline | Ready requirements, design decisions and completion criteria | PLAN/TASK breakdown, feature/criterion links, sequencing, dependencies, write scope, authorized/excluded actions, verification strategy, milestones, estimates or explicit uncertainty, delivery risks | Requested planning content is authored; required preflight and strict validation pass; check results and open items are reported. Owner approval, decision application and TASK gate passage belong to execution readiness, not planning completion. |
| Implementation | Current applied PLAN decision, ready TASK and upstream basis | Code, configuration and other planned deliverables; checks during development; updated implementation notes and trace; visible deviations and defects | Scoped behavior is implemented and ready for its required verification; failures and remaining work are explicit; implementation is not presented as verified acceptance |
| Verification and integration | Identifiable build/deliverable versions and current criteria | Relevant static, unit, integration, browser and live-environment checks; expected/actual outcomes, evidence bound to the checked version, defect resolution and regression results | Required profiles and criteria have current eligible evidence; release-blocking defects are resolved; unrun, partial, stale or inconclusive checks remain explicit |
| Customer acceptance | Verified candidate and current acceptance scope | Review or demonstration, customer feedback, disposition of deviations, exact candidate/criteria references, required human acceptance decision | Required final customer acceptance has current cryptographic approval for its subject; a demonstration or technical PASS alone does not satisfy it |
| Deployment and delivery | Release candidate, operational readiness and required acceptance | Deployment/delivery procedure, environment/configuration basis, rollout and rollback preparation, release notes, operational checks, matching high-risk approvals | The authorized release is delivered and required post-deployment checks are evidenced; deployment does not itself close the project |
| Closure and handover | Delivery and applicable acceptance obligations satisfied | Delivery, handover and maintenance-readiness evidence; ownership and runbook information; explicit disposition of remaining obligations | The project's closure contract and relevant gates pass; unresolved blocking work is not renamed as complete |
| Maintenance and evolution | Delivered baseline and incoming incidents or feedback | Support and defect analysis, revised requirements, change impact, planned corrections or increments, updated deliverables and regression evidence | Each change satisfies the stages and approvals applicable to its scope; earlier release history and acceptance remain attributable to their original versions |

Stage readiness is evaluated for the declared scope. A release may contain
several increments, each of which establishes its own upstream basis and goes
through implementation and verification. Completing one increment does not
claim readiness for the rest of the project. Overall delivery and closure still
require the complete applicable contract.

Use existing lifecycle values as descriptive progress markers. Requirements
normally sit in `SPECIFYING`; design and planning can be described across
`SPECIFYING` and `PLANNING`. There is no separate `DESIGN` runtime state.
Revisiting requirements during `BUILDING` is a change cycle, not permission to
invent a backward transition or reset project history.

## Iteration within the lifecycle

### Requirements, tasks and execution order

A PLAN organizes the tasks needed to satisfy one or more requirements, their
dependencies and execution order. Task count and granularity can evolve as the
agent learns what implementation requires. Adding or splitting a task does not
by itself mean the user requested another feature or changed an agreement.

Distinguish two decisions: what outcome and constraints the user agrees to,
and how the work is broken down and scheduled to achieve them. The agent may
refine the latter within the agreed requirements, acceptance criteria, scope,
cost/schedule commitments, capabilities and risk boundaries. No separate
business approval is needed solely for that refinement. A change to those
commitments needs impact analysis and the appropriate owner decision.

Plan count does not determine decision count. One reviewed execution scope may
be organised into several plans without asking for one owner decision per plan.
Task or plan creation, splitting, sequencing and switching within the decided
scope are agent operations. Coverage must remain demonstrable against the
presented outcomes, acceptance and verification obligations, capabilities,
conditions, risks and delivery commitments. A new plan is neither a new
business requirement by itself nor permission for work outside those bounds.
Explicit execution-scope contracts support that sharing across single-level
plans. Legacy approvals retain their original fingerprint semantics.

Determine order from technical dependencies, risk and efficiency during
planning, or from the user's stated priorities; either may change during work.
A preference is not a technical dependency. Honor user priority among feasible
tasks and complete the necessary prerequisites first. If the requested order
conflicts with a prerequisite or changes a delivery commitment, explain the
constraint and offer a feasible sequence before making the material tradeoff.
Do not invent a serial dependency where work can proceed independently.

For example, a registration requirement can produce UI, API, persistence and
verification tasks. Splitting verification into success and duplicate-account
cases refines the work if those behaviors were already required. Adding social
login changes the requested capability. Similarly, prioritizing checkout can
bring forward the minimum order-data work it depends on without reprioritizing
every unrelated order-management feature.

The runtime enforces these bounds through an explicit versioned execution-scope
contract; compatibility with older exact-bound approvals is described below.

### Iteration loop

Use small, reviewable increments within the approved scope. At each iteration:

1. Select ready TASKs by owner priority, dependencies and available capacity;
   identify the intended outcome, acceptance criteria, and verification.
2. Confirm that upstream requirements/design and the PLAN decision still cover
   the selected work; check the TASK gate before implementation.
3. Implement and run the relevant checks; surface defects and changed assumptions
   when found rather than waiting for a distant final test stage.
4. Review the actual deliverable and evidence, obtain feedback, and distinguish
   implemented, verified and accepted outcomes.
5. Apply the change process below to feedback that changes a baseline. Select
   the next eligible work, and continue within current authority.

Timeboxes, demonstrations, retrospectives and backlog ordering are useful when
they serve the project; no fixed sprint duration or mandatory ceremony is
imposed. Backlog candidates remain discovery/planning until selected into a
PLAN with executable TASKs. Reordering within existing scope and dependencies
does not itself require a new business decision under the reviewed execution
scope. Changing the agreed contract requires a decision on the material delta.
An iteration is not a child PLAN, and this policy does not enable plan hierarchy.

## Change classification

Requirements, designs, plans, code, documents, builds and delivery artifacts can
all be revised at any stage. Classify the actual effect before choosing records
or approvals; the size of the edit is not the deciding factor.

| Change | Agent response | Authority and verification consequence |
|---|---|---|
| New input or a draft clarification | Preserve its source and update draft interpretation, requirements or design; identify conflicts | Discovery/planning may proceed within the request; no implementation authority is created |
| Task addition, split or sequence refinement within agreed requirements and constraints | Update the breakdown and feasible order; trace tasks to the existing criteria and retain the reason | No new decision when explicit execution-scope coverage and prerequisites remain valid; legacy exact-bound approvals retain their original semantics |
| Explanatory correction with no normative effect | Correct prose and retain appropriate trace; confirm that behavior, scope and criteria did not change | Existing authority applies only if fingerprints and gates remain current; a product-document edit still needs its authorized TASK |
| Defect or deliverable revision within the approved contract | Use the covering TASK or plan the required rework; preserve the old attempt and identify changed outputs | Continue only if TASK scope and current approval cover the work; changed artifacts require fresh relevant verification even when the PLAN fingerprint is unchanged |
| Requirement, design-contract, scope, priority commitment, dependency, criterion or verification-contract change | Assess feasibility and impact; prepare affected requirements, design and PLAN/TASK scope; retain the prior baseline | Record and apply the single owner proceed decision on the prepared change as its PLAN approval; reassess dependent evidence and any acceptance/release approvals |
| Change after verification, acceptance or delivery | Identify the original release and the new target version; follow the same impact and planning process | Old evidence/acceptance proves only its original subject; obtain new applicable verification, acceptance and production approvals before claiming them for the revision |

A request to change agreed requirements, acceptance criteria, scope or material
constraints requires a `CR-*` change record with its impact and disposition.
A draft clarification, task refinement or in-contract correction does not
automatically need a separate CR or CHANGE approval. Preserve the old artifact
version and refresh applicable evidence even when no CR is needed. Adding a new
TASK within an explicit reviewed scope retains authority when its coverage
and prerequisites pass. Legacy exact-bound approvals still bind task structure.
Change, exception and closure approval records remain optional unless the
applicable contract or higher-risk policy requires them.

## Change cycle and propagation

The routine sequence is **assess feasibility -> assess impact -> ask once ->
record the decision -> implement and verify**. Preparing the records is the
agent's responsibility, not another decision the user must make.

1. **Capture and assess feasibility.** Preserve the prompt/document and identify
   the requested before/after behavior, reason, priority and baseline version.
   Assess technical feasibility, constraints, alternatives and uncertainty.
   Distinguish a supported conclusion from a hypothesis. If feasibility needs
   an executable experiment, plan that investigation within applicable authority;
   do not present uncertain full implementation as already proven possible.
2. **Assess impact and prepare the proposal.** Identify effects on requirements,
   design, features, data/interfaces, TASKs, dependencies, effort/schedule,
   risks, verification, acceptance and delivery. Name affected versions and
   paths, the basis for treating other parts as unaffected, and material
   assumptions or open questions. Prepare the PLAN/TASK changes, verification
   and applicable recovery approach before the decision request. Preserve the
   old baseline and distinguish the proposal from approved work. Use canonical
   fields for governed meaning, `plan sync` for derived links, and preflight,
   strict validation and the fingerprint required by the current runtime.
3. **Ask once and record the actual decision.** Present feasibility, proposed
   scope, impact, uncertainties, conditions and verification as one proposal
   bound to the prepared fingerprint, then ask whether to proceed. The owner's explicit
   response approving that proposal is the change approval and the routine
   PLAN decision. Record its actual source and apply it; do not ask again under
   another label such as PLAN approval, TASK approval or permission to test.
   Do not record an unanswered request as approved. A declined or deferred
   change is not implemented; the prior approved version and its history remain.
4. **Implement and verify.** Pass the actual TASK gate and perform the described
   work. Update trace and deliverables without silently expanding scope.
   Verify changed behavior and affected integrations; retain unaffected evidence
   only when its subject, criteria, bindings, profile and freshness remain valid.
   Record new observations and result/review attempts where that workflow applies.
   If material new impact appears, use the reconfirmation rule below before
   proceeding with the affected work. Follow applicable high-risk approvals.
5. **Reconcile and continue.** Report the revised version, verified outcomes,
   remaining limits and next eligible work. Resolve open items only after their
   propagation and evidence are complete. Do not reset project history or
   relabel the entire prior delivery as unapproved because a revision exists.

### When to ask again

Ask again when new information materially changes the outcome, acceptance
criteria, affected components/data, dependencies, cost/schedule commitments,
important feasibility assumptions, risk, required authority or conditions
presented to the owner. State the new delta, alternatives and consequence and
pause affected work. Continue unrelated work only under current authority.
Use the bounds stated in the proposal; disclose uncertainty rather than inventing
an unagreed universal cost or schedule threshold.

Do not ask again merely because the agent splits a task, adjusts a feasible
sequence, records the decision, fixes an in-scope implementation defect, or
runs already described verification. A newly proposed change not covered by the
owner's decision goes through the cycle once. Legacy fingerprint compatibility
is handled below and must not be disguised as a new business requirement.

For example, after the owner approves email registration with its described
validation and storage impact, separating duplicate-email tests into another
task does not call for a new change decision. Discovering that implementation
would migrate existing customer data or materially delay delivery requires
explaining that new impact before continuing. Production-data approval remains
a separate high-risk boundary.

Stop affected work and its dependents while their prerequisites are invalid.
Unrelated work may continue under valid task-specific execution-scope coverage.
A shared constraint or explicit dependency change, invalid record or global
blocker can still stop broader work. Legacy exact-bound plans can become stale
as a whole; neither mode permits bypassing the gate based on an impact estimate.
Use `blocked_by` and the existing G0/G1 scopes according to their real semantics.
This current execution stop does not erase the approval or verification history
of the prior version and does not by itself require changing a running release.

### Current runtime compatibility

Use `plan prepare-scope` before presenting the owner decision. The explicit
`harness.execution-scope/v1` contract binds agreed outcomes, criteria, path and
capability boundaries, risk ceiling, criterion-specific verification and material constraints.
Covered tasks may be split, reordered or organized into several single-level
plans. Apply the same decision to each covered plan; that command records
applicability and does not create another owner decision.

| Situation | Runtime treatment |
|---|---|
| Covered task refinement or another plan within the same contract | Check containment, prerequisites and the selected task gate; no new approval record |
| Same reviewed change represented by PLAN and CHANGE | Reuse the applicable PLAN decision only when the change definition was included in its reviewed scope or exact legacy snapshot |
| Earlier decision replaced or no longer applicable | Preserve and verify historical snapshots and attestations; enforce current authority separately |
| Descriptive version/progress or known unordered-list edits | Versioned scope/task fingerprints ignore that bookkeeping; material definitions remain bound |
| Obsolete derived reference | Sync removes only proven derived extras; explicit or ambiguous dependencies remain |
| Sibling task changes | Retain unrelated authority and verification only while their actual subjects, scope, dependencies and artifact bindings remain current |
| Decision package already provides a fingerprint | Reuse it while inputs remain unchanged; recording/application still check freshness |

Legacy plans without this contract retain exact PLAN/TASK fingerprint binding.
They are readable and executable under their original rules. Preparing a new
scope contract is an explicit migration of the reviewed subject and needs an
owner decision on that contract; never reinterpret an old decision as wider
permission. See [Approvals](APPROVALS.md) and [Runtime gaps](RUNTIME_GAPS.md).

Materially changed outcomes, weaker verification, broader paths/capabilities or
changed constraints need feasibility and impact assessment and one new informed
decision. The five cryptographic high-risk boundaries remain mandatory. Invalid
history or stale evidence is not repaired by inventing another owner decision.

## Baselines and review boundaries

A baseline identifies the content/version relied on by dependent work, together
with source trace, criteria, relevant decisions and evidence. It is not a
promise that the content will never change. Retain the previous basis and the
reason for replacement so the original release can still be explained.

Keep three questions distinct: what was approved for the prior version, whether
the owner approved this concrete change, and what has been verified for the
revised version. A proposed change, an unfinished revision or a stale current
PLAN does not retroactively undo a valid historical decision. Conversely, a
prior approval is not evidence that the revision works. If new evidence reveals
a defect in the old version, record that finding and its actual impact; preserve
the original observation without continuing an unsupported current PASS claim.

Review stage readiness against the table and the project's explicit criteria.
Use the existing owner PLAN decision to approve routine executable scope in one
package, including the necessary requirements and design basis. Do not invent a
human sign-off at every phase or repeat a decision for an unchanged fingerprint.
Explicit contractual stage approvals and the five high-risk boundaries still
apply. Internal reviews and feedback do not substitute for either.

Record the method's required content using the existing source, requirement,
feature, PLAN/TASK, change, open-item and evidence structures when the relevant
work needs them. Results, reviews and handoffs remain conditional on release,
audit, independent review or ownership transfer. Do not initialize a project,
create placeholder records, or migrate its schemas merely to adopt this policy.
