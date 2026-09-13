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

Assign stable project-unique IDs to every new Markdown document and its
independently tracked items. Determine boundaries and prefixes from content;
`REQ-00001`, `API-00001`, `SCR-00001` and `TASK-<AREA>-00001` are examples, not
a closed list. Choose and record additional types autonomously. Follow the
[ID convention](docs/DATA_MODEL.md#item-ids), link items and check coverage,
uniqueness and references; preserve IDs across revisions and moves.
