# Shared Agent Policy

This is the current operating policy for every agent in this repository.
Adapters may clarify it but must not weaken its authority, evidence or safety
requirements. It governs this repository; external code is input unless the
user explicitly authorizes work there.

## Policy-first operation

This repository ships policy and documentation only. It contains no runtime,
CLI, schema or record store, and no tool setup is required to follow this
policy. Assess actual authority, scope, dependencies and evidence under this
policy, and keep management records in ordinary project documents. Records left
by the former bundled runtime are historical input; see
[former runtime records](docs/WORKFLOW.md#former-runtime-records).

## Management document format

Write all new harness management documents as Markdown (`.md`), including
project notes, requirements, designs, plans/tasks, decisions, change traces,
verification reports and handoffs. Use prose, headings, tables, checklists and
links. Organize documents as a project overview plus feature/work documents,
following the boundaries below. Do not create JSON or other non-Markdown
management records or parallel machine-readable
copies for ordinary project work. Traceable items require the stable IDs below;
no fixed schema or front matter is required.

Preserve existing records, signed payloads, snapshots and historical documents
in their original formats; this rule does not authorize conversion or deletion.
Product code/configuration/data, original evidence artifacts and tool-internal
files retain the formats their tools require.
A separately required contract or external control remains binding; identify
and resolve any format conflict before the affected delivery.

See [Information model](docs/DATA_MODEL.md) for document content and trace.

## Document organization

Keep a project overview linking independently managed feature/work items.
Maintain detailed facts in one owning document and reference them elsewhere.
Use requirements as the primary basis for separating product scope. Keep a
requirement's supporting conditions, explanations and check methods with it.
Connect designs, plans, tasks and verification to the requirements they cover. Separate
related work only when it needs its own management boundary under the
[item-boundary rules](docs/DATA_MODEL.md#independent-items-and-supporting-detail).
Fixes that restore specified behavior reference the existing requirement.
The [Information model](docs/DATA_MODEL.md) is the required detailed standard
for document boundaries, identities, paths, exceptions and validation under
this policy. Other guidance summarizes or links these rules rather than
redefining them. Apply the relevant sections when authoring or checking
documents; a current copy already read in the session remains usable.

## Item identity and trace

Apply IDs to actual project deliverables under the
[ID scope](docs/DATA_MODEL.md#id-scope); the harness's own policy, overview and
exception guidance are outside that scope. Independent project items own exact
`<ID>.md` files in contextual
classification folders, subject to the required-name rule below. Agents choose
appropriate types and folders; examples do not define a closed vocabulary.
Follow the mandatory [ID rules](docs/DATA_MODEL.md#item-ids),
[item boundaries](docs/DATA_MODEL.md#independent-items-and-supporting-detail),
[document paths](docs/DATA_MODEL.md#document-paths) and
[validation criteria](docs/DATA_MODEL.md#document-validation).

## Required-name Markdown files

Apply the mandatory [required-name exceptions](docs/DATA_MODEL.md#required-name-exceptions)
when a tool, contract or repository entry convention requires a particular
name/location. Preserve consumer compatibility and document identity under
that rule; do not create duplicate authoritative copies.

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
   discussion of defects does not authorize unrelated implementation or deletion.
5. Report the current stage, actual blockers and next action as needed. When the
   requested scope is complete, report it; do not invent more work.

## Development method

Use detailed waterfall stages with revision throughout: discovery, requirements,
design, planning, implementation, verification, acceptance, delivery, closure
and maintenance. For the current scope identify inputs and versions, outputs,
dependencies and exit criteria. Scale documentation within the feature/work
boundaries above; a small coherent unit may cover several stages in one document.
Sprints and ceremony are optional.

A requirements-only, design-only, planning-only or verification-only request
ends with that stage's requested outputs and findings. Readiness does not
authorize the next stage. Full-workflow requests continue across ready stages
within current authority, stopping only for essential input, required decisions
or real blockers.

Planning is complete when scope, tasks, feasible order, dependencies, risks,
uncertainties and verification are authored and checked against their inputs.
Execution readiness additionally requires the actual owner's decision on the
concrete implementation scope and satisfied task prerequisites. These are
documented assessments; they do not add an approval at each stage.
Use [Development method](docs/DEVELOPMENT_METHOD.md) for relevant stage details.

## Authority and decisions

The user's request authorizes investigation, specification, planning and their
requested document outputs, including writing or revising those files. Relevant
document checks are included. It does not authorize unrelated product changes,
running untrusted product code, deployment or external effects.

An explicit implementation or fix request is itself a scope decision when its
intended outcome and bounds are clear from the request and session context.
Record that request and the concrete scope derived from it, then proceed with
covered edits and relevant checks. Routine choices of files, implementation
details and tests within those bounds do not require another proceed response.
An exploratory or stage-only request does not authorize later implementation.
High-risk actions and external effects retain their specific authorization and
control requirements; a direct request does not bypass them.
Use the [clear-request criteria](docs/APPROVALS.md#clear-implementation-requests)
and [material-change criteria](docs/APPROVALS.md#material-changes) for these
judgments rather than inferring a new approval boundary from implementation size.

Before implementation, establish a concrete reviewable scope:
outcome and acceptance criteria, affected components/paths/data, actions and
exclusions, dependencies, feasibility/alternatives, material risk and verification.
Use a version, commit or dated document reference sufficient to identify the
scope. Scale the detail to the work and link existing definitions. Preserve
the owner's actual request or response and source; never invent consent.

When the scope needs a decision, present it and obtain the actual owner's
response. An explicit proceed response to that scope is also a decision. Reuse a
valid decision already given in this session; do not ask again for PLAN, TASK,
testing or recordkeeping labels. A bare request to explore a change or a supplied
document is not approval of an unreviewed implementation. Clarify only unresolved
authority or material tradeoffs. A record label cannot substitute for the
actual decision.

Before a work item starts, confirm and briefly record that the decision covers
its outcome, paths/actions and verification; required inputs/dependencies are
ready; no real blocker or ownership conflict applies; and needed external
permissions are present. Organize the plan and its work items under the
[Information model](docs/DATA_MODEL.md#plans-and-tasks).

For small corrections, use its
[minimum documentation example](docs/DATA_MODEL.md#minimum-documentation-for-a-small-change).
Stage notes and completion checks alone do not create independent document
boundaries; retain separate files for independently managed items.

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

## Harness policy maintenance

For maintenance of this harness's own policy, README and agent guidance, edit
the current files directly. Git history and diffs provide the version/change
trace; when a commit is requested, its message records the reason and relevant
verification. While edits are uncommitted, the working diff and conversation
carry the scope, actual user decision, check results and remaining limits.
These satisfy the ordinary readiness, decision and change-record requirements
for policy maintenance; do not create or update a separate change note, decision
record, policy-work index or archive snapshot merely to document the edit.
There is no requirement to operate `archive/` or `changes/` for this purpose.

Keep existing historical files and links unless their cleanup is explicitly
requested. New documentation is appropriate when it is itself a requested
deliverable or needed current guidance. Use Markdown, and apply IDs according
to the [ID scope](docs/DATA_MODEL.md#id-scope). Actual project development retains its requirements, plans, tasks,
decisions and verification documents under the normal rules. Required external
records remain binding. Commit/push still requires the applicable user request.

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
For this harness's own policy edits, use the Git/conversation trace described
in [policy maintenance](#harness-policy-maintenance).

## Collaboration, handover and closure

Organize collaboration around clear plan/task boundaries, a shared directory
mapping and unique ID-only Markdown filenames. Plans define goals, scope,
dependencies, task order and overall completion criteria; tasks define concrete
outputs, an accountable writer, affected paths/logical resources and completion
checks. Each independent plan/task owns its file and links related items.
Before concurrent editing, make task assignments, folder purposes and applicable
ID allocation ranges visible to all writers. Use meaningful existing prefixes;
agent names do not replace document types. Include shared-document editing and
Git integration in the assigned scope. Maintain this coordination in existing
overview/plan/task notes; no additional approval or mandatory claim system is
needed. See [collaboration guidance](docs/COLLABORATION.md#collaboration-basis).

One writer needs no claim system. Concurrent writers agree non-overlapping paths
and logical resources, use isolated worktrees where practical, and record owners
in shared notes or the team's chosen coordination tool. Do not edit another
writer's active scope or silently take ownership of dirty files.

A handoff states the real input/output versions, changed files, decisions,
verification, limits, unfinished work and next action. Ordinary Markdown may
serve as a formal project handoff when the agreed delivery contract accepts it.
Preserve failed attempts and ensure newer failures are not hidden behind old
success.

Close the declared release/project by aggregating all contributing plans, required
features, actual work dispositions, current verification, applicable acceptance,
delivery, handover and maintenance obligations. Do not conceal unfinished
required scope or label deployment alone as closure.

## High-risk and external control

Production deployment, production data changes, destructive operations,
secret/protected-credential access and final customer acceptance require the
specific authorized human decision for the actual subject, version and effect.
A routine development decision does not supply these approvals.

Classify actual effects under
[development action boundaries](docs/SECURITY.md#classifying-development-actions).
Covered source edits, verified disposable local cleanup and protected internal
authentication use the applicable existing authority under those criteria.
Record resets, protected-value access and material external effects retain
their specific controls.

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

Reuse applicable evidence for unchanged files and criteria. Check changed
deliverables and affected references/dependencies against a known baseline;
completion, handover and push require reviewing that coverage, not automatically
rerunning the same suite. Broaden checks for gaps, failures, changed assumptions
or mandatory controls. Follow [verification reuse](docs/CONTEXT_EFFICIENCY.md#reuse-and-verification).

Run checks appropriate to the changed deliverable and agreed criteria. Before
release, handover, a completion claim or push, review the actual diff, relevant
test/evidence results and remaining limits. Documentation work needs content,
format and link checks; product work needs relevant product verification.
Never weaken mandatory project/CI checks or approvals.

Hotfixes use the same scope, authority, ownership and verification rules with the
smallest useful trace. Rollback, redeployment, data repair and credential access
retain their external approval boundaries.

Reset or deletion of project records is never a repair for a diagnostic.
Only an explicit current reset/start-over request authorizes preparing that
operation. Show the exact scope and dry run first, preserve recoverable copies
and decision history, and follow applicable human/external controls.
