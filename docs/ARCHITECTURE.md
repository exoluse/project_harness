# Architecture

The harness is a repository policy and documentation framework.
[AGENTS.md](../AGENTS.md) defines the operating policy.

## Responsibilities

| Layer | Responsibility | Authority limit |
|---|---|---|
| User/customer | Objectives, concrete scope decisions and applicable acceptance | A decision covers only its actual reviewed bounds. |
| Policy and adapters | Workflow, trace, verification and safety requirements | Text does not enforce external permissions. |
| Agent and project documents | Scope/prerequisite assessment, implementation, evidence and reporting | The agent cannot create human consent or claim unrun checks passed. |
| Project tooling | Whatever the governed project already uses for build, test and validation | Tool output is evidence for what it checked, never authority. |
| External controls | Protected CI, environments, access controls and human execution/approval | Required controls cannot be bypassed through local policy or record edits. |

## Default flow

User objective and existing sources lead to versioned requirements, design and
planning as requested. Actual owner decisions cover concrete implementation
scope. The agent checks work-item prerequisites, performs covered work, verifies
the changed subject and reports results and limitations.

Project documents connect the overview, independently managed items and their
evidence through stable references. The [Information model](DATA_MODEL.md)
defines their organization and detailed rules under
[AGENTS.md](../AGENTS.md#document-organization).
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
| `tools/check-docs.mjs` | Optional dependency-free Node check of relative links, heading anchors, `Last checked:` dates and ID-named files; see [guidance maintenance](CONTEXT_EFFICIENCY.md#maintaining-policy-guidance). |
| Existing `.harness/` records in an adopted project | Records left by the retired runtime; see [former runtime records](WORKFLOW.md#former-runtime-records). |

The repository ships no workflow runtime, schema or record store. Its policy
and guidance use Markdown; the document checker reads them and writes nothing. Former runtime records in adopted projects keep their
original formats; a governed project supplies its own build and test tooling.

See [Workflow](WORKFLOW.md), [Data model](DATA_MODEL.md) and
[Security](SECURITY.md) for the operating details.
