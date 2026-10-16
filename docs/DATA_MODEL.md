# Project Information Model

This is the detailed standard for project document organization, identity,
paths, exceptions and validation under
[AGENTS.md](../AGENTS.md#document-organization). Other guidance links these
definitions.

This file is long; do not load it whole. Pick the sections for the work from
the table below and read only those. Locate each by its heading text: for
example, search for `## Item IDs` and read to the next `## ` heading.
Follow a link into another section only when the rule being applied depends on
it. Every section that applies to the work remains mandatory; a section that
does not apply is not required reading.

| Work | Sections to read |
|---|---|
| Create, name or rename a project document | [ID scope](#id-scope), [Item IDs](#item-ids), [Document paths](#document-paths), the single-writer paragraphs of [Allocation reuse](#allocation-and-validation-reuse), [Document validation](#document-validation) |
| Decide whether something is a separate item | [Item boundaries](#independent-items-and-supporting-detail) |
| Document bounded low-risk work | [Minimum documentation for a small change](#minimum-documentation-for-a-small-change) |
| Write or update an overview, plan or task | [Document organization](#document-organization), [Plans and tasks](#plans-and-tasks), [Summary ownership and updates](#summary-ownership-and-updates) |
| Record or follow up an unresolved question | [Open items](#open-items) |
| Resume work that spans sessions, or record where it stands | [Resumption state](#resumption-state) |
| Several teams, delegated ID ranges or an external tracker | [Area overviews](#area-overviews), the range record in [Allocation reuse](#allocation-and-validation-reuse), [External work trackers](#external-work-trackers) |
| Check documents before a completion claim | [Document validation](#document-validation), then the sections its rows name for the changed content |
| Keep a consumer-required name, write project or subtree instruction files, or adopt or sync the harness copy | [Required-name exceptions](#required-name-exceptions), [Project instruction files](#project-instruction-files), [Harness copy](#harness-copy), [Path-scoped instruction files](#path-scoped-instruction-files) |

Reference existing non-Markdown records, product files such as `package.json`
and original evidence such as logs in their own formats. Do not convert or
delete them automatically. Summarize verification in Markdown and link those
original artifacts.

## ID scope

The harness's own policy, framework overview, exception guidance and agent
instructions do not receive document or rule IDs. This applies to new guidance
as well as existing files, including `AGENTS.md`, the harness `README.md` and
its policy documentation, in this repository and in a project's
[harness copy](#harness-copy). Use meaningful or consumer-required Markdown
names; no ID filename, classification-folder mapping or exception-ID registry is
needed for these guidance files. Maintain them through Git under
[policy maintenance](../AGENTS.md#harness-policy-maintenance).

A project's own root and path-scoped
[instruction files](#project-instruction-files) receive no ID either. They are
project records, not harness guidance. The project maintains them within its
authorized work, not under harness policy maintenance.

Actual project deliverables remain subject to the ID rules: project overviews,
requirements, designs, plans, tasks, decisions, research and verification, among
others. Classify by purpose, not filename or folder: a framework overview
explains how to use the harness; a project overview tracks a project's outcomes
and work. A project document does not become exempt by being called a guide
or exception. Examples in harness guidance remain illustrative, not allocations.
Keep existing IDs; this distinction does not authorize stripping them from
records. Explicit contract or external identity requirements remain
binding.

## Suggested information

| Information | Minimum useful content |
|---|---|
| Project overview | Objective, baseline, shared conventions and links to owning decisions, work and resumption positions. |
| Project entry | Stack and runtime versions, build, test and static-check commands with where each runs (such as locally or in CI), the top-level code layout, writer rules no other record owns and any [model roster](CONTEXT_EFFICIENCY.md#project-model-roster). The project's [root instruction file](#project-instruction-files) owns these. |
| Project conventions | Integration/branch model, quality criteria and shared verification environments, such as staging or a live-equivalent environment. The project overview owns these. |

Record entry and convention facts that are actually decided or observed, with
their source/version. Record each when it is decided or found at intake, not as
a placeholder, and mark an undecided one as undecided. Other records,
including verification records, link them instead of copying them.

Other records take their content from the rules that own them:

- requirements and design from the
  [stage contract](DEVELOPMENT_METHOD.md#stage-contract);
- plans and tasks from [plans and tasks](#plans-and-tasks);
- decisions from [Approvals](APPROVALS.md#preparing-and-recording-one-decision);
- open items from [open items](#open-items);
- verification from [verification](WORKFLOW.md#verification-and-completion);
- change trace from the
  [change cycle](DEVELOPMENT_METHOD.md#change-cycle-and-propagation);
- intake from
  [existing-project intake](DEVELOPMENT_METHOD.md#existing-project-intake-and-reverse-engineering);
- handoffs from [transfer](COLLABORATION.md#transfer-and-integration).

## Document organization

Use a project overview for shared context and navigation, with independently
scoped documents grouped in [folders by document kind](#folders-by-document-kind).
The agent records the document root and folder mapping, reusing established
project conventions. Feature/work units remain logical groups
in the overview and relationships between items regardless of physical layout.
A project with several such units must not default to a single accumulating
file for each document type.
Each requirement owns its REQ file and links the separate owning design, plan,
task and verification files needed at the requested stage. Shared definitions
or work keep one owning file linked by all covered requirements. Create files
when their stage/output is needed, not as placeholders for future stages.
Bounded low-risk work follows the
[compact documentation](#minimum-documentation-for-a-small-change) exception.

The overview holds the objective, shared project context, links to shared
requirements and architecture, baseline, resumption links and an index of units.
It also states the document and item-ID convention, including agent-selected
extensions and any allocation ownership. It records the
[project conventions](#suggested-information) once they are decided or
observed, and states an undecided convention as such. It links the project
entry for the stack and check commands.
Each index entry states its scope and material dependencies and links the unit's
owning documents. Follow those links for current status under
[summary ownership](#summary-ownership-and-updates).

Use requirements as the primary basis for separating product scope under the
[item-boundary rules](#independent-items-and-supporting-detail). Connect design,
planned work and verification to the requirements they cover. Keep supporting
detail within its owning document role and link the other roles' definitions.
Length alone does not create a new item; use sections and navigation
when accumulated supporting detail obscures scope, decisions or evidence.
Record the chosen boundaries and rationale briefly in the overview or work note.

Every unit links back to its overview and applicable shared specifications.
Connect requirements and acceptance criteria to the covering design, planned
work and actual verification. Use item IDs with file or anchor links, optionally
in a compact trace table.
Links may be many-to-many: several plans can implement one requirement, and a
shared design can support several features. State cross-unit dependencies and
the relevant input versions.

When adding a new unit, add its index entry and relevant dependency links.
When scope changes, update the owning detail, affected links and overview
summary, keeping the decisions and evidence that still apply. New work uses
these boundaries even when earlier work lives in a large file; reference that
baseline.
Do not automatically split, move or rewrite existing records merely to adopt
the layout. Any authorized reorganization must keep IDs and repair links;
version history keeps the reviewed versions. A requested stage still ends at
its own outputs.

### Summary ownership and updates

Keep each current fact in one owning location, within a file as well as across files:

- Requirements own expected outcomes and acceptance criteria.
- Designs and contracts own behavior and structure.
- Plans own order, dependencies and overall completion criteria.
- Work items own execution state, execution mode, immediate next action and
  dependency links. Shared decisions may be inherited by reference.
- Verification records own actual check results; open items own unresolved
  findings, their follow-up and resolution.

Designated tracker ownership follows [external work trackers](#external-work-trackers).
[Compact work](#minimum-documentation-for-a-small-change) may keep otherwise
missing definitions in separate sections of one work document.

Use links for current navigation. Overviews and parent plans link work and its
[resumption position](#resumption-state); they do not repeat child statuses,
execution modes, blocker explanations, next actions or pass counts.
A parent's own integration condition remains its responsibility, linked to its
providers. Completing a child does not establish that condition.

For a progress request, read the owners and derive the answer at that time under
[status reporting](WORKFLOW.md#status-and-trace-reporting).
A kept report is a deliverable at its source version, not a current view.
Derive a required current view from the owning records each time it is
refreshed; a report cannot supply current readiness.

Update an overview or parent when its own scope, dependency, navigation or
decision changes. A child status change alone requires no parent edit.
When affected work exposes an old duplicate current claim, replace it with an
owner link. Do not rewrite a delivered report to match later events or launch
an unrelated document migration.

Before relying on a current fact, follow its owner link. Resolve discrepancies
under [current-state updates](WORKFLOW.md#updating-current-work-state).
Coordinate edits to shared navigation through its owner under
[collaboration](COLLABORATION.md#coordination-waits).

### Area overviews

Split navigation into area overviews when one project overview no longer works
as a readable index or shared edit point. For example:

- several teams or work streams edit it concurrently;
- its unit index obscures current scope;
- subsystems, services or repositories progress independently.

Size alone is not the criterion. Record the split and its reason in the project
overview.

The project overview remains the root. An area overview has its own document
ID, links back to the root and follows the same organization rules for its area.

| Content | Owning overview |
|---|---|
| Objective, shared constraints and specifications (or links), document root and shared folder mapping, area index, cross-area dependencies, allocation delegations | Project (root) overview |
| Area unit index, resumption links, area-specific folder extensions, consumption of delegated ID ranges | Area overview |
| Detailed definitions, decisions and evidence | Owning item documents, as without areas |

Each area index entry links the area overview and states its scope, accountable
owner and material dependencies. Area folder extensions
must not redefine a shared mapping or prefix. A requirement or design used by
several areas has one owning definition. Keep it at the root or in a designated
owning area, and link it from the others. Current-state links lead downward to
their owners; apply [summary ownership](#summary-ownership-and-updates).
An area may nest further only when it meets the same split criterion.

Root overview edits follow its assigned owner under the
[collaboration basis](COLLABORATION.md#collaboration-basis); area writers route
root changes through that owner or an agreed transfer. New areas can start with
their own overview. Moving existing index entries or allocations out of an
established overview is a reorganization. It needs a matching request, preserves
IDs and repairs links.

## Plans and tasks

A plan organizes an outcome across work items. It defines:

- the goal, and the scope it includes and excludes;
- the input requirements and design;
- dependencies and a feasible task order;
- overall completion criteria.

A project can use `PLAN` for general, backend or screen implementation plans.
Plans link to the owning task files. API contracts and screen specifications
are inputs to plans, not plans themselves. Preserve established project
meanings where they differ.

A task is a concrete output that the actual work assigns and completes as a
separate unit. Implementation steps serving that output may stay in its file.
Its owning task file is named under the project's ID convention and records:

- the expected output, and the accountable writer or that it is unassigned;
- the affected paths and logical resources, and the inputs the work reads;
- parent plan and input links, and prerequisites;
- current [state](WORKFLOW.md#task-states), ordered actions and concrete
  completion checks;
- the current execution mode and the declared stop conditions.

Supply or link the implementation details and verification scenarios required
by the selected [planning depth](DEVELOPMENT_METHOD.md#choosing-planning-depth).
Resolve ownership before concurrent execution. These are content requirements,
not mandatory headings or front matter.

### Starting or resuming from the task

Use the task document as the entry point. Its opening description makes the
current basis easy to find:

- the scoped outcome;
- the relevant requirement and design sections;
- the governing decision and input versions;
- the completion checks;
- the next action or blocker.

Link existing owners and sections. Do not copy their content or build another
index. Where no task is needed yet, the selected plan or stage-output document
supplies this entry; do not create a placeholder task. Resolve conflicting
inputs under the [change cycle](DEVELOPMENT_METHOD.md#change-cycle-and-propagation)
before relying on them, and follow links to affected shared constraints.

### What the task declares

A resuming session reads each of these from the item instead of reconstructing
it from an earlier conversation.

**Write scope.** Write only the paths and logical resources the task declares.

- Declare a newly required path, shared file or generated artifact before
  editing it.
- Name excluded targets where an adjacent path would otherwise look in scope.
- Reading an input does not make it writable. Keep the sources the work
  consumes distinct from the targets it may change.

Necessity does not widen the scope. Extend the declaration under the
[change cycle](DEVELOPMENT_METHOD.md#change-cycle-and-propagation), or stop when
that extension needs a decision the work does not have.

**Declared inputs.** Declare the inputs the item reads as deliberately as the
targets it writes. Name the governing instructions, requirement and design
sections, contracts, source files and prior outputs the result depends on, with
the versions read. A missing, unreadable or changed input is then recognizable
as a stop condition rather than a surprise mid-execution.

Reading something outside that set is not a violation. Add it to the
declaration when it turns out to carry the result, and reassess the item when
it contradicts an input already declared.

**Shared paths.** Where another item also owns or consumes a declared path,
record it as shared and state how this item may touch it. The normal answer is
consume-only, with any unavoidable registration or integration edit named as
such.

A defect in a shared component belongs to the item that owns it. Return it
there under [fixes across work-item boundaries](WORKFLOW.md#fixes-across-work-item-boundaries); the
consuming item's declared scope, review and evidence do not cover that
component. Where two items must both write a shared path, order them or assign
one writer under the [collaboration basis](COLLABORATION.md#collaboration-basis)
before either starts.

**Completion checks.** Record the actual commands or check targets and the
environment they run in, referencing the
[project entry and conventions](#suggested-information) where they exist. A resuming
writer or a separate auditor then runs the same check instead of inventing an
equivalent one.

A check that cannot be named concretely is not yet a completion criterion.
Naming a check does not run it; see
[verification and completion](WORKFLOW.md#verification-and-completion).

**Execution mode.** Record what the work may presently produce: analysis and
specification only, review output only, or implementation and its checks.

The mode states the consequence of the actual decision recorded under
[Approvals](APPROVALS.md#preparing-and-recording-one-decision), and names that
decision. It is not a permission the item grants itself, and widening it is a
separate decision. Where the item and the actual decision disagree, the
decision governs and the item is corrected.

**Authorized sub-scopes.** A long-running item can hold several scopes
authorized at different times. Keep the item's own mode at the narrowest
current standing, and record each authorized sub-scope separately:

- what it covers;
- the decision and date that authorized it;
- its own write scope and exclusions;
- its completion checks.

A later authorization does not widen the earlier ones or lift the item's own
mode. A finished sub-scope stays recorded rather than being folded into the
item's general text. One authorized part does not make the whole item
implementable.

**Stop conditions.** Record the conditions that stop the item before they
occur. These are the inputs, contracts, fixtures, authority and scope
boundaries whose absence or change makes continuing unsafe or meaningless.
Declared stop conditions make a stop recognizable while the work runs rather
than only in hindsight.

They do not replace the
[real blockers](../AGENTS.md#current-state-evidence-and-real-blockers), which stop
affected work whether or not the item listed them. An unlisted condition is not
permission to continue past it.

### Plans, tasks and their files

**Requirements and boundaries.** Plans and tasks reference the requirements
they cover; the relationship can be many-to-many. Keep plan and task
definitions in their respective files, with local sections allowed under
[compact documentation](#minimum-documentation-for-a-small-change). Split
further on actual output, assignment and completion boundaries under the
[boundary criteria](#independent-items-and-supporting-detail).

**Where status lives.** Keep task definitions and execution status in their
owning files, and link the actual check results from the verification
documents. Plans hold order, dependencies and navigation links. Apply
[summary ownership and updates](#summary-ownership-and-updates) instead of
copying detailed task states into each parent. A task shared by several plans
retains one ID, one owning file and one writer.

Assess completion of the planned outcome against its scope and criteria, using
task outcomes and applicable combined verification. Planning itself ends when
the plan and task definitions satisfy the completion checks for the selected
[planning depth](DEVELOPMENT_METHOD.md#choosing-planning-depth). Planning
completion does not require those tasks to have executed. Planning-only work
records intended checks without claiming execution.

**Parent and child plans.** A parent plan may organize child plans, such as
area or work-stream plans. The parent owns the cross-plan goal, the scope split
between children, integration work, ordering between children and overall
completion criteria. Each child owns its own scope, tasks and checks.

The parent's planning completion checks cover that cross-plan content. They
reuse a child's passed planning checks for its stated scope and versions, and
recheck a child whose inputs changed. Completing every child does not complete
the parent outcome while integration work or parent criteria remain.

**Directories and ownership.** Directory ownership and task ownership
complement each other. Record the document root and type-to-folder mapping in
the overview, and the actual edit scope in the task. Two tasks may work in one
directory when their file and resource boundaries are clear. A folder name or
document ID alone does not assign work. Use the
[collaboration basis](COLLABORATION.md#collaboration-basis) to make these
boundaries and ID allocations visible to concurrent writers.

### Resumption state

Work spanning sessions keeps one navigation record naming its current item,
the next item in the sequence, and the first owning sections to read.
Place it near the start of its owning document or link it from the opening.

The plan owns this position for a single plan. An overview may own navigation
across plans or [areas](#area-overviews); it links each plan's position.
A standalone work item may hold its own position without a separate plan.

Link the current item's execution mode, immediate next action, prerequisites
and blockers instead of restating them. Link the last established checkpoint's
evidence and any release, acceptance or closure conditions in their owning records.
If this document owns one of those facts, keep it once and link its section.
A short ordered reading list is enough; no second status table is needed.

Move the position when work actually moves. A changed task result requires an
update to its owner, not a rewrite of every entry pointer.
Version history keeps past positions; keep no position log.

A pointer establishes no permission, readiness or pass. The actual decision
and evidence govern under [Approvals](APPROVALS.md#preparing-and-recording-one-decision)
and [verification](WORKFLOW.md#verification-and-completion).

## Item IDs

**Which documents get an ID.** Apply identity rules to every Markdown
deliverable within the [ID scope](#id-scope), whatever its subject. Such
deliverables include specifications, research, guides, meeting notes, reviews,
reports, handoffs and kinds not listed here.

- A document representing one primary item uses that item's ID.
- A collection can use a document ID such as `DOC-001`.
- An overview itself also has an identity.

Choose the identity before creating the file and use it in the index;
[document paths](#document-paths) defines filename and body placement. A
document ID is not a substitute for the identities of its independently tracked
contents. Use the [item-boundary rules](#independent-items-and-supporting-detail)
to identify those, and apply IDs to new traceable items added to existing
Markdown. Requirements, acceptance criteria, designs, plans, tasks, decisions,
findings, changes, risks, issues and verification are examples, not an
exhaustive list.

**The format table.** Use the project's recorded ID format table. There is no
mandatory token length, serial width, universal AREA segment or fixed number of
segments. Prefer simple semantic prefixes, and add a classification or parent
segment only when the project needs it. The
[folder table](#folders-by-document-kind) lists starter formats such as
`REQ-NNN`, `SCR-{surface}-NNN` and `TASK-{work}-NNN`; its rows are examples,
not a closed vocabulary or allocated IDs.

In the starter formats, `NNN` is a three-digit serial starting at `001`. A
final `NN` is a child serial starting at `01`. The child's `NNN` copies its
parent's serial: `OD` details an `OI`, and `CT` and `BT` check an `API`.
Starter `surface` values are `PC`, `MOB` and `AD` (desktop, mobile and
administrator screens). Starter `work` values are `PC`, `MOB`, `API`, `ADMIN`
and `COMMON` (desktop UI, mobile UI, backend, admin UI and shared work). A
cross-component task uses `COMMON` and describes its scope in the body.
Register others, such as `DB` or `AI`, when the work needs them. A
classification describes work scope; it does not assign a person or authority.

The project overview owns the table, or links its one owning dictionary where
separate management is useful. Record each kind's meaning, exact format, allowed
classification values, serial width and start, allocation scope and any
parent-ID rule. A small project can use a few rows in the overview. Create or
extend a dictionary when needed; no separate file or full catalog is required. A
separately managed project dictionary follows the ordinary document-ID and path
rules. Harness guidance remains outside the ID scope.

Agents reuse established formats, and add missing kinds or classifications
within the authorized work without asking for each token. Register an addition
before allocating against it. Preserve existing meanings, and avoid synonyms or
overlapping formats that make an ID ambiguous. Different kinds can use different
axes: screen platform and task work area need not share a code list. Technology,
audience and feature metadata can stay in the body instead of the ID.

**Reading an ID.** Interpret an ID using its whole registered format. In the
starter formats, `API-001` identifies an API contract, and its method, path,
version and coverage are specified in the body. `PLAN-001` can plan its
implementation, and `TASK-API-003` can implement it.

Task numbers do not derive from plan numbers; record the actual plan,
requirement, design and contract links. Shared tasks may link to several plans.
A `FEATURE` groups related items through links. It does not duplicate the
requirements it groups, and it does not require one item of every type.

**Allocating a serial.** Allocate flat and classified serials project-wide per
complete prefix, such as `REQ` or `TASK-API`. Two feature folders or parent
plans cannot each restart `TASK-API-001`. Hierarchical formats allocate the
child serial per child kind and identified parent, as recorded in the format
table. Under `CT-API-NNN-NN`, for example, `CT-API-012-01` is a contract test of
`API-012`, and a backend test `BT-API-012-01` has a separate counter.

Complete IDs are unique project-wide, regardless of folder or checkout. Only new
provisional IDs may collide temporarily, under
[branch allocation](#branch-allocation-and-collision-repair).

Before allocating a child, verify its parent's owning definition and format
mapping, and link the parent in the body. Matching numbers imply no other
relationship. A parent segment records identity, not a mutable dependency: where
current coverage changes, preserve the ID and update the links.
An actual replacement or split follows the identity rules below. Parent detail
that needs no independent management can remain a section without a new ID.

Search existing definitions, retained and retired IDs and reservations before
choosing the next unused serial, reusing a verified allocation basis. Concurrent
writers use non-overlapping ranges, unless the recorded arrangement uses the
tracker or isolated-branch exceptions under
[allocation reuse](#allocation-and-validation-reuse). Where the available width
is exhausted, record a compatible extension for new IDs and check consumers and
collisions before allocating. Do not wrap counters, reuse IDs or automatically
pad or rename older records.

**Placing the ID.** Put the ID visibly in the owning heading or table row, and
provide a stable anchor. An ID-only heading such as `### REQ-001` with a
descriptive title in the body works, as does an explicit anchor for an
identified table row. References use the ID as link text and resolve to that
item's anchor, even within one file.

**Keeping an ID stable.** Keep IDs unchanged when content is revised, renamed,
reordered or moved, and update links after moves. Only new provisional branch
IDs may be renumbered for an allocation collision, under
[branch allocation](#branch-allocation-and-collision-repair). Never reuse
deleted or retired IDs.

For a split or merge, record the old item's disposition and the links to the new
items; version history keeps its earlier content. Identity alone does
not identify a reviewed version, prove approval or establish a passed check.

**Existing IDs and records.** Existing IDs and existing records remain valid;
link to older material without bulk retroactive relabeling. This includes
five-digit IDs and existing `TYPE-AREA` conventions. Earlier harness examples
used `API` for backend plans and `SCR` for screen plans; retain those meanings
wherever they are already established.

A shorter serial is not permission to reuse the same prefix for a different
purpose in that project. Use the existing convention, or register a distinct
unambiguous prefix. A requested migration has its own scope. Externally required
document formats remain binding; resolve a real conflict rather than silently
omitting identity requirements.

## Document paths

Except for [required-name files](#required-name-exceptions), every new project
Markdown document uses `<document-root>/<classification-path>/<ID>-<slug>.md`.
The ID portion exactly matches the owning document ID, including the tokens,
separators and number widths in the project's format table. The slug names the
item's subject, so a reader can tell files apart without opening them. It is
not part of identity, allocation or parent relationships.

The slug consists of exactly two lowercase ASCII words joined by one hyphen
(`kebab-case`), matching `[a-z]+-[a-z]+`. Use a hyphen between the complete ID
and the slug, for example `API-024-service-context.md` or
`TASK-UI-025-popup-migration.md`. A single word, additional words, digits,
spaces, underscores and non-ASCII letters are invalid in the slug. Write the
full title, in any language, in the body.

Name the subject the item keeps for its lifetime, such as `account-lock` or
`cloud-save`. Leave out versions, states and dates, such as `final`, `draft` or
`fixed`. Those change while the identity stays, and a renamed file needs every
link to it repaired.

Identify the complete ID from its registered format, including any parent/child
segments, rather than treating the last hyphen or number as its boundary.
Verify that the ID and slug have an unambiguous interpretation under the
project's formats before creating the file.

Show the ID without the slug near the top of the body and in stable ID anchors.
Keep the full title and context in the body and overview. Reference links use
the ID as their label and the actual owning filename/anchor as their target.
An ID in the body or directory alone does not satisfy the filename rule.

Established `<ID>.md` filenames remain valid. Do not rename them merely to add
a slug; that is a reorganization and needs a matching request. For example,
`overview/DOC-001.md` and `overview/DOC-001-project-overview.md` are
alternative names for the same identity; `overview.md` needs a required-name
exception. Keep one current owning file per ID across all folders: a different
slug, or adding/removing a slug, does not create another item. Do not keep both
filename forms as duplicate owning files.

Preserve the ID when changing a slug. Do not automatically rename files when
titles change. When a filename changes within authorized work, update the
overview/index path and all affected links.
The rule covers all document kinds, including overviews, shared specifications,
research, reports, changes and handoffs.

### Folders by document kind

Group new documents by kind beneath the chosen document root, such as
`project-docs/`. Use the following default mapping where the project has no
established mapping. Each folder holds the separate files for that kind;
it is not one combined file per kind.

| Document kind | Starter ID format | Default folder beneath the document root |
|---|---|---|
| Project or area overview | `DOC-NNN` | `overview/` |
| Requirements | `REQ-NNN` | `requirements/` |
| Separately managed acceptance criteria | Project-registered `AC` format | `requirements/acceptance/` |
| Feature navigation | `FEATURE-NNN` | `features/` |
| Design and shared architecture | `DES-NNN` | `designs/` |
| API contracts | `API-NNN` | `contracts/` |
| Screen specifications | `SCR-{surface}-NNN` | `screens/` |
| Plans | `PLAN-NNN` | `plans/` |
| Tasks | `TASK-{work}-NNN` | `tasks/` |
| Open items | `OI-NNN` | `open-items/` |
| Standalone decisions | `DEC-NNN` | `decisions/` |
| Architecture decisions | `ADR-NNN` | `decisions/architecture/` |
| Separately managed open-item resolutions | `OD-NNN-NN` | `decisions/open-items/` |
| Verification records | `VER-NNN` | `verifications/` |
| Separately managed contract checks | `CT-API-NNN-NN` | `verifications/contracts/` |
| Separately managed backend checks | `BT-API-NNN-NN` | `verifications/backend/` |
| Changes | `CHG-NNN` | `changes/` |
| Handoffs | `HANDOFF-NNN` | `handoffs/` |
| Research | Project-registered format | `research/` |
| Guides | Project-registered format | `guides/` |
| Meeting notes | Project-registered format | `meetings/` |
| Reviews | Project-registered format | `reviews/` |
| Progress and recurring reports | Project-registered format | `reports/` |
| Separately managed dictionaries | `DOC-NNN` | `dictionaries/` |

Choose the folder by the document's purpose, not its ID prefix alone.
For example, a `DOC` overview and a `DOC` dictionary belong in different folders.
As another example, a deployment guide belongs in `guides/`, even when its ID
also uses `DOC`. These are placement defaults, not required deliverables or new
ID allocations. Use [item boundaries](#independent-items-and-supporting-detail) to decide whether
content needs its own file. A folder row does not require splitting supporting
detail out of its owner or the [compact documentation rules](#minimum-documentation-for-a-small-change).

Record the chosen root and kind-to-folder mapping in the project overview.
Reuse established names and hierarchy, including [area extensions](#area-overviews).
When no convention exists, start with kind folders directly beneath the root.
Add subfolders for a surface, subsystem or work area when navigation needs them,
such as `screens/pc/` or `tasks/backend/`. A feature spanning several kinds links
their owning files; it does not collect copies in a second folder.

Before creating a document of an unmapped kind, select and record its folder
within the authorized work. Do not use the root or a miscellaneous folder as
the fallback for unrelated kinds. The agent makes routine mapping choices
without asking the user to classify each document. Apply each mapping
consistently within its recorded scope.

Folder changes preserve IDs and repair overview/item links; they do not
authorize migrating existing records. Do not create empty type folders or
placeholder files before they are needed. Group feature relationships through
the overview and owning documents, independently of the physical layout.
For example, `plans/PLAN-001-user-search.md` links to a task at
`tasks/TASK-API-001-search-endpoint.md` and an input contract at
`contracts/API-001-user-search.md`.

## Allocation and validation reuse

**Where the record lives.** Use an `ID allocation` section, or its
local-language equivalent, in the actual project overview, including a
[compact work document serving that role](#minimum-documentation-for-a-small-change).
That is the default shared allocation record. Where the team already uses
another shared Markdown location, link its exact file and section from the
overview and maintain the allocation there only. Folder names stay contextual;
writers must be able to discover one authoritative location for each scope.

**The checked basis.** Establish an initial basis by checking project-wide
definitions, retained and retired IDs, earlier allocations and outstanding
reservations. Record the checked version and scope, the result and any limits
once, then reuse that record with subsequent allocation changes. When creating
the first overview, include its own ID in this check and record the basis there.
No pre-existing registry is necessary.

**One writer.** Take the case of a single writer without delegated ranges or
outstanding reservations. In that case, the allocation section needs only each
allocation scope, its next serial and a link to that shared checked basis.

- Advance the serial when allocating. Never move it backward or fill earlier
  gaps.
- The initial serial must exceed every used, retired or previously allocated
  serial in that scope.
- Existing owning document links identify issued items. No per-allocation owner,
  range reservation or gap-disposition table is required.

For example, `TASK-API: next 004` means `001` through `003` cannot be newly
allocated, whether used, retired or skipped. Do not invent a disposition for
unused gaps. Where prior allocations are
uncertain, reconcile them before choosing the serial.

**Concurrent writers.** Record the allocation arrangement once in the allocation
section before introducing them. Use the shared range record below unless one of
the two exceptions applies. Returning to a single writer requires reconciling
prior ranges, reservations and pending branch allocations first; the simple
counter cannot silently supersede them.

Two arrangements need no range or owner record:

- A registered format may take its serial from a designated
  [external work tracker](#external-work-trackers) key, such as
  `TASK-{area}-{issue}`. The tracker then allocates, and the overview records
  the format and tracker. Kinds without such a format, such as `REQ` or `OI`,
  still need one of the other arrangements.
- Writers on separate branches may use a per-scope next serial with provisional
  IDs and collision repair, under
  [branch allocation](#branch-allocation-and-collision-repair).

These exceptions replace the range table. They do not replace the checked
allocation basis or the identity rules.

**Areas and delegated ranges.** With [area overviews](#area-overviews), the root
allocation section delegates non-overlapping serial ranges per allocation scope
to areas, and records each delegation's owner and verified basis. The area
overview's allocation section records consumption within its delegated ranges;
the root does not repeat it.

Complete IDs stay unique project-wide, and areas do not introduce their own
prefixes for an existing type. When an area exhausts a range, obtain a new
delegation from the root allocation owner before allocating further.

**The range record.** For allocation using reserved or delegated ranges, use a
compact Markdown table with the following minimum information, reusing shared
baseline notes for rows checked together:

| Field | Required content |
|---|---|
| Allocation scope | Registered complete prefix, such as `TASK-API`; for hierarchical formats, child kind and parent, such as `CT` for `API-012`. |
| Verified basis | Commit/version and scope checked, including definitions, retained/retired IDs and outstanding reservations; actual check result and any limits. A version alone is not proof of verification. |
| Allocated range | Inclusive serial bounds assigned within that allocation scope, using its recorded width. |
| Owner | Writer responsible for consuming the range; identify any agreed transfer. |
| Disposition | Used serials or owning-document links, retired serials, and remaining reserved/available numbers. Record gaps explicitly rather than assuming everything below the largest number was used. |

These are required contents, not fixed column spellings or a new machine schema.
For example, take a hypothetical `TASK-API` range `001` through `020` owned by
writer A. Its row may state: used `001` and `003`, retired `002`, remaining
`004` through `020` reserved for A. Its row must also link the actual checked
basis. This example does not allocate IDs in this harness repository.

Do not create a second registry or a new document per allocation.

**Consuming a range.** Within an assigned range, consume unused serials and
record their disposition. Reuse the verified basis plus subsequent allocation
changes instead of reading every document for each new ID. Folder, feature or
checkout boundaries do not reset the sequence.

Exhausted ranges need a new non-overlapping allocation. Check shared allocation
changes before extending or transferring a range; uncertain, conflicting or
stale reservations must be reconciled first. A local highest-number search alone
does not account for other writers or retired IDs.

**Validating later definitions.** Compare newly defined IDs with that basis and
with other new definitions, and check changed files plus affected references. For
delegated ranges, check new definitions against the area's range, and check root
delegations for overlap whenever they change.

Broaden the scan when baseline coverage is missing or unreliable, when
allocation conflicts appear, or when changes to conventions or validation rules
affect prior results. Preserve project-wide uniqueness and never reuse retired
IDs. This changes how evidence is obtained, not the identity or filename
requirements. See
[verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification).

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

Where decisions, signed payloads or verification artifacts still carry the old
ID, record the old ID with its source version/path and the new ID in the owning
plan/work note. Do not rewrite those artifacts; link them through that mapping
and assess their applicability rather than inventing a new PASS.
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
and fulfillment need their own assessment. Search and the export of search
results are two such commitments. Requirements may depend on one another;
technical independence is not required. A shared security or performance
constraint can also be a requirement when it has its own scope and fulfillment
criteria.

Keep the conditions, rationale, examples, parent-specific acceptance criteria
and check methods that explain one requirement with that requirement. A
separately executable assertion or test does not alone make a new requirement.
Stages, algorithms, code files and test commands are not requirement boundaries.
When an acceptance criterion actually needs its own acceptance disposition,
use an AC item linked to its requirement. Do not relabel such a criterion as a
new REQ.

Before assigning a new REQ, check existing requirements. A correction that
restores an already specified behavior references the existing REQ; adding a
test for it does not create another REQ. Revise the same requirement under its
existing ID when its identity remains the same; version history keeps the prior
version. A new commitment or an actual split/merge follows the existing
[identity rules](#item-ids). Identity does not authorize a material
change to the requirement or acceptance criteria.

### Related work and supporting detail

Designs, plans, tasks, changes and verification reference the requirements
they cover. These relationships may be many-to-many. A shared design or check
has one owning definition linked to all relevant REQs. Preserve separate
requirement, design, plan, task and verification files under
[document organization](#document-organization), reusing shared definitions
without creating a copy for every requirement.

Give related work a separate ID/file when the actual work needs any of these:

- a separately assigned or delivered output;
- its own completion/decision status;
- a shared definition maintained across requirements.

Keep implementation steps and supporting explanations in their owning item.
Merely being able to assign a step to someone else, run a test separately or
link a paragraph is insufficient. Small size or a common owner does not remove
a real separate work boundary.

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
| A bounded correction has no management definitions to reuse | Under the conditions below, one work document can own the correction's missing definitions and serve as its overview. |

Ordinary prose, navigation and explanatory headings need no independent ID.
Do not use compact planning or the word "metadata" to conceal
separately managed items inside a single growing document.

### Minimum documentation for a small change

For [compact work](DEVELOPMENT_METHOD.md#choosing-planning-depth), use the
existing owning work document and link applicable requirements and contracts.
Update another owning definition only when its facts or instructions change.

Missing local approach, plan and verification definitions may live in sections
of that work document. Keep planned checks separate from actual results.
Do not create separate DES, PLAN or VER files solely to fill those roles.
An independently managed requirement or shared definition still has its own
owner under [item boundaries](#independent-items-and-supporting-detail).
Existing owners and required contractual files retain their roles.

The work note holds what the
[compact procedure](DEVELOPMENT_METHOD.md#choosing-planning-depth) records
before, during and after the work. Link existing verification records instead
of copying them. Task declarations still apply; references to existing
instructions satisfy them.

Reuse the overview and its folder/ID conventions where they exist.
If no management records exist to reuse, one work document may also serve as
the overview when all of these hold:

- One writer handles one compact work item.
- No additional independently managed requirement, shared definition or output
  needs its own owner.
- No project or contractual rule requires a separate overview.

Use the work item's ID and kind folder; no additional DOC ID or overview file
is needed. Keep its bounded objective, baseline and analysis limits near the
start. Record only the document root, folder/ID conventions and allocation basis
actually needed. Hold known check commands and environments here only while the
project has no root instruction file to own them. The normal identity,
allocation and validation rules still apply. Entry links point to this document;
its owned sections satisfy overview references without duplicating task state.

When authorized work expands beyond these conditions, establish a separate
overview before starting the affected work. Transfer current shared context,
conventions and allocations there, and link the original work item. Replace
live sections with links. In a closed work record, link the new owner; version
history keeps the prior context. Preserve the work item's ID and evidence.
Do not combine existing owners or accumulate
unrelated work to keep a single file. If scope grows, establish only the new
independent owners or detailed planning that the change requires before the
affected work starts. Extend closed
work under [verification and completion](WORKFLOW.md#verification-and-completion).

## Required-name exceptions

This section applies to project deliverables within the [ID scope](#id-scope).
The harness's own guidance is excluded there and needs no exception-ID mapping.

Keep an exact filename/location when a consuming tool, project contract or
repository entry convention requires it. Examples include a tool-required
`SKILL.md` and a repository landing `README.md`. Project instruction files are
outside the [ID scope](#id-scope) and need no exception. These files are
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

For example, suppose a tool requires a skill the project ships at
`skills/report/SKILL.md`. Retain that path, record its document ID and the
consumer requirement in the index, and add the ID to its body if compatible. A normal requirements document continues to use
`requirements/REQ-001-user-search.md` under the chosen document root. The agent assesses
and documents the exception within the already authorized task; preserving a
required name does not need an additional approval ceremony.

### Project instruction files

A project's own root instruction file is the root `AGENTS.md`, `CLAUDE.md` or
other tool file a session loads before it reads anything else. The project owns
it. In an adopting project the tool adapters stay in the
[harness copy](#harness-copy); never put the project entry there. The root file
is the one document whose cost is paid in every session. It owns the
[project entry](#suggested-information), the facts the work cannot start
without and that rarely change:

- the stack and runtime versions actually in use;
- the real build/test/static-check commands and where each runs, such as
  locally or in CI;
- the top-level code layout;
- writer rules that no other record owns;
- the [model roster](CONTEXT_EFFICIENCY.md#project-model-roster), where the
  project designates one.

Where several tools are used, keep the project entry in one of their files and
let the others route to it. Where a project has no root instruction file yet,
its overview holds the project entry until one exists. Then move the entry and
leave a link.

Add a short entry pointer to the project overview, its
[non-authoritative](DEVELOPMENT_METHOD.md#non-authoritative-inputs) designations
and the owning [resumption state](#resumption-state) for work in progress.
Keep separate pointers for separate streams or [areas](#area-overviews) instead
of merging them into one list. Link the current position and ordered reading list there without
maintaining another copy of task status in the entry file.
For an eligible [compact work document](#minimum-documentation-for-a-small-change)
serving as the overview, the entry route points to that document and its sections.

Before reporting project instruction setup or harness adoption complete, check
the entry route against the project's actual state:

- Where the project uses the [harness copy](#harness-copy) layout, each tool's
  entry file reaches the policy and that tool's adapter in the copy. The entry
  file records the copy's folder and source commit, and the copy matches that
  commit without local edits.
- The root instruction file reaches the project overview and, where work is
  active, its current resumption record.
- The stack, actual check commands and top-level code layout are recorded
  here, and the overview's conventions are linked. Mark undecided entries
  honestly; do not invent commands to complete setup.
- Each recorded check runs where the entry says it runs. For a check agents
  run, try it in the agent's sandbox. Where it cannot run there, record where
  it runs and who runs it.
- Where the project keeps a model roster, each listed model was confirmed in
  the actual tool and account. Tool configuration pins the main session to a
  strongest-tier model.
- The project's landing README introduces the project and links its overview.
  Link the harness usage guide separately, preserving existing guidance and
  required entry names when integrating it.

These checks apply to authorized adoption or instruction maintenance. A read-only
review reports missing entry information without creating files.

Keep other owning content out of it. An entry file that accumulates requirement
decisions, item-level instructions or verification gates becomes a second
owning definition that drifts from the first. Every session also loads it in
full, including the sessions it has nothing to do with. Move such content to
the item that owns it and link it, under
[summary ownership](#summary-ownership-and-updates). The entry file carries no
authority of its own: an execution mode, a decision and a pass stay with the
records that own them.

### Harness copy

A project that adopts the harness keeps two sets of files apart:

- **The harness copy.** The harness repository's tracked files, unchanged, in
  one folder of the project: `harness/` by default, or another name where the
  project already uses that one. Do not use `.harness/`, which holds
  [former runtime records](WORKFLOW.md#former-runtime-records). Links inside
  the copy are relative, so they work wherever the folder sits.
- **The project's entry files.** The root `AGENTS.md`, `CLAUDE.md` or other
  tool file that a session loads first. The project owns them. They route to
  the policy and the tool's adapter in the copy and hold the
  [project entry](#project-instruction-files).

Do not edit the copy inside the project. Put project additions in the entry
files or the owning project records. Make a harness change in the harness
repository and bring it in by sync. The
[Claude](../CLAUDE.md#in-an-adopting-project) and
[Codex](../CODEX_START_PROMPT.md#in-an-adopting-project) adapters give each
tool's route from the entry file into the copy.

Record the copy's folder and the harness commit it came from once, in the
entry file that holds the project entry. A sync replaces the folder's contents
with a newer commit's tracked files and updates that record, so files the
harness removed disappear too. Nothing needs merging, because the project never
edited the copy. Read the harness changes between the two commits before
relying on the new rules.

The `AGENTS.md` and `CLAUDE.md` inside the copy are the governing policy and
its adapter. They are not path-scoped rules for the copy's folder.

A project that copied the harness into its own root keeps that layout until a
requested reorganization moves it. Until then, a sync applies the harness
changes between the recorded source commit and the new one. Merge changed files
with their local edits, and remove or rename files the harness removed or
renamed. Where the project entry is kept, record the new source commit and the
files that still carry local edits. Before a move, compare each
harness file with the harness commit it came from, so that every local edit is
relocated rather than lost. The move places the harness files in the copy folder
and the local content in project-owned entry files or records. It repairs
project links into the moved files.

### Path-scoped instruction files

A project may keep an instruction file next to the area it governs, such as a
subtree's own `AGENTS.md` or tool adapter. The purpose is that rules for one
part of a repository need not sit in the root file every session loads. Where
these files exist, read the ones covering the paths the current work touches,
in addition to the root policy and adapter. Start with the file closest to those
paths, and name the applicable ones among a work item's inputs.

A path-scoped file adds detail for its subtree. It cannot weaken the root
policy, a contract or an external control. Where it appears to, the root
governs and the conflict is resolved rather than followed. Keep each rule in
one file at the narrowest path covering its subject instead of copying it into
several. Record these paths and their scope in the overview so a session can
tell which apply without scanning the tree. They keep the name their consumer
requires and, as instruction files, need no ID or exception entry.

## Document validation

Before completing document work, apply these checks to the requested stage.
Use [allocation reuse](#allocation-and-validation-reuse) and
[verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification) to determine
the affected scope and reusable evidence.

| Check | Evidence to verify |
|---|---|
| Coverage and ownership | Determine ID scope first. Each in-scope document and independent item has an ID and one owning definition. Requirement boundaries describe distinct commitments, and supporting conditions remain with their requirement. Separately managed work references the REQs it covers. For compact work, check linked existing owners, distinct planned/actual results and any required split. Check source/objective links for work before requirements are established. Overviews reference owners; harness guidance needs no identity or path-mapping checks. |
| Identity and allocation | Verify that new definitions are unique against one another and the shared allocation basis. Also verify that they do not collide with retained/retired IDs or reservations, and that they fall within any delegated range. Only provisional branch IDs permit temporary cross-branch collisions under [branch collision checks](#branch-allocation-and-collision-repair); resolve them before integration. Compare IDs independently of slugs or folders, and distinguish definitions, references and illustrative examples. |
| Project ID convention | Each new ID matches its registered format, classification values, width and allocation scope. For a hierarchical ID, verify the parent mapping, owning parent and body link. Check dictionary extensions and existing meanings without renaming retained IDs. |
| Area overviews and trackers | Root and area overview entries resolve and hold only their owned content. Designated tracker information has no parallel Markdown record. Tracker references carry a resolvable key/link. Relied-on tracker state is recorded where a decision, completion or handoff depends on it. |
| Ordinary paths | Each new file matches its document kind's recorded folder mapping and one allowed filename form in [Document paths](#document-paths). Check new kinds against [Folders by document kind](#folders-by-document-kind), including recorded extensions and existing conventions. Check ID/body/anchor agreement, the slug's presence and syntax on new files, unambiguous ID boundaries, one owning file per ID, and updated links after renames. |
| Required-name files | Verify the actual consumer name/location/format, index ID/path/reason mapping, and body/index ID agreement when the body permits an ID. Otherwise verify the stated body-format restriction. |
| Links and trace | Overview entries and item/anchor links resolve to the intended owners; requirements, design, planned work and actual evidence cover the requested stage. The [document checker](CONTEXT_EFFICIENCY.md#document-checker) can supply the resolution part; whether a link reaches the intended owner and the trace coverage still need review. |
| Current instructions and navigation | Apply [current-state updates](WORKFLOW.md#updating-current-work-state) to affected task states, execution modes, prerequisites, next actions and summaries. No superseded instruction or history note remains beside the current one. For adoption or entry-file changes, check the [project entry route](#project-instruction-files). Link resolution alone does not establish currentness. |
| Planning detail and omissions | Apply the review for the selected [planning depth](DEVELOPMENT_METHOD.md#choosing-planning-depth): source coverage, executable work, applicable scenarios, concrete verification and honest unknown dispositions. Compact plans do not require detailed-plan tables. Valid IDs and links alone do not establish an adequate plan. |
| Open-item trace | For affected open items, verify their [required content](#open-items), owning references and [lifecycle disposition](WORKFLOW.md#open-item-lifecycle). Closure/reopening must record its evidence and update affected definitions and dependency status; a status change alone is insufficient. |
| Scope and current state | No unauthorized migration or relabeling of existing records; IDs stay unchanged. Documents hold only the current state under [current state only](DEVELOPMENT_METHOD.md#current-state-only): no history notes, superseded text or snapshots. Unrun verification is not reported as success. |
| Document quality | Content is consistent with its inputs, Markdown structure is valid and applicable format/contract requirements are met. |

Required-name checks replace ordinary path/name/body checks only to the extent
required by the documented consumer constraint; identity, links and other checks
remain applicable. Do not treat every existing descriptive filename as a new
exception. Existing records keep their names and applicable prior evidence.
The [document checker](CONTEXT_EFFICIENCY.md#document-checker) can supply the
filename-derived part of the identity and path checks.

## Open items

An open item is an unresolved question, decision, prerequisite, contradiction
or finding that needs follow-up to establish scope, readiness or completion.
It can arise at any stage. Routine work already defined by a task does not
need a second issue merely because it is unfinished. A failed check stays
in its owning verification record, linked from the work. The failed check's
unresolved impact still needs the follow-up information below when work
continues or is handed off.

Some questions are answered and checked within the same work session, with no
remaining follow-up or independent management boundary. Such a question needs
only these in the owning work note: the question, the answer and the
authoritative source/evidence with its relevant version. Incorporate any
affected definition/check there or link the updated owner. No separate OI,
owner/timing fields or transition log is required for that completed
clarification. This shortcut does not supply human decisions or
product verification: actual authority, evidence and material-change rules
still apply. If the answer leaves a dependency, unresolved impact or handoff,
use the follow-up content below.

Use the existing [item boundaries](#independent-items-and-supporting-detail).
Keep a parent-specific question in the owning requirement, design, plan or
task when it needs no separate management boundary. A separately
assigned investigation, decision or shared issue with its own completion status
owns its own ID/file: an `OI` by default, or a registered kind such as `RISK`
where the project tracks that kind separately. Retain existing IDs
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

These are content requirements, not a fixed schema or a separate registry.
Compact sections/tables and links suffice. A project overview indexes shared
or blocking items where needed for navigation; detailed tracking has one owner.
Do not create a parallel issue list, record for every checklist cell, or new
file for each state transition. Follow the
[open-item lifecycle](WORKFLOW.md#open-item-lifecycle) for handling and checks.
When open items are designated to an [external tracker](#external-work-trackers),
the tracker item holds this content and Markdown documents link it.

## External work trackers

A project may designate an existing tracker — GitHub Issues, Jira, Linear — as
the authoritative record for selected kinds of management information. Task
assignment and status, open items and progress are the usual ones.

Designation is an actual owner decision. A tracker link, an existing integration
or an authenticated tool does not designate one. Record the designation in the
project overview, or in the relevant [area overview](#area-overviews):

| Designation | Required detail |
|---|---|
| Tracker and scope | Tool, project/space or repository, and the areas using it. |
| Owned information | Kinds of information whose authoritative record is the tracker; everything else stays in Markdown. |
| Identity and references | Key format and how Markdown documents reference items (key with a resolvable link). |
| Agent operations | Operations the agent may perform as routine parts of covered work, such as creating in-scope items, updating status or assignment, and adding links or comments. |
| Required content | Where the tracker holds content this model requires, such as an open item's resolution criterion and next action (fields, templates or comments). |

For each designated kind, the tracker is the single authoritative record. Do not
keep a parallel Markdown list or a copy of its status, assignment or history;
link the tracker item instead.

The tracker key identifies an item the tracker owns. It needs no harness ID or
allocation. A registered document-ID format may embed that key as its serial
under [allocation reuse](#allocation-and-validation-reuse). The document then
has one ID, and the tracker supplies its number.

Some such items need a detailed Markdown definition, such as task implementation
detail. That document keeps its own document ID and records the key. The tracker
owns status and assignment; the document owns the detailed definition.

Requirements, acceptance criteria, design, decisions and verification evidence
stay in versioned Markdown. Where the project already keeps them in a system
with attributable version history, reference the item and its version there
instead.

Where a decision, readiness assessment, completion claim or handoff relies on
tracker state, record the key and the observed state. Put them in the owning
Markdown record, with the observed state's date or version. That records what
was relied on. It is not a mirror to maintain.

These are external effects, and they need matching authorization under
[Security](SECURITY.md#authenticated-tools-and-protected-values):

- operations beyond the recorded agent operations;
- changes to tracker workflows, permissions or automation;
- messages that reach people outside the designated use.

Where the tracker is unavailable, note pending updates in the current work note
and apply them when access returns. That note is not the authoritative status.

Changing or ending a designation is an owner decision. Preserve existing items
and links, and record where each kind of information is owned from then on.
