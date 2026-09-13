# Legacy Runtime Findings

> **Optional CLI reference — not current project workflow requirements.**
> These findings describe static review of runtime revision `7261297`, not
> executed reproductions or fixes made by the policy transition. The bundled
> implementation is unchanged. Follow [AGENTS.md](../AGENTS.md) and
> [Workflow](WORKFLOW.md#optional-runtime) for current authority and readiness.

The B1–B8 limitations can still affect deliberately selected legacy commands.
They are not prerequisites for ordinary document-based project progress.
Required external/contractual checks remain binding, and no failed CLI check
may be reported as PASS. Preserve the legacy history and diagnose actual impact.

## Current progress blockers

B identifiers are documentation labels, not canonical open items or gate levels.
Each entry distinguishes legacy behavior and the verification needed before
claiming a runtime fix. Proposed remedies below are not implementation authority.
The heading is retained for historical links; these are blockers of the legacy
command path, not a mandatory list to resolve before project work.

### B1. Historical evidence and strict validation

Current: `validate_project` checks every evidence binding against the working
tree, including historical or STALE evidence. Old bindings still warn after new
evidence is recorded; strict rejects warnings. Changed criteria can also make
old VERIFIED subjects invalid. Sources: [validation](../.harness/tooling/project_harness/validation.py),
[strict exit handling](../.harness/tooling/project_harness/cli.py).

Required behavior: separate historical integrity from current applicability.
Until implemented, retain old observations and report the exact strict blocker.
Do not rewrite hashes, delete history or turn unverified work into PASS.
Verification needed: revise a verified file/criterion, add real new evidence and
retain old history without blocking valid new work; tampering and use of stale
evidence as current proof must still fail.

### B2. Acceptance and deployment TASK execution

Current: TASK execution permits APPROVED, BUILDING, VERIFYING and MAINTAINING,
but not CUSTOMER_ACCEPTANCE or DEPLOYING. Those latter states lack a direct
rework return. Entry to CUSTOMER_ACCEPTANCE also uses the feature gate with its
default customer-approval requirement. Sources: [gates](../.harness/tooling/project_harness/gates.py),
[transitions](../.harness/tooling/project_harness/lifecycle_mutations.py).

Check the full execution/feedback path before entering those states. If blocked,
report the state and operation; never relabel the phase, reset or hand-edit state
to deploy. Verification needed: candidate -> acceptance feedback -> authorized
rework -> renewed verification/acceptance -> gated deployment -> post-deploy
checks, with missing or mismatched action approvals still denied.

### B3. High-risk PLAN assurance

Current: PLAN actions outside the procedural local-action allowlist require a
cryptographic PLAN approval in addition to matching capability approvals.
Sources: [assurance escalation](../.harness/tooling/project_harness/approvals.py),
[capability gates](../.harness/tooling/project_harness/gates.py).

Current policy uses specific human decisions and independent external controls;
see [high-risk decisions](APPROVALS.md#plans-containing-high-risk-capabilities).
Selecting the legacy CLI still encounters the additional signed PLAN requirement.
Any future separation of routine scope decisions from action permits must verify
that local-only scope remains procedural and no high-risk action succeeds without
its matching current permit and reviewed PLAN coverage.

### B4. Closure across multiple PLANs

Current: every project-required feature must belong to the one active PLAN even
when execution used several PLANs. Source: [closure gate](../.harness/tooling/project_harness/gates.py).

Current policy closes from a release inventory across contributing plans;
a legacy active-PLAN rejection does not alone block that document-based review.
Do not invent a final implementation PLAN or reassign past TASKs to pass the CLI.
Verification needed: aggregate two PLANs with different features, whether under
shared or separate decisions, and close only when the full release contract is
satisfied. Omitting unfinished required scope must still fail.

### B5. Project closure dependency manifest

Current: closure requires project `approval_dependencies`; `plan sync` manages
PLAN dependencies only. Sources: [sync](../.harness/tooling/project_harness/authoring.py),
[closure diagnostics](../.harness/tooling/project_harness/gates.py).

Document-based closure uses a release inventory and requires no such field;
see [closure preparation](WORKFLOW.md#closure-preparation). The earlier policy
workaround for an explicit project manifest is preserved in the archive.
Do not mutate legacy records solely to follow the current document workflow. Verification needed for future
automation: derive the same complete manifest, reject missing/unsafe paths and
preserve signed snapshots when its live version changes.

### B6. Formal records for a single writer

Current: `result submit` and `handoff create` require an active claim. Sources:
[CLI](../.harness/tooling/project_harness/cli.py),
[result submission](../.harness/tooling/project_harness/workflow.py).

Current policy allows a truthful document result/handoff when the delivery
contract accepts it; see [formal-record handling](COLLABORATION.md#formal-records-for-a-single-writer).
The legacy commands still enforce claims. Claim-free CLI formal lineage remains
unimplemented; do not fabricate a past claimed attempt. Verification needed: truthful
single-writer results/handoffs preserve baseline, ownership and observations;
unknown dirty work, overlapping writers and stale attempts remain rejected.

### B7. Unrelated drafts and global strict validation

Current: an incomplete required CANDIDATE feature warns even outside the selected
scope; global strict rejects it. `next` also reports all validation errors before
selecting work. Sources: [validation](../.harness/tooling/project_harness/validation.py),
[guidance](../.harness/tooling/project_harness/guidance.py).

Keep unselected ideas as attributable input until required canonical fields can
be authored truthfully. Preserve existing drafts; never delete them or mark
required work optional to silence checks. Report remaining strict failures
without calling unrelated product work defective. Verification needed: separate
global integrity, selected-scope readiness and future draft completeness;
actual dependencies and global corruption must still block execution.

### B8. Checkout transfer

Current: Git does not transfer procedural markers or protected authority, and
decisions bind their repository root. An exact confirmation retry can restore
a missing marker only while the original payload and provenance remain applicable.
Source: [procedural recording](../.harness/tooling/project_harness/approvals.py).

Current work checks the real decision source, coverage and destination authority;
see [decision recovery](APPROVALS.md#checkout-transfer-and-decision-recovery).
A missing CLI marker alone is not a policy-first decision boundary. For selected
legacy commands, distinguish same-root recovery from differently bound payloads;
never install markers by hand. General cross-root CLI migration is unimplemented. Verification needed: exact valid
retries are idempotent; conflicting latest decisions, changed roots and revoked
or stale subjects cannot be silently replayed.

## Other guidance inconsistencies

`create_work_item` still warns unconditionally that adding a TASK to an approved
PLAN requires a fresh decision. For explicit scope contracts, use actual coverage
and preflight results with the existing decision when valid. For legacy exact
fingerprints, retain their currentness restriction. Do not invent consent because
of that warning. Source: [authoring](../.harness/tooling/project_harness/authoring.py).

The prior documentation-output approval mismatch is removed by current policy:
a request for requirements/design/planning documents authorizes those outputs
and relevant document checks. It does not authorize unrelated implementation.

## Earlier routine-path fixes

The entries below are retained descriptions of earlier legacy-runtime changes,
not current workflow instructions or new verification results. All command,
state, gate and schema requirements in this section apply to that optional CLI.

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
| Historical STALE/SUPERSEDED approvals failed strict validation | Validate original approval snapshots and attestations as history; enforce latest-decision applicability at execution. Evidence staleness remains B1 above. Tampering still fails closed. |
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

Address the relevant B1–B8 criteria before claiming the legacy CLI implements a
complete delivery workflow. Ordinary policy-first delivery does not depend on
those changes. Earlier routine-path
fixes and explicit shared scope are implemented. Hierarchical
plans in [Plan hierarchy](PLAN_HIERARCHY.md) and broader Markdown migration in
[Record format](RECORD_FORMAT.md) remain separate designs. Shared authority
already works across single-level plans; those future designs are not required
to avoid per-plan owner decisions.
