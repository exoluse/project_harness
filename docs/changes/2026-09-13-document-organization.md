# CHG-00001

Feature/work document organization and autonomous Markdown item identity.

## Overview and baseline

Baseline: `2b4668ff99f90c3415dba32ff63c371fc964f27f`; Git status was clean
before this change on 2026-09-13 in the Windows/PowerShell workspace.
This is one coherent policy change, so its requested stages share this document.
The document uses its primary change ID. Its parent index is the
[information model](../DATA_MODEL.md#current-document-work), with shared rules
in [AGENTS.md](../../AGENTS.md).

Scope: governing policy, README, Codex/Claude entry guidance, data model,
development method, workflow, architecture, context guidance, web example and
this change note. Product/runtime code, schemas, existing project records,
signed history and archives are excluded. The initial scope included no migration,
commit, push or external action; [DEC-00002](#dec-00002) adds Git delivery.
Readiness: inputs are available, no dirty-file ownership
conflict was found, and local policy edits need no external permission.

Local navigation: [decision](#dec-00001), [design](#des-00001),
[plan](#plan-00001), [content verification](#ver-00001),
[format/link verification](#ver-00002), [identity verification](#ver-00003).

## DEC-00001

Decision source: the owner reported one Markdown file per document type.
The assistant proposed a project overview with separate feature/work documents,
shared specifications, linked trace and combined sections for small work.
The owner replied in this conversation: "응. 그 구조야."

During the same policy edit, the owner requested item IDs, giving
`REQ-00001`, `API-00001`, `SCR-00001` and `TASK-XXX-00001` as examples, then
clarified: "딱 이것만 국한되는게 아니야. 너가 알아서 생성하는 모든 md 파일은 이런 식으로 정책을 가져가야 한다는 말이야."
and "그걸 너가 판단해서 만들어야해."

The decision covers this policy change and document checks. The expanded target
applies IDs to every newly created Markdown document and its independently
tracked contents; the agent determines appropriate types and item boundaries.
The examples are not an exhaustive catalog. This is policy authority, not a
decision to migrate existing records or implement runtime enforcement.

## Requirements and acceptance criteria

Each row's acceptance criterion is part of its requirement identity.

| ID | Outcome and acceptance criterion | Design / work / verification |
|---|---|---|
| <a id="req-00001"></a>REQ-00001 | A project overview indexes independently scoped feature/work documents and common specifications; independent units are not accumulated by default in one file per type. | [DES-00001](#des-00001), [TASK-DOC-00001](#task-doc-00001), [VER-00001](#ver-00001) |
| <a id="req-00002"></a>REQ-00002 | Small coherent work can combine stage sections; the guidance avoids trivial-task files and empty future stages. | [DES-00001](#des-00001), [TASK-DOC-00001](#task-doc-00001), [VER-00001](#ver-00001) |
| <a id="req-00003"></a>REQ-00003 | Shared specifications, requirements, design, work and evidence remain linked with dependencies and preserved baselines. | [DES-00001](#des-00001), [TASK-DOC-00001](#task-doc-00001), [VER-00002](#ver-00002) |
| <a id="req-00004"></a>REQ-00004 | Every new Markdown document and independently tracked item receives an appropriate stable ID; the agent chooses unlisted types and boundaries without requiring the user to enumerate them. | [DES-00001](#des-00001), [TASK-DOC-00001](#task-doc-00001), [VER-00003](#ver-00003) |
| <a id="req-00005"></a>REQ-00005 | Type-prefixed five-digit serials are unique per full prefix project-wide, survive revisions/moves, are not reused and link explicitly to actual parent items. | [DES-00001](#des-00001), [TASK-DOC-00001](#task-doc-00001), [VER-00003](#ver-00003) |
| <a id="req-00006"></a>REQ-00006 | Entry points, supporting guidance and this new change note consistently apply the policy; scope, Markdown and links pass review. | [DES-00001](#des-00001), [TASK-DOC-00002](#task-doc-00002), [TASK-DOC-00003](#task-doc-00003), [VER-00001](#ver-00001), [VER-00002](#ver-00002), [VER-00003](#ver-00003) |

## DES-00001

This design covers [REQ-00001](#req-00001), [REQ-00002](#req-00002),
[REQ-00003](#req-00003), [REQ-00004](#req-00004), [REQ-00005](#req-00005)
and [REQ-00006](#req-00006), implemented through [PLAN-00001](#plan-00001).

Before: unrestricted consolidation of document contents, no concrete split
criteria, and optional IDs. After: project overview and independent work units,
with an open, agent-selected type vocabulary and stable identities for all new
Markdown documents and independently tracked contents. Detailed rules live in
the [information model](../DATA_MODEL.md#item-ids), with authoritative scope in
[AGENTS.md](../../AGENTS.md#item-identity-and-trace) and aligned entry guidance.

The small-unit exception keeps this note in one file; stable heading/row
anchors supply resolvable item links. A fixed document count, mandatory directory
layout or closed prefix catalog would not meet the varied scope of future work.
No automatic legacy migration or runtime enforcement is introduced.

## PLAN-00001

Execute the scope in [DEC-00001](#dec-00001) using [DES-00001](#des-00001).
The tasks are ordered below; documentation inputs are ready, and each task
remains within the policy-only paths/actions and verification described above.

### TASK-DOC-00001

Parent: [PLAN-00001](#plan-00001). Update the governing document boundaries and
ID rules in `AGENTS.md` and `docs/DATA_MODEL.md` for
[REQ-00001](#req-00001) through [REQ-00005](#req-00005). Implemented; verified
by [VER-00001](#ver-00001) and [VER-00003](#ver-00003).

### TASK-DOC-00002

Parent: [PLAN-00001](#plan-00001). After [TASK-DOC-00001](#task-doc-00001),
align README, entry guidance, development/workflow/architecture/context docs
and examples for [REQ-00006](#req-00006). Implemented; verification is recorded
under [VER-00001](#ver-00001).

### TASK-DOC-00003

Parent: [PLAN-00001](#plan-00001). After [TASK-DOC-00002](#task-doc-00002),
review the actual diff and check Markdown, local links and ID definitions for
[REQ-00006](#req-00006). Results belong to [VER-00001](#ver-00001),
[VER-00002](#ver-00002) and [VER-00003](#ver-00003). Completed with static
document verification.

## Risks and handling

| ID | Risk and treatment |
|---|---|
| <a id="risk-00001"></a>RISK-00001 | Excessive fragmentation: split independently tracked units, keep explanatory prose unnumbered and allow small-unit sections. |
| <a id="risk-00002"></a>RISK-00002 | Duplicate facts or IDs: keep one owning definition, search existing IDs, allocate per full prefix and check references. |
| <a id="risk-00003"></a>RISK-00003 | Accidental history rewrite: preserve existing records/IDs and require separately scoped migration. |

## VER-00001

Subject: this policy working-tree change on the baseline above. Method: static
review of the actual diff against [REQ-00001](#req-00001),
[REQ-00002](#req-00002) and [REQ-00006](#req-00006), checking the remaining
trace/ID rules as well. Expected: coherent scope, aligned guidance and no
runtime/archive edits. Result: STATIC_VERIFIED. The actual tracked diff and new
change note cover 12 Markdown files within the declared scope. Review confirmed
independent-unit split criteria, the small-unit exception, all-new-Markdown
identity coverage, autonomous type selection and consistent entry guidance.
A targeted search found no remaining current-policy statements making IDs
optional. The runtime, schemas, historical records and archive are unchanged.

## VER-00002

Subject: all changed/new Markdown files for this change. Method: Git whitespace
check and PowerShell UTF-8, fence and local file/anchor checks for
[REQ-00003](#req-00003) and [REQ-00006](#req-00006). Expected: no whitespace,
decoding, fence or link errors. Result: STATIC_VERIFIED. `git diff --check`
passed; the PowerShell check passed for all 12 changed/new Markdown files and
149 local file/anchor links, including strict UTF-8 decoding, document titles,
trailing whitespace and balanced fences. The first validation attempt stopped
at a PowerShell `String.Split` overload mismatch before completing link checks;
replacing it with the `-split` operator allowed the full check to pass. No
product/runtime test or rendered-browser check was run.

## VER-00003

Subject: new document/item definitions and references for this change. Method:
review coverage, scan project Markdown for ID definitions and distinguish
references/examples, then check duplicates and anchor references for
[REQ-00004](#req-00004), [REQ-00005](#req-00005) and [REQ-00006](#req-00006).
Expected: one owning definition per real ID, no collisions with historical IDs,
appropriate identities for all new traceable items and explicit task parents.
Result: STATIC_VERIFIED. A scan of all 21 project Markdown files, including
hidden/ignored paths outside `.git`, found 19 unique real heading/row ID
definitions and one new document with its primary change ID. Review confirmed
coverage for the change, decision, six requirements, design, plan, three tasks,
three risks and three verification items. Task parents and trace links resolve;
inline syntax examples and references were distinguished from definitions.
The check validates this deliverable, not automatic enforcement in future runs.

## Handoff and limits

This note is linked from the information model's current-work index. The
initial ID namespace search found no five-digit IDs of these types in existing
Markdown; examples added to policy guidance are labeled as syntax examples or
presented inline as illustrative conventions. The first attempt to add ID rules
was rejected by `apply_patch` for an unmatched context; it changed no files and
the corrected patch was applied. No check failure is treated as a pass.

At initial policy completion, the statically verified changes remained in the
local working tree for review. Future document creation
uses the updated entry guidance. No required work remains in this policy scope.
The work does not establish future agent behavior in another project; no
product, browser or live-environment verification, customer acceptance or
deployment is claimed.

## DEC-00002

After reviewing the completed policy work, the owner requested in this
conversation: "커밋 & 푸시해." This authorizes committing the reviewed 12-file
Markdown change and pushing the current `main` branch to its configured
upstream, `origin/main`, for [CHG-00001](#chg-00001). Product/runtime changes,
force pushes and history rewrites remain outside this delivery scope.

Preflight: Git status contains only this change's known files. `git fetch origin`
succeeded; `HEAD` and `origin/main` both resolve to the baseline above, with
zero commits ahead or behind. The prior content review remains applicable;
this delivery decision note is the only added content since policy completion.
The delivery sequence is document recheck, explicit file staging, commit, normal
push, and confirmation of the remote commit and working-tree status. The final
conversation response will report the actual commit/push receipt.

Delivery-preparation recheck: the same PowerShell document check passed for
12 Markdown files, 151 local file/anchor links and 20 unique real IDs across
21 project Markdown files, including this additional decision. UTF-8, titles,
fences, whitespace and new-document identity checks passed, as did
`git diff --check`. This extends the earlier evidence to the delivery note.

The initial commit attempt stopped because Git author identity was unset;
no commit or push occurred in that attempt. The latest five commits consistently
use `exoluse <exoluse@gmail.com>`. The retry uses that existing repository
identity through command-scoped Git options, without changing global settings.
