# Codex Start Prompt

Read the current `AGENTS.md` once, identify the user's scope and existing
decisions, and inspect the relevant project notes and working-tree changes.
Use the policy-first workflow: document actual readiness and verification,
without mandatory CLI startup, initialization, record schemas or runtime gates.

Write new harness management documents only as Markdown (`.md`), using ordinary
sections, tables and links without required schemas or front matter. Do not
create parallel JSON records. Preserve existing records and apply the product,
evidence, legacy runtime and external-control boundaries in `AGENTS.md`.

Keep a project overview with shared context/status and links to feature/work
documents. Give independently scoped features or changes separate documents;
combine stage sections only within a small coherent unit. Do not keep appending
all new work to one requirements, design or plan file. Link requirements,
design, work and verification; create only the requested stage outputs. Follow
[document organization](docs/DATA_MODEL.md#document-organization).

Give every new Markdown document and its independently tracked items stable
project-unique IDs. Determine meaningful item boundaries and prefixes from the
content: `REQ-00001`, `API-00001`, `SCR-00001` and `TASK-API-00001` are examples,
not an exhaustive list. Choose and record new types as needed without asking
the user to classify each one. Follow the [ID convention](docs/DATA_MODEL.md#item-ids),
link items and preserve IDs across revisions/moves; check coverage, uniqueness
and references. Apply this to guides, research, reviews and handoffs as well.

Store every new project Markdown document at
`<document-root>/<classification-path>/<DOCUMENT-ID>.md`, for example
`project-docs/requirements/REQ-00001.md`. The filename is exactly the body
document ID plus `.md`, with no title/date suffix. Use type folders for all
kinds, including overviews, tasks, reports and handoffs; choose new mappings
autonomously. Root/folder names and nesting are contextual choices, not a fixed
schema; record and consistently reuse the mapping. Independently managed items
have their own files. Group features
through overview/item links. Check folder mapping and exact filename/body ID
agreement; preserve existing records and externally required formats.

Preserve the requested stopping point, user/unknown work and external high-risk
controls. Optional CLI diagnostics do not grant authority or automatically stop
unrelated work. Policy-only requests authorize guidance edits, not runtime
implementation, deletion or project-record migration.
