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

Apply the [item-boundary rules](#independent-items-and-supporting-detail)
when splitting work. Keep tightly coupled stage notes in the owning item and
use links for independently managed requirements, designs, tasks and evidence.
Split accumulated detail when it obscures scope, decisions or evidence.
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

Ordinary prose, navigation and explanatory headings need no independent ID.
Do not use the small-change exception or the word "metadata" to conceal
separately managed items inside a single growing document.

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
| Coverage and ownership | Determine ID scope first. Each in-scope document and independent item has an ID and one owning definition; overviews reference owners and supporting detail meets the item-boundary rules. Harness guidance needs no identity or path-mapping checks. |
| Identity and allocation | New definitions are unique project-wide and do not collide with retained/retired IDs or reservations; distinguish definitions, references and illustrative examples. |
| Ordinary paths | Each new file matches the recorded folder mapping and the filename/body identity specified in [Document paths](#document-paths). |
| Required-name files | Verify the actual consumer name/location/format, index ID/path/reason mapping, and body/index ID agreement when the body permits an ID. Otherwise verify the stated body-format restriction. |
| Links and trace | Overview entries and item/anchor links resolve to the intended owners; requirements, design, planned work and actual evidence cover the requested stage. |
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
