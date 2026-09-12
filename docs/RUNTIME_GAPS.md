# Runtime Gaps on the Routine Path

Status: **the audited routine-path gaps below are fixed in the runtime.**
This document retains the original finding headings for troubleshooting links.
Use `next` for normal routing and [Workflow](WORKFLOW.md) for commands. Manual
state-pointer edits and artificial lifecycle detours are no longer needed.

## 1. Nothing sets the active plan

Fixed: `plan apply-decision` sets `current_plan` and `active_plan` atomically
with the applied decision and event. A recorded decision alone grants no task
execution. A selected task must still pass its gate.

## 2. The decision can be applied only from `DECISION_READY`

Fixed: application accepts supported pre-decision states and moves them to
`APPROVED`. Planning completion remains distinct from execution readiness;
planning-only work stops before owner confirmation or decision application.

## 3. A changed plan cannot be re-applied

Fixed: a new current decision can replace a stale or superseded decision during
development while preserving the ongoing lifecycle state. Closed or cancelled
projects are not implicitly reopened. Prior-version approval history remains
intact; current applicability and historical integrity are separate checks.

## 4. `next` gives the wrong instructions at the approval step

Fixed: incomplete drafts report `NEEDS_PLAN_DETAIL` with planning blockers.
Prepared routine work reports `NEEDS_PLAN_APPROVAL` and `approval confirm`;
the five high-risk boundaries retain the signed flow. A recorded decision
awaiting application reports `NEEDS_DECISION_APPLIED`. Guidance is bounded by
the user's request and never constitutes approval.

## 5. Drafts are empty and the preflight needs content the CLI cannot write

Fixed: the CLI can author requirement statements and criteria, feature criteria
and verification profiles/bindings, plan references and verification strategy,
and task write scope, verification and risk. `plan prepare-scope` creates a
reviewable execution-scope contract before the owner decides. Empty drafts
remain valid authoring starts, but are not presented as planning complete.

## 6. The examples omitted `--authorized-action`

Fixed: routine examples name the authorized actions. Confirmation must cover
the actions presented in the reviewed scope. Agents transcribe the owner's
actual prompt decision; they do not invent decision provenance.

## 7. No command changes a plan's status

Fixed: `transition --kind plan --to CLOSED|SUPERSEDED` records retirement with
a reason. Closing requires terminal tasks. Switching to unrelated scope
refuses unfinished live work and retires a completed previous plan. Plans
sharing one explicit scope may remain executable together. `next` reports
`SCOPE_COMPLETE` when the selected scope is finished instead of inventing work.

## 8. PLAN approval also binds routine task refinement

Fixed for explicitly prepared `harness.execution-scope/v1` contracts: approval
binds reviewed requirements, criteria, criterion-specific verification obligations, path
boundaries, capabilities, risk ceiling, explicit dependencies and constraints.
Task splitting and feasible reordering within that contract do not alter its
fingerprint. `new plan --scope-from` and `plan apply-decision --plan` allow
several single-level plans to use the same actual decision after coverage checks.

Task-specific coverage blocks changed outcomes and out-of-scope work; unrelated
tasks can retain authority when their own covered subjects remain unchanged.
Global blockers, shared dependency changes and invalid records can still stop
broader work. New material scope needs one new informed decision. No broad
permission is inferred from a plan title or an earlier prompt.

Legacy approvals keep their exact original fingerprint semantics. Adding an
explicit contract changes the reviewed subject and needs a decision on that
contract; an existing signature or prompt record is never reinterpreted as
wider permission. See [Approvals](APPROVALS.md).

## Additional duplication mismatches

| Original finding | Implemented behavior |
|---|---|
| Historical STALE/SUPERSEDED records failed strict validation | Validate original snapshots and attestations as history; enforce latest-decision applicability at execution. Tampering still fails closed. |
| PLAN and CHANGE needed separate decision records | An explicitly reviewed CHANGE may reference the same applicable PLAN decision through scope coverage or an exact legacy dependency snapshot. |
| Sync retained obsolete derived references | Track generated dependencies; remove only proven obsolete derived entries. Preserve ambiguous legacy extras. |
| Version bookkeeping and unordered lists changed hashes | Versioned contracts normalize known unordered fields and omit descriptive progress/version bookkeeping. Legacy hashes remain unchanged. |
| Sibling changes staled unrelated results/claims/handoffs | Scope hashes remain stable under covered refinement; task subjects, coverage, artifact/evidence bindings and other applicability checks still run. |
| Repeated fingerprint display | Reuse the decision package while inputs remain unchanged. Mutation-time authority and freshness checks remain. |
| Finished plans prompted new tasks | Report scope completion; the user determines whether there is more work. |

## Why the self-tests did not catch the original CLI gaps

Earlier fixtures pre-populated state pointers, and tests named as reaching
execution readiness stopped at approval guidance. Those test names and
expectations now describe draft/planning boundaries accurately.

`test_scope_runtime.py` adds a CLI scenario from initialization through scope
authoring, planning checks, one synthetic prompt decision, application, task
gates, covered refinement, retirement and a second plan under that same decision.
It does not hand-set state pointers. Separate regressions cover changed-scope
resumption, preserved history, tampering, revocation, out-of-scope rejection,
shared CHANGE decisions and independent-task coverage. Synthetic lifecycle
transitions are not customer acceptance or production verification.

## Order of work

Routine-path fixes and explicit shared scope are implemented. Hierarchical
plans in [Plan hierarchy](PLAN_HIERARCHY.md) and broader Markdown migration in
[Record format](RECORD_FORMAT.md) remain separate designs. Shared authority
already works across single-level plans; those future designs are not required
to avoid per-plan owner decisions.
