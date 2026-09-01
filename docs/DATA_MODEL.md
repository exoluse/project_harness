# Data Model

## Canonical repository records

| Directory | Prefix | Purpose |
|---|---|---|
| `.harness/sources/` | `SRC-` | Customer/external input with authority, role, and interpretation status |
| `.harness/artifacts/` | `ART-` | Registered file/bundle path, media type, digest, and execution trust |
| `.harness/requirements/` | `REQ-` | Versioned functional, non-functional, operational, and security requirements |
| `.harness/features/` | `FUNC-` | Implementable capabilities and criterion-level completion contracts |
| `.harness/plans/` | `PLAN-` | Versioned execution subject, workstreams, capabilities, exclusions, and verification strategy |
| `.harness/work-items/` | `TASK-` | Bounded agent tasks, dependencies, criterion scope, write scope, locks, and checks |
| `.harness/open-items/` | `OI-` | Questions, decisions, assumptions, risks, dependencies, conflicts, and blockers |
| `.harness/evidence/` | `EVD-` | Verification observations, profiles, subject fingerprints, bindings, and limitations |
| `.harness/approvals/` | `APR-` | Imported signed human decisions bound to exact subjects and snapshots |
| `.harness/changes/` | `CR-` | New requests/artifacts, classification, affected scope, impact, and decision |
| `.harness/results/` | `RES-` | Terminal worker-attempt results and build/evidence fingerprints |
| `.harness/reviews/` | `VRD-` | Verdicts bound to one exact result/build |
| `.harness/handoffs/` | `HOF-` | Immutable agent-to-agent exact-state transfer records |

`.harness/project.json` contains project policy, required features, approval dependencies, and the project closure contract. `.harness/state.json` points to the active plan/baselines/release and current lifecycle state.

Events and approval baseline snapshots live in `.harness/events/` and `.harness/baselines/`. Approval request drafts live in `.harness/decisions/`; they are not approvals until signed, installed in the protected external ledger, and imported as `APR-*`.

## Full trace

The expected connected chain is:

```text
SRC/ART -> REQ -> FUNC -> completion criterion -> TASK
                               |                    |
                               v                    v
                              EVD <- RES attempt -> VRD review
```

`trace <id>` walks incoming and outgoing references across canonical records. Feature completion criteria and project closure criteria are indexed as first-class synthetic trace nodes even though they are nested in their owner JSON record.

Plan preflight checks both directions: planned requirements need realizing features, required features/criteria need implementing tasks, and tasks must stay inside the plan's requirement/feature/criterion and capability boundaries.

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

An `APR-*` stores authority/sequence/decision identity, approval type, subject ID/path/fingerprint, decision, actions/conditions, baseline snapshot manifest, and embedded signed-request attestation. Its currentness is re-evaluated against the fixed external authority and protected ledger; the highest authority sequence for a type/subject wins.

## Claims and shared mailboxes

Claims are live leases, not canonical project records. In Git projects they reside under `<git-common-dir>/project-harness-runtime/leases/`, alongside shared inbox/outbox, acknowledgment, and handoff-acceptance state. In no-Git projects they fall back to `.harness/runtime/` and are single-writer.

Dispatch IDs use `DSP-*`; claims use `CLM-*`. A handoff or result retains the claim ID and task/plan fingerprints so later readers can reconstruct the attempt boundary.

## Results, reviews, and latest-attempt semantics

A result contains exact changed files and their states, verification commands/outcomes, computed verification state (`PASS`, `FAIL`, or `INCOMPLETE`), evidence refs/fingerprints, limitations, task/plan fingerprints, base/head commit, and build fingerprint.

Submitting `RES-*` releases the claim. Multiple results for one task are attempts, not cumulative votes. Gates select the highest numeric result ID for that task. They then select the highest numeric review ID referring to that exact result.

A `VRD-*` stores reviewer alias, verdict, basis/checks, result fingerprint, and build fingerprint. PASS cannot be recorded on a non-PASS or stale result. Reviewer alias inequality is procedural self-review prevention, not cryptographic authentication.

## Project closure contract

The default closure criteria are `DELIVERY`, `HANDOVER`, and `MAINTENANCE_READINESS`. Each required criterion declares profiles and evidence. Project closure additionally requires required features in the active approved plan, completed and Git-integrated tasks, each latest attempt independently reviewed PASS, zero active claims, no active `G0/G1`, a closure-ready lifecycle state, exact approval dependencies, and a current signed `PROJECT_CLOSURE` approval.
