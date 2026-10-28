# Project Information Model

This is the detailed standard for project document organization, identity,
paths, exceptions and validation under
[AGENTS.md](../AGENTS.md#document-organization). Other guidance links these
definitions.

This file is long; do not load it whole. Pick the sections for the work from
the table below and read only those. Locate each by its heading text: for
example, search for `## Item identity` and read to the next `## ` heading.
Follow a link into another section only when the rule being applied depends on
it. Every section that applies to the work remains mandatory; a section that
does not apply is not required reading.

| Work | Sections to read |
|---|---|
| Create, name or rename a project document | [Identity scope](#identity-scope), [Item identity](#item-identity), [Document paths](#document-paths), [Path checks](#path-checks-and-verification-reuse), [Document validation](#document-validation) |
| Decide whether something is a separate item | [Item boundaries](#independent-items-and-supporting-detail) |
| Document bounded low-risk work | [Minimum documentation for a small change](#minimum-documentation-for-a-small-change) |
| Write or update an overview, plan or task | [Document organization](#document-organization), [Plans and tasks](#plans-and-tasks), [Summary ownership and updates](#summary-ownership-and-updates) |
| Record or follow up an unresolved question | [Open items](#open-items) |
| Resume work that spans sessions, or record where it stands | [Resumption state](#resumption-state) |
| Several teams, shared paths or an external tracker | [Area overviews](#area-overviews), [Path checks](#path-checks-and-verification-reuse), [External work trackers](#external-work-trackers) |
| Check documents before a completion claim | [Document validation](#document-validation), then the sections its rows name for the changed content |
| Keep a consumer-required name, write project or subtree instruction files, or adopt or sync the harness copy | [Required-name exceptions](#required-name-exceptions), [Project instruction files](#project-instruction-files), [Harness copy](#harness-copy), [Path-scoped instruction files](#path-scoped-instruction-files) |

Reference existing non-Markdown records, product files such as `package.json`
and original evidence such as logs in their own formats. Do not convert or
delete them automatically. Summarize verification in the commit message, or in
Markdown for a failure that still stands, and link those original artifacts.

<a id="id-scope"></a>

## Identity scope

Project Markdown deliverables use their canonical paths as identity under
[item identity](#item-identity). This includes overviews, requirements, designs,
plans, tasks, decisions, research and verification.
Use semantic paths for new work. Do not create sequential document or item IDs.

Harness policy, framework overviews, exception guidance and agent instructions
keep meaningful or consumer-required names. They need no project folder mapping
or identity registry, here or in a project's [harness copy](#harness-copy).
Maintain harness guidance under [policy maintenance](../AGENTS.md#harness-policy-maintenance).
A project's own [instruction files](#project-instruction-files) also keep their
required paths without an exception entry. The project owns those files.

Preserve existing filenames, IDs and externally required identities.
This policy change does not authorize migrating existing project records.
Examples in harness guidance illustrate paths; they do not create project items.

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
- contract-required handoff documents from
  [transfer](COLLABORATION.md#transfer-and-integration).

## Document organization

Use a project overview for shared context and navigation, with independently
scoped documents grouped by [area and purpose](#folders-by-area-and-purpose).
The agent records the document root and folder mapping, reusing established
project conventions. Feature/work units remain logical groups
in the overview and relationships between items regardless of physical layout.
A project with several such units must not default to a single accumulating
file for each document type.
Each requirement owns its requirement file and links the separate design, plan,
task and verification owners needed at the requested stage. Shared definitions
or work keep one owning file linked by all covered requirements. Create files
when their stage/output is needed, not as placeholders for future stages.
Bounded low-risk work follows the
[compact documentation](#minimum-documentation-for-a-small-change) exception.

The overview holds the objective, shared project context, links to shared
requirements and architecture, baseline, resumption links and an index of units.
It also records document paths, folder conventions and shared ownership
boundaries. It records the
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
work and planned checks. Use descriptive file or section links, optionally
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
the layout. An authorized reorganization repairs path and anchor references;
version history keeps the reviewed versions. A requested stage still ends at
its own outputs.

Before removing or renaming a heading or anchor, search the project for links
to it. Repair them in the same change, or keep the anchor. Keep it where a link
lies outside the work's editing scope. An explicit HTML anchor can keep an old
fragment working after its heading changes.

### Summary ownership and updates

Keep each current fact in one owning location, within a file as well as across files:

- Requirements own expected outcomes and acceptance criteria.
- Designs and contracts own behavior and structure.
- Plans own order, dependencies and overall completion criteria.
- Work items own execution state, execution mode, immediate next action and
  dependency links. Shared decisions may be inherited by reference.
- Verification records own planned checks and failures that still stand; open
  items own unresolved questions until their answer is in its owner.

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

The project overview remains the root. An area overview has its own canonical
path, links back to the root and follows the same organization rules for its area.

| Content | Owning overview |
|---|---|
| Objective, shared constraints and specifications (or links), document root and shared folder mapping, area index, cross-area dependencies, shared path ownership | Project (root) overview |
| Area unit index, resumption links, area-specific folder conventions, path ownership | Area overview |
| Detailed definitions, decisions and evidence | Owning item documents, as without areas |

Each area index entry links the area overview and states its scope, accountable
owner and material dependencies. Area folder extensions
must not redefine a shared path or duplicate an owning definition.
A requirement or design used by several areas has one owning definition. Keep it at the root or in a designated
owning area, and link it from the others. Current-state links lead downward to
their owners; apply [summary ownership](#summary-ownership-and-updates).
An area may nest further only when it meets the same split criterion.

Root overview edits follow its assigned owner under the
[collaboration basis](COLLABORATION.md#collaboration-basis); area writers route
root changes through that owner or an agreed transfer. New areas can start with
their own overview. Moving existing index entries out of an established overview
is a reorganization. It needs a matching request and repairs affected links.

## Plans and tasks

A plan organizes an outcome across work items. It defines:

- the goal, and the scope it includes and excludes;
- the input requirements and design;
- dependencies and a feasible task order;
- overall completion criteria.

A project can use general, backend or screen implementation plans.
Plans link to the owning task files. API contracts and screen specifications
are inputs to plans, not plans themselves. Preserve established project
meanings where they differ.

A task is a concrete output that the actual work assigns and completes as a
separate unit. Implementation steps serving that output may stay in its file.
Its owning task file follows the project's path convention and records:

- the expected output, and the accountable writer or that it is unassigned;
- the affected paths and logical resources, and the inputs the work reads;
- parent plan and input links, and prerequisites;
- current [state](WORKFLOW.md#task-states), ordered actions and concrete
  completion checks;
- the current execution mode and the declared stop conditions.

Supply or link the implementation details and verification scenarios required
by the selected [planning depth](DEVELOPMENT_METHOD.md#choosing-planning-depth).
Resolve ownership before concurrent execution. These are content requirements,
not mandatory headings or front matter. A task file lasts until the task is
done or cancelled, under
[current state only](DEVELOPMENT_METHOD.md#current-state-only).

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
sections, contracts, source files and prior outputs the result depends on. A
missing, unreadable or changed input is then recognizable
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
- the decision that authorized it;
- its own write scope and exclusions;
- its completion checks.

A later authorization does not widen the earlier ones or lift the item's own
mode. Delete a sub-scope once it is finished; the commit message carries its
checks. One authorized part does not make the whole item
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
owning files. Passed check results are in commit messages, and failures that
still stand in the verification documents. Plans hold order, dependencies and
navigation links. Apply
[summary ownership and updates](#summary-ownership-and-updates) instead of
copying detailed task states into each parent. A task shared by several plans
retains one canonical path, one owning file and one writer.

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
complement each other. Record the document root and folder conventions in
the overview, and the actual edit scope in the task. Two tasks may work in one
directory when their file and resource boundaries are clear. A folder name or
document path alone does not assign work. Use the
[collaboration basis](COLLABORATION.md#collaboration-basis) to make these
boundaries and shared paths visible to concurrent writers.

### Resumption state

Work spanning sessions keeps one navigation record naming its current item,
the next item in the sequence, and the first owning sections to read.
Place it near the start of its owning document or link it from the opening.

The plan owns this position for a single plan. An overview may own navigation
across plans or [areas](#area-overviews); it links each plan's position.
A standalone work item may hold its own position without a separate plan.

Link the current item's execution mode, immediate next action, prerequisites
and blockers instead of restating them. Link any release, acceptance or closure
conditions in their owning records; the commit history holds the last
checkpoint's evidence. While the current item's work is uncommitted, also keep
its starting state and handoff notes here until the commit. Without Git, keep
the latest checks and request basis here too.
If this document owns one of those facts, keep it once and link its section.
A short ordered reading list is enough; no second status table is needed.

Move the position when work actually moves. A changed task state requires an
update to its owner, not a rewrite of every entry pointer.
Version history keeps past positions; keep no position log.

A pointer establishes no permission, readiness or pass. The actual decision
and evidence govern under [Approvals](APPROVALS.md#preparing-and-recording-one-decision)
and [verification](WORKFLOW.md#verification-and-completion).

<a id="item-ids"></a>

## Item identity

**Canonical identity.** Identify a document by its project-root-relative path,
including filename and extension. Use forward slashes, for example
`project-docs/user/user-search.md`. The project overview records the document
root and folder conventions. Shorten a displayed path relative to that root
only when its context is unambiguous.

Each independently managed item has one owning document under
[item boundaries](#independent-items-and-supporting-detail).
A collection or compact work document may own supporting sections.
Identify a referenced section by its owning path and stable fragment, such as
`project-docs/user/user-search.md#acceptance`.
Use heading anchors or explicit HTML anchors; no separate sequence or item-ID
registry is required.

**Uniqueness and references.** Keep one current owning definition for each item.
Different paths must not duplicate the same authoritative definition.
The same basename may occur in different folders; it is not a project-wide identity.
Do not create paths differing only in letter case.
Use exact tracked spelling in links, including on case-insensitive filesystems.

Link to the owning file or section using a meaningful label or its path.
State the document's role, title and scope near the start of its body.
The path need not be copied into every body heading.
Relationships come from explicit links, not similar names or shared folders.
Plans, tasks, contracts and checks link the definitions they actually cover.
Parent/child relationships also use links, not copied serials or path-derived authority.

**Stable identity.** Keep paths and referenced fragments stable through ordinary
content or title changes. Do not rename files automatically when titles change.
Never repurpose a deleted or retired path for an unrelated item.
A reopened item may return at its former path from version history.

A path identifies an item, not its reviewed version or verification result.
For version-dependent decisions, evidence or handoffs, include the commit/version
and owning path or fragment. Across repositories, also name the repository or project.
A bare path does not identify an immutable candidate.

**Moves, splits and merges.** Within an authorized reorganization, repair overview
entries, incoming links and referenced fragments in the same change.
Search references before removing a path or anchor.
Preserve an anchor or coordinate reference repair when a consumer is outside
this work's editing scope. Unresolved required references block affected completion.

For a split or merge, link successor definitions and update affected trace.
Where current work depends on a predecessor, identify its version and former path.
Keep reviewed or signed artifacts unchanged.
Link them to the current owner where needed and assess whether their evidence applies.
Version history holds earlier content; create no duplicate owner or archive
merely to preserve a former path.

**Existing and external identities.** Existing numbered filenames and IDs remain valid.
Preserve them and their meanings when revising their content.
New documents use semantic paths; do not continue a counter merely because older
records are numbered. Existing references may retain their established ID labels.
Preserve externally required identities. Resolve any conflicting external numbering
requirement before affected work; do not introduce a harness sequence.
Keep external tracker keys with resolvable links under
[external work trackers](#external-work-trackers).
Do not add a harness sequence or derive a new document ID from a tracker key.
A requested migration of existing records has its own scope and reference checks.

## Document paths

Name new ordinary Markdown documents by their enduring subject, without a
sequential prefix: `<document-root>/<area-or-purpose>/<subject>.md`.
For example, use `project-docs/user/user-search.md` for a search requirement
and `project-docs/user/user-search-design.md` for its separately managed design.
A root overview can be `project-docs/overview.md`.

Use lowercase ASCII words separated by hyphens for new ordinary names.
There is no fixed word count. Digits may express a genuine subject, such as
`oauth2-login.md`; do not use them as allocation counters.
Leave mutable versions, statuses and dates out of ordinary names.
Write the full title, in any language, in the body.
[Required-name files](#required-name-exceptions) and existing names retain their formats.

Distinguish independently managed outputs by subject and role.
Use a role suffix, subfolder or specific output name when needed, such as
`user-search-plan.md` or `user-search-api-task.md`.
Do not combine independently managed requirements, designs, tasks or verification
merely because their paths share a feature name.
Apply [item boundaries](#independent-items-and-supporting-detail), including
[compact documentation](#minimum-documentation-for-a-small-change).

<a id="folders-by-document-kind"></a>

### Folders by area and purpose

Group new documents by functional area or feature when no established layout exists.
Record the document root and folder conventions in the project overview.
Shared definitions have one designated owning location.
Existing kind-based folders remain valid; do not migrate them automatically.

| Purpose | Illustrative path beneath `project-docs/` |
|---|---|
| Project overview | `overview.md` |
| Area overview | `user/overview.md` |
| Requirement | `user/user-search.md` |
| Separately managed acceptance criteria | `user/user-search-acceptance.md` |
| Design | `user/user-search-design.md` |
| API contract | `user/user-search-api.md` |
| Screen specification | `user/user-search-screen.md` |
| Plan | `user/user-search-plan.md` |
| Separately managed tasks | `user/user-search-api-task.md`, `user/user-search-ui-task.md` |
| Verification | `user/user-search-verification.md` |
| Open question | `user/search-permission-question.md` |
| Shared architecture | `shared/access-control-design.md` |
| Research, guides, reviews and reports | An enduring subject name in its owning area or a recorded purpose folder |

These paths illustrate placement, not required deliverables or one file per role.
Create files only when their independently managed outputs are needed.
Another requirement or task needs its own meaningful subject or output name,
not an incremented suffix. Feature relationships may span folders through links.

Choose and record a new area or purpose folder within authorized work when needed.
The agent makes routine placement choices without asking the user to classify each document.
Add deeper folders only when navigation needs them.
Do not create empty folders, placeholders or duplicate feature indexes.
Shared conventions belong in the overview; detailed content stays with its owner.

<a id="allocation-and-validation-reuse"></a>

## Path checks and verification reuse

Before creating a document, inspect the overview and search existing owning paths
and subjects. Check relevant version history when a proposed path may have prior use.
Reuse an existing definition when it is the same item.
Choose a distinct meaningful path for a different item.
Do not maintain next-number counters, reserved ranges or document-ID dictionaries
for new work.

Use a checked baseline and subsequent changes to scope later checks.
For new or moved documents, check path uniqueness, case, ownership and affected links
against current records and relevant history.
Searching one folder cannot establish that another folder has no owner for the same item.
Record check scope, version, result and limits under
[verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification).
Create no separate path registry; use the overview, owning files and version history.

With concurrent writers, agree actual paths and logical outputs under the
[collaboration basis](COLLABORATION.md#collaboration-basis).
Area ownership does not permit duplicating a shared definition.
Check current shared work before choosing a path.
A clean local checkout cannot prove another writer has not chosen it.

<a id="branch-allocation-and-collision-repair"></a>

### Branch path collisions and integration

Before integrating isolated branches, compare new paths, subjects and owner links
against the current integration branch and other changes being integrated.
Writers may create the same path for different outputs, or different paths for one output.
Resolve both cases with the affected owners.

For the same item, reconcile content into one owner and repair references.
For different items, choose distinct subject or role names and repair references.
Never overwrite another writer's content or append a sequence to avoid deciding ownership.

Keep source versions and former paths where earlier decisions or evidence still rely on them.
Preserve published history and reviewed artifacts.
Repair required external references through their authorized owner.
Unresolved ownership or ambiguous required references block affected integration.

## Independent items and supporting detail

Requirements are the primary basis for separating product scope. Establish
what must be satisfied, then organize the design, work and verification needed
to satisfy it. Each independently managed requirement owns one canonical file;
other independently managed items retain their appropriate types and owning
files under [document paths](#document-paths).

### Requirement boundaries

A requirement states an intended behavior, outcome or constraint.
Create a separate requirement for a meaningful commitment needing its own scope
and fulfillment assessment. Search and the export of search
results are two such commitments. Requirements may depend on one another;
technical independence is not required. A shared security or performance
constraint can also be a requirement when it has its own scope and fulfillment
criteria.

Keep the conditions, rationale, examples, parent-specific acceptance criteria
and check methods that explain one requirement with that requirement. A
separately executable assertion or test does not alone make a new requirement.
Stages, algorithms, code files and test commands are not requirement boundaries.
When an acceptance criterion actually needs its own acceptance disposition,
use a separate acceptance-criterion document linked to its requirement.
Do not relabel that criterion as a new requirement.

Before creating a requirement, check existing requirements. A correction that
restores an already specified behavior references the existing requirement;
adding a test for it does not create another requirement.
Revise the same requirement at its existing path when it remains the same item; version history keeps the prior
version. A new commitment or an actual split/merge follows the existing
[identity rules](#item-identity). Identity does not authorize a material
change to the requirement or acceptance criteria.

### Related work and supporting detail

Designs, plans, tasks, changes and verification reference the requirements
they cover. These relationships may be many-to-many. A shared design or check
has one owning definition linked to all relevant requirements. Preserve separate
requirement, design, plan, task and verification files under
[document organization](#document-organization), reusing shared definitions
without creating a copy for every requirement.

Give related work a separate owning file when the actual work needs any of these:

- a separately assigned or delivered output;
- its own completion/decision status;
- a shared definition maintained across requirements.

Keep implementation steps and supporting explanations in their owning item.
Merely being able to assign a step to someone else, run a test separately or
link a paragraph is insufficient. Small size or a common owner does not remove
a real separate work boundary.

Expected behavior and acceptance criteria belong to the requirement. Planned
checks and failures that still stand belong to the verification document
referencing it; passed results go to the commit message. Do not duplicate
authoritative definitions or evidence. A failed check is a result, not by
itself a new tracked item.

Discovery, research, project overviews and other work can precede or support
requirements. Use the appropriate document type and actual objective/source
without inventing a requirement or approval to fill a link. Link requirements when they
are established. Decisions, issues and other records retain their own types
when separately managed; requirements do not replace every other identity.

| Situation | Required treatment |
|---|---|
| Login and search have distinct requirements, even with the same owner | Separate requirement files; the overview groups them by feature. |
| Search results must be exportable as a file in addition to being searchable | A separate export requirement linked to the search requirement and relevant work. |
| An empty search result must display a count of zero | A condition/acceptance detail in the search requirement, unless separately managed acceptance requires an acceptance-criterion item. |
| One requirement has input examples, rationale and parent-specific acceptance details | Sections of that requirement; no new file or identity for each explanation. |
| A fix restores the specified search count, or a regression test checks it | Reference the existing search requirement from the change/work and checks; no new requirement solely for the fix or test. |
| An acceptance criterion is separately tracked with its own disposition | Its own acceptance-criterion file, linked to the parent requirement. |
| A backend plan includes tasks managed as separate outputs | Each task has its own file under the project path convention; the plan contains links and sequence/dependency information. |
| Several plans cover the same requirement | Reference the same owning requirement file rather than copy its definition. |
| A small correction restores an existing requirement | Reuse the requirement's linked files and put changed detail in its owners. Keep change trace in the work note only while the change is in progress; the commit message carries the results. |
| A bounded correction has no management definitions to reuse | Under the conditions below, one work document can own the correction's missing definitions and serve as its overview. |

Ordinary prose, navigation and explanatory headings need no separate item identity.
Do not use compact planning or the word "metadata" to conceal
separately managed items inside a single growing document.

### Minimum documentation for a small change

For [compact work](DEVELOPMENT_METHOD.md#choosing-planning-depth), use the
existing owning work document and link applicable requirements and contracts.
Update another owning definition only when its facts or instructions change.

Missing local approach, plan and verification definitions may live in sections
of that work document. Keep planned checks separate from failures that still
stand; passing results go to the commit message.
Do not create separate design, plan or verification files solely to fill those roles.
An independently managed requirement or shared definition still has its own
owner under [item boundaries](#independent-items-and-supporting-detail).
Existing owners and required contractual files retain their roles.

The work note holds what the
[compact procedure](DEVELOPMENT_METHOD.md#choosing-planning-depth) records
before and during the work. Delete it once the work is done, under
[current state only](DEVELOPMENT_METHOD.md#current-state-only). Link existing
verification records instead of copying them. Task declarations still apply;
references to existing instructions satisfy them.

Reuse the overview and its folder/path conventions where they exist.
If no management records exist to reuse, one work document may also serve as
the overview when all of these hold:

- One writer handles one compact work item.
- No additional independently managed requirement, shared definition or output
  needs its own owner.
- No project or contractual rule requires a separate overview.

Use the work item's canonical path; no additional overview file is needed.
Keep its bounded objective, baseline and analysis limits near the start. Record only the document root, path conventions and ownership context
actually needed. Hold known check commands and environments here only while the
project has no root instruction file to own them.
The normal identity, path and validation rules still apply.
Entry links point to this document;
its owned sections satisfy overview references without duplicating task state.
When the work is done, delete its work sections.
The project context stays as the overview.

When authorized work expands beyond these conditions, establish a separate
overview before starting the affected work. Transfer current shared context,
conventions and shared ownership there, and link the original work item. Replace
live sections with links.
Preserve the work item's path unless the reorganization covers its move.
Do not combine existing owners or accumulate
unrelated work to keep a single file. If scope grows, establish only the new
independent owners or detailed planning that the change requires before the
affected work starts. Add scope to finished work under
[verification and completion](WORKFLOW.md#verification-and-completion).

## Required-name exceptions

Keep an exact filename or location when a consuming tool, project contract or
repository entry convention requires it. Examples include `SKILL.md` and a
repository landing `README.md`. The actual path is the document's identity;
no substitute ID or duplicate ordinary-name file is required.

For a project deliverable outside ordinary naming or placement conventions,
link its actual path and consumer/contract reason from the overview or index.
Instruction files and harness guidance follow [identity scope](#identity-scope)
and need no exception entry. Identity, trace, scope and verification still apply.

For example, a shipped skill may remain at `skills/report/SKILL.md`.
Link its path and consumer requirement; create no second file under the document root.
Keep independently managed definitions in their owners.
The agent preserves required names within authorized work without another approval ceremony.

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
requires and, as instruction files, need no exception entry.

## Document validation

Before completing document work, apply these checks to the requested stage.
Use [path checks](#path-checks-and-verification-reuse) and
[verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification) to determine
the affected scope and reusable evidence.

| Check | Evidence to verify |
|---|---|
| Coverage and ownership | Each independently managed item has one owning document under the boundary rules. Supporting detail stays with its owner. Work links covered requirements or pre-requirement sources. Compact work keeps planned checks apart from standing failures. Overviews link owners. |
| Path identity | Canonical paths and referenced fragments resolve unambiguously. No case-only path collisions or duplicate owners exist. New paths do not repurpose unrelated retired items. Apply branch collision checks before integration. |
| Project conventions | New ordinary names use semantic paths under the recorded root and area/purpose conventions. Check role distinctions, tracked case, stable anchors and repaired references after moves. New work has no sequential IDs, counters or reserved ranges. |
| Existing and required-name files | Preserve established names, IDs and externally required identities. Index required-name deliverables by actual path and consumer constraint. Create no duplicate ordinary-name copies. |
| Area overviews and trackers | Root and area entries resolve and hold only their owned content. Tracker-owned information has no parallel Markdown record. Tracker references carry resolvable keys/links. Record relied-on state with its decision, or in the commit message for completion or handoff. |
| Links and trace | Overview and item/section links reach intended owners. Requirements, design, work and evidence cover the requested stage. No required link points to a removed path or anchor. Version-dependent references identify source version and path. Resolution alone does not establish meaning or coverage. |
| Current instructions and navigation | Apply [current-state updates](WORKFLOW.md#updating-current-work-state) to affected states, execution modes, prerequisites, next actions and summaries. Remove superseded instructions. Check the [project entry route](#project-instruction-files) for adoption or entry-file changes. |
| Planning detail and omissions | Apply selected [planning depth](DEVELOPMENT_METHOD.md#choosing-planning-depth): source coverage, executable work, scenarios, concrete verification and honest unknown dispositions. Valid paths and links alone do not establish an adequate plan. |
| Open-item trace | Verify affected open items' [content](#open-items), owning references and [lifecycle disposition](WORKFLOW.md#open-item-lifecycle). Delete closed items only after incorporating answers and reassessing dependents. |
| Scope and current state | No unauthorized migration of existing records. Keep only decisions in force, blocking questions, standing failures and current positions under [current state only](DEVELOPMENT_METHOD.md#current-state-only). Unrun checks are not success. |
| Document quality | Content agrees with inputs. Markdown structure and applicable format/contract requirements hold. |

The [document checker](CONTEXT_EFFICIENCY.md#document-checker) can supply link
and anchor resolution checks. Path conventions, unique logical ownership,
retired-path reuse, trace meaning and content need review beyond that tool.
Required-name constraints replace ordinary naming checks only to their stated extent.

## Open items

An open item is an unresolved question, decision, prerequisite, contradiction
or finding that needs follow-up to establish scope, readiness or completion.
It can arise at any stage. Routine work already defined by a task does not
need a second issue merely because it is unfinished. A failed check stays
in its owning verification record, linked from the work. The failed check's
unresolved impact still needs the follow-up information below when work
continues or is handed off.

Some questions are answered and checked within the same work session, with no
remaining follow-up or independent management boundary. Put its answer into
the affected definition or check, and give the authoritative source with its
relevant version in the commit message. No note, separate open item, owner/timing
fields or transition log is required for that completed clarification. This
shortcut does not supply human decisions or product verification: actual
authority, evidence and material-change rules still apply. If the answer leaves
a dependency, unresolved impact or handoff, use the follow-up content below.

Use the existing [item boundaries](#independent-items-and-supporting-detail).
Keep a parent-specific question in the owning requirement, design, plan or
task when it needs no separate management boundary. A separately
assigned investigation, decision or shared issue with its own completion status
owns a separate semantic path, such as `user/search-permission-question.md`.
State whether it is a question, risk or other finding in its body. Retain
existing identities and link actual decisions and resolution tasks without copying them. Moving work between plans does not create a new identity for the same
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
| Answer | For a RESOLVED item, the checked answer with its source and version, until they are in the owning definitions. |
| Deferral | For a deferred item, the reason, authority and retained obligation. |

Once its answer is in the owning definitions, the item is closed and deleted
under the [open-item lifecycle](WORKFLOW.md#open-item-lifecycle).
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

The tracker key and its resolvable link identify an item the tracker owns.
The tracker supplies any issue number; do not add a harness sequence.
Tracker identity does not replace a Markdown document's canonical path.

Some such items need a detailed Markdown definition, such as task implementation
detail. That document uses its own semantic path and links the tracker key.
The tracker owns status and assignment; the document owns the detailed definition.

Requirements, acceptance criteria, design and decisions stay in versioned
Markdown, and passed-check evidence in commit messages. Where the project
already keeps them in a system with attributable version history, reference
the item and its version there instead.

Where a decision relies on tracker state, record the key and the observed state
with that decision, with the observed state's date or version. A completion
claim or handoff that relies on it states them in the commit message. That
records what was relied on; it is not a mirror to maintain.

These are external effects, and they need matching authorization under
[Security](SECURITY.md#authenticated-tools-and-protected-values):

- operations beyond the recorded agent operations;
- changes to tracker workflows, permissions or automation;
- messages that reach people outside the designated use.

Where the tracker is unavailable, note pending updates in the current work note
and apply them when access returns. That note is not the authoritative status.

Changing or ending a designation is an owner decision. Preserve existing items
and links, and record where each kind of information is owned from then on.
