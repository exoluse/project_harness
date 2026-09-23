# Project Information Model

This is the required detailed standard for project document organization,
identity, paths, exceptions and validation, designated by
[AGENTS.md](../AGENTS.md#document-organization). Keep information-model rules
here; the linked ID dictionary provides starter formats and selection guidance.
Other guidance links these definitions and may show brief summaries or examples.
The [management format policy](../AGENTS.md#management-document-format)
governs Markdown, existing records and tool-required formats.

This file is long; do not load it whole. Pick the sections for the work from
the two tables below and read only those, locating each by its heading text
(for example, search for `## Item IDs` and read to the next `## ` heading).
Follow a link into another section only when the rule being applied depends on
it. Every section that applies to the work remains mandatory; a section that
does not apply is not required reading.

| Work | Sections to read |
|---|---|
| Create, name or rename a project document | [ID scope](#id-scope), [Item IDs](#item-ids), [Document paths](#document-paths), the single-writer paragraphs of [Allocation reuse](#allocation-and-validation-reuse), [Document validation](#document-validation) |
| Decide whether something is a separate item | [Item boundaries](#independent-items-and-supporting-detail) |
| Document a small correction | [Minimum documentation for a small change](#minimum-documentation-for-a-small-change) |
| Write or update an overview, plan or task | [Document organization](#document-organization), [Plans and tasks](#plans-and-tasks), [Summary ownership and updates](#summary-ownership-and-updates) |
| Record or follow up an unresolved question | [Open items](#open-items) |
| Resume work that spans sessions, or record where it stands | [Resumption state](#resumption-state) |
| Several teams, delegated ID ranges or an external tracker | [Area overviews](#area-overviews), the range record in [Allocation reuse](#allocation-and-validation-reuse), [External work trackers](#external-work-trackers) |
| Check documents before a completion claim | [Document validation](#document-validation), then the sections its rows name for the changed content |

| Need | Governing section |
|---|---|
| Harness guidance or project deliverable | [ID scope](#id-scope) |
| Overview and relationships | [Document organization](#document-organization) |
| Progress summaries and update scope | [Summary ownership and updates](#summary-ownership-and-updates) |
| Several teams, streams or subsystems | [Area overviews](#area-overviews) |
| Plan/task responsibilities | [Plans and tasks](#plans-and-tasks) |
| Current position of long-running work | [Resumption state](#resumption-state) |
| Identity, types and numbering | [Item IDs](#item-ids) |
| Project ID formats and optional classification codes | [Document ID dictionary](ID_DICTIONARY.md) |
| Canonical filename and folder mapping | [Document paths](#document-paths) |
| Separate item or supporting detail | [Item boundaries](#independent-items-and-supporting-detail) |
| Consumer-required name/location | [Required-name exceptions](#required-name-exceptions) |
| Instructions scoped to a subtree | [Path-scoped instruction files](#path-scoped-instruction-files) |
| Completion checks | [Document validation](#document-validation) |
| Reuse of checked allocations | [Allocation reuse](#allocation-and-validation-reuse) |
| Work status kept in an external tool | [External work trackers](#external-work-trackers) |

Preserve existing non-Markdown records and reference them without automatic
conversion or deletion. Product files such as `package.json`, original evidence
such as logs or test reports, and tool-internal files retain their required
formats. Summarize verification in Markdown and link to those original artifacts. Contractual delivery formats and external controls remain binding;
resolve actual conflicts before the affected delivery.

## ID scope

The harness's own policy, framework overview, exception guidance and agent
instructions do not receive document or rule IDs. This applies to new guidance
as well as existing files, including `AGENTS.md`, the harness `README.md` and
its policy documentation. Use meaningful or consumer-required Markdown names;
no ID filename, classification-folder mapping or exception-ID registry is needed
for these guidance files. Maintain them through Git under
[policy maintenance](../AGENTS.md#harness-policy-maintenance).

Actual project deliverables remain subject to the ID rules: project overviews,
requirements, designs, plans, tasks, decisions, research and verification, among
others. Classify by purpose, not filename or folder: a framework overview
explains how to use the harness; a project overview tracks a project's outcomes
and work. A project document does not become exempt by being called a guide
or exception. Examples in harness guidance remain illustrative, not allocations.
Preserve existing historical IDs; this distinction does not authorize stripping
them from records. Explicit contract or external identity requirements remain
binding.

## Suggested information

| Information | Minimum useful content |
|---|---|
| Project note | Objective, current stage, baseline, decisions, progress, blockers and next action. |
| Project conventions | Build, test and static-check commands, verification environments, integration/branch model and quality criteria that are actually decided or observed, with their source/version. Record each when it is decided or found at intake, not as a placeholder; verification records reference them. |
| Source/intake | Origin, version, analysis scope, ownership and reliability/limitations. |
| Requirements | Intended outcomes, constraints, acceptance criteria and material source trace. |
| Design | Components, interfaces/data, alternatives, requirement coverage and open risks. |
| Plan | Goal, scope, source-to-work/check coverage, linked implementation detail, dependencies, ordered task links, overall completion criteria, open-item dispositions, [resumption state](#resumption-state) for work spanning sessions and actual decision reference. |
| Task/work item | Concrete output, owner, affected paths/logical resources, declared inputs and shared paths, current execution mode, plan/input links, prerequisites, ordered actions, applicable implementation detail, declared stop conditions, status and concrete completion checks with their actual commands. |
| Decision | Concrete scope/version, actual owner request or response/source, bounds and conditions. |
| Change trace | Request, before/after, impact, affected work, decision and verification. |
| Open item | Question/finding and evidence; continued follow-up adds state, responsibility, impact, next action and resolution history under [Open items](#open-items). |
| Verification | Subject/version, method/environment, expected/observed result, artifacts and limits. |
| Release/handoff | Contributions, versions, decisions, current evidence, unfinished obligations and next owner/action. |

Keep supporting conditions and implementation steps in their owning files.
Requirements and their design, plan, task and verification definitions use
separate files under [document organization](#document-organization), with the
bounded [small-change exception](#minimum-documentation-for-a-small-change).
A plan may organize nested task links or reference several plans; no
single-active-plan field is required.

## Document organization

Use a project overview for shared context and navigation, with documents for
independently scoped items stored in suitable classification folders. The agent
chooses folder names, nesting and the document root for the project's content,
workflow and existing conventions. Feature/work units remain logical groups
in the overview and relationships between items regardless of physical layout.
A project with several such units must not default to a single accumulating
file for each document type.
Each requirement owns its REQ file and links the separate owning design, plan,
task and verification files needed at the requested stage. Shared definitions
or work keep one owning file linked by all covered requirements. Create files
when their stage/output is needed, not as placeholders for future stages.

The [small-change exception](#minimum-documentation-for-a-small-change) permits
otherwise missing definitions for one correction to share a work document.
For that exception, references to owning requirement, design, plan and
verification documents mean the corresponding sections or linked existing
owners. It does not combine independently managed items or relocate existing
definitions.

The overview holds the objective, shared project context, links to shared
requirements and architecture, baseline, current summary and an index of units.
It also states the document/item-ID convention, including agent-selected
extensions and any allocation ownership, and records the
[project conventions](#suggested-information) for build, test and check
commands, verification environments and integration once they exist. A new
project adds them when its design or plan decides them; intake records those
observed in an existing project. An undecided convention is stated as such.
Each index entry links to the unit's documents and states its scope, stage/status
and material dependencies. Keep detailed decisions and evidence in their owning
documents and link to them instead of maintaining duplicate accounts.

Use requirements as the primary basis for separating product scope under the
[item-boundary rules](#independent-items-and-supporting-detail). Connect design,
planned work and verification to the requirements they cover. Keep supporting
detail within its owning document role and link the other roles' definitions.
Length alone does not create a new item; use sections and navigation
when accumulated supporting detail obscures scope, decisions or evidence.
Record the chosen boundaries and rationale briefly in the overview or work note.

The following example applies [document paths](#document-paths). Folder names
and nesting are illustrative; the IDs are not allocations in this repository.
Create only documents needed for the requested stage:

```text
project-docs/
  overview/
    DOC-001.md                  # Shared context and feature/work index
  requirements/
    REQ-001.md                  # Sign-in requirement
    REQ-002.md                  # Search requirement
  designs/
    DES-001.md                  # Shared architecture
    DES-002.md                  # Sign-in design
  features/
    FEATURE-001.md              # Links sign-in requirement and related work
  contracts/
    API-001.md                  # Sign-in API contract
  screens/
    SCR-PC-001.md               # Desktop sign-in screen specification
  plans/
    PLAN-001.md                 # Implementation order and task links
  tasks/
    TASK-API-001.md
    TASK-PC-001.md
  verifications/
    VER-001.md
  decisions/
    DEC-001.md
  changes/
    CHG-001.md                  # Change trace when separately required
  handoffs/
    HANDOFF-001.md
```

Every unit links back to its overview and applicable shared specifications.
Connect requirements and acceptance criteria to the covering design, planned
work and actual verification using item IDs with file/anchor links, optionally
in a compact trace table.
Links may be many-to-many: several plans can implement one requirement, and a
shared design can support several features. State cross-unit dependencies and
the relevant input versions. When verification has not run, record that state
in the plan instead of creating evidence or implying success.

When adding a new unit, add its index entry and relevant dependency links.
When scope changes, update the owning detail, affected links and overview
summary while preserving prior decisions and evidence. New work uses these
boundaries even when earlier work lives in a large file; reference that baseline.
Do not automatically split, move or rewrite existing records merely to adopt
the layout. Any authorized reorganization must preserve reviewed versions and
repair links. A requested stage still ends at its own outputs.

### Summary ownership and updates

Detailed facts have one owner: requirements own expected outcomes and acceptance
criteria; designs/contracts own behavior and structure; plans own order,
dependencies and overall completion criteria; tasks own execution and task
status; verification documents own actual check results. Designated tracker
ownership follows [external work trackers](#external-work-trackers).

Plans and overviews summarize their own scope's progress, major stage, blockers
and material dependencies, linking the owning facts and evidence. Select summary
detail needed for those judgments; do not duplicate task-by-task status or test
logs at every level. A task's completion does not establish requirement-level
verification, customer acceptance or overall completion.

Use the owning [impact assessment](DEVELOPMENT_METHOD.md#change-cycle-and-propagation)
to update summaries when their stated scope, stage, blockers, dependencies,
commitments or evidence applicability changes, or a referenced path changes.
An edit to a child does not alone require edits at every parent level. If a
summary includes exact counts or individual statuses, keep those accurate too;
an unchanged high-level label cannot justify retaining a false detailed claim.

Route shared-summary updates through their owner under
[collaboration](COLLABORATION.md#coordination-waits). Pending reflection in a
shared summary must not hide a known blocker or supply readiness. Check current
owning records before dependent work starts/resumes and before relying on a
summary for a decision, handoff or completion claim; reconcile relevant summaries
before that use. Stop propagation at levels whose facts and judgments remain
valid. Preserve historical snapshots with their dates/versions rather than
maintaining them as parallel current status.

### Area overviews

Split navigation into area overviews when one project overview no longer works
as a readable index or shared edit point: for example, several teams or work
streams edit it concurrently, its unit index obscures current scope, or
subsystems, services or repositories progress independently. Size alone is not
the criterion. Record the split and its reason in the project overview.

The project overview remains the root. An area overview has its own document
ID, links back to the root and follows the same organization rules for its area.

| Content | Owning overview |
|---|---|
| Objective, shared constraints and specifications (or links), document root and shared folder mapping, area index, cross-area dependencies, allocation delegations | Project (root) overview |
| Area unit index, area progress summary, area-specific folder extensions, consumption of delegated ID ranges | Area overview |
| Detailed definitions, decisions and evidence | Owning item documents, as without areas |

Each area index entry links the area overview and states its scope, accountable
owner, stage/status summary and material dependencies. Area folder extensions
must not redefine a shared mapping or prefix. A requirement or design used by
several areas has one owning definition, kept at the root or in a designated
owning area and linked from the others. Summaries flow upward from owning items
to the area overview and from area overviews to the root; no level keeps a
second detailed account. An area may nest further only when it meets the same
split criterion.

Root overview edits follow its assigned owner under the
[collaboration basis](COLLABORATION.md#collaboration-basis); area writers route
root changes through that owner or an agreed transfer. New areas can start with
their own overview. Moving existing index entries or allocations out of an
established overview is a reorganization: it needs a matching request,
preserves IDs, history and reviewed versions, and repairs links.

## Plans and tasks

A plan organizes an outcome across work items. It defines the goal, included
and excluded scope, input requirements/design, dependencies, feasible task order
and overall completion criteria. A project can use `PLAN` for general, backend
or screen implementation plans; plans link to the owning task files. API
contracts and screen specifications are inputs to plans, not automatically
plans themselves. Preserve established project meanings when they differ.

A task is a concrete output that the actual work assigns and completes as a
separate unit. Implementation steps serving that output may remain in its file.
Its owning task file, named under the project's ID convention, records the
expected output, accountable writer, affected paths and logical resources,
parent plan/input links, prerequisites,
current status, ordered actions and concrete completion checks. Supply or link
the applicable implementation details and verification scenarios required by
the selected [planning depth](DEVELOPMENT_METHOD.md#choosing-planning-depth).
Before assignment is known, state that
it is unassigned; resolve ownership before concurrent execution. These are
content requirements, not mandatory headings or front matter.

Use the task document as the entry for starting or resuming that work. Its
opening description must make the current basis easy to find: the scoped
outcome, relevant requirement/design sections, governing decision and input
versions, completion checks, and next action or blocker. Link existing owners
and sections instead of copying their content or creating another index.
The selected plan or stage-output document supplies this entry when no task
is needed yet; do not create a placeholder task. Resolve conflicting inputs
under the [change cycle](DEVELOPMENT_METHOD.md#change-cycle-and-propagation)
before relying on them, and follow links to affected shared constraints.

During execution, a task's recorded paths and logical resources also bound its
writes. Edit what the task declares, and declare a newly required path, shared
file or generated artifact in the task before editing it. Name excluded targets
where an adjacent path would otherwise look in scope. An edit outside the
declared scope stays out of scope even when it appears necessary: extend the
declaration first under the
[change cycle](DEVELOPMENT_METHOD.md#change-cycle-and-propagation), or stop when
that extension needs a decision the work does not have. Inputs a task reads are
not writable by virtue of being read; keep the sources the work consumes
distinct from the targets it may change.

Declare the inputs the item reads as deliberately as the targets it writes.
Name the governing instructions, requirement/design sections, contracts, source
files and prior outputs the result actually depends on, with the versions read.
A declared input set tells a resuming session which basis to re-establish
instead of rediscovering it, and makes a missing, unreadable or changed input
recognizable as a stop condition rather than a surprise mid-execution. Reading
something outside that set is not a violation; add it to the declaration when it
turns out to carry the result, and reassess the item when it contradicts an
input already declared.

Where a declared path or resource is also owned or consumed by another item,
record it as shared and state how this item may touch it: normally consume-only,
with any unavoidable registration or integration edit named as such. A defect
found in a shared component belongs to the item that owns it. Return it there
under the [open-item lifecycle](WORKFLOW.md#open-item-lifecycle) instead of
repairing it inside the consuming item, whose declared scope, review and
evidence do not cover that component. Where two items must both write a shared
path, order them or assign one writer under the
[collaboration basis](COLLABORATION.md#collaboration-basis) before either
starts.

Record the item's completion checks as the actual commands or check targets and
the environment they run in, referencing the
[project conventions](#suggested-information) where they exist. A resuming
writer or a separate auditor then runs the same check instead of inventing an
equivalent one, and a check that cannot be named concretely is not yet a
completion criterion. Naming a check does not run it; see
[verification and completion](WORKFLOW.md#verification-and-completion).

Record the item's current execution mode alongside that scope: what the work
may presently produce, such as analysis and specification only, review output
only, or implementation and its checks. The mode states the consequence of the
actual decision recorded under
[Approvals](APPROVALS.md#preparing-and-recording-one-decision) and names that
decision; it is not a permission the item grants itself, and widening it is a
separate decision. A session resuming the item reads the mode there instead of
re-deriving authority from an earlier conversation. Where the item and the
actual decision disagree, the decision governs and the item is corrected.

Record the conditions that stop the item before they occur: the inputs,
contracts, fixtures, authority and scope boundaries whose absence or change
makes continuing unsafe or meaningless. Declared stop conditions make a stop
recognizable while the work runs rather than only in hindsight. They do not
replace the [real blockers](../AGENTS.md#history-evidence-and-real-blockers),
which stop affected work whether or not the item listed them, and an unlisted
condition is not permission to continue past it.

Plans and tasks reference the requirements they cover. One requirement can
need several tasks, and one task can serve several requirements. Keep plan and
task definitions in their respective files, except for the
[small-change exception](#minimum-documentation-for-a-small-change), and use
actual output, assignment and completion boundaries to split further. Reuse
shared files across requirements; do not create duplicate definitions or
placeholders for unrequested stages.
Use the [boundary criteria](#independent-items-and-supporting-detail) for small
changes, supporting detail and work before requirements are established.

Keep task definitions and execution status in their owning files, linking actual
check results from verification documents. Plans contain
links, ordering and useful progress summaries; update those summaries from the
tasks. A task shared by several plans retains one ID, owning file and writer.
Apply [summary ownership and updates](#summary-ownership-and-updates) rather
than copying detailed task states into each parent. Completion of the planned
outcome is assessed against its scope and criteria using task outcomes and
applicable combined verification. Planning itself ends
when the plan and task definitions satisfy the
completion checks for the selected [planning depth](DEVELOPMENT_METHOD.md#choosing-planning-depth);
it does not require those tasks to have executed. Planning-only work records
intended checks without claiming execution.

A parent plan may organize child plans, such as area or work-stream plans. The
parent owns the cross-plan goal, scope split between children, integration work,
ordering between children and overall completion criteria; each child owns its
own scope, tasks and checks. The parent's planning completion checks cover that
cross-plan content and reuse the children's passed planning checks for their
stated scope and versions, rechecking a child whose inputs changed. Completing
every child does not complete the parent outcome while integration work or
parent criteria remain.

Keep the source inventory and coverage links in the existing plan/work document,
or reference their owning sections when already maintained. Supporting source
entries, checklist dispositions and verification scenarios do not create new
item identities solely to fill a table. Requirement details stay with their
requirement; task instructions stay with their task. A plan's summary must lead
to those concrete definitions rather than substitute for them.

Directory ownership and task ownership complement each other. Record the chosen
document root and type-to-folder mapping in the overview, and the actual edit
scope in tasks. Two tasks may work in one directory if their file/resource
boundaries are clear. A folder name or document ID alone does not assign work.
Use the [collaboration basis](COLLABORATION.md#collaboration-basis) to make these
boundaries and ID allocations visible to concurrent writers.

### Resumption state

Work that spans sessions is re-entered repeatedly, often by a different session
or writer. Keep one record stating where it currently stands, so re-entry starts
from the recorded position instead of a reconstruction of an earlier
conversation. Name there:

- the item or step in progress, and the one that comes next;
- the last completed checkpoint and the evidence that established it;
- the current blocker, if any, and the point work resumes from once it clears;
- the conditions still standing between the work and its release, acceptance or
  closure;
- the short ordered set of documents a session reads first to re-establish the
  basis.

The owning plan holds this for a single plan; a program spanning several plans
or [areas](#area-overviews) keeps one such record in the overview that owns its
navigation. It points at owning records rather than copying them, and where it
disagrees with one, the owning record governs under
[summary ownership](#summary-ownership-and-updates) and the pointer is corrected.

State the present position and let history live where it belongs. A pointer that
accumulates successive updates stops answering the question it exists for: move
superseded positions into the decision, verification or change records that own
them, and keep the entry list short enough to be read on every re-entry.

A pointer records position, not permission. It establishes no execution mode,
decision or pass; those stay with the actual decision under
[Approvals](APPROVALS.md#preparing-and-recording-one-decision) and the evidence
under [verification](WORKFLOW.md#verification-and-completion). Naming the next
item does not authorize starting it.

## Item IDs

Apply identity rules to every Markdown deliverable within the
[ID scope](#id-scope), whatever its subject: specifications, research,
guides, meeting notes, reviews, reports, handoffs or kinds not listed here.
Assign the document an ID appropriate to its purpose. A document representing
one primary item uses that item's ID; a collection can use a document ID such
as `DOC-001`. Choose the identity before creating the file and use it in
the index; [document paths](#document-paths) defines filename/body placement.
An overview itself also has an identity. A document ID is not a substitute for
the identities of its independently tracked contents.

Use the [item-boundary rules](#independent-items-and-supporting-detail) to
identify independently tracked contents. Apply IDs to new traceable items
added to existing Markdown as well. Requirements, acceptance criteria, designs,
plans, tasks, decisions, findings, changes, risks, issues and verification are
examples, not an exhaustive list.

Use the project's recorded ID format table. There is no mandatory token
length, serial width, universal AREA segment or fixed number of segments.
Prefer simple semantic prefixes and add a classification or parent segment
only when the project needs it. The [ID dictionary](ID_DICTIONARY.md) offers
starter formats such as `REQ-001`, `SCR-PC-001` and `TASK-API-001`; its rows are
examples, not a closed vocabulary or allocated IDs.

The project overview owns the format table, or links its one owning dictionary
when separate management is useful. Record each kind's meaning, exact format,
allowed classification values, serial width/start, allocation scope and any
parent-ID rule. A small project can use a few rows in the overview. Create or
extend a dictionary when needed; no separate file or full catalog is required.
A separately managed project dictionary follows the ordinary document-ID and
path rules. Harness guidance remains outside the ID scope.

Agents reuse established formats and add missing kinds or classifications
within the authorized work without asking for each token. Register additions
before allocation, preserve existing meanings, and avoid synonyms or overlapping
formats that make an ID ambiguous. Different kinds can use different axes:
screen platform and task work area need not share a code list. Technology,
audience and feature metadata can stay in the body instead of the ID.

Interpret an ID using its whole registered format. In the starter dictionary,
`API-001` identifies an API contract; its method/path, version and coverage are
specified in the body. `PLAN-001` can plan its implementation, and
`TASK-API-003` can implement it. Task numbers do not derive from plan numbers:
record actual plan, requirement, design and contract links. Shared tasks may
link to several plans. A `FEATURE` groups related items through links; it does
not duplicate the requirements it groups or require one item of every type.

Allocate flat and classified serials project-wide per complete prefix, such
as `REQ` or `TASK-API`. Two feature folders or parent plans cannot each restart
`TASK-API-001`. Hierarchical formats allocate the child serial per child kind
and identified parent, as recorded in the format table. For example, under
`CT-API-NNN-NN`, `CT-API-012-01` is a contract test of `API-012`; a backend test
`BT-API-012-01` has a separate counter. Complete IDs are unique project-wide,
regardless of folder or checkout, subject only to the temporary collisions of
new provisional IDs under [branch allocation](#branch-allocation-and-collision-repair).

Before allocating a child, verify its parent's owning definition and format
mapping, and link the parent in the body. Matching numbers imply no other
relationship. A parent segment records identity, not a mutable dependency:
if current coverage changes, preserve the ID and record new links and history;
an actual replacement/split follows the identity rules below. Parent detail
that needs no independent management can remain a section without a new ID.

Search existing definitions, retained/retired IDs and reservations before
choosing the next unused serial, reusing a verified allocation basis. Concurrent
writers use non-overlapping ranges unless the recorded arrangement uses the
tracker or isolated-branch exceptions under [allocation reuse](#allocation-and-validation-reuse).
If the available width is exhausted, record a compatible extension for new IDs
and check consumers and collisions before allocation; do not wrap counters,
reuse IDs or automatically pad/rename older records.

Put the ID visibly in the owning heading or table row. Provide a stable anchor,
for example an ID-only heading `### REQ-001` with a descriptive title in the
body, or an explicit anchor for an identified table row. References use the ID
as link text and resolve to that item's anchor, even within one file.

Keep IDs unchanged when content is revised, renamed, reordered or moved; update
links after moves. Only new provisional branch IDs may be renumbered for an
allocation collision under [branch allocation](#branch-allocation-and-collision-repair).
Never reuse deleted/retired IDs. For a split or merge, record
the old item's disposition and links to the new items without overwriting its
decision or evidence history. Identity alone does not identify a reviewed
version, prove approval or establish a passed check.

Existing IDs and historical records remain valid; use links to older material
without bulk retroactive relabeling. This includes five-digit IDs and existing
`TYPE-AREA` conventions. Earlier harness examples used `API` for backend plans
and `SCR` for screen plans; retain those meanings wherever already established.
Do not treat a shorter serial as permission to reuse the same prefix for a
different purpose in that project. Use its existing convention or register a
distinct unambiguous prefix. A requested migration has its own scope.
Externally required document formats remain binding; resolve a real conflict
rather than silently omitting identity requirements.

## Document paths

Except for [required-name files](#required-name-exceptions), every new project
Markdown document uses `<document-root>/<classification-path>/<ID>.md` or
`<document-root>/<classification-path>/<ID>-<slug>.md`. The ID portion exactly
matches the owning document ID, including the tokens, separators and number
widths in the project's format table. The optional slug is a short description
for readability, not part of identity, allocation or parent relationships.

When present, the slug consists of exactly two lowercase ASCII words joined
by one hyphen (`kebab-case`), matching `[a-z]+-[a-z]+`. Use a hyphen between
the complete ID and the slug, for example `API-024-service-context.md`.
Descriptions such as `service-context` or `admin-login` are optional; a single
word, additional words, digits, spaces or underscores within the slug are invalid.
Identify the complete ID from its registered format, including any parent/child
segments, rather than treating the last hyphen or number as its boundary.
Verify that the ID and slug have an unambiguous interpretation under the
project's formats before creating the file.

Show the ID without the slug near the top of the body and in stable ID anchors.
Keep the full title and context in the body and overview. Reference links use
the ID as their label and the actual owning filename/anchor as their target.
An ID in the body or directory alone does not satisfy the filename rule.
For example, `overview/DOC-001.md` and `overview/DOC-001-project-overview.md` are
alternative names for the same identity; `overview.md` needs a required-name
exception. Keep one current owning file per ID across all folders: a different
slug, or adding/removing a slug, does not create another item. Do not keep both
filename forms as duplicate owning files.

Preserve the ID when changing a slug. Do not automatically rename files when
titles change. When a filename changes within authorized work, update the
overview/index path and all affected links, and retain version history.
The rule covers all document kinds, including overviews, shared specifications,
research, reports, changes and handoffs.

The agent chooses and records the root and classification-to-folder mapping
in the project overview, reusing project conventions. Examples include `REQ`
to `requirements`, `API` to `contracts`, `SCR` to `screens`, `PLAN` to `plans`
and `TASK` formats to `tasks`. These are not reserved names: `specs/requirements`,
`plans/backend` or `work-items` are also possible. Select and record suitable
folders for new kinds or changed context without asking the user to classify
each one. Reuse mappings consistently within their stated scope.

Folder changes preserve IDs and repair overview/item links; they do not
authorize historical-record migration. Do not create empty type folders or
placeholder files before they are needed. Group feature relationships through
the overview and owning documents, independently of the physical layout.
For example, `plans/PLAN-001.md` links to a task at `tasks/TASK-API-001.md`
and an input contract at `contracts/API-001.md`.

## Allocation and validation reuse

Use an `ID allocation` section (or its local-language equivalent) in the actual
project overview as the default shared allocation record. If the team already
uses another shared Markdown location, link its exact file/section from the
overview and maintain the allocation there only. Folder names stay contextual;
writers must be able to discover one authoritative location for each scope.

Establish an initial basis by checking project-wide definitions, retained and
retired IDs, allocation history and outstanding reservations. Record the checked
version/scope, result and any limits once; reuse it with subsequent allocation
changes. When creating the first overview, include its own ID in this check and
record the basis there. No pre-existing registry is necessary.

For a single writer without delegated ranges or outstanding reservations, the
allocation section needs only each allocation scope and its next serial, plus
a link to that shared checked basis. Advance the serial when allocating; never
move it backward or fill earlier gaps. The initial serial must exceed every
used, retired or previously allocated serial in that scope. Existing owning
document links identify issued items; no per-allocation owner, range reservation
or gap-disposition table is required. For example, `TASK-API: next 004` means
`001` through `003` cannot be newly allocated, whether used, retired or skipped.
Preserve their actual history without inventing a disposition for unused gaps.
If prior allocations are uncertain, reconcile them before choosing the serial.

Before introducing concurrent writers, record the allocation arrangement once
in the allocation section. Use the shared range record below unless one of the
two exceptions applies. Returning to a single writer requires reconciling prior
ranges, reservations and pending branch allocations first; the simple counter
cannot silently supersede them.

Two arrangements need no range or owner record. A registered format may take
its serial from a designated [external work tracker](#external-work-trackers)
key, such as `TASK-{area}-{issue}`; the tracker then allocates, and the
overview records the format and tracker. Writers on separate branches may
instead use a per-scope next serial with provisional IDs and collision repair
under [branch allocation](#branch-allocation-and-collision-repair). These exceptions
replace the range table, not the checked allocation basis or history rules.

With [area overviews](#area-overviews), the root allocation section delegates
non-overlapping serial ranges per allocation scope to areas and records each
delegation's owner and verified basis. The area overview's allocation section
records consumption within its delegated ranges; the root does not repeat it.
Complete IDs stay unique project-wide, and areas do not introduce their own prefixes
for an existing type. When an area exhausts a range, obtain a new delegation
from the root allocation owner before allocating further.

For allocation using reserved or delegated ranges, use a compact Markdown table
with the following minimum information, reusing shared baseline notes for rows
checked together:

| Field | Required content |
|---|---|
| Allocation scope | Registered complete prefix, such as `TASK-API`; for hierarchical formats, child kind and parent, such as `CT` for `API-012`. |
| Verified basis | Commit/version and scope checked, including definitions, retained/retired IDs and outstanding reservations; actual check result and any limits. A version alone is not proof of verification. |
| Allocated range | Inclusive serial bounds assigned within that allocation scope, using its recorded width. |
| Owner | Writer responsible for consuming the range; identify any agreed transfer. |
| Disposition | Used serials or owning-document links, retired serials, and remaining reserved/available numbers. Record gaps explicitly rather than assuming everything below the largest number was used. |

These are required contents, not fixed column spellings or a new machine schema.
For example, a hypothetical `TASK-API` range `001` through `020` owned by
writer A may state: used `001` and `003`, retired `002`, remaining
`004` through `020` reserved for A. Its row must also link the actual checked
basis. This example does not allocate IDs in this harness repository.

Harness guidance outside the [ID scope](#id-scope) needs no
allocation table simply to maintain policy. Do not create a second registry or
a new document per allocation.

Within an assigned range, consume unused serials and record their disposition.
Reuse the verified basis plus subsequent allocation changes instead of reading
every document for each new ID. Folder, feature or checkout boundaries do not
reset the sequence. Exhausted ranges need a new non-overlapping allocation.
Check shared allocation changes before extending or transferring a range;
uncertain, conflicting or stale reservations must be reconciled first. A local
highest-number search alone does not account for other writers or retired IDs.

For subsequent document validation, compare newly defined IDs with that basis
and other new definitions, and check changed files plus affected references.
For delegated ranges, check new definitions against the area's range and check
root delegations for overlap whenever they change.
Broaden the scan when baseline coverage is missing or unreliable, allocation
conflicts appear, or changes to conventions/validation rules affect prior
results. Preserve project-wide uniqueness and never reuse retired IDs. This
changes how evidence is obtained, not the identity or filename requirements.
See [verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification).

### Branch allocation and collision repair

This exception applies only when the recorded arrangement uses isolated
branches and reviewed integration. New IDs allocated on those branches are
provisional until their first integration into the designated integration
branch. Existing IDs and IDs issued by a tracker or shared reservation remain
fixed; they do not become provisional when copied to a branch.

Fetch and inspect the integration branch's allocation basis before allocating.
Choose an unused serial beyond its recorded allocations and the branch's own
allocations, and advance the local counter. Fetch cannot reveal all concurrent
unmerged work, so a provisional ID may collide with one on another branch.
Identify provisional items in decisions, evidence and handoffs by their source
commit/version and owning path as well as their ID; a bare ID is insufficient.

Before integration, compare new IDs against the current integration branch,
retained/retired IDs and reservations. The first integrated item keeps its ID;
renumber only the later item's provisional ID if it collides. Repair its
filename, body, anchors, current references and any provisional child IDs derived
from it, update the counter and check the resulting links and uniqueness.
Resolve collisions before integration; integration fixes the resulting IDs.

Record the old ID with its source version/path and the new ID in the owning
plan/work note. Preserve original decisions, signed payloads and verification
artifacts with their original references; link them through that mapping and
assess their applicability rather than rewriting them or inventing a new PASS.
Repair known external references through their authorized owner; unresolved
ambiguous references block affected integration. Use forward edits, preserving
published history. This exception does not permit renumbering established items
or reusing retired IDs.

## Independent items and supporting detail

Requirements are the primary basis for separating product scope. Establish
what must be satisfied, then organize the design, work and verification needed
to satisfy it. Each separately identified requirement owns one REQ ID/file;
other independently managed items retain their appropriate types and owning
files under [document paths](#document-paths).

### Requirement boundaries

A requirement states an intended behavior, outcome or constraint. Assign a
separate REQ when it expresses a separately meaningful commitment whose scope
and fulfillment need their own assessment, such as search and exporting search
results. Requirements may depend on one another; technical independence is
not required. A shared security or performance constraint can also be a
requirement when it has its own scope and fulfillment criteria.

Keep the conditions, rationale, examples, parent-specific acceptance criteria
and check methods that explain one requirement with that requirement. A
separately executable assertion or test does not alone make a new requirement.
Stages, algorithms, code files and test commands are not requirement boundaries.
If an acceptance criterion actually needs its own acceptance disposition, use
an AC item linked to its requirement rather than relabeling it as a new REQ.

Before assigning a new REQ, check existing requirements. A correction that
restores an already specified behavior references the existing REQ; adding a
test for it does not create another REQ. Revise the same requirement under its
existing ID when its identity remains the same, preserving prior versions and
decisions. A new commitment or an actual split/merge follows the existing
[identity and history rules](#item-ids). Identity does not authorize a material
change to the requirement or acceptance criteria.

### Related work and supporting detail

Designs, plans, tasks, changes and verification reference the requirements
they cover. These relationships may be many-to-many. A shared design or check
has one owning definition linked to all relevant REQs. Preserve separate
requirement, design, plan, task and verification files under
[document organization](#document-organization), reusing shared definitions
without creating a copy for every requirement.

Give related work a separate ID/file when the actual work needs a separately
assigned or delivered output, its own completion/decision status, or a shared
definition maintained across requirements. Keep implementation steps and
supporting explanations in their owning item. Merely being able to assign a
step to someone else, run a test separately or link a paragraph is insufficient.
Small size or a common owner does not remove a real separate work boundary.

Expected behavior and acceptance criteria belong to the requirement; actual
check results belong to the verification document referencing it. Work documents
link those results. Do not duplicate authoritative definitions
or evidence. A failed check is a result, not by itself a new tracked item.

Discovery, research, project overviews and other work can precede or support
requirements. Use the appropriate document type and actual objective/source
without inventing a REQ or approval to fill a link. Link requirements when they
are established. Decisions, issues and other records retain their own types
when separately managed; requirements do not replace every other identity.

| Situation | Required treatment |
|---|---|
| Login and search have distinct requirements, even with the same owner | Separate `REQ` files; the overview groups them by feature. |
| Search results must be exportable as a file in addition to being searchable | A separate export REQ linked to the search requirement and relevant work. |
| An empty search result must display a count of zero | A condition/acceptance detail in the search requirement, unless separately managed acceptance requires an AC item. |
| One requirement has input examples, rationale and parent-specific acceptance details | Sections of that requirement; no new file or independent ID for each explanation. |
| A fix restores the specified search count, or a regression test checks it | Reference the existing search REQ from the change/work and checks; no new REQ solely for the fix or test. |
| An acceptance criterion is separately tracked with its own disposition | Its own `AC` file, linked to the parent requirement. |
| A backend plan includes tasks managed as separate outputs | Each task has its own file under the project ID convention; the plan contains links and sequence/dependency information. |
| Several plans cover the same requirement | Reference the same owning requirement file rather than copy its definition. |
| A small correction restores an existing requirement | Reuse the requirement's linked files, put changed detail and results in their respective owners, and keep source/change trace in the owning plan/work note. |
| A bounded correction has no management definitions to reuse | When the conditions below hold, keep the correction's missing definitions in sections of one work document, linked from the overview. |

Ordinary prose, navigation and explanatory headings need no independent ID.
Do not use compact planning or the word "metadata" to conceal
separately managed items inside a single growing document.

### Minimum documentation for a small change

For a correction eligible for [compact planning](DEVELOPMENT_METHOD.md#choosing-planning-depth),
reuse the requirement's existing design, plan, task and verification files.
Keep their IDs and document roles; create a new item only when identity and
work boundaries require it. Preserve completed work and old evidence rather
than rewriting them as the new correction. Do not claim an unreviewed baseline
is reusable.

Missing definitions may share one ID-named work document when all of these hold:

- The work qualifies for compact planning, has one accountable writer at a time
  and one correction outcome with one completion boundary.
- The expected result and existing contracts are established from attributable
  sources. No new independently managed requirement, shared design/contract or
  additional output needing separate assignment/completion is being introduced.
- Existing owning definitions remain in place and are linked. Only otherwise
  missing content goes in the work document; there is no parallel definition or
  evidence copy, including information owned by a designated tracker.
- No applicable project or delivery requirement mandates separate files.

State the basis briefly in the work document and use its normal work-item ID,
such as `TASK-001`. Keep source/expected behavior, approach, plan/execution and
actual verification distinguishable in sections. These supporting sections
need no separate REQ, DES, PLAN or VER IDs or files solely to fill document
roles; a parent-plan link may point to the plan section. Link an existing REQ
when available; otherwise attribute the bounded expected behavior to its source
without reconstructing the feature's full requirements. New commitments still
follow the requirement-boundary rules. Applying this exception within covered
work requires no additional approval.

Keep the project overview and its normal ID/path/allocation conventions. With
no existing management documents, this means an overview and one work document
for the correction. Reuse an existing overview; do not create another entry
document. The [worked example](EXAMPLE_WEB_PROJECT.md#small-correction-without-existing-management-documents)
shows this arrangement. Neither missing documents nor the number of source
files alone decides planning depth.

The following content remains required, in existing owners or the allowed
sections. It is not a mandatory set of headings or new files:

| Owning content | Content for this correction |
|---|---|
| Requirement/source and expected behavior | Reference the established outcome and acceptance conditions. If no requirement is recorded, establish the bounded expectation from its actual source; do not invent a new commitment. |
| Design/contract | Reuse applicable behavior and contracts; update the correction's approach and affected interactions where the design changes. |
| Plan | Link the actual request and baseline, record the impact assessment and reuse basis once, and specify affected scope, order, dependencies and planned checks. Reuse readiness under [Approvals](APPROVALS.md#coverage-and-currentness); record the compact planning review and remaining prerequisites here. |
| Task | Identify the writer, cause, chosen correction, affected paths, ordered execution, status and completion checks. Link the owning plan, design and verification files or sections instead of copying them. |
| Verification | Record the candidate version, method/environment, expected and observed results, evidence, failures, unrun checks and limits after execution. Keep planned checks distinct from actual results even when both are in one file. |
| Overview | Keep links and the relevant summary current under [summary updates](#summary-ownership-and-updates). Update ID allocation only when an item is actually allocated. |

The files or sections must provide the same executable detail as any
implementation plan. Complete the [compact review](DEVELOPMENT_METHOD.md#choosing-planning-depth)
before implementation and record actual results only after the checks run.
No separate coverage matrix, per-area N/A table or duplicate review log is required.

Use a change section in the owning plan/work document for the request, impact
and history. A separate CHANGE/CR record is needed only when the agreed project
or external process requires it, under the
[change cycle](DEVELOPMENT_METHOD.md#change-cycle-and-propagation); it links
the owning definitions and evidence. Keep each affected owner current so an
implementer need not reconstruct its instructions from successive change notes.
Preserve history and do not consolidate existing records into the work document.

If the work grows beyond the exception, establish the necessary independent
owning items and repair current links before the affected work starts. For
example, a new export commitment needs its own requirement; a design now shared
by several requirements needs its own owner; concurrent writers need separately
assigned work. Retain the original correction ID, decisions and evidence, link
extracted content to its new owner and avoid duplicate current definitions.
Use detailed planning when its triggers apply. A regression scenario alone
does not need another ID, and unrelated corrections must not accumulate in the
same work document. Allocation, filenames and required external deliverables
retain their normal rules.

## Required-name exceptions

This section applies to project deliverables within the [ID scope](#id-scope).
The harness's own guidance is excluded there and needs no exception-ID mapping.

Keep an exact filename/location when a consuming tool, project contract or
repository entry convention requires it. Examples include a tool's `AGENTS.md`,
`CLAUDE.md` or `SKILL.md`, and a repository landing `README.md`. These files are
exceptions to the ID-based filename and classification-path requirements, not
to identity, trace, scope or verification. The exception must have a concrete
consumer/contract reason; personal filename preference is insufficient.

Choose the stable document ID as usual. Put it in the body when permitted by
the required format, and record its ID, canonical path and exception reason/
source in the overview/index. If the required body cannot include an ID, the
index supplies the identity mapping. Link to the actual required-name file;
do not create an ID-named duplicate just to satisfy the ordinary layout.
Independently managed content still has one owning definition; use links to
other item documents rather than duplicating them into an entry file.

For example, when a consumer requires a root `AGENTS.md`, retain that path,
record its document ID and the consumer requirement in the index, and add the
ID to its body if compatible. A normal requirements document continues to use
`requirements/REQ-001.md` under the chosen document root. The agent assesses
and documents the exception within the already authorized task; preserving a
required name does not need an additional approval ceremony.

### Path-scoped instruction files

A project may keep an instruction file next to the area it governs, such as a
subtree's own `AGENTS.md` or tool adapter, so that rules for one part of a
repository do not have to sit in the root file every session loads. Where they
exist, read the ones covering the paths the current work touches, closest path
first, in addition to the root policy and adapter, and name the applicable ones
among a work item's inputs.

A path-scoped file adds detail for its subtree. It cannot weaken the root
policy, a contract or an external control; where it appears to, the root
governs and the conflict is resolved rather than followed. Keep each rule in
one file at the narrowest path covering its subject instead of copying it into
several, and record these paths and their scope in the overview so a session
can tell which apply without scanning the tree. They keep the name their
consumer requires under the [exceptions above](#required-name-exceptions).

## Document validation

Before completing document work, apply these checks to the requested stage.
Use [allocation reuse](#allocation-and-validation-reuse) and
[verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification) to determine
the affected scope and reusable evidence.

| Check | Evidence to verify |
|---|---|
| Coverage and ownership | Determine ID scope first. Each in-scope document and independent item has an ID and one owning definition; requirement boundaries describe distinct commitments, supporting conditions remain with their requirement, and separately managed work references the REQs it covers. For a small-change document, check the exception's conditions, linked existing owners, distinct planned/actual results and any required split. Check source/objective links for work before requirements are established. Overviews reference owners; harness guidance needs no identity or path-mapping checks. |
| Identity and allocation | Verify that new definitions are unique against one another and the shared allocation basis, do not collide with retained/retired IDs or reservations, and fall within any delegated range. Only provisional branch IDs permit temporary cross-branch collisions under [branch collision checks](#branch-allocation-and-collision-repair); resolve them before integration. Compare IDs independently of slugs or folders, and distinguish definitions, references and illustrative examples. |
| Project ID convention | Each new ID matches its registered format, classification values, width and allocation scope. For a hierarchical ID, verify the parent mapping, owning parent and body link. Check dictionary extensions and existing meanings without renaming retained IDs. |
| Area overviews and trackers | Root and area overview entries resolve and hold only their owned content; designated tracker information has no parallel Markdown record; tracker references carry a resolvable key/link, and relied-on tracker state is recorded where a decision, completion or handoff depends on it. |
| Ordinary paths | Each new file matches the recorded folder mapping and one allowed filename form in [Document paths](#document-paths). Check ID/body/anchor agreement, optional slug syntax and unambiguous ID boundaries, one owning file per ID, and updated links after renames. |
| Required-name files | Verify the actual consumer name/location/format, index ID/path/reason mapping, and body/index ID agreement when the body permits an ID. Otherwise verify the stated body-format restriction. |
| Links and trace | Overview entries and item/anchor links resolve to the intended owners; requirements, design, planned work and actual evidence cover the requested stage. The [document checker](CONTEXT_EFFICIENCY.md#document-checker) can supply the resolution part; whether a link reaches the intended owner and the trace coverage still need review. |
| Planning detail and omissions | Apply the review for the selected [planning depth](DEVELOPMENT_METHOD.md#choosing-planning-depth): source coverage, executable work, applicable scenarios, concrete verification and honest unknown dispositions. Compact plans do not require detailed-plan tables. Valid IDs and links alone do not establish an adequate plan. |
| Open-item trace | For affected open items, verify their [required content](#open-items), owning references and [lifecycle disposition](WORKFLOW.md#open-item-lifecycle). Closure/reopening must retain evidence and update affected definitions and dependency status; a status change alone is insufficient. |
| Scope and history | No unauthorized migration or historical relabeling; IDs and prior decision/evidence history are preserved, and unrun verification is not reported as success. |
| Document quality | Content is consistent with its inputs, Markdown structure is valid and applicable format/contract requirements are met. |

Required-name checks replace ordinary path/name/body checks only to the extent
required by the documented consumer constraint; identity, links and other checks
remain applicable. Do not treat every existing descriptive filename as a new
exception. Existing records keep their names and applicable prior evidence.

The [document checker](CONTEXT_EFFICIENCY.md#document-checker) can supply the
filename-derived part of the identity and path checks: duplicate owning files,
repeated ID-only headings, slug syntax, filename/body ID agreement and unlinked
ID-named files. Registered formats, folder mapping, allocation and whether an
ID names the intended item still need review.

## Trace and baselines

Use commits, snapshots or document versions to identify the basis of important
claims and decisions. Preserve material source-to-requirement-to-design-to-work
relationships without requiring every optional record type.

When recovering documents from code, label observation, inference, confirmed
intent and uncertainty. Link observations to the inspected revision and source
locations. Keep current implementation and proposed target separate.

## Open items

An open item is an unresolved question, decision, prerequisite, contradiction
or finding that needs follow-up to establish scope, readiness or completion.
It can arise at any stage. Routine work already defined by a task does not
need a second issue merely because it is unfinished. A failed check stays
in its owning verification record, linked from the work; its unresolved impact
still needs the follow-up information below when work continues or is handed off.

A question answered and checked within the same work session, with no remaining
follow-up or independent management boundary, needs only the question, answer
and authoritative source/evidence with its relevant version in the owning work
note. Incorporate any affected definition/check there or link the updated owner.
No separate OI, owner/timing fields or transition log is required for that
completed clarification. This shortcut does not supply human decisions or
product verification: actual authority, evidence and material-change rules
still apply. If the answer leaves a dependency, unresolved impact or handoff,
use the follow-up content below.

Use the existing [item boundaries](#independent-items-and-supporting-detail).
Keep a parent-specific question and its history in the owning requirement,
design, plan or task when it needs no separate management boundary. A separately
assigned investigation, decision or shared issue with its own completion status
owns the appropriate ID/file, such as an `ISSUE` or `RISK`; retain existing IDs
and reference actual decisions and resolution tasks rather than duplicating
them. Moving work between plans does not create a new identity for the same
issue. Small size alone does not exempt independently managed items.

For items needing continued follow-up, use the following content. Inherit
owner, scope and review milestone from the parent when unambiguous; record
only differing values locally. Do not invent dates, owners or intermediate
states merely to fill fields.

| Content | What to record in the owning item or linked authoritative section |
|---|---|
| Subject and source | The concrete question, missing input or conflicting observations; discovery source and relevant version, distinguishing facts from assumptions. |
| State and accountability | Current lifecycle state, accountable follow-up owner, actual resolver/decision authority where different, and any explicitly unassigned responsibility. |
| Impact | Affected requirements, criteria, plans/tasks and dependents; what cannot be planned, started or completed, and what can proceed independently. |
| Next action and timing | Investigation, decision or prerequisite action; provider being awaited, expected output, needed-by milestone/date and next review trigger. Use event-based timing when no date is established. |
| Resolution criterion | Observable evidence or attributable decision that will answer the question or satisfy the prerequisite, and how it will be checked. |
| Outcome and propagation | Answer/result, applicable decision/evidence and version, remaining limits, updated owning definitions and dependent-readiness assessment; for deferral/exclusion, the reason, authority and retained obligation. |
| History | Prior and new state/disposition, reason, actor and actual date or version reference for material transitions, including closure and reopening. Preserve prior answers and failed attempts. |

These are content requirements, not a fixed schema or a separate registry.
Compact sections/tables and links suffice. A project overview indexes shared
or blocking items where needed for navigation; detailed tracking has one owner.
Do not create a parallel issue list, record for every checklist cell, or new
file for each state transition. Follow the
[open-item lifecycle](WORKFLOW.md#open-item-lifecycle) for handling and checks.
When open items are designated to an [external tracker](#external-work-trackers),
the tracker item holds this content and Markdown documents link it.

## External work trackers

A project may designate an existing tracker, such as GitHub Issues, Jira or
Linear, as the authoritative record for selected kinds of management
information, typically task assignment and status, open items and progress.
Designation is an actual owner decision; a tracker link, existing integration or
authenticated tool alone does not designate one. Record it in the project
overview (or the relevant [area overview](#area-overviews)):

| Designation | Required detail |
|---|---|
| Tracker and scope | Tool, project/space or repository, and the areas using it. |
| Owned information | Kinds of information whose authoritative record is the tracker; everything else stays in Markdown. |
| Identity and references | Key format and how Markdown documents reference items (key with a resolvable link). |
| Agent operations | Operations the agent may perform as routine parts of covered work, such as creating in-scope items, updating status or assignment, and adding links or comments. |
| Required content | Where the tracker holds content this model requires, such as an open item's resolution criterion, next action and history (fields, templates or comments). |

For each designated kind, the tracker is the single authoritative record. Do not
keep a parallel Markdown list or copy of its status, assignment or history;
link the tracker item instead. The tracker key identifies an item the tracker
owns and needs no harness ID or allocation. A registered document-ID format
may embed that key as its serial under [allocation reuse](#allocation-and-validation-reuse);
the document then has one ID and the tracker supplies its number. When such an item needs a detailed
Markdown definition, such as task implementation detail, that document keeps its
own document ID and records the key: the tracker owns status and assignment,
the document owns the detailed definition.

Requirements, acceptance criteria, design, decisions and verification evidence
stay in versioned Markdown unless the project already keeps them in a system
with attributable version history; then reference the item and its version.
When a decision, readiness assessment, completion claim or handoff relies on
tracker state, record the key and the observed state with its date or version in
the owning Markdown record. That records what was relied on; it is not a mirror
to maintain.

Operations beyond the recorded agent operations, changes to tracker workflows,
permissions or automation, and messages that reach people outside the designated
use are external effects that need matching authorization under
[Security](SECURITY.md#authenticated-tools-and-protected-values). If the tracker
is unavailable, note pending updates in the current work note and apply them
when access returns; that note is not the authoritative status. Changing or
ending a designation is an owner decision; preserve existing items and links and
record where each kind of information is owned from then on.

## Decisions and evidence

Store only actual decisions with truthful attribution; record labels do not
grant authority. A decision can cover several plans within its bounds. Keep
the reviewed prior version when commitments change.

Evidence describes what actually happened to a particular subject. Keep
IMPLEMENTED, STATIC_VERIFIED, INTEGRATION_VERIFIED, BROWSER_VERIFIED,
LIVE_ENV_VERIFIED, CUSTOMER_ACCEPTED and CLOSED distinct. Unrun, failed, stale,
ambiguous or partial evidence is not PASS. Check current applicability without
rewriting old observations or concealing newer failures.

Never include secrets, private keys or protected credential material.
Reference externally controlled approval receipts without copying protected
authority into project files.

## Completion and closure

A completion claim covers the requested deliverable and its actual verification.
Release/project closure aggregates all contributing plans, required outcomes,
decisions, evidence and applicable acceptance/delivery/maintenance obligations.
A release inventory is sufficient; no canonical closure dependency manifest is
required under this policy.

## Harness policy maintenance

Maintain this harness's policy and guidance directly under
[policy maintenance](../AGENTS.md#harness-policy-maintenance). Git history
replaces a policy-change index and separate archive/change-note files.
Earlier policy records and their allocated IDs remain discoverable in Git
history; removing their working-tree copies does not make those IDs reusable.
The document and ID rules above continue to govern actual project deliverables.
