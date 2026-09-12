# Development Method

This is the operating policy for a detailed waterfall lifecycle with agile
revision throughout the project. Waterfall stages define what must be understood,
produced, and verified. Agile iterations allow requirements, plans, and
deliverables to evolve as feedback and evidence arrive. A completed stage is a
versioned basis for dependent work and may be reopened through the change process.

`AGENTS.md` remains canonical for authority. This document specifies agent
behavior using existing records and gates. It introduces no schema fields,
runtime states, commands, automatic transitions, or new approval types. The
current CLI limitations and interim operations remain in [Workflow](WORKFLOW.md).

## User and agent responsibilities

The user supplies documents, prompts, priorities, corrections, and decisions.
The agent preserves the input, distinguishes explicit requirements from its
interpretation, authors the necessary records, and advances authorized work.
The user is not expected to write record front matter, operate the CLI, or edit
state files. Added documents are input to interpret, not automatic approval.

Ask for essential missing information when it cannot be resolved from the
available material. Prepare a concrete decision package before requesting a
PLAN decision; after an actual decision, record and apply it and continue through
the task gates. Batch related decisions where practical. Do not stop at every
stage or iteration to obtain permission already provided by the current PLAN.
High-risk signatures remain outside the agent and the prompt-only routine path.

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
| Planning and baseline | Ready requirements, design decisions and completion criteria | PLAN/TASK breakdown, feature/criterion links, sequencing, dependencies, write scope, authorized/excluded actions, verification strategy, milestones, estimates or explicit uncertainty, delivery risks | Preflight and strict validation pass; the owner decides on the exact PLAN fingerprint; the decision is applied; a TASK passes its gate before execution |
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

These are policy distinctions. Current runtime compatibility is described below;
the existing fingerprint gate still binds task structure as well as commitments.

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
does not itself require a new business decision. Today, editing a
fingerprint-bound field can still require a fresh runtime PLAN confirmation.
An iteration is not a child PLAN, and this policy does not enable plan hierarchy.

## Change classification

Requirements, designs, plans, code, documents, builds and delivery artifacts can
all be revised at any stage. Classify the actual effect before choosing records
or approvals; the size of the edit is not the deciding factor.

| Change | Agent response | Authority and verification consequence |
|---|---|---|
| New input or a draft clarification | Preserve its source and update draft interpretation, requirements or design; identify conflicts | Discovery/planning may proceed within the request; no implementation authority is created |
| Task addition, split or sequence refinement within agreed requirements and constraints | Update the breakdown and feasible order; trace tasks to the existing criteria and retain the reason | No new business decision solely for refinement; the current runtime may still invalidate its PLAN fingerprint and require confirmation before execution |
| Explanatory correction with no normative effect | Correct prose and retain appropriate trace; confirm that behavior, scope and criteria did not change | Existing authority applies only if fingerprints and gates remain current; a product-document edit still needs its authorized TASK |
| Defect or deliverable revision within the approved contract | Use the covering TASK or plan the required rework; preserve the old attempt and identify changed outputs | Continue only if TASK scope and current approval cover the work; changed artifacts require fresh relevant verification even when the PLAN fingerprint is unchanged |
| Requirement, design-contract, scope, priority commitment, dependency, criterion or verification-contract change | Record before/after, reason and impact; update affected requirements, design and PLAN/TASK references; retain the prior baseline | A changed approved subject or bound dependency needs a fresh owner PLAN decision and application; reassess dependent evidence and any acceptance/release approvals |
| Change after verification, acceptance or delivery | Identify the original release and the new target version; follow the same impact and planning process | Old evidence/acceptance proves only its original subject; obtain new applicable verification, acceptance and production approvals before claiming them for the revision |

A request to change agreed requirements, acceptance criteria, scope or material
constraints requires a `CR-*` change record with its impact and disposition.
A draft clarification, task refinement or in-contract correction does not
automatically need a separate CR or CHANGE approval. Preserve the old artifact
version and refresh applicable evidence even when no CR is needed. Adding a new
TASK currently changes the runtime's approved subject and requires renewed
PLAN authority, even when the requirement and agreement remain unchanged.
Change, exception and closure approval records remain optional unless the
applicable contract or higher-risk policy requires them.

## Change cycle and propagation

1. **Capture.** Preserve the prompt/document and identify its source, requested
   outcome, reason, priority and affected baseline. Label inferred meaning and
   resolve material ambiguity before treating it as a requirement.
2. **Assess.** Record before/after behavior and impact on requirements, design,
   interfaces/data, PLAN/TASK scope, schedule/effort, dependencies, risks,
   verification, acceptance, deployment, operations and already delivered work.
   Name affected record IDs, paths and versions; state what was assessed as
   unaffected and why. Unknown impact remains an open item, not a safe assumption.
3. **Disposition.** Propose inclusion now, deferral to a later increment,
   alternatives or rejection with consequences. Obtain owner input where the
   business choice is unresolved. Do not silently trade required scope or
   acceptance quality for a schedule target. A business preference is not yet
   executable approval of an unreviewed PLAN.
4. **Revise the basis.** Preserve the prior approved content in its existing
   snapshots/history and version the replacement. Propagate the decision through
   requirements, design, feature criteria, PLAN/TASK scope and verification.
   Use `plan sync` for derived relationships. Governed meaning belongs in the
   canonical fields, not only in explanatory prose. Do not overwrite old
   approvals, evidence, result attempts or acceptance to make them appear current.
5. **Restore authority.** Distinguish a changed agreement from ordinary task
   refinement. The former requires the owner's decision; the latter does not
   introduce a separate business approval. Under the current runtime, when the
   approved subject or bound dependencies change,
   preflight and validate again, present one consolidated package including the
   delta, impact, risks, open items, conditions and new fingerprint, then record
   and apply the owner's actual decision. Pass the TASK gate before resuming
   implementation. Follow the current [Workflow](WORKFLOW.md#changing-an-approved-plan)
   for runtime interim steps; this policy does not remove them.
6. **Rework and verify.** Revise the authorized deliverables, rerun checks for
   changed behavior and affected integrations, and record current evidence.
   Retain unchanged evidence only when its subject, criteria, bindings, profile
   and freshness still satisfy the gate. Use a new result/review attempt when
   that audit workflow applies. Revisit applicable acceptance and deployment
   decisions before claiming the changed version is accepted or live.
7. **Reconcile.** Resolve open items only after their named propagation targets
   and evidence are complete. Report the changed baseline, actual verification
   level, remaining work and next eligible step. Continue the project without
   resetting completed history or reconstructing unrelated records.

Stop affected work and its dependents while their prerequisites are invalid.
Unrelated work may continue only under valid current authority. In the current
single-level implementation, changing an approved PLAN or its bound scope can
make the decision stale for every TASK in that PLAN. Do not claim task-local
approval isolation or bypass that stop on the basis of a small impact estimate.
Use `blocked_by` and the existing G0/G1 scopes according to their real semantics.

### Current runtime compatibility

The runtime does not yet separate agreed outcomes and constraints from the
TASK breakdown in the PLAN fingerprint. As a result, even ordinary task
addition or a change to recorded dependencies can require a new confirmation
and temporarily stop the PLAN. This is an implementation mismatch with the
refinement policy, documented in [Runtime gaps](RUNTIME_GAPS.md#8-plan-approval-also-binds-routine-task-refinement).
No new approval-free runtime path is provided by this document.

Until separately authorized runtime work addresses it, keep canonical task
relationships accurate, follow the actual gate, and report this reason when
another confirmation is required. Do not omit tasks, hide changed normative
fields in prose, invent a decision, or reuse an old confirmation for a new
fingerprint to avoid the mismatch.

## Baselines and review boundaries

A baseline identifies the content/version relied on by dependent work, together
with source trace, criteria, relevant decisions and evidence. It is not a
promise that the content will never change. Retain the previous basis and the
reason for replacement so the original release can still be explained.

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
