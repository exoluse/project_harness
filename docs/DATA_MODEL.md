# Project Information Model

This is the required detailed standard for project document organization,
identity, paths, exceptions and validation, designated by
[AGENTS.md](../AGENTS.md#document-organization). Keep definitions here; other
guidance links them and may show brief summaries or examples.
The [management format policy](../AGENTS.md#management-document-format)
governs Markdown, existing records and tool-required formats.

| Need | Governing section |
|---|---|
| Harness guidance or project deliverable | [ID scope](#id-scope) |
| Overview and relationships | [Document organization](#document-organization) |
| Plan/task responsibilities | [Plans and tasks](#plans-and-tasks) |
| Identity, types and numbering | [Item IDs](#item-ids) |
| Canonical filename and folder mapping | [Document paths](#document-paths) |
| Separate item or supporting detail | [Item boundaries](#independent-items-and-supporting-detail) |
| Consumer-required name/location | [Required-name exceptions](#required-name-exceptions) |
| Completion checks | [Document validation](#document-validation) |
| Reuse of checked allocations | [Allocation reuse](#allocation-and-validation-reuse) |

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
| Source/intake | Origin, version, analysis scope, ownership and reliability/limitations. |
| Requirements | Intended outcomes, constraints, acceptance criteria and material source trace. |
| Design | Components, interfaces/data, alternatives, requirement coverage and open risks. |
| Plan | Goal, scope, source-to-work/check coverage, linked implementation detail, dependencies, ordered task links, overall completion criteria, open-item dispositions and actual decision reference. |
| Task/work item | Concrete output, owner, affected paths/logical resources, plan/input links, prerequisites, ordered actions, applicable implementation detail, status and concrete completion checks. |
| Decision | Concrete scope/version, actual owner request or response/source, bounds and conditions. |
| Change trace | Request, before/after, impact, affected work, decision and verification. |
| Verification | Subject/version, method/environment, expected/observed result, artifacts and limits. |
| Release/handoff | Contributions, versions, decisions, current evidence, unfinished obligations and next owner/action. |

Within a small coherent change, tightly coupled stage notes can be sections
in its document. Independently managed items use separate files in their type
folders. A plan may organize nested task links or reference several plans;
no single-active-plan field is required.

## Document organization

Use a project overview for shared context and navigation, with documents for
independently scoped items stored in suitable classification folders. The agent
chooses folder names, nesting and the document root for the project's content,
workflow and existing conventions. Feature/work units remain logical groups
in the overview and relationships between items regardless of physical layout.
A project with several
such units must not default to a single accumulating file for each document type.
For a small project with only one coherent unit, overview and detail may remain
in one document until a split criterion applies.

The overview holds the objective, shared constraints, shared requirements and
architecture (or links to them), baseline, current summary and an index of units.
It also states the document/item-ID convention, including agent-selected
extensions and any allocation ownership.
Each index entry links to the unit's documents and states its scope, stage/status
and material dependencies. Keep detailed decisions and evidence in their owning
documents and link to them instead of maintaining duplicate accounts.

Use requirements as the primary basis for separating product scope under the
[item-boundary rules](#independent-items-and-supporting-detail). Connect design,
planned work and verification to the requirements they cover. Keep tightly
coupled stage notes in the owning item and use links for separately managed
outputs. Length alone does not create a new item; use sections and navigation
when accumulated supporting detail obscures scope, decisions or evidence.
Record the chosen boundaries and rationale briefly in the overview or work note.

The following example applies [document paths](#document-paths). Folder names
and nesting are illustrative; the IDs are not allocations in this repository.
Create only documents needed for the requested stage:

```text
project-docs/
  overview/
    DOC-00001.md                   # Shared context and feature/work index
  requirements/
    REQ-00001.md                   # Sign-in requirement
    REQ-00002.md                   # Search requirement
  designs/
    DES-00001.md                   # Shared architecture
    DES-00002.md                   # Sign-in design
  backend-plans/
    API-00001.md
  screen-plans/
    SCR-00001.md
  tasks/
    TASK-API-00001.md
    TASK-SCR-00001.md
  verifications/
    VER-00001.md
  decisions/
    DEC-00001.md
  changes/
    CHG-00001.md                   # Small change with tightly coupled notes
  handoffs/
    HANDOFF-00001.md
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

## Plans and tasks

A plan organizes an outcome across work items. It defines the goal, included
and excluded scope, input requirements/design, dependencies, feasible task order
and overall completion criteria. Backend `API`, screen `SCR` and general `PLAN`
documents are examples of plans; they link to the owning task files.

A task is a concrete output that the actual work assigns and completes as a
separate unit. Implementation steps serving that output may remain in its file.
Its owning `TASK-<AREA>` file records the expected output, accountable writer,
affected paths and logical resources, parent plan/input links, prerequisites,
current status, ordered actions and concrete completion checks. Supply or link
the applicable implementation details and verification scenarios required by
the [detailed planning procedure](DEVELOPMENT_METHOD.md#detailed-planning-procedure).
Before assignment is known, state that
it is unassigned; resolve ownership before concurrent execution. These are
content requirements, not mandatory headings or front matter.

Plans and tasks reference the requirements they cover. One requirement can
need several tasks, and one task can serve several requirements. Create a
separate plan/task file when its outcome, assignment or completion needs that
management boundary; do not generate a full set of stage files for every REQ.
Use the [boundary criteria](#independent-items-and-supporting-detail) for small
changes, supporting detail and work before requirements are established.

Keep task definitions and detailed results in their owning files. Plans contain
links, ordering and useful progress summaries; update those summaries from the
tasks. A task shared by several plans retains one ID, owning file and writer.
Completion of the planned outcome is assessed against its scope and criteria
using task outcomes and applicable combined verification. Planning itself ends
when the plan and task definitions satisfy the
[planning completion checks](DEVELOPMENT_METHOD.md#planning-completion-checks);
it does not require those tasks to have executed. Planning-only work records
intended checks without claiming execution.

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

## Item IDs

Apply identity rules to every Markdown deliverable within the
[ID scope](#id-scope), whatever its subject: specifications, research,
guides, meeting notes, reviews, reports, handoffs or kinds not listed here.
Assign the document an ID appropriate to its purpose. A document representing
one primary item uses that item's ID; a collection can use a document ID such
as `DOC-00001`. Choose the identity before creating the file and use it in
the index; [document paths](#document-paths) defines filename/body placement.
An overview itself also has an identity. A document ID is not a substitute for
the identities of its independently tracked contents.

Use the [item-boundary rules](#independent-items-and-supporting-detail) to
identify independently tracked contents. Apply IDs to new traceable items
added to existing Markdown as well. Requirements, acceptance criteria, designs,
plans, tasks, decisions, findings, changes, risks, issues and verification are
examples, not an exhaustive list.

Use semantic uppercase type prefixes and five-digit serials, starting at
`00001`. Reuse established project conventions and the applicable examples
below. For an unlisted document or item kind, choose and document an appropriate
prefix autonomously; user approval of each prefix or item boundary is not
required. The table is a starting vocabulary, not a closed set of allowed types.
These syntax examples do not allocate real project IDs.

| Item | ID example | Meaning |
|---|---|---|
| Document or overview collecting items | `DOC-00001` | A document identity when no primary item supplies it. |
| Requirement | `REQ-00001` | Intended outcome or constraint. |
| Independent acceptance criterion | `AC-00001` | A separately tracked checkable condition. |
| Design item | `DES-00001` | A component, interface, data or other design specification. |
| Backend plan | `API-00001` | A backend implementation/work plan, not an API endpoint identifier. |
| Screen plan | `SCR-00001` | A plan for an individual screen. |
| General or cross-cutting plan | `PLAN-00001` | Work not best classified as a backend or screen plan. |
| Task/work item | `TASK-API-00001`, `TASK-SCR-00001` | A task in the named work area. |
| Decision | `DEC-00001` | An attributable actual decision. |
| Change | `CHG-00001` | A tracked change and its impact. |
| Risk or open issue | `RISK-00001`, `ISSUE-00001` | An independently tracked uncertainty or unresolved issue. |
| Verification item | `VER-00001` | A check with subject, criteria and explicit execution status/results. |

For example, a research report can use an agent-selected `RES` document prefix
and `FIND` for independently referenced findings; meeting notes can use `MTG`
with existing `DEC` and `TASK` types for decisions and actions. A guide can use
`GUIDE` and identify independently maintained procedures as appropriate. Choose
these based on the actual content and existing conventions, not by creating
all these record types in advance. Record each added prefix's meaning and
allocation scope in the overview so subsequent work uses it consistently.

In `TASK-<AREA>-00001`, replace `<AREA>` (the user's `XXX`) with a registered
uppercase work-area token: `API`, `SCR`, `DOC` for documentation, or `GEN` for
general work. Additional uppercase type/area tokens can be recorded in the
overview when needed; do not invent a new spelling for an existing type.
The serial is independent of the parent plan: `TASK-API-00003` may belong to
`API-00002`. Record the actual parent plan ID and link, plus the requirements,
design and dependencies it covers. Shared tasks may link to several plans.

Interpret an ID using its complete registered prefix and final five-digit
serial; do not infer meaning from an isolated token. The following are syntax
examples, not allocations:

| ID | Complete prefix | Type and meaning |
|---|---|---|
| `DOC-00001` | `DOC` | Overview/collection document; `DOC` is the document-type prefix. |
| `TASK-DOC-00001` | `TASK-DOC` | Task in the documentation area; `TASK` is the type and `DOC` is the area. |
| `API-00001` | `API` | Backend plan, not an endpoint or route. |
| `TASK-API-00001` | `TASK-API` | Backend task; its parent plan is identified by an explicit link. |

An endpoint is identified in its specification by its actual method/path or
the project's endpoint convention, for example `GET /orders`; it is not assigned
an `API` plan ID merely because it is an API. Keep the established ID vocabulary
and register a distinct meaningful type for a separately tracked endpoint
specification if needed. Token reuse in different positions does not merge
allocation counters or justify renaming existing IDs.

Serial allocation is project-wide per complete prefix. Two feature files must
not both define `REQ-00001`; two API plans must not each restart their tasks at
`TASK-API-00001`. `TASK-API-00001` and `TASK-SCR-00001` are distinct IDs. Search
existing definitions and retained/retired IDs before choosing the next unused
serial, reusing a verified baseline under the rules below. Concurrent writers
reserve non-overlapping ranges or prefixes in shared
Markdown notes; no separate JSON registry is required.

Put the ID visibly in the owning heading or table row. Provide a stable anchor,
for example an ID-only heading `### REQ-00001` with a descriptive title in the
body, or an explicit anchor for an identified table row. References use the ID
as link text and resolve to that item's anchor, even within one file.

Keep IDs unchanged when content is revised, renamed, reordered or moved; update
links after moves. Never reuse deleted/retired IDs. For a split or merge, record
the old item's disposition and links to the new items without overwriting its
decision or evidence history. Identity alone does not identify a reviewed
version, prove approval or establish a passed check.

Existing IDs and historical records remain valid; use links to older material
without bulk retroactive relabeling. A requested migration has its own scope.
Externally required document formats remain binding; resolve a real conflict
rather than silently omitting identity requirements.

## Document paths

Except for [required-name files](#required-name-exceptions), every new project
Markdown document uses `<document-root>/<classification-path>/<DOCUMENT-ID>.md`.
The entire filename stem exactly matches the owning document ID, including
uppercase type tokens and the five-digit serial. Show the document ID near the
top of the body. Titles and descriptions belong in the body and overview;
do not append a title, date or description to the filename.
A body ID or ID-bearing directory alone does not satisfy this rule.
Use `overview/DOC-00001.md`, not `overview.md` or `DOC-00001-overview.md`.
The rule covers all document kinds, including overviews, shared specifications,
research, reports, changes and handoffs.

The agent chooses and records the root and classification-to-folder mapping
in the project overview, reusing project conventions. Examples include `REQ`
to `requirements`, `API` to `backend-plans`, `SCR` to `screen-plans` and
`TASK-<AREA>` to `tasks`. These are not reserved names: `specs/requirements`,
`plans/backend` or `work-items` are also possible. Select and record suitable
folders for new kinds or changed context without asking the user to classify
each one. Reuse mappings consistently within their stated scope.

Folder changes preserve IDs and repair overview/item links; they do not
authorize historical-record migration. Do not create empty type folders or
placeholder files before they are needed. Group feature relationships through
the overview and owning documents, independently of the physical layout.
For example, `backend-plans/API-00001.md` links to its owning task files at
`tasks/TASK-API-00001.md` and other applicable paths.

## Allocation and validation reuse

Use an `ID allocation` section (or its local-language equivalent) in the actual
project overview as the default shared allocation record. If the team already
uses another shared Markdown location, link its exact file/section from the
overview and maintain the allocation there only. Folder names stay contextual;
writers must be able to discover one authoritative allocation location.

Use a compact Markdown table with the following minimum information, reusing
shared baseline notes for rows checked together:

| Field | Required content |
|---|---|
| Complete prefix | Registered type/area meaning, such as `TASK-DOC`. |
| Verified basis | Commit/version and scope checked, including definitions, retained/retired IDs and outstanding reservations; actual check result and any limits. A version alone is not proof of verification. |
| Allocated range | Inclusive serial bounds assigned within that prefix. |
| Owner | Writer responsible for consuming the range; identify any agreed transfer. |
| Disposition | Used serials or owning-document links, retired serials, and remaining reserved/available numbers. Record gaps explicitly rather than assuming everything below the largest number was used. |

These are required contents, not fixed column spellings or a new machine schema.
For example, a hypothetical `TASK-DOC` range `00001` through `00020` owned by
writer A may state: used `00001` and `00003`, retired `00002`, remaining
`00004` through `00020` reserved for A. Its row must also link the actual checked
basis. This example does not allocate IDs in this harness repository.

Establish the basis by inspecting project-wide definitions, retained allocation
history and reservations before allocating. When creating the first project
overview, check and assign its own ID as part of the initial allocation and
record that basis in the new overview; no pre-existing registry is necessary.
A single writer uses the same concise section and may reserve only the numbers
currently needed. Harness guidance outside the [ID scope](#id-scope) needs no
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
Broaden the scan when baseline coverage is missing or unreliable, allocation
conflicts appear, or changes to conventions/validation rules affect prior
results. Preserve project-wide uniqueness and never reuse retired IDs. This
changes how evidence is obtained, not the identity or filename requirements.
See [verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification).

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
has one owning definition linked to all relevant REQs. Do not create one copy
or a complete set of stage documents per requirement.

Give related work a separate ID/file when the actual work needs a separately
assigned or delivered output, its own completion/decision status, or a shared
definition maintained across requirements. Keep implementation steps and
supporting explanations in their owning item. Merely being able to assign a
step to someone else, run a test separately or link a paragraph is insufficient.
Small size or a common owner does not remove a real separate work boundary.

Expected behavior and acceptance criteria belong to the requirement; actual
check results may remain in the work document or a separately managed
verification document referencing it. Do not duplicate authoritative definitions
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
| A backend plan includes tasks managed as separate outputs | Each task has a `TASK-<AREA>` file; the plan contains links and sequence/dependency information. |
| Several plans cover the same requirement | Reference the same owning requirement file rather than copy its definition. |
| A small change records its source, scope rationale and observed check result | These may be metadata/stage notes of that change; independently managed requirements/tasks still get separate files. |

Ordinary prose, navigation and explanatory headings need no independent ID.
Do not use the small-change exception or the word "metadata" to conceal
separately managed items inside a single growing document.

### Minimum documentation for a small change

For one bounded correction with one set of completion criteria, keep the
expected correction, design rationale, work steps and check results in the
owning change document and reference the existing requirement. A development
stage, an implementation step or a test command does not by itself require a
separate `REQ`, `DES`, `PLAN`, `TASK` or `VER` file. Link existing requirements
and other owning documents instead of
redefining them. Apply any contractually required separate deliverables.

For example, correcting the displayed count for an empty search result can
use an existing project overview plus `changes/CHG-00001.md`. This is an
illustration, not an allocated ID, actual decision or verification result.
Choose the real unused ID and folder using the project's existing conventions.
The change document can contain the following sections:

| Section | Minimum useful content for this example |
|---|---|
| Source and scope | Actual fix request/source, input revision, expected empty-result count, affected component and exclusions; link the existing search REQ, or identify the actual expected-behavior source if no requirement is yet recorded. |
| Approach and readiness | Cause and chosen correction, relevant alternatives/risks, responsible writer, ready dependencies and confirmation that the request covers the edits and checks. |
| Work steps | Inspect the count calculation, make the covered correction and check empty and non-empty results; record progress here. |
| Verification | Candidate version, method/environment, expected and observed counts, original evidence links where available, failures and unrun checks. |
| Completion | Result against the stated criterion, remaining limits and applicable delivery/next action. |

The overview links this change and updates its summary and ID allocation in
their existing sections. No separate decision, plan, task or verification
document is needed solely to repeat those sections. A project with only one
coherent unit may use the existing combined overview/detail option under
[document organization](#document-organization), subject to the same identity
and boundary rules. This example adds no new exemption from ID allocation.

Split out a new requirement when the requested result adds a separate
commitment, such as exporting search results. Split related work only for an
actual separate assignment, delivery, decision or completion boundary, such
as an independently assigned backend change or a separately tracked acceptance
criterion. A regression check used only to establish the count fix's completion
remains supporting detail, even though it can be run
independently. Preserve existing owners, IDs and history when linking or
splitting; this guidance does not authorize consolidating existing records.

## Required-name exceptions

This section applies to project deliverables within the [ID scope](#id-scope).
The harness's own guidance is excluded there and needs no exception-ID mapping.

Keep an exact filename/location when a consuming tool, project contract or
repository entry convention requires it. Examples include a tool's `AGENTS.md`,
`CLAUDE.md` or `SKILL.md`, and a repository landing `README.md`. These files are
exceptions to the ID-only basename and classification-path requirements, not
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
`requirements/REQ-00001.md` under the chosen document root. The agent assesses
and documents the exception within the already authorized task; preserving a
required name does not need an additional approval ceremony.

## Document validation

Before completing document work, apply these checks to the requested stage.
Use [allocation reuse](#allocation-and-validation-reuse) and
[verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification) to determine
the affected scope and reusable evidence.

| Check | Evidence to verify |
|---|---|
| Coverage and ownership | Determine ID scope first. Each in-scope document and independent item has an ID and one owning definition; requirement boundaries describe distinct commitments, supporting conditions remain with their requirement, and separately managed work references the REQs it covers. Check source/objective links for work before requirements are established. Overviews reference owners; harness guidance needs no identity or path-mapping checks. |
| Identity and allocation | New definitions are unique project-wide and do not collide with retained/retired IDs or reservations; distinguish definitions, references and illustrative examples. |
| Ordinary paths | Each new file matches the recorded folder mapping and the filename/body identity specified in [Document paths](#document-paths). |
| Required-name files | Verify the actual consumer name/location/format, index ID/path/reason mapping, and body/index ID agreement when the body permits an ID. Otherwise verify the stated body-format restriction. |
| Links and trace | Overview entries and item/anchor links resolve to the intended owners; requirements, design, planned work and actual evidence cover the requested stage. |
| Planning detail and omissions | For planning deliverables, apply the [planning completion checks](DEVELOPMENT_METHOD.md#planning-completion-checks): original-source coverage, detailed executable work, scenario/integration coverage, concrete verification and honest unknown dispositions. Valid IDs and links alone do not establish an adequate plan. |
| Scope and history | No unauthorized migration or historical relabeling; IDs and prior decision/evidence history are preserved, and unrun verification is not reported as success. |
| Document quality | Content is consistent with its inputs, Markdown structure is valid and applicable format/contract requirements are met. |

Required-name checks replace ordinary path/name/body checks only to the extent
required by the documented consumer constraint; identity, links and other checks
remain applicable. Do not treat every existing descriptive filename as a new
exception. Existing records keep their names and applicable prior evidence.

## Trace and baselines

Use commits, snapshots or document versions to identify the basis of important
claims and decisions. Preserve material source-to-requirement-to-design-to-work
relationships without requiring every optional record type.

When recovering documents from code, label observation, inference, confirmed
intent and uncertainty. Link observations to the inspected revision and source
locations. Keep current implementation and proposed target separate.

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
