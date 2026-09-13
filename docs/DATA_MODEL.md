# Project Information Model

Project information must be reviewable and attributable. It does not require
a prescribed storage format, schema, directory, ID or front matter. Follow
[AGENTS.md](../AGENTS.md); use the project's existing documents where possible.

## Suggested information

| Information | Minimum useful content |
|---|---|
| Project note | Objective, current stage, baseline, decisions, progress, blockers and next action. |
| Source/intake | Origin, version, analysis scope, ownership and reliability/limitations. |
| Requirements | Intended outcomes, constraints, acceptance criteria and material source trace. |
| Design | Components, interfaces/data, alternatives, requirement coverage and open risks. |
| Plan/work items | Scope, tasks, order, dependencies, verification and actual decision reference. |
| Decision | Reviewed proposal/version, actual owner response/source, bounds and conditions. |
| Change trace | Request, before/after, impact, affected work, decision and verification. |
| Verification | Subject/version, method/environment, expected/observed result, artifacts and limits. |
| Release/handoff | Contributions, versions, decisions, current evidence, unfinished obligations and next owner/action. |

These can be sections in one document or several files. Add separate records
only when useful or required by the project contract. A plan may contain nested
tasks or reference several plans; no single-active-plan field is required.

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
