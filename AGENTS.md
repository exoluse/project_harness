# Shared Agent Policy

This is the current operating policy for every agent in this repository.
Adapters may clarify it but must not weaken its authority, evidence or safety
requirements. It governs this repository; external code is input unless the
user explicitly authorizes work there.

## Policy-first operation

Ordinary project work does not require the bundled CLI. Assess actual authority,
scope, dependencies and evidence under this policy. When using the tool, consult
[optional runtime](docs/WORKFLOW.md#optional-runtime).

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

Keep a project overview with shared goals/constraints, current status and links
to feature or work documents. For work spanning independently scoped features
or changes, create separate documents for those units; do not default to one
ever-growing requirements, design or plan file for the whole project.

Split when a unit needs its own scope/acceptance criteria, design decisions,
dependencies, owner, verification or delivery history to be reviewed independently.
Within a small coherent change, tightly coupled stage notes may be sections in
its document. Independently managed requirements, designs, plans and tasks use
their own files in the corresponding type folders. Do not create a file per
paragraph or empty documents beyond the user's requested stopping point.

Keep shared requirements and architecture at project level and link to them
from affected units. Link each unit's requirements, design, plan and actual
verification, including cross-unit dependencies. Maintain the overview's links
and summary as work changes; detailed facts have one maintained source.
Classify new project documents in suitable folders, using the exact ID-only
filenames below. Folder names, nesting and the document root are chosen for
the project; `project-docs/requirements/` is an example, not a mandatory path.
Maintain feature/work grouping in the overview and item links regardless of
the physical layout. Preserve existing records and reviewed
versions; apply this structure to new work and organize existing documents only
within the authorized scope. See [organization guidance](docs/DATA_MODEL.md#document-organization).

## Item identity and trace

Apply this principle to every Markdown document the agent creates in the
authorized project scope, including guides, research, reviews, meeting notes,
reports and handoffs, not just requirements/design/planning documents. Give
each new document an identity: reuse its primary item's ID when it represents
one item, or assign an appropriate document ID when it collects several items.
Except for [required-name files](#required-name-markdown-files), use
`<document-root>/<classification-path>/<DOCUMENT-ID>.md` for every new project
Markdown document, with the exact same ID visible near the top of its body.
For example, use `project-docs/requirements/REQ-00001.md`,
`project-docs/designs/DES-00001.md` and `project-docs/tasks/TASK-API-00001.md`.
The filename is only the ID and `.md`; descriptive suffixes such as
`REQ-00001-login.md` are not allowed. Titles belong in the document body and
overview. This includes overviews, shared specifications, research, reports
and handoffs. A body ID or an ID-bearing directory alone is insufficient.
Choose the document type, folder and ID before creating the file. The agent
chooses folder names and hierarchy from the content, workflow and existing
project conventions; none of the example folder names is mandatory. Record
and consistently reuse the project's classification mapping, extending it
autonomously for new kinds. If a folder changes, preserve IDs and update links.

Give each independently managed requirement, design, plan, task or other
primary item its own `<ID>.md` in its type folder. Overviews and collections
index those documents rather than absorbing their authoritative detail.
An independent item has its own outcome/scope or is separately assigned,
accepted, completed, decided or verified. Technical dependencies do not remove
that management boundary. Separate requirements or tasks remain separate items
even when they are short, share a feature/owner or appear in one small change.

Supporting descriptions, examples, metadata and acceptance details that define
only their parent item's meaning or completion stay in the parent's document.
They have no independently managed status or outcome; a heading or a linkable
paragraph alone does not make them independent items. If a supporting detail
acquires its own management boundary, give it its own ID/file and link it from
the parent. A plan lists links to its task files. A small change may keep tightly
coupled stage notes, but may not relabel independent requirements/tasks as
metadata to avoid separate files. See [item boundaries](docs/DATA_MODEL.md#independent-items-and-supporting-detail).
Assign a project-unique, stable ID to each independently tracked item. The agent
determines meaningful item boundaries from the document's purpose, including
requirements, criteria, design items, plans, tasks, decisions, findings, changes,
risks, issues and verification; this is an open set, not a fixed list.
Ordinary prose, metadata, navigation and explanatory headings need no item ID.
A reference or summary retains the original item's ID and links to its owning
definition; it does not create another item or duplicate authoritative detail.

Use type prefixes and five-digit serials: `REQ-00001` for requirements,
`API-00001` for backend plans, `SCR-00001` for screen plans, and
`TASK-<AREA>-00001` for tasks, such as `TASK-API-00001` or `TASK-SCR-00001`.
The task area identifies its work category, not the exact parent plan; link
parent plans explicitly. The [ID convention](docs/DATA_MODEL.md#item-ids)
provides starting examples. For a new document or item kind, the agent chooses
a meaningful type prefix and useful granularity, records the choice and
continues without asking the user to name each type. Reuse applicable project
conventions; the example prefixes do not limit which documents receive IDs.

Record the convention and any additional prefixes in the project overview.
Allocate serials across the project for each full prefix, never restarting at
file or feature boundaries. Check existing IDs before allocation; concurrent
writers reserve distinct prefixes or ranges in their shared Markdown notes.
Reuse a verified allocation baseline and consume the assigned unused range;
check intervening allocations instead of rescanning every document for each ID.
If coverage or ownership is uncertain, reconcile it before allocating. Follow
[allocation reuse](docs/DATA_MODEL.md#allocation-and-validation-reuse).
Preserve IDs across moves, title changes and revisions. Never renumber or reuse
retired IDs; link replacements when items split, merge or are superseded.

Use IDs with resolvable file/anchor links for relationships. An ID is neither
a version nor approval or verification evidence; preserve the applicable
baseline, actual decision and observed result separately. Check every new
Markdown type folder and exact filename against its body ID (or its documented
required-name mapping), plus ID coverage,
uniqueness and references before document completion. Preserve existing IDs
and historical records; this rule does not authorize bulk retroactive relabeling.
New traceable items added to existing Markdown follow the same identity rule.
Preserve externally required document formats and resolve an actual conflict
before affected delivery; do not silently omit identity requirements.

## Required-name Markdown files

The exact `<ID>.md` filename and classification-path rule has a narrow exception
for a name or location required by a tool, a project contract, or a repository
entry convention. Examples include `AGENTS.md`, `CLAUDE.md`, `SKILL.md` and the
repository landing `README.md` when their consumer requires that path/name.
Keep the required name/location so the consumer can find the file. Do not
create a duplicate `<ID>.md` copy of its authoritative content.

Assign a stable document ID and show it in the body when the consumer's format
permits it. Record the ID, canonical path and concrete reason/source for the
exception in the project overview/index. If the required body format also
forbids an ID, keep the identity mapping only in that index. References resolve
to the required-name file; independently managed contents still follow the
item-boundary rules. An ordinary project note gets no exception merely because
an author prefers a descriptive filename.

The agent checks the actual consumer/contract requirement and records this
exception under the existing task authority; no additional permission is
needed solely to preserve a required name. Verify the name/location and
applicable consumer format, the index mapping, identity uniqueness and links
instead of demanding an ID-only basename. Other scope, safety and external
approval requirements remain binding. Existing records need no bulk renaming
or retroactive labeling. See [required names](docs/DATA_MODEL.md#required-name-exceptions).

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
permissions are present. A plan and its work items can be Markdown sections or
a checklist with stable item links. Independently managed items use separate
`<ID>.md` files in their type folders; front matter is not required.

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
deliverable or needed current guidance; apply the Markdown/ID rules to such
files. Actual project development retains its requirements, plans, tasks,
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
