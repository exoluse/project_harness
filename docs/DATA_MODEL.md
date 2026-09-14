# Project Information Model

Project information must be reviewable and attributable. Write all new harness
management documents as Markdown (`.md`) with stable IDs for traceable items;
use suitable classification folders and exact `<ID>.md` filenames, without
fixed schemas or front matter. Follow
[AGENTS.md](../AGENTS.md#management-document-format) and use a project overview
and feature/work documents as described below. Use prose, tables, checklists
and links instead of creating JSON records or parallel structured copies of
management documents.

Preserve existing non-Markdown records and reference them without automatic
conversion or deletion. Product files such as `package.json`, original evidence
such as logs or test reports, and optional legacy CLI internal files retain their
required formats. Summarize verification in Markdown and link to those original
artifacts. Contractual delivery formats and external controls remain binding;
resolve actual conflicts before the affected delivery.

## Suggested information

| Information | Minimum useful content |
|---|---|
| Project note | Objective, current stage, baseline, decisions, progress, blockers and next action. |
| Source/intake | Origin, version, analysis scope, ownership and reliability/limitations. |
| Requirements | Intended outcomes, constraints, acceptance criteria and material source trace. |
| Design | Components, interfaces/data, alternatives, requirement coverage and open risks. |
| Plan | Goal, scope, dependencies, ordered task links, overall completion criteria and actual decision reference. |
| Task/work item | Concrete output, owner, affected paths/logical resources, plan/input links, prerequisites, status and completion checks. |
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

Split a unit into separate documents when any of these boundaries needs
independent review or tracking:

- A feature or change has its own outcome, scope and acceptance criteria.
- Design decisions or interfaces need a distinct review and revision history.
- Work has a separate owner, dependency chain, verification or delivery cycle.
- Accumulated detail makes the current scope, decision or evidence hard to find.

Choose independent item boundaries first and store their documents by type.
A small fix can use one change document with tightly coupled stage notes;
separately managed requirements or tasks still have their own linked files.
A larger feature connects its requirements, designs, plans, tasks and evidence
through the overview and item links. File count and line count are not completion
criteria; do not create one file per checklist item or empty stage templates.
Briefly record the chosen boundaries and rationale in the overview or work note.

The rule is classification by document nature plus exact `<ID>.md` filenames.
The root `project-docs`, folder names and nesting below are examples, not a
fixed directory schema. Choose them for the project and record the mapping.
These example IDs are not allocations in this repository. Create only files
for requested stages:

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

A task is a concrete unit that can be assigned and completed independently.
Its owning `TASK-<AREA>` file records the expected output, accountable writer,
affected paths and logical resources, parent plan/input links, prerequisites,
current status and completion checks. Before assignment is known, state that
it is unassigned; resolve ownership before concurrent execution. These are
content requirements, not mandatory headings or front matter.

Keep task definitions and detailed results in their owning files. Plans contain
links, ordering and useful progress summaries; update those summaries from the
tasks. A task shared by several plans retains one ID, owning file and writer.
Completion of the planned outcome is assessed against its scope and criteria
using task outcomes and applicable combined verification. Planning itself ends
when the plan and task definitions are authored and checked against their inputs;
it does not require those tasks to have executed. Planning-only work records
intended checks without claiming execution.

Directory ownership and task ownership complement each other. Record the chosen
document root and type-to-folder mapping in the overview, and the actual edit
scope in tasks. Two tasks may work in one directory if their file/resource
boundaries are clear. A folder name or document ID alone does not assign work.
Use the [collaboration basis](COLLABORATION.md#collaboration-basis) to make these
boundaries and ID allocations visible to concurrent writers.

## Item IDs

Apply identity rules to every Markdown document the agent creates within the
authorized project scope, whatever its subject: specifications, research,
guides, meeting notes, reviews, reports, handoffs or kinds not listed here.
Assign the document an ID appropriate to its purpose. A document representing
one primary item uses that item's ID; a collection can use a document ID such
as `DOC-00001`. Choose the identity before creating the file, use it as the
entire filename stem, show it near the top of the body and use it in the index.
An overview itself also has an identity. A document ID is not a substitute for
the identities of its independently tracked contents.

The agent determines which contents need independent reference, revision,
assignment or verification and gives each such item an ID. Requirements,
separately tracked acceptance criteria, design items, plans, tasks, decisions,
findings, changes, risks, open issues and verification items are examples,
not an exhaustive whitelist. New traceable items added to existing Markdown
follow the same rule. Descriptive paragraphs, metadata fields, navigation
entries and ordinary headings do not require separate IDs. A criterion kept as
part of one requirement uses that requirement's identity. A separately managed
criterion gets its own `AC` ID and file. Many referenced IDs may appear in one
document, but that does not authorize defining several independent items there.
Use the [boundary rules](#independent-items-and-supporting-detail) below.

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

Serial allocation is project-wide per complete prefix. Two feature files must
not both define `REQ-00001`; two API plans must not each restart their tasks at
`TASK-API-00001`. `TASK-API-00001` and `TASK-SCR-00001` are distinct IDs. Search
existing definitions and retained/retired IDs before choosing the next unused
serial, reusing a verified baseline under the rules below. Concurrent writers
reserve non-overlapping ranges or prefixes in shared
Markdown notes; no JSON registry or runtime initialization is required.

Put the ID visibly in the owning heading or table row. Provide a stable anchor,
for example an ID-only heading `### REQ-00001` with a descriptive title in the
body, or an explicit anchor for an identified table row. References use the ID
as link text and resolve to that item's anchor, even within one file.

Except for [required-name files](#required-name-exceptions), every newly
generated project Markdown file uses
`<document-root>/<classification-path>/<DOCUMENT-ID>.md`. The entire filename
stem must exactly match the owning document's ID, including uppercase type tokens and
the five-digit serial. Do not add a title, date or descriptive suffix to the
filename. This covers overview/index, shared context, requirements, designs,
plans, tasks, research, reports, changes and handoffs alike. Use
`overview/DOC-00001.md`, not `overview.md` or `DOC-00001-overview.md`.

Each independently managed requirement belongs in its own file, normally named
`requirements/REQ-00001.md`. A plan at `backend-plans/API-00001.md` links its
tasks at `tasks/TASK-API-00001.md` and other task paths. Collection/overview
documents have their own ID and index the owning documents; they do not replace
them with one growing requirements or task file. Explanations, acceptance
criteria belonging to one requirement, and tightly coupled stage notes within
a small change may remain in that owning document. Independently managed items
get separate files when those boundaries apply; do not split every paragraph.

Record the classification-to-folder mapping in the project overview. Examples
include `REQ` to `requirements`, `DES` to `designs`, `API` to `backend-plans`,
`SCR` to `screen-plans`, `TASK-<AREA>` to `tasks`, and `VER` to `verifications`.
These are not reserved directory names: a project may use `specs/requirements`,
`plans/backend`, `work-items` or another meaningful structure. Reuse the chosen
convention consistently within its stated scope. For a new kind or changed
context, the agent selects suitable folders and prefixes and records them
without asking the user to classify them. Folder changes preserve IDs and
update overview/item links; they do not authorize historical-record migration.
Do not create empty type folders or placeholder files before they are needed.
Group a feature's requirement/design/plan/task/verification links in the overview
and record the feature in the owning documents; keep physical storage consistent
with the project's chosen classification rather than blindly copying the example.

Keep IDs unchanged when content is revised, renamed, reordered or moved; update
links after moves. Never reuse deleted/retired IDs. For a split or merge, record
the old item's disposition and links to the new items without overwriting its
decision or evidence history. Identity alone does not identify a reviewed
version, prove approval or establish a passed check.

Before completion, check that every new Markdown document and all traceable
items in the changed deliverables have IDs, every new file is in its mapped
type folder with exactly `<body-document-ID>.md` as its filename or satisfies
the documented required-name exception, definitions
are unique within the project, serials do not collide with retained IDs, and references resolve
to the intended items. Distinguish
definitions from references and clearly marked examples during this check.
Existing IDs and historical records remain valid; use links to older material
without bulk retroactive relabeling. A requested migration has its own scope.
Externally required document formats remain binding; identify and resolve a
real format conflict rather than silently skipping this rule.

## Allocation and validation reuse

Establish a verified allocation basis for each needed complete prefix using
existing definitions, retired IDs and outstanding reservations. Record its
covered version/scope and the assigned ranges in the existing shared overview
or allocation notes. Do not create a second registry or new file per allocation.
If no reliable basis exists, inspect the relevant project-wide definitions and
retained allocation history before selecting a free range.

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

Use one owning file per independently managed primary item. Independence is
about management, not technical isolation: a requirement or task can depend on
another and still need its own ID/file. An item has an independent boundary
when it has its own outcome/scope or can be separately assigned, accepted,
completed, decided or verified. Small size, a common owner, one feature or one
release does not remove that boundary.

Supporting detail only explains or qualifies its parent's meaning/completion;
it has no separate outcome or management status. Keep those descriptions,
examples, metadata and parent-specific acceptance details in the parent's file.
An independently linkable paragraph alone is not a separate work item. If the
detail later needs separate tracking, give it a new ID/file, link it from the
parent and preserve the prior version and decision history.

| Situation | Required treatment |
|---|---|
| Login and search have distinct requirements, even with the same owner | Separate `REQ` files; the overview groups them by feature. |
| One requirement has input examples, rationale and parent-specific acceptance details | Sections of that requirement; no new file or independent ID for each explanation. |
| An acceptance criterion is separately tracked with its own disposition | Its own `AC` file, linked to the parent requirement. |
| A backend plan includes separately assignable tasks | Each task has a `TASK-<AREA>` file; the plan contains links and sequence/dependency information. |
| Several plans cover the same requirement | Reference the same owning requirement file rather than copy its definition. |
| A small change records its source, scope rationale and observed check result | These may be metadata/stage notes of that change; independently managed requirements/tasks still get separate files. |

Before completing documents, check that every independent item has exactly one
owning file and that embedded detail has no separate management boundary.
Do not use the small-change exception or the word "metadata" to conceal
separately managed items inside a single growing document.

## Required-name exceptions

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

Verification checks the actual required name/location and applicable consumer
format, index ID/path/reason mapping, uniqueness and links. Where the body has
an ID, check it against the index; otherwise check the stated format restriction.
Replace ordinary path/name/body-ID checks only to the extent required by the
documented consumer constraint; the index mapping and other applicable checks
remain required. Do not treat every existing descriptive filename as a new
exception or relabel history in bulk. Existing records keep their names and
applicable prior evidence.

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

## Existing runtime records

Existing JSON and Markdown records under `.harness/` are preserved. They retain
their legacy schemas and meaning when read or changed with the optional CLI.
Ordinary project documents do not become CLI records simply because they use
the words plan, task or approval.

Do not rewrite signed snapshots, derived runtime fields or events to make a
document-based workflow pass a legacy gate. Runtime record migration is separate
implementation work requiring its own scope and verification. The
[record-format proposal](RECORD_FORMAT.md) is a legacy design reference, not a
format requirement for current project documents.

## Policy change trace: 2026-09-13

- Baseline: `6b4d41f803ca914b18613aef812f0a60260261af`; the working tree was clean
  before this policy edit.
- Decision source: in this session, the owner replied "정책을 수정하자\~!" to the
  proposal to use only `.md` for new management documents, preserve existing
  records/signatures and exclude product configuration and CLI implementation.
- Before/after: unrestricted management document formats become Markdown-only
  for new documents; schemas and front matter remain unnecessary.
- Scope and readiness: governing policy, tool entry guidance, README and related
  documentation only. The decision covers these edits and document checks;
  required inputs are available, with no ownership conflict or external action.
- Verification criteria: review the diff for consistent scope and preserved
  exceptions; check whitespace, Markdown structure and local links. Runtime code,
  schemas, existing project records and archived policy are outside this change.
- Verification result: STATIC_VERIFIED for the policy edit on this baseline in
  the Windows/PowerShell workspace. Diff review confirmed the intended scope;
  `git diff --check` found no whitespace errors. A PowerShell check passed for
  all 10 changed Markdown files and 56 local links, including heading targets,
  text decoding and balanced code fences. The initial Python-based check could
  not run (`python -` exited 1); the PowerShell check supplied the replacement
  evidence. Product/runtime tests were not run for this documentation-only edit.

## Current document work

The current ID convention is defined in [Item IDs](#item-ids). This repository's
new policy-change note uses `CHG`, `DEC`, `REQ`, `DES`, `PLAN`, `TASK-DOC`,
`RISK` and `VER` with project-wide serials per full prefix. `DOC` identifies the
documentation task area in `TASK-DOC`. One writer allocated these IDs after
searching the existing Markdown; historical records retain their formats/IDs.
For new change notes, this repository reuses its existing `docs` document root
and `changes` classification folder: `docs/changes/<CHG-ID>.md`. Folder names
in illustrative layouts are not mandatory replacements for this mapping.

| Work | Scope and state | Dependencies |
|---|---|---|
| [CHG-00001](changes/2026-09-13-document-organization.md#chg-00001) | Feature/work organization and autonomous IDs for every new Markdown document and tracked item; policy scope complete, STATIC_VERIFIED in the local working tree. | [DEC-00001](changes/2026-09-13-document-organization.md#dec-00001), [PLAN-00001](changes/2026-09-13-document-organization.md#plan-00001); no runtime change. |
| [CHG-00002](changes/2026-09-13-readme-guidance.md#chg-00002) | README examples, ID wording and document guidance aligned; scope complete, STATIC_VERIFIED in the local working tree. | [DEC-00003](changes/2026-09-13-readme-guidance.md#dec-00003); uses the current document/ID policy. |
| [CHG-00003](changes/CHG-00003.md#chg-00003) | Contextual classification folders and exact ID-only Markdown filenames; policy scope complete, STATIC_VERIFIED. | Owner clarification and Git delivery authorization are recorded in the change note; no runtime change or historical migration. |
| [CHG-00004](changes/CHG-00004.md#chg-00004) | Item-boundary and required-name clarification; unused HTML guide removed; scope complete, STATIC_VERIFIED. | Owner explicitly authorized policy corrections and deletion of the current HTML guide; archive preserved. |
| [CHG-00005](changes/CHG-00005.md#chg-00005) | Clarify plan/task responsibilities, shared directory mapping and concurrent ID allocation as the collaboration basis. | Owner authorized these policy edits in this session; verification and scope are recorded in the change note. |
| [CHG-00006](changes/CHG-00006.md#chg-00006) | Direct-request authority, allocation/check reuse and concise agent entry guidance. | Owner authorized the efficiency policy changes and re-review; scope and evidence are recorded in the change note. |
