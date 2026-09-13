# Architecture

The harness is a repository policy and documentation framework with optional
legacy tooling. [AGENTS.md](../AGENTS.md) defines the operating policy.
A project can proceed without Python, CLI initialization or schema records.

## Responsibilities

| Layer | Responsibility | Authority limit |
|---|---|---|
| User/customer | Objectives, concrete scope decisions and applicable acceptance | A decision covers only its actual reviewed bounds. |
| Policy and adapters | Workflow, trace, verification and safety requirements | Text does not enforce external permissions. |
| Agent and project documents | Scope/prerequisite assessment, implementation, evidence and reporting | The agent cannot create human consent or claim unrun checks passed. |
| Optional bundled CLI | Legacy record authoring, diagnostics and reports | Implemented schemas/gates remain unchanged; output is not consent. |
| External controls | Protected CI, environments, access controls and human execution/approval | Required controls cannot be bypassed through local policy or record edits. |

## Default flow

User objective and existing sources lead to versioned requirements, design and
planning as requested. Actual owner decisions cover concrete implementation
scope. The agent checks work-item prerequisites, performs covered work, verifies
the changed subject and reports results and limitations.

New harness management documents use Markdown (`.md`), including sections in
existing Markdown files. Existing records and tool-required formats are preserved
under the [format policy](../AGENTS.md#management-document-format). There is no
required state machine, single active plan, claim record or approval fingerprint.
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
| `scripts/`, `.harness/tooling/` | Optional legacy runtime and repository checks; unchanged by the policy transition. |
| Existing `.harness/` project records | Preserved legacy information; no initialization or migration is required. |
| `docs/archive/runtime-required-policy/` | Exact pre-transition policy text, including pending policy edits, for historical reference. |

## Compatibility and limitations

A policy change does not implement new CLI behavior. The runtime still uses
its existing schemas, state transitions, approval mechanics and claim checks.
[Runtime gaps](RUNTIME_GAPS.md) describes legacy findings from static review,
not defects fixed by this transition.

Classify diagnostics by actual impact. Missing authority, invalid current proof,
unsafe actions and required dependencies block affected work. Tool-specific
format/state limitations do not alone block ordinary authorized document-based
work. A separately mandated CI/tool check remains mandatory until its authorized
owner changes that process.

See [Workflow](WORKFLOW.md), [Data model](DATA_MODEL.md) and
[Security](SECURITY.md) for the operating details.
