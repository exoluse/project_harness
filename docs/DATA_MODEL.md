# Data Model

## Canonical repository records

| Directory | Prefix | Purpose |
|---|---|---|
| `.harness/sources/` | `SRC-` | Customer/external input with authority, role, and interpretation status |
| `.harness/artifacts/` | `ART-` | Registered file/bundle path, media type, digest, and execution trust |
| `.harness/requirements/` | `REQ-` | Versioned functional, non-functional, operational, and security requirements |
| `.harness/features/` | `FUNC-` | Implementable capabilities and criterion-level completion contracts |
| `.harness/plans/` | `PLAN-*.md` | Execution planning reference, workstreams, dependencies, capabilities, exclusions, and verification strategy. Child plans with category ids such as `API-001.md` are specified in [Plan hierarchy](PLAN_HIERARCHY.md) and arrive with `harness.plan/v2` |
| `.harness/work-items/` | `TASK-*.md` | Executable work units required before implementation, with dependencies, criterion scope, write scope, locks, checks, and capability-specific approval refs |
| `.harness/open-items/` | `OI-` | Questions, decisions, assumptions, risks, dependencies, conflicts, and blockers |
| `.harness/evidence/` | `EVD-` | Verification observations, profiles, subject fingerprints, bindings, and limitations |
| `.harness/approvals/` | `APR-` | Human decisions with declared assurance, exact subjects, actions, provenance/attestation, and snapshots |
| `.harness/changes/` | `CR-` | New requests/artifacts, classification, affected scope, impact, and decision |
| `.harness/results/` | `RES-` | Terminal worker-attempt results and build/evidence fingerprints |
| `.harness/reviews/` | `VRD-` | Verdicts bound to one exact result/build |
| `.harness/handoffs/` | `HOF-` | Immutable agent-to-agent exact-state transfer records |

`.harness/project.json` identifies the project only by a human `name` and a fixed `id` of `PROJECT`; it contains the PLAN-gated execution, claim/record modes, high-risk approval policy, required features, approval dependencies, and the project closure contract. `.harness/state.json` contains the lifecycle and a `current_plan` that is null during initial discovery and required before implementation. Before implementation, `active_plan` and `active_decision` must materialize the current human PLAN approval.

Events and approval baseline snapshots live in `.harness/events/` and `.harness/baselines/`. Cryptographic approval request drafts live in `.harness/decisions/`; they are not approvals until signed, installed in the protected external ledger, and imported as `APR-*`.

### PLAN and TASK Markdown

PLAN and TASK use `.md` files because people create and review them directly. A strict YAML-style front matter block contains the complete schema-validated record. The Markdown body that follows is reserved for readable explanations and is preserved by lifecycle mutations. Gates and fingerprints consume only the front matter, so body prose cannot silently grant capabilities or alter execution authority.

The front matter grammar is dependency-free and intentionally narrow: two-space indentation, string keys, and JSON-compatible quoted scalars, arrays, and objects. Duplicate keys, tabs, invalid indentation, mixed list/object blocks, missing delimiters, and malformed values are errors. Legacy PLAN/TASK JSON can still be read so existing projects do not fail abruptly; newly created records and this repository use Markdown.

## Full trace

The expected connected chain is:

```text
SRC/ART -> REQ -> FUNC -> completion criterion -> TASK
                               |                    |
                               v                    v
                              EVD <- RES attempt -> VRD review
```

`trace <id>` walks incoming and outgoing references across canonical records. Feature completion criteria and project closure criteria are indexed as first-class synthetic trace nodes even though they are nested in their owner JSON record.

Plan preflight checks both directions: planned requirements need realizing features, required features/criteria need implementing tasks, and tasks must stay inside the plan's declared boundaries. A current passing preflight and human PLAN decision are execution gates for routine work.

High-impact work-item capabilities use `capability_approval_refs`, a capability-to-`APR-*` map included in the task fingerprint. Production deployment, production-data change, destructive cleanup, and secret access require their matching cryptographic approval types. Ordinary external Git synchronization needs no capability approval of its own: fetch and a normal push to the configured upstream run under the applied PLAN decision like any other routine action, while force pushes, tag pushes, branch deletion, and other targets require separate explicit user authorization. A stale, unrelated, mismatched, or non-current approval reference cannot satisfy the task gate.

`report decision-package PLAN-*` projects this connected model into one human decision package. `report completion` projects required feature gates plus technical and authorized closure without changing canonical state.

## Source and artifact authority

A source records where input came from, whether it is raw/reference/review/approved/contract authority, its artifact role, and whether interpretation is explicit or inferred. An artifact separately binds a path and SHA-256 and states execution trust.

Neither source authority nor a file hash grants execution permission. HTML, JavaScript, office files, generated prompts, and other active content remain untrusted until a separate safe-execution decision.

## Open-item gates

- `G0`: global plan/task stop; blocks named feature/criterion completion and all closure.
- `G1`: blocks named tasks/features/criteria and all closure.
- `G2`: visible assumption/warning; work may continue under its recorded boundary.
- `G3`: monitored; no current gate block.

Active states include `OPEN`, `ANALYZING`, `WAITING_DECISION`, `WAITING_EXTERNAL`, `DECISION_READY`, `BLOCKED`, `DEFERRED`, and `REOPENED`. Unknown states fail closed.

A `RESOLVED` or `CANCELLED` item is actually closed only when its resolution contains summary, decider, matching decision authority, resolution time, nonempty propagation targets, evidence references, and baseline references. Propagation targets and evidence records must exist, and baseline paths must resolve to files. List every affected target explicitly; the validator does not infer propagation. Otherwise the item remains active.

## Feature completion contract

Each feature traces to one or more requirements and contains criterion objects. Every required criterion declares:

- stable criterion ID and observable statement;
- required flag;
- verification plan;
- one or more required verification profiles;
- one or more required file/directory binding paths;
- current eligible evidence references.

The criterion fingerprint excludes mutable evidence references but includes its normative statement, verification plan, profiles, and bindings. Changing the contract therefore invalidates old evidence while adding a new evidence reference does not redefine the criterion.

## Evidence

Evidence results are distinct:

`NOT_TESTED`, `COLLECTED`, `PARTIAL`, `INCONCLUSIVE`, `FAILED`, `VERIFIED`, `STALE`, and `REVOKED`.

Required completion accepts only current `VERIFIED` evidence with ambiguity `NONE` or `LOW`, a required profile, the current criterion fingerprint, and all required bindings. A binding stores the path, type, and digest; directories use a deterministic recursive tree digest.

Evidence states exactly what it proves, method, environment, subject version, expected/actual observation, limitations, and ambiguity. A passing task result cannot substitute arbitrary evidence for a criterion, and evidence bound to an unrelated file cannot satisfy a required path.

## Plans, approvals, and baselines

A plan's `approval_subject` includes its requirement, feature, and work-item references, workstreams, verification strategy, authorized/excluded actions, and invalidation triggers. `approval_dependencies` lists the exact canonical records snapshotted with the plan decision.

An `APR-*` stores its assurance and local record sequence plus authority/decision identity, approval type, subject ID/path/fingerprint, decision, actions/conditions, baseline snapshot manifest, and attestation. A `PROCEDURAL` PLAN attestation records the direct human confirmation and exact confirmed payload; it is required before any implementation but does not authenticate identity cryptographically. A `CRYPTOGRAPHIC` attestation embeds the signed request and is re-evaluated against the fixed external authority and protected ledger. The latest local decision for a type/subject controls repository gates without falling back when that latest record is invalid. Procedural records must also match the Git-common latest-decision marker and global procedural authority sequence; within a cryptographic authority, the highest valid protected sequence controls.

## Claims and shared mailboxes

Claims are live leases, not canonical project records. In Git projects they reside under `<git-common-dir>/project-harness-runtime/leases/`, alongside shared inbox/outbox, acknowledgment, handoff-acceptance, and `human-decisions/` state. The human-decision runtime contains the decision mutex, procedural sequence counter, and subject-keyed latest markers used by every linked worktree. In no-Git projects runtime falls back to `.harness/runtime/` and is single-writer.

Runtime markers never enter the repository and are not copied by Git. Canonical records themselves need not be committed either: the harness gates on what is present in the working tree. A procedural `APR-*` that reaches another checkout, whether committed or copied, has no matching marker there and is non-current until the owner repeats the exact confirmation in that checkout's primary worktree. This portability limit is fail-closed and does not turn the runtime marker into an authentication root.

Dispatch IDs use `DSP-*`; claims use `CLM-*`. A handoff or result retains the claim ID and task/plan fingerprints so later readers can reconstruct the attempt boundary.

## Results, reviews, and latest-attempt semantics

A result contains exact changed files and their states, verification commands/outcomes, computed verification state (`PASS`, `FAIL`, or `INCOMPLETE`), evidence refs/fingerprints, limitations, task/plan fingerprints, base/head commit, and build fingerprint.

Submitting `RES-*` releases the claim. Multiple results for one task are attempts, not cumulative votes. Gates select the highest numeric result ID for that task. They then select the highest numeric review ID referring to that exact result.

A `VRD-*` stores reviewer alias, verdict, basis/checks, result fingerprint, and build fingerprint. PASS cannot be recorded on a non-PASS or stale result. Reviewer alias inequality is procedural self-review prevention, not cryptographic authentication.

## Project closure contract

The default closure criteria are `DELIVERY`, `HANDOVER`, and `MAINTENANCE_READINESS`. When closure is asserted, each required criterion needs eligible evidence, no active `G0/G1`, no outstanding concurrent claims, and a closure-ready lifecycle state. Closure requires an active human-approved plan; a cryptographic `PROJECT_CLOSURE` record remains required only when the project policy requires it. Final customer acceptance remains a separate cryptographic boundary when required.
