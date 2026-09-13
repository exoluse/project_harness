# Claude Code Adapter

Read the current `AGENTS.md` once per session; it is the operating policy.
Use the user's request and relevant project documents to determine stage,
authority, remaining work and verification. Inspect Git status before edits.

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

The bundled runtime is optional. Do not require `next`, `init`, PLAN/TASK schemas,
fingerprints, decision application or CLI gates for ordinary project work.
If used, report its real output and distinguish record diagnostics from actual
project blockers. Protected CI and external controls remain mandatory where
applicable.

Reuse actual decisions within their scope; stop for missing authority, material
changes or real dependencies. Keep user/unknown work and truthful history.
Policy-only requests permit guidance edits, without initialization, runtime
implementation or deletion.
