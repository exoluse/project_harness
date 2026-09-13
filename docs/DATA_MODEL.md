# Project Information Model

Project information must be reviewable and attributable. Write all new harness
management documents as Markdown (`.md`); no fixed schema, directory, ID or front
matter is required. Follow [AGENTS.md](../AGENTS.md#management-document-format);
reuse sections in existing Markdown documents where possible. Use prose, tables,
checklists and links instead of creating JSON records or parallel structured
copies of management documents.

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
