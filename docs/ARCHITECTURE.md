# Architecture

The harness is a repository policy and documentation framework.
[AGENTS.md](../AGENTS.md) defines the operating policy.

## Responsibilities

| Layer | Responsibility | Authority limit |
|---|---|---|
| User/customer | Objectives, concrete scope decisions and applicable acceptance | A decision covers only its actual reviewed bounds. |
| Policy and adapters | Workflow, trace, verification and safety requirements | Text does not enforce external permissions. |
| Agent and project documents | Scope/prerequisite assessment, implementation, evidence and reporting | The agent cannot create human consent or claim unrun checks passed. |
| Bundled tools | Record authoring, diagnostics and reports | See [tool usage](WORKFLOW.md#optional-runtime). |
| External controls | Protected CI, environments, access controls and human execution/approval | Required controls cannot be bypassed through local policy or record edits. |

## Default flow

User objective and existing sources lead to versioned requirements, design and
planning as requested. Actual owner decisions cover concrete implementation
scope. The agent checks work-item prerequisites, performs covered work, verifies
the changed subject and reports results and limitations.

New harness management documents use Markdown (`.md`), organized as a project
overview linking feature/work documents. Stage sections can share a file within
a small coherent unit; independently scoped units have separate documents. See
[document organization](DATA_MODEL.md#document-organization).
Traceable items use [stable type-prefixed IDs](DATA_MODEL.md#item-ids) and
resolvable item links; these identities do not enforce approval or verification.
New project Markdown uses `<document-root>/<classification-path>/<ID>.md`;
the filename stem exactly matches the body document ID, including overview and shared-context
documents. Features group item links; the agent chooses physical classification
folders and hierarchy for the project rather than following fixed directory names.
Supporting descriptions stay in their parent item; separately managed outcomes
and work get their own files. Tool/contract/repository-required filenames retain
their paths with indexed identity under the
[required-name exception](DATA_MODEL.md#required-name-exceptions).
Existing records and tool-required formats are preserved
under the [format policy](../AGENTS.md#management-document-format).
Closure aggregates the actual contributions and obligations.

Existing code can supply observations for reverse engineering. It does not
prove intent, correctness or customer acceptance. Preserve source versions and
separate current implementation from proposed changes.

## Repository map

| Path | Current role |
|---|---|
| `AGENTS.md` | Canonical operating policy. |
| `CLAUDE.md`, start prompts | Tool entry guidance consistent with the policy. |
| `README.md`, `docs/` | Workflow, decisions, security, examples and reference material. |
| `scripts/`, `.harness/tooling/` | Bundled tools; see [usage and limitations](WORKFLOW.md#optional-runtime). |
| Existing `.harness/` project records | Tool-managed records. |

See [Workflow](WORKFLOW.md), [Data model](DATA_MODEL.md) and
[Security](SECURITY.md) for the operating details.
