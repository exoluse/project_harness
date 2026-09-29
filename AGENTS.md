# Shared Agent Policy

This is the governing policy for every agent in this repository. It states the
common boundaries and directs work to the owning detailed rules. Adapters and
summaries must not weaken those rules. External code is input unless the user
explicitly authorizes work there.

## Policy-first operation

This repository ships policy and documentation, plus one optional
[document checker](tools/check-docs.mjs) for links, anchors, dated facts and
ID-named files. It contains no workflow runtime, schema or record store; no setup is required and
the checker is never a prerequisite for work. Assess actual authority,
scope, dependencies and evidence, using ordinary project documents. Records
left by the former runtime are historical input; see
[former runtime records](docs/WORKFLOW.md#former-runtime-records).

## Management document format

Write new management documents as Markdown (`.md`), without parallel JSON or
other machine-readable management copies. No fixed schema or front matter is
required. Preserve existing records, signed payloads, snapshots and historical
documents in their original formats; this does not authorize conversion or
deletion. Product files, original evidence and tool-internal files retain their
required formats. A designated [external work tracker](docs/DATA_MODEL.md#external-work-trackers)
may own selected management information instead of Markdown; it is the owning
record, not a parallel copy. Contracts and external controls remain binding;
resolve any format conflict before affected delivery.

## Document organization

Keep a project overview linking independently managed feature/work items, with
one owning definition per item. For a standalone compact task, its work document
may also serve as the overview under
[compact documentation](docs/DATA_MODEL.md#minimum-documentation-for-a-small-change).
Projects with several teams, streams or subsystems may split navigation into
[area overviews](docs/DATA_MODEL.md#area-overviews). Requirements are the
primary basis for product scope.

- Supporting conditions stay with their requirement, and a fix references the
  existing requirement.
- Keep requirements, designs, plans, tasks and verification in their owning
  files. Link shared definitions instead of duplicating them.
- Bounded low-risk work uses [compact documentation](docs/DATA_MODEL.md#minimum-documentation-for-a-small-change),
  reusing existing owners and keeping missing local definitions in its work document.

The [Information model](docs/DATA_MODEL.md) owns the mandatory rules for
boundaries, identities, paths, exceptions and validation. Apply them when
authoring or checking documents. Other guidance links these definitions rather
than maintaining competing versions.

## Item identity and trace

Actual project deliverables use stable IDs and `<ID>.md` or `<ID>-<slug>.md`
filenames in folders grouped by document kind under the project's document root.
Use the [folder mapping](docs/DATA_MODEL.md#folders-by-document-kind), preserving
established project conventions. The optional slug is a short description, not
part of the ID. Harness policy and guidance are outside
the [ID scope](docs/DATA_MODEL.md#id-scope). Before allocating or reorganizing,
apply the Information model's [ID rules](docs/DATA_MODEL.md#item-ids),
[boundaries](docs/DATA_MODEL.md#independent-items-and-supporting-detail) and
[paths](docs/DATA_MODEL.md#document-paths); examples are not a closed vocabulary.

## Required-name Markdown files

When a tool, contract or repository entry convention requires a name/location,
apply [required-name exceptions](docs/DATA_MODEL.md#required-name-exceptions).
Preserve consumer compatibility and identity without duplicate owning files.

## Startup and context

1. Read this policy and the adapter for your tool once per session:
   [CLAUDE.md](CLAUDE.md) for Claude Code,
   [CODEX_START_PROMPT.md](CODEX_START_PROMPT.md) for Codex. A tool may load
   only one of the two files by itself, so read the other. A current supplied
   copy counts. Reuse unchanged context. Where the project keeps
   [path-scoped instructions](docs/DATA_MODEL.md#path-scoped-instruction-files),
   read those covering the paths this work touches.
2. Identify the objective, stopping point and existing decisions. Classify work
   as analysis/specification, policy maintenance or implementation/verification/
   delivery. Discussion of defects does not authorize unrelated edits or deletion.
3. Inspect Git status before writing, and apply
   [starting execution](docs/WORKFLOW.md#starting-execution-in-a-working-tree)
   before a work item's first edit. Without Git, inspect targets and preserve
   a versioned copy before replacement. Protect user/unknown work and ownership.
4. Read the relevant project overview, owning items and the detailed rules below
   before the affected action or completion claim. Where the work records a
   [resumption state](docs/DATA_MODEL.md#resumption-state), enter from it
   instead of reconstructing an earlier session, and confirm it against the
   owning records. Current copies already read
   in the session count; follow necessary linked definitions. No full-tree read,
   mandatory startup command or routine rereading of all guidance is required.
5. Report stage, actual blockers and next action as needed; stop at the requested
   output and report completion without inventing more work.

This table routes work to its owning rules. Applicable detail is mandatory,
even when this policy or a README summarizes it; unrelated detail need not be loaded.
Open a detailed rule file by section, not whole: search for the linked heading
and read from it to the next heading of the same level. For
[DATA_MODEL.md](docs/DATA_MODEL.md), first read only its opening tables, which
end at the first `## ` heading, to choose the sections for the work.

| Trigger | Read and apply |
|---|---|
| Author or check project documents | Determine [ID scope](docs/DATA_MODEL.md#id-scope), then apply the relevant Information model sections for boundaries, allocation, paths and validation. |
| Apply the harness to a project or maintain its entry instructions | [Project instruction files](docs/DATA_MODEL.md#project-instruction-files) and, for a subtree, [path-scoped instructions](docs/DATA_MODEL.md#path-scoped-instruction-files). |
| Split an overview, delegate ID ranges or use an external tracker | [Area overviews](docs/DATA_MODEL.md#area-overviews), [allocation reuse](docs/DATA_MODEL.md#allocation-and-validation-reuse) or [external work trackers](docs/DATA_MODEL.md#external-work-trackers). |
| Prepare stage outputs or recover an existing project | Relevant [Development method](docs/DEVELOPMENT_METHOD.md) stage and intake sections. |
| Resolve conflicting inputs or rank competing sources | [Input precedence](docs/DEVELOPMENT_METHOD.md#input-precedence) and any precedence the owning project records. |
| Treat material as communication-only, superseded or to be replaced | [Non-authoritative inputs](docs/DEVELOPMENT_METHOD.md#non-authoritative-inputs) and the designation recorded in the owning overview or plan. |
| Create, revise or declare a plan complete | [Planning depth](docs/DEVELOPMENT_METHOD.md#choosing-planning-depth) and the applicable procedure and completion checks. |
| Establish scope, interpret delegation, change commitments, cancel or resume | Relevant [Approvals](docs/APPROVALS.md) criteria, including [delegated judgment](docs/APPROVALS.md#decision-requests-and-delegated-judgment), and the actual request/decision. |
| Start/transition work, resolve open items or close a release | Relevant [Workflow](docs/WORKFLOW.md) procedure and owning project records. |
| Resume work, move its position or hand it off | [Resumption state](docs/DATA_MODEL.md#resumption-state), [current work state](docs/WORKFLOW.md#updating-current-work-state) and [work-item readiness](docs/WORKFLOW.md#scope-decisions-and-work-item-readiness). |
| Record a disposition short of PASS, or withdraw an overturned pass | [Verification and completion](docs/WORKFLOW.md#verification-and-completion) and the owning verification records. |
| Report project progress or requirement trace coverage | [Status and trace reporting](docs/WORKFLOW.md#status-and-trace-reporting) and the owning project records. |
| Produce a report the project owes on a schedule | [Recurring reports](docs/WORKFLOW.md#recurring-reports) and the source that owns each figure. |
| Coordinate writers, hand off or integrate Git work | Relevant [Collaboration](docs/COLLABORATION.md) procedure, shared assignments and allocations. |
| Classify data loss, credential access or high-risk/external effects | Relevant [Security](docs/SECURITY.md) boundaries and applicable external controls before acting. |
| Configure agent tool permissions or sandboxing for a project | [Tool-level supporting controls](docs/SECURITY.md#tool-level-supporting-controls). |
| Plan checks, reuse evidence or determine recheck scope | [Verification reuse and scheduling](docs/CONTEXT_EFFICIENCY.md#reuse-and-verification), [verification methods](docs/WORKFLOW.md#verification-and-completion) and applicable project checks. |
| Delegate work or choose a model tier | [Subagent delegation](docs/COLLABORATION.md#subagent-delegation), [model selection](docs/CONTEXT_EFFICIENCY.md#model-selection-and-delegation) and the relevant adapter mapping. |
| Maintain this harness's guidance | [Policy maintenance](#harness-policy-maintenance) and [guidance maintenance](docs/CONTEXT_EFFICIENCY.md#maintaining-policy-guidance). |
| Interpret former runtime records | [Former runtime records](docs/WORKFLOW.md#former-runtime-records). |

## Development method

Use waterfall stages with revision throughout under
[Development method](docs/DEVELOPMENT_METHOD.md#stage-contract). Identify input
versions, outputs, dependencies and exit criteria for the requested scope;
use compact planning by default for bounded, reversible work with a clear outcome.
Apply [detailed planning triggers](docs/DEVELOPMENT_METHOD.md#choosing-planning-depth)
to affected scope. Sprints are optional.
Stage-only requests end with their outputs. Full-workflow requests continue
across ready stages within actual authority; readiness does not grant authority.

The plan and linked specifications/tasks are the primary implementation basis.
Planning is complete only after the procedure and completion checks for the
selected [planning depth](docs/DEVELOPMENT_METHOD.md#choosing-planning-depth)
pass, including source coverage, executable detail and unknown dispositions.
Listing consequential unknowns is not a pass. Execution additionally requires
the owner's concrete scope decision and ready prerequisites; these assessments
do not add human approval at every stage.

## Authority and decisions

Requests authorize their investigation, specification, planning and document
outputs with relevant checks. They do not authorize unrelated product edits,
untrusted product-code execution, deployment or external effects. A clear
implementation/fix request supplies its scope decision under
[Approvals](docs/APPROVALS.md#clear-implementation-requests); record the actual
request and derived scope, then perform covered edits and checks without a
second proceed response. Carry that scope onto the work item as its
[execution mode and stop conditions](docs/DATA_MODEL.md#plans-and-tasks), so a
later session reads them there rather than reconstructing the conversation.
Declare the item's inputs and shared paths with that scope, and keep its
completion checks named as actual commands. Where an item accumulates parts
authorized at different times, keep each part's scope with the decision that
authorized it.
Exploratory or stage-only requests do not authorize later implementation;
high-risk controls still apply.

Before implementation, establish a versioned, reviewable scope under
[decision preparation](docs/APPROVALS.md#preparing-and-recording-one-decision).
Apply [coverage and currentness](docs/APPROVALS.md#coverage-and-currentness)
for work-item readiness, reusing the owning assessment and recording changes
instead of repeating unchanged facts. Never invent consent or infer it from
record labels, supplied documents or passing checks.

For an uncovered commitment, apply the [material-change criteria](docs/APPROVALS.md#material-changes),
prepare the delta and obtain the actual owner's decision before affected work.
Clarify only unresolved authority, essential input or material choices; continue
independent covered work. Apply [cancellation and resumption](docs/APPROVALS.md#cancellation-withdrawal-and-resumption)
to the affected scope, preserving actual effects, unfinished work and history.

## Harness policy maintenance

An explicit policy-edit request authorizes the requested guidance, README and
adapter edits directly, not scripts, runtime, schemas, existing project records
or external systems. Edit current files; Git history/diffs and this conversation
carry scope, actual decisions, verification and limits, satisfying policy-work
readiness and trace requirements. Do not add change notes, decision records,
policy-work indexes or archive snapshots merely to document these edits.

Preserve existing historical files and links unless cleanup is explicitly
requested. Add documentation only as a requested deliverable or needed guidance;
apply the ID scope. Actual project work and required external records retain
their normal rules. Commit/push requires a matching request; commit messages
record the reason and relevant verification.

## Existing project intake and reverse engineering

Apply [existing-project intake](docs/DEVELOPMENT_METHOD.md#existing-project-intake-and-reverse-engineering)
at the actual stage, preserving progress, policies/tooling and history; resolve
integration conflicts before adoption. Establish baseline, dirty work, analysis
boundaries and actual implementation/deployment status. Distinguish observed
implementation, inferred intent, confirmed requirements and unknowns using
versioned sources. Keep proposed changes separate; reading code/tests proves
neither intent nor success. Plan remaining work and report coverage and limits.

## History, evidence and real blockers

Preserve original decisions, versions, observations and limitations. Assess their
current applicability separately; changed outputs do not erase valid history.
Keep IMPLEMENTED, STATIC_VERIFIED, INTEGRATION_VERIFIED, BROWSER_VERIFIED,
LIVE_ENV_VERIFIED, CUSTOMER_ACCEPTED and CLOSED distinct. Record actual method,
version/environment, expected/observed result and limits. Failed, unrun, partial,
ambiguous or stale evidence is not PASS; documents do not prove product success,
and a result obtained against a stand-in subject proves only that stand-in.
A subject examined without a pass, blocked on a missing input or not applicable
carries its own disposition and never joins a pass count. A pass that a later
check overturns is withdrawn explicitly, with the affected records corrected and
the condition for restoring it recorded, under
[verification](docs/WORKFLOW.md#verification-and-completion).

Missing authority, unsafe actions, unresolved required inputs, unreliable
decision provenance, contradictory current evidence and ownership conflicts
stop affected work and dependents. Stop globally only for a global condition;
unrelated drafts or stale history alone do not stop valid work. Keep failures
visible and never hide newer failures behind older success.

Manage unresolved questions/findings through the [open-item lifecycle](docs/WORKFLOW.md#open-item-lifecycle)
and [owning records](docs/DATA_MODEL.md#open-items), including follow-up,
resolution evidence, propagation and reopening. Labels cannot remove blockers.
Trace material changes under the [change cycle](docs/DEVELOPMENT_METHOD.md#change-cycle-and-propagation);
incorporate decisions from conversation into current owning instructions before
dependent work relies on them. Policy maintenance uses the Git/conversation
trace above.

## Collaboration, handover and closure

One writer needs no claim system. Before concurrent editing, establish the
[collaboration basis](docs/COLLABORATION.md#collaboration-basis): shared plan/task
boundaries, directory mapping, ID allocations and non-overlapping ownership,
including shared documents and Git integration; branch isolation with
reviewed merges and tracker-owned assignment can supply it. Use worktrees
where practical; in one working tree keep a single writing participant active
while read-only review runs alongside. Never take over another writer's active
scope or unknown dirty work silently.

For [handoff and integration](docs/COLLABORATION.md#transfer-and-integration),
carry actual versions, decisions, evidence, limits, unfinished work and next
action. Git operations stay within authorized delivery scope: stage by explicit
path so a commit carries only the item's changes, fetch before normal push and
preserve both histories; force/tag pushes, branch deletion, different targets
and published-history rewrites need separate explicit authorization.

Apply [closure preparation](docs/WORKFLOW.md#closure-preparation) across all
contributing work and applicable acceptance, delivery, handoff and maintenance
obligations. Deployment alone is not closure; do not conceal unfinished scope.

## High-risk and external control

Production deployment/data changes, destructive operations, secret/protected-
credential access and final customer acceptance require specific authorized
human decisions for the actual subject, version and effect, with independently
controlled approval/execution boundaries under [Security](docs/SECURITY.md).
Routine development authority is insufficient; preserve stronger external controls.

Classify actual effects under [development action boundaries](docs/SECURITY.md#classifying-development-actions).
Covered source edits and verified disposable cleanup use existing authority
under those criteria, and so does an already authenticated tool that uses its
credential internally without exposing it. Opening a credential file, dumping
environment variables or otherwise reading a raw token, cookie or key is
protected-credential access and needs its own specific decision. Never approve for a human,
forge provenance, alter approval authority or access a human signing key.
Customer acceptance requires the authorized customer's attributable sign-off.

Never store secrets or protected authority material in documents/logs or execute
untrusted content with privileged access. External messaging and material
external side effects require matching explicit authorization; policy edits
grant none.

## Verification and exceptional paths

Before completion, release, handover or push, review the actual diff, evidence
coverage and limits. Check changed deliverables and affected dependencies;
reuse applicable evidence under [verification reuse](docs/CONTEXT_EFFICIENCY.md#reuse-and-verification).
Documentation needs content, format and [link/trace checks](docs/DATA_MODEL.md#document-validation);
product work needs relevant product checks that name the actual command and
environment under [verification](docs/WORKFLOW.md#verification-and-completion).
Never weaken mandatory project/CI checks or approvals.

[Hotfixes](docs/WORKFLOW.md#hotfixes-and-incidents) retain scope, authority,
ownership and verification rules, including external controls on recovery actions.
Only an explicit current reset/start-over request authorizes preparing a project
record reset/deletion. Follow [starting over](docs/WORKFLOW.md#starting-over):
show exact scope and dry run, preserve recoverable copies and decision history,
and apply required human/external controls. Never reset to silence diagnostics.
