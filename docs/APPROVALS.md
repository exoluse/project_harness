# Human Approval Operations

Routine approval is the owner's prompt response to a concrete reviewed scope.
The agent records it; the runtime validates its provenance, applicability and
execution prerequisites. Planning-only work ends after authoring and required
checks, before any execution decision.

## Who decides and who checks

An explicit response such as "Proceed with this scope" is enough when it clearly
refers to the prepared proposal. No magic phrase, typed fingerprint or user-run
command is required. Preserve the actual message and reference; never infer
consent from silence, an added document or an unreviewed request.

`approval confirm` records that human decision. `plan apply-decision` applies
it to a covered plan. TASK gates check readiness; their PASS does not create
consent or claim verification, customer acceptance or delivery.

Routine PLAN decisions use `PROCEDURAL` assurance. They record provenance and
do not cryptographically authenticate identity. Five boundaries require
`CRYPTOGRAPHIC` assurance regardless of project configuration:

| Approval type | Subject |
|---|---|
| `PRODUCTION_DEPLOYMENT` | project |
| `PRODUCTION_DATA_CHANGE` | change |
| `DESTRUCTIVE_ACTION` | change |
| `SECRET_ACCESS` | change |
| `CUSTOMER_ACCEPTANCE` | feature |

## One decision for a concrete change

Use `plan prepare-scope` before the decision to author a versioned execution
scope with reviewed requirement/feature definitions, write boundaries,
capabilities, exclusions, maximum risk, verification obligations and constraints.
The command grants no authority. `report decision-package` includes these bounds,
their fingerprint and preflight results for the owner's review.

After the owner decides, task splitting and unordered path/capability lists
within those bounds do not need another decision. New single-level plans can
reuse the scope through `new plan --scope-from PLAN-0001`; apply the same decision
with `plan apply-decision --approval APR-0001 --plan PLAN-0002`. Application is
bookkeeping, not another question. Each task still needs its own passing gate.

A meaningful change outside the bounds requires feasibility/impact analysis,
updated scope preparation and one new prompt decision. Application preserves
ongoing development state. Do not reset lifecycle pointers by hand. Legacy
PLANs without `decision_scope` retain their original exact fingerprint contract;
preparing a new scope is explicit and never reinterprets an old approval.

Include a CHANGE in the prepared scope with `--change CR-0001` before the owner
reviews it. The covered CHANGE can then use the same PLAN decision reference.
An exact change snapshot explicitly included among legacy PLAN dependencies is
also supported. A later decision does not erase that original CHANGE approval;
execution still requires current TASK authority. Unreviewed or materially changed
CHANGE records fail validation;
a record label does not grant additional approval or waive high-risk gates.

Historical decisions are checked against their preserved snapshots and actual
attestation. Normal staleness or supersession does not fail strict validation.
Current execution applicability is checked by gates. Damaged history still fails
closed; never delete history, fabricate consent or copy stale evidence as PASS.

## Routine PLAN confirmation

The following commands are performed by the agent. Author complete PLAN/TASK
content, then prepare the scope and package before asking for the decision:

```powershell
python scripts/harness.py plan sync PLAN-0001
python scripts/harness.py plan prepare-scope PLAN-0001 --write-boundary src --write-boundary tests --max-risk MEDIUM
python scripts/harness.py validate --strict
python scripts/harness.py report decision-package PLAN-0001

# After the owner actually approves the presented scope by prompt:
python scripts/harness.py approval confirm `
  --type PLAN --subject .harness/plans/PLAN-0001.md --decision APPROVED `
  --approver <owner> --basis "Owner approved the presented execution scope" `
  --confirm-fingerprint <package-fingerprint> --confirmation-id <unique-id> `
  --confirmation-channel chat --confirmation-reference <actual-owner-message> `
  --authorized-action LOCAL_IMPLEMENTATION --authorized-action LOCAL_TESTS `
  --authorized-action DOCUMENTATION --acknowledge-procedural
python scripts/harness.py plan apply-decision --approval APR-0001
```

Use the actual reviewed boundaries, actions and risk ceiling; examples are not
authority. A new decision needs a unique confirmation id. Retrying an identical
payload and provenance with that id is idempotent while applicable; conflicting
reuse fails. A retry does not need another owner question.

Application selects the plan, prepares lifecycle state and records the changes
atomically. It accepts a prepared decision from discovery/planning and resumes
a changed decision during development. An unrelated live plan must finish or be
explicitly superseded before switching; plans sharing the same scope can remain
executable together. `transition --kind plan --to CLOSED|SUPERSEDED` records
retirement; CLOSED requires terminal tasks and is not project/customer acceptance.

Task verification must retain the prepared commands for its selected criteria.
`criterion_verification` records those obligations; `verification` records their
common commands. Independent criteria can use different checks without requiring
every task to repeat every other task's commands. Author these before the decision.
Evidence profiles and bindings remain independently required for completion claims.

A procedural decision authorizes only local safe actions. High-impact actions
keep the cryptographic flow below and matching capability-specific approval.

## Protected authority

The authority config is fixed outside the repository:

- Windows: `C:\ProgramData\ProjectHarness\authorities\<directory>-<root-digest>.json`
- POSIX: `/etc/project-harness/authorities/<directory>-<root-digest>.json`

The name is derived from the repository the harness governs, so several harnesses on one machine stay distinct without any of them carrying a project identity, and `doctor` reports the exact path this repository expects.

It identifies the repository root, a pinned SSH allowed-signers file, a signature namespace, the permitted high-risk approval types, and a protected append-only decision ledger. The coding-agent account must not be able to modify the config, signer list, private key, ledger, or authoritative verifier.

## Request and import flow

1. Confirm that `python scripts/harness.py doctor` reports the protected authority `READY`.
2. Run the relevant preflight and inspect the exact subject.
3. Prepare an expiring request.
4. A human owner or approval broker signs it and atomically appends the exact request/signature pair to the protected ledger.
5. Import the public decision into the repository and check currentness.

Example:

```powershell
$request = ".harness/decisions/production.request.json"
python scripts/harness.py approval prepare `
  --output $request `
  --type PRODUCTION_DEPLOYMENT `
  --subject .harness/project.json `
  --decision APPROVED `
  --approver owner@example.com `
  --basis "Reviewed exact production target and rollback" `
  --authorized-action PRODUCTION_DEPLOYMENT

# Human/broker only: sign and append the exact request/signature to the protected ledger.

python scripts/harness.py approval record --request $request --signature "${request}.sig"
python scripts/harness.py approval check APR-0001
```

The agent may prepare the request, but may not sign it, install it in the protected ledger, run a human confirmation on someone's behalf, invent provenance, or infer approval from chat or repository text.

## Currentness and reversal

Current-approval checks re-verify the signature, protected-ledger presence and ordering, reviewed subject fingerprint, dependency snapshots, decision status and conditions. Historical validation verifies the preserved decision without requiring it to remain latest. Changed governed scope or an invalid current decision blocks its use for execution; history remains attributable to the original version.

Record reversal as a later protected decision (`REJECTED`, `REVISION_REQUIRED`, `DEFERRED`, or `REVOKED`). Never delete prior approvals or ledger entries. An approval permits only the named action on the exact subject; it does not imply another high-risk approval or execute anything by itself.
