# Claude Code Start Prompt

Follow `CLAUDE.md` and the current `AGENTS.md`. Start from the user's requested
scope, existing decisions and relevant project notes. No mandatory harness CLI
command or initialization is needed. Preserve actual scope, evidence, ownership
and human/external approval boundaries. Policy-only follow-ups stay policy-only.

Write new harness management documents only as Markdown (`.md`), without
parallel JSON records or required schemas/front matter. Follow `AGENTS.md` for
preserving existing records and the formats required by products and tools.

Use a project overview linking independently scoped feature/work documents.
Combine stage sections for small coherent units; split independent units and
link requirements, design, plans and verification. Do not default to one growing
file per document type or create outputs beyond the requested stage. See
[document organization](docs/DATA_MODEL.md#document-organization).

For collaboration, distinguish plans (goals, scope, dependencies and task order)
from tasks (outputs, accountable writers, edit boundaries and completion checks).
Before concurrent editing, share the chosen folder mapping and non-overlapping
ID allocations; use the same semantic prefixes across agents and checkouts.
Assign shared-document editing and Git integration as part of the work.
Use existing overview/plan/task notes for this coordination; follow the
[collaboration basis](docs/COLLABORATION.md#collaboration-basis).

Assign stable project-unique IDs to every new Markdown document and its
independently tracked items. Determine boundaries and prefixes from content;
`REQ-00001`, `API-00001`, `SCR-00001` and `TASK-<AREA>-00001` are examples, not
a closed list. Choose and record additional types autonomously. Follow the
[ID convention](docs/DATA_MODEL.md#item-ids), link items and check coverage,
uniqueness and references; preserve IDs across revisions and moves.

Except for the required-name files described below, new project Markdown uses
`<document-root>/<classification-path>/<DOCUMENT-ID>.md`, such as
`project-docs/requirements/REQ-00001.md`. Use the exact body ID as the filename
stem, without descriptive suffixes. Give independently managed items their own
files, group features through links and choose folders/prefixes for new kinds
autonomously. Folder/root names and nesting are examples, not a fixed schema;
record the project's chosen mapping. Check the folder mapping and filename/body
match, including overviews and handoffs. Preserve existing records and
externally required formats.

Separate independently managed outcomes/work into their own files; keep only
parent-specific explanations and criteria in the parent. Preserve names/paths
required by tools, contracts or repository entry conventions, record their
document ID/path/reason in the overview and add the ID to the body when allowed.
Avoid duplicate copies and extra approval solely for the required name; check
the [required-name exception](docs/DATA_MODEL.md#required-name-exceptions).
