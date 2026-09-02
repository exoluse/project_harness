# PLAN-0002 proposal: governed operation and self-hosting hardening

Status: non-authoritative proposal for human review. This file is not a plan
baseline, approval, task grant, or claim. No work described below may start
until the corresponding canonical records exist, validate, and receive the
required human decision.

## 1. Why a new plan is required

PLAN-0001 established the harness record model, gates, claims, reports, and
standalone package. Two correctness gaps found during the first audit were
repaired within that approved scope:

- `c21f048` completes typed trace relationships across projects, closure
  criteria, features, tasks, results, reviews, and evidence.
- `849fc02` keeps project closure evidence references out of the normative
  project fingerprint while retaining closure requirements and profiles in it.

The next improvements change the operating contract rather than repair those
two implementations. In particular, commands that mutate canonical evidence,
criterion state, feature state, project state, or plan state need explicit
write scopes and transition rules. PLAN-0001 does not grant them.

There is also a bootstrap gap: an ordinary agent cannot claim new canonical
plan and task paths until an approved task grants those paths, while those
grants do not exist until the canonical records are created. For this one
transition, the human owner or a protected bootstrap coordinator must
materialize the proposed source/change/requirement/feature/plan/work-item
records. An agent must not infer that authority from this proposal or run plan
confirmation on the owner's behalf.

## 2. Proposed outcome

Make routine harness operation explicit, fail-closed, and self-demonstrating:

1. operators can record evidence and request legal lifecycle transitions
   without hand-editing related JSON records;
2. the harness repository exercises those operations on its own work while
   preserving the distinction between implementation, verification, review,
   acceptance, and closure;
3. validation and reporting avoid repeated whole-repository reconstruction;
4. large control-plane modules are split only after behavior is pinned by
   tests; and
5. the vendored runtime and test tiers have an explicit upgrade and support
   policy.

## 3. Proposed requirement and feature

Proposed requirement `REQ-0008`:

> The harness shall provide governed, auditable commands for recording
> evidence and changing lifecycle state, and shall apply its own governance to
> prove those commands without weakening human authority or completion gates.

Proposed feature `FUNC-0007`, **Governed lifecycle operation**.

Suggested completion criteria:

### AC-FUNC-0007-001 — Evidence recording

An operator command records an observed evidence claim using the registered
profile, exact subject and criterion fingerprints, declared file or directory
bindings, command outcome, hashes, provenance, and limitations. It validates
all inputs before replacing canonical files, refuses stale or out-of-scope
subjects, never executes commands copied from mutable records, and does not
promote lifecycle state merely because an evidence file was created.

### AC-FUNC-0007-002 — Legal transitions

An operator command exposes the allowed next states for requirements,
features, work items, plans, and projects and applies only transitions whose
current gates pass. The change and its event are committed as one recoverable
operation; validation failure leaves no partial canonical update. Repeating
the same request is deterministic and cannot duplicate an event silently.

### AC-FUNC-0007-003 — Authority preservation

No command may create, infer, install, confirm, or substitute a human
decision. Approval, exception, production, customer-acceptance, and closure
operations continue to require their configured assurance and explicit
capabilities. Read-only advice clearly identifies the exact missing authority.

### AC-FUNC-0007-004 — Governed bootstrap

The repository documents and tests a bounded bootstrap path for proposing the
next canonical change without creating an unclaimable write cycle. Drafts are
non-authoritative; only a human owner or protected coordinator may move the
initial records into the canonical control plane, after which normal plan,
task, and claim gates apply.

### AC-FUNC-0007-005 — Self-hosted evidence

The harness uses the released commands to record evidence for a real local
harness change and demonstrates traceability through result and independent
review. This criterion requires current evidence; a fixture, unit test, or the
implementer's own PASS is not independent review or acceptance.

## 4. Proposed work order

### TASK-0007 — Specify and pin lifecycle operations

Define the transition graph, evidence input contract, failure atomicity,
idempotency, and authority matrix before implementation. Add adversarial tests
for stale fingerprints, path escape, invalid profiles, failed gates, duplicate
requests, partial writes, and attempted self-approval.

Suggested scope: lifecycle/evidence schemas, validation helpers, CLI surface,
focused tests, and operator documentation. Canonical `.harness` records are
excluded from the implementation claim.

### TASK-0008 — Implement evidence and transition commands

Implement only the contracts pinned by TASK-0007. Prefer a shared service
layer used by the CLI and reports so that mutations have one enforcement path.
Keep read-only inspection separate from mutation. Run focused RED/GREEN tests
first and the complete repository gate before submitting a result.

### TASK-0009 — Self-host the workflow

Create an exact, separately approved claim for the canonical records that the
dogfood exercise must change. Use the new command path for one bounded local
change, collect current evidence, submit a result, and obtain a review from a
different recorded agent or protected CI boundary. Report each achieved level
separately; do not turn a green unit suite into integration, browser, live,
customer, or closure evidence.

### TASK-0010 — Cache immutable evaluation context

Measure the current gate and report paths, then introduce an immutable
`EvaluationContext` (or equivalent) that loads and validates repository state
once per command. Preserve diagnostics and ordering. Add a regression benchmark
based on a checked-in representative fixture; choose the threshold from the
measured baseline rather than an unsupported target.

### TASK-0011 — Decompose oversized control-plane modules

After TASK-0007 through TASK-0010 have pinned behavior, split schema
validation, gates, and CLI dispatch along authority boundaries. Keep public
imports compatible or provide an explicit migration. No behavior change is
authorized merely by moving code.

### TASK-0012 — Runtime lifecycle and test tiers

Document the supported Python/runtime matrix and vendored dependency update
procedure, including license and upstream-test checks. Separate fast contract
tests from slow repository scenarios while keeping the full protected gate
mandatory for result and closure evidence. A fast tier must never be reported
as the full suite.

## 5. Required canonical write scopes

The materialized plan must give each task exact paths. At minimum, it must
distinguish:

- implementation: `src/project_harness/**`, schemas, tests, and docs;
- control-plane dogfood: only the named `.harness/evidence`, feature, project,
  plan, result, review, event, and handoff records required by TASK-0009;
- bootstrap: the exact new source/change/requirement/feature/criterion/plan and
  work-item files used to establish PLAN-0002; and
- generated runtime coordination records under the shared Git-common runtime.

Broad `.harness/**` write authority is not recommended. Dirty or actively
claimed paths remain out of scope.

## 6. Verification and decision gates

Every implementation task should require its focused tests and
`python scripts/check_repo.py`. Mutation tasks additionally need subprocess
tests against temporary Git repositories so claim, base/head, rollback, and
concurrency behavior are exercised without modifying the working control
plane. Protected CI or an external orchestrator remains necessary for
adversarial independence.

Before PLAN-0002 can be approved, the decision package should include:

1. the raw source request and this interpretation as separate records;
2. affected requirement, feature, criterion, task, and closure fingerprints;
3. exact task capabilities, forbidden actions, write scopes, and dependencies;
4. a resolved decision for the bootstrap path and mutation atomicity model;
5. strict validation and plan-gate output; and
6. the exact approval request for the human owner to confirm personally.

## 7. Explicit exclusions

This proposal does not authorize production deployment, external messaging,
destructive cleanup, secrets or private-key access, automatic human approval,
customer acceptance, project closure, weakening cryptographic requirements,
or treating procedural agent IDs as authenticated separation.

## 8. Requested human decision

The owner should decide whether to materialize this proposal as PLAN-0002 with
the work order above. Approval of the general direction is not enough to start
work: the canonical plan fingerprint, work-item scopes, capabilities, and
bootstrap authority must be visible in the final decision package. The owner
must perform the configured confirmation; an agent may only prepare and report
the request.
