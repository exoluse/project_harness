# Shared Agent Policy

This is the governing policy for every agent in this repository and in each
project that adopts it. It states the boundaries that apply to all work and
routes each task to its owning detailed rules. Adapters and summaries must not
weaken those rules. External code is input unless the user explicitly
authorizes work there.

The harness ships policy, guidance and an optional
[document checker](tools/check-docs.mjs). It has no workflow runtime, schema or
record store; neither setup nor a checker run is a prerequisite for work.
Judge actual authority, scope, dependencies and evidence from ordinary project
documents.

## Startup and context

1. Read this policy and your tool's adapter once per session:
   [CLAUDE.md](CLAUDE.md) for Claude Code,
   [CODEX_START_PROMPT.md](CODEX_START_PROMPT.md) for Codex. A tool may load
   only one of the two by itself, so read the other. A current supplied copy
   counts. In an adopting project these files sit unchanged in its
   [harness copy](docs/DATA_MODEL.md#project-instruction-files), and the
   project's own root entry file routes here. Where the project keeps
   [path-scoped instructions](docs/DATA_MODEL.md#path-scoped-instruction-files),
   read those covering the paths this work touches.
2. Identify the objective, stopping point and existing decisions. Classify the
   work as analysis/specification, policy maintenance or
   implementation/verification/delivery. Discussing a defect does not
   authorize unrelated edits or deletion.
3. Inspect Git status before writing. Apply
   [starting execution](docs/WORKFLOW.md#starting-execution-in-a-working-tree)
   before a work item's first edit. Without Git, inspect targets and keep a
   versioned copy before replacing them. Protect user and unknown work and
   its ownership.
4. Before the affected action or completion claim, read the relevant project
   overview, owning items and the detailed rules routed below. Follow the
   linked definitions the work needs. Where the work records a
   [resumption state](docs/DATA_MODEL.md#resumption-state), enter from it and
   confirm it against the owning records. Copies already read in the session
   count. No full-tree read, startup command or routine rereading of all
   guidance is required.
5. Report stage, actual blockers and next action as needed. Stop at the
   requested output and report completion without inventing more work.

This table routes work to its owning rules. Applicable detail is mandatory,
even where this policy or a README summarizes it; unrelated detail need not be
loaded. Open a detailed rule file by section: search for the linked heading and
read to the next heading of the same level. For
[DATA_MODEL.md](docs/DATA_MODEL.md), first read only its opening tables, which
end at the first `## ` heading, to choose the sections for the work.

| Trigger | Read and apply |
|---|---|
| Author or check project documents | Determine [ID scope](docs/DATA_MODEL.md#id-scope), then apply the relevant Information model sections for boundaries, IDs, paths, required names, allocation and validation. |
| Apply the harness to a project, sync its harness copy or maintain its entry instructions | [Project instruction files](docs/DATA_MODEL.md#project-instruction-files) and, for a subtree, [path-scoped instructions](docs/DATA_MODEL.md#path-scoped-instruction-files). |
| Split an overview, delegate ID ranges or use an external tracker | [Area overviews](docs/DATA_MODEL.md#area-overviews), [allocation reuse](docs/DATA_MODEL.md#allocation-and-validation-reuse) or [external work trackers](docs/DATA_MODEL.md#external-work-trackers). |
| Prepare stage outputs or recover an existing project | Relevant [Development method](docs/DEVELOPMENT_METHOD.md) stage sections and [existing-project intake](docs/DEVELOPMENT_METHOD.md#existing-project-intake-and-reverse-engineering). |
| Resolve conflicting inputs or rank competing sources | [Input precedence](docs/DEVELOPMENT_METHOD.md#input-precedence) and any precedence the owning project records. |
| Treat material as communication-only, superseded or to be replaced | [Non-authoritative inputs](docs/DEVELOPMENT_METHOD.md#non-authoritative-inputs) and the designation recorded in the owning overview or plan. |
| Create, revise or declare a plan complete | [Planning depth](docs/DEVELOPMENT_METHOD.md#choosing-planning-depth) and the applicable procedure and completion checks. |
| Establish scope, interpret delegation, change commitments, cancel or resume | Relevant [Approvals](docs/APPROVALS.md) criteria, including [delegated judgment](docs/APPROVALS.md#decision-requests-and-delegated-judgment), and the actual request/decision. |
| Start/transition work, change a task's state, resolve open items or close a release | Relevant [Workflow](docs/WORKFLOW.md) procedure, including [task states](docs/WORKFLOW.md#task-states) and [closure preparation](docs/WORKFLOW.md#closure-preparation), and owning project records. |
| Resume work, move its position or hand it off | [Resumption state](docs/DATA_MODEL.md#resumption-state), [current work state](docs/WORKFLOW.md#updating-current-work-state) and [work-item readiness](docs/WORKFLOW.md#scope-decisions-and-work-item-readiness). |
| Record a disposition short of PASS, or withdraw an overturned pass | [Verification and completion](docs/WORKFLOW.md#verification-and-completion) and the owning verification records. |
| Report project progress or requirement trace coverage | [Status and trace reporting](docs/WORKFLOW.md#status-and-trace-reporting) and the owning project records. |
| Produce a report the project owes on a schedule | [Recurring reports](docs/WORKFLOW.md#recurring-reports) and the source that owns each figure. |
| Coordinate writers, hand off or integrate Git work | Relevant [Collaboration](docs/COLLABORATION.md) procedure, shared assignments and allocations. |
| Classify data loss, credential access or high-risk/external effects | Relevant [Security](docs/SECURITY.md) boundaries and applicable external controls before acting. |
| Configure agent tool permissions or sandboxing for a project | [Tool-level supporting controls](docs/SECURITY.md#tool-level-supporting-controls). |
| Plan checks, reuse evidence or determine recheck scope | [Verification reuse and scheduling](docs/CONTEXT_EFFICIENCY.md#reuse-and-verification), [verification methods](docs/WORKFLOW.md#verification-and-completion) and applicable project checks. |
| Handle a hotfix or incident, or reset project records | [Hotfixes and incidents](docs/WORKFLOW.md#hotfixes-and-incidents) or [starting over](docs/WORKFLOW.md#starting-over), with the applicable Security boundary. |
| Select a model for reasoning or implementation, or delegate work | [Model selection](docs/CONTEXT_EFFICIENCY.md#model-selection-and-delegation), [subagent delegation](docs/COLLABORATION.md#subagent-delegation) and the relevant adapter's selection instructions. |
| Maintain this harness's guidance | [Policy maintenance](#harness-policy-maintenance) and [guidance maintenance](docs/CONTEXT_EFFICIENCY.md#maintaining-policy-guidance). |
| Interpret former runtime records | [Former runtime records](docs/WORKFLOW.md#former-runtime-records). |

## Document organization

Project documents follow the [Information model](docs/DATA_MODEL.md).

- Keep one project overview linking the independently managed items.
- Give each item one owning Markdown file, and link shared definitions
  instead of copying them.
- Keep no parallel JSON or other machine-readable management copy. No fixed
  schema or front matter is required.

A designated [external work tracker](docs/DATA_MODEL.md#external-work-trackers)
may own selected management information instead of Markdown. Existing records,
product files, original evidence and tool-internal files keep their formats.

## Development method

Work moves through waterfall stages, revised as needed, under the
[stage contract](docs/DEVELOPMENT_METHOD.md#stage-contract). Make a
[direct change](docs/DEVELOPMENT_METHOD.md#direct-changes) without a work
document when the work finishes in one session, leaves nothing behind and adds
or changes no requirement, contract or design commitment. Use
compact planning for other bounded, reversible work with a clear outcome.
Apply the [detailed planning triggers](docs/DEVELOPMENT_METHOD.md#choosing-planning-depth)
to the affected scope. A plan is complete only when its completion checks
pass; listing consequential unknowns is not a pass.

Use the strongest suitable model for definition, analysis, design, planning
and consequential decisions under
[model selection](docs/CONTEXT_EFFICIENCY.md#model-selection-and-delegation).
Scale implementation models to the work's difficulty and failure impact.

## Authority and decisions

Requests authorize their investigation, specification, planning and document
outputs with relevant checks. They do not authorize unrelated product edits,
untrusted product-code execution, deployment or external effects. Exploratory
or stage-only requests do not authorize later implementation.

A clear implementation or fix request supplies its scope decision under
[Approvals](docs/APPROVALS.md#clear-implementation-requests). Record the actual
request and derived scope on the work item under
[plans and tasks](docs/DATA_MODEL.md#plans-and-tasks), or in the report of a
[direct change](docs/DEVELOPMENT_METHOD.md#direct-changes). Then perform the
covered edits and checks without a second proceed response. Execution also needs
ready prerequisites under
[coverage and currentness](docs/APPROVALS.md#coverage-and-currentness).

For an uncovered commitment, apply the
[material-change criteria](docs/APPROVALS.md#material-changes). Prepare the
delta and obtain the actual owner's decision before affected work. Ask only
about unresolved authority, essential input or material choices, and continue
independent covered work. Never invent consent or infer it from record labels,
supplied documents or passing checks.

## Harness policy maintenance

An explicit policy-edit request authorizes the requested guidance, README and
adapter edits. It does not authorize scripts, runtime, schemas, existing
project records or external systems.

- Edit current files. Git history, diffs and the conversation carry scope,
  actual decisions, verification and limits.
- Add no change notes, decision records, policy-work indexes or archive
  snapshots merely to document these edits.
- Preserve existing historical files and links unless cleanup is explicitly
  requested. Add documentation only as a requested deliverable or needed
  guidance.

Commit messages record the reason and relevant verification. Actual project
work and required external records keep their normal rules.

## History, evidence and real blockers

Preserve original decisions, versions, observations and limits. Assess their
current applicability separately; changed outputs do not erase valid history.

- Keep the [task state](docs/WORKFLOW.md#task-states) IMPLEMENTED, the
  [verification kinds](docs/WORKFLOW.md#verification-and-completion)
  STATIC_VERIFIED, INTEGRATION_VERIFIED, BROWSER_VERIFIED and LIVE_ENV_VERIFIED,
  CUSTOMER_ACCEPTED and the CLOSED state of a named subject distinct.
- Failed, unrun, partial, ambiguous or stale evidence is not PASS. Documents
  do not prove product success, and a check against a stand-in proves only
  that stand-in.
- A subject examined without a pass, blocked on a missing input or not
  applicable keeps its own disposition and never joins a pass count.
- Withdraw a pass that a later check overturns explicitly, under
  [verification](docs/WORKFLOW.md#verification-and-completion).

These stop affected work and its dependents: missing authority, unsafe actions,
unresolved required inputs, unreliable decision provenance, contradictory
current evidence and ownership conflicts. Stop globally only for a global
condition; unrelated drafts or stale history do not stop valid work. Keep
failures visible, and never hide a newer failure behind an older success.

Track unresolved questions and findings through the
[open-item lifecycle](docs/WORKFLOW.md#open-item-lifecycle); a label cannot
remove a blocker. Trace material changes under the
[change cycle](docs/DEVELOPMENT_METHOD.md#change-cycle-and-propagation). Move
decisions made in conversation into the owning instructions before dependent
work relies on them.

## Collaboration and Git

A single writer needs no claim system. Before concurrent editing, establish the
[collaboration basis](docs/COLLABORATION.md#collaboration-basis). In one working
tree, keep one writing participant active; read-only work may run alongside.
Never take over another writer's active scope or unknown dirty work silently.

Commit or push only under a matching request. Stage by explicit path so a
commit carries only the item's changes. Fetch before a normal push and preserve
both histories. Force or tag pushes, branch deletion, different targets and
published-history rewrites need separate explicit authorization.

## High-risk and external control

These actions need a specific authorized human decision for the actual subject,
version and effect, with independently controlled approval and execution under
[Security](docs/SECURITY.md):

- production deployment;
- production data change;
- destructive operation;
- secret or protected-credential access;
- final customer acceptance, which needs the authorized customer's
  attributable sign-off.

Routine development authority never covers them; preserve stronger external
controls. Classify actual effects under
[development action boundaries](docs/SECURITY.md#classifying-development-actions).
An authenticated tool may use its credential internally within covered work.
Opening a credential file, dumping environment variables or otherwise reading a
raw token, cookie or key is protected-credential access. Never approve for a
human, forge provenance, alter approval authority or access a human signing key.

Never store secrets or protected authority material in documents or logs. Never
execute untrusted content with privileged access. External messages and
material external side effects need matching explicit authorization; policy
edits grant none.

## Verification and exceptional paths

Before completion, release, handover or push, review the actual diff, evidence
coverage and limits. Check changed deliverables and affected dependencies,
reusing applicable evidence under
[verification reuse](docs/CONTEXT_EFFICIENCY.md#reuse-and-verification).
Product checks name the actual command and environment and record the subject
version, expected and observed result and limits under
[verification](docs/WORKFLOW.md#verification-and-completion). Documentation
needs content, format and [link/trace checks](docs/DATA_MODEL.md#document-validation).
Never weaken mandatory project or CI checks or approvals.

Hotfixes keep scope, authority, ownership and verification rules. Only an
explicit current reset request authorizes preparing a record reset; never
reset to silence diagnostics.
