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
with sign-in and search features, maintain an overview linking separate
`features/sign-in/` and `features/search/` documents and their shared requirements
and architecture. Each feature can have its own requirements, design and plan;
a small search empty-state change can instead use one document with those
sections. Record why the units are separate and link their dependencies. See
the [illustrative layout](DATA_MODEL.md#document-organization).

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

The document request authorizes those files and their relevant checks. It does
not require `init`, PLAN/TASK records or executing unfamiliar product code.
Report document coverage and open items at this stopping point.

## 2. Prepare one concrete implementation decision

If implementation is requested, present the proposed outcome and acceptance
criteria, affected routes/components/data, exclusions, dependencies, feasible
options, risks and checks. Identify the proposal version.

An actual owner response such as “Proceed with this scope” is recorded with its
source. Do not copy this example as a real decision. Reuse an already applicable
decision without asking again under a different plan or task label.

## 3. Implement across several plans

Within a feature, frontend and API work may be sections of its plan when they
share a small coherent scope, or separate linked plans when ownership,
dependencies or verification need independent tracking. The overview indexes
the feature documents, and each work item identifies dependencies and verification.
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
can contribute; no single active PLAN is required. A Markdown handoff is
sufficient if the delivery contract accepts it.

## Optional tooling

The bundled CLI may inspect existing legacy records when useful. Its schemas,
state rules and approval checks remain unchanged. Record tool limitations
honestly; do not manufacture history to fit this example. Independently required
CI checks and human approvals remain binding. See
[Workflow](WORKFLOW.md#optional-runtime).
