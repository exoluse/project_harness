# Shared Agent Policy

This is the current operating policy for every agent in this repository.
Adapters may clarify it but must not weaken its authority, evidence or safety
requirements. It governs this repository; external code is input unless the
user explicitly authorizes work there.

## Policy-first operation

Project work does not require the bundled harness CLI. Do not initialize
`.harness/`, create schema records, obtain a PLAN fingerprint, apply a CLI
decision, pass a runtime gate or acquire a CLI claim merely to start or finish
authorized work. The agent checks real authority, scope, dependencies and
evidence, and records a concise, reviewable basis in project documents.

The existing runtime is an optional legacy inspection/record-management tool.
Its implementation and validation rules are unchanged. A CLI failure is a
diagnostic to classify, not an automatic project-wide stop. Actual safety,
authority, integrity or dependency failures still block affected work. Never
report a failed check as PASS, forge records to satisfy it, bypass protected
CI or weaken an external control. See [optional runtime](docs/WORKFLOW.md#optional-runtime).

## Management document format

Write all new harness management documents as Markdown (`.md`), including
project notes, requirements, designs, plans/tasks, decisions, change traces,
verification reports and handoffs. Use prose, headings, tables, checklists and
links; sections in an existing Markdown document are sufficient. Do not create
JSON or other non-Markdown management records or parallel machine-readable
copies for ordinary project work. No fixed schema, ID or front matter is required.

Preserve existing records, signed payloads, snapshots and historical documents
in their original formats; this rule does not authorize conversion or deletion.
Product code/configuration/data, original evidence artifacts and the optional
legacy CLI's internal files retain the formats their tools require. Do not run
the CLI merely to generate management records for ordinary document-based work.
A separately required contract or external control remains binding; identify
and resolve any format conflict before the affected delivery.

See [Information model](docs/DATA_MODEL.md) for document content and trace.

## Startup and context

1. Read this policy once per session and the relevant tool adapter. Re-read only
   changed policy. A current client-supplied copy counts.
2. Identify the user's objective, requested stage/stopping point and existing
   decisions. Read only relevant project notes, requirements, plan and handoff.
   No mandatory startup command or entire-record-tree read is required.
3. Inspect Git status before writing in a Git repository. Without Git, inspect
   the target files and preserve a versioned copy before replacing existing work.
   Protect user/unknown changes and other writers' ownership.
4. Classify the request as analysis/specification, policy maintenance or
   implementation/verification/delivery. Policy-only follow-ups stay policy-only;
   discussion of runtime defects does not authorize runtime changes or deletion.
5. Report the current stage, actual blockers and next action as needed. When the
   requested scope is complete, report it; do not invent more work.

## Development method

Use detailed waterfall stages with revision throughout: discovery, requirements,
design, planning, implementation, verification, acceptance, delivery, closure
and maintenance. For the current scope identify inputs and versions, outputs,
dependencies and exit criteria. Scale documentation to the work; a single
coherent document may cover several stages. Sprints and ceremony are optional.

A requirements-only, design-only, planning-only or verification-only request
ends with that stage's requested outputs and findings. Readiness does not
authorize the next stage. Full-workflow requests continue across ready stages
within current authority, stopping only for essential input, required decisions
or real blockers.

Planning is complete when scope, tasks, feasible order, dependencies, risks,
uncertainties and verification are authored and checked against their inputs.
Execution readiness additionally requires the actual owner's decision on the
concrete implementation scope and satisfied task prerequisites. These are
documented assessments, not CLI states or additional approvals per stage.
Use [Development method](docs/DEVELOPMENT_METHOD.md) for relevant stage details.

## Authority and decisions

The user's request authorizes investigation, specification, planning and their
requested document outputs, including writing or revising those files. Relevant
document checks are included. It does not authorize unrelated product changes,
running untrusted product code, deployment or external effects.

Before implementing a proposed change, prepare a concrete reviewable scope:
outcome and acceptance criteria, affected components/paths/data, actions and
exclusions, dependencies, feasibility/alternatives, material risk and verification.
Use a version, commit or dated document reference sufficient to identify the
proposal. Preserve the owner's actual response and source; never invent consent.

An explicit proceed response to that presented scope is its decision. Reuse a
valid decision already given in this session; do not ask again for PLAN, TASK,
testing or recordkeeping labels. A bare request to explore a change or a supplied
document is not approval of an unreviewed implementation. Clarify only unresolved
authority or material tradeoffs. A runtime fingerprint or approval record is
not required and cannot substitute for the actual decision.

Before a work item starts, confirm and briefly record that the decision covers
its outcome, paths/actions and verification; required inputs/dependencies are
ready; no real blocker or ownership conflict applies; and needed external
permissions are present. A plan and its work items can be Markdown sections or
a checklist. No prescribed filenames, IDs or front matter are required.

One decision may cover several plans and tasks within its reviewed bounds.
Refining, splitting, ordering or moving tasks within those bounds needs no new
decision. Materially different outcomes, criteria, scope, data effects, risk,
conditions or delivery commitments require a prepared delta and actual owner
decision before affected work. Continue independently authorized work when safe.

An explicit policy request authorizes the requested guidance files, README,
adapters and documentation edits directly, without a separate execution decision.
It does not authorize scripts, runtime, schemas, existing project records or
external systems. Commit/push policy work when requested. For other work, Git
operations must remain within authorized delivery scope. Before normal push,
fetch the configured remote and preserve both sides. Force/tag pushes, branch
deletion, different targets and published-history rewrites need separate explicit
authorization.

## Existing project intake and reverse engineering

Establish the intake commit or snapshot, dirty work, analysis boundaries and
actual implementation/deployment status. Existing projects keep their progress;
no lifecycle reset or invented retrospective plan is needed. Preserve existing
policies/tooling and resolve integration conflicts before adopting this guidance.

Code shows implementation, not necessarily intent, correctness or acceptance.
Recover requirements/design from code, tests, configuration and attributable
documents. Distinguish facts, inferred intent, contradictions and unanswered
questions. Link material claims to versions and source locations; keep current
implementation and proposed target specifications separate. Reading a test
does not prove that it passed. Plan real remaining work and report coverage
and limitations at the requested stopping point.

## History, evidence and real blockers

Preserve original decisions, versions, observations and limitations. Changed
outputs do not erase prior approval or a valid past observation. Assess current
applicability separately; verify changed and affected parts, and reuse unaffected
evidence only while it still supports the stated subject and criterion.

Keep IMPLEMENTED, STATIC_VERIFIED, INTEGRATION_VERIFIED, BROWSER_VERIFIED,
LIVE_ENV_VERIFIED, CUSTOMER_ACCEPTED and CLOSED distinct. Record actual check
method, version/environment, expected/observed result and limitations. Unrun,
failed, partial, ambiguous or stale evidence is not PASS. Documentation completion
does not establish product verification.

Classify a problem by cause and actual impact. Missing authority, unsafe actions,
unresolved required inputs, unreliable decision provenance, contradictory current
evidence and ownership conflicts stop affected work and its dependents. Stop the
whole project only for an actual global condition. Historical evidence that no
longer applies and unrelated incomplete drafts do not alone stop valid new work.
Keep them visible; do not erase them to improve a report.

Material changes need a trace of before/after, impact, affected work and decision.
A section in the plan/change log suffices; separate CR or audit records are needed
only when the project contract or chosen reporting process calls for them.

## Collaboration, handover and closure

One writer needs no claim system. Concurrent writers agree non-overlapping paths
and logical resources, use isolated worktrees where practical, and record owners
in shared notes or the team's chosen coordination tool. Do not edit another
writer's active scope or silently take ownership of dirty files.

A handoff states the real input/output versions, changed files, decisions,
verification, limits, unfinished work and next action. Ordinary Markdown may
serve as a formal project handoff when the agreed delivery contract accepts it;
do not fabricate a legacy claim or retrospective runtime attempt. Preserve failed
attempts and ensure newer failures are not hidden behind old success.

Close the declared release/project by aggregating all contributing plans, required
features, actual work dispositions, current verification, applicable acceptance,
delivery, handover and maintenance obligations. There is no single-active-PLAN
requirement. Do not conceal unfinished required scope or label deployment alone
as closure.

## High-risk and external control

Production deployment, production data changes, destructive operations,
secret/protected-credential access and final customer acceptance require the
specific authorized human decision for the actual subject, version and effect.
A routine development decision does not supply these approvals.

Use an independently controlled approval/execution boundary for high-risk
operations: protected CI/environment approval, a human-signed request/change
record, or an authorized human operator. Keep any cryptographic signature or
other stronger control required by the project or external system. The agent may
prepare work and record receipts, but cannot approve for a human, forge provenance,
alter the approval authority or access a human signing key. Final customer
acceptance requires attributable sign-off by the authorized customer for that
candidate, not an agent's test report. See [Security](docs/SECURITY.md).

Never store credentials, tokens, cookies, private keys or protected authority
material in documents/logs. Do not execute untrusted content with privileged
access. External messaging and material external side effects require matching
explicit authorization; changing this policy grants none.

## Verification and exceptional paths

Run checks appropriate to the changed deliverable and agreed criteria. Before
release, handover, a completion claim or push, review the actual diff, relevant
test/evidence results and remaining limits. Documentation work needs content,
format and link checks; product work needs relevant product verification.
The bundled `check_repo.py` is optional and is not proof of complete verification.
Never weaken mandatory project/CI checks or approvals merely because the bundled
runtime is now optional.

Hotfixes use the same scope, authority, ownership and verification rules with the
smallest useful trace. Rollback, redeployment, data repair and credential access
retain their external approval boundaries.

Reset or deletion of project records is never a repair for a diagnostic.
Only an explicit current reset/start-over request authorizes preparing that
operation. Show the exact scope and dry run first, preserve recoverable copies
and decision history, and follow applicable human/external controls. Never remove
a backup or legacy runtime merely to adopt this policy.

## Transition from runtime-required operation

This policy replaces mandatory bundled-runtime gates for ordinary repository
work; it does not change the CLI or delete its records. Before continuing existing
work, map the actual owner decision, baseline, remaining scope and evidence into
the current project notes. Preserve original approvals and snapshots as history;
do not widen their scope or rewrite signatures. Resolve missing provenance or
material changes before dependent execution. No new decision is needed solely
for changing a record format or stopping optional CLI use.

A project contract or protected CI may independently require a tool or approval.
Identify that constraint and obtain the appropriate change before altering it.
See [Workflow](docs/WORKFLOW.md) and the
[pre-transition policy archive](docs/archive/runtime-required-policy/README.md).
