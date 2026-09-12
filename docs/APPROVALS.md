# Human Approval Operations

Routine execution approval is the owner's explicit prompt response to a concrete reviewed proposal. The agent records that decision; the runtime checks its applicability and execution prerequisites. The current implementation requires a PLAN, a TASK listed in it, and that human decision materialized by `plan apply-decision` before execution.

## Who decides and who checks

The owner can say "Proceed with this scope" or an equivalent clear response.
No magic phrase, fingerprint copied into chat, or user-run CLI command is
required. The agent prepares the proposal and fingerprint before asking,
preserves the actual response and its source, and records it against that
unchanged proposal. Clarify an ambiguous response; never treat silence or
an unreviewed scope as consent.

The runtime does not grant approval. `approval confirm` records a human
decision, `plan apply-decision` applies it, and gates check whether execution
conditions are satisfied. PASS alone is not user consent; failure blocks the
affected execution without cancelling the prior decision as history. The
high-risk signature requirements below are separate from routine prompt approval.

`PLAN` approval carries `PROCEDURAL` assurance by default: it records a direct confirmation from the human project owner rather than authenticating them. Cryptographic approval is reserved for five high-risk boundaries:

| Approval type | Subject | Required assurance |
|---|---|---|
| `PRODUCTION_DEPLOYMENT` | project | `CRYPTOGRAPHIC` |
| `PRODUCTION_DATA_CHANGE` | change | `CRYPTOGRAPHIC` |
| `DESTRUCTIVE_ACTION` | change | `CRYPTOGRAPHIC` |
| `SECRET_ACCESS` | change | `CRYPTOGRAPHIC` |
| `CUSTOMER_ACCEPTANCE` | feature | `CRYPTOGRAPHIC` |

PLAN records are mandatory once execution is prepared, while initial discovery may have none. PLAN approval is mandatory before execution. `CHANGE`, `EXCEPTION`, and `PROJECT_CLOSURE` approvals remain optional process records.

The [development method](DEVELOPMENT_METHOD.md) defines stage readiness reviews
and agile change cycles. A readiness review is not a new approval type and does
not demand a separate owner decision at every waterfall stage. Consolidate
routine scope and its requirement/design basis in the single change decision.
The owner's proceed response to the prepared feasibility/impact proposal is
recorded as the PLAN decision; it does not need a second PLAN or TASK approval.
Task refinement and sequence adjustments within agreed requirements and constraints
need no separate business decision. The current runtime nevertheless requires
a fresh PLAN confirmation for changed bound task structure; [the compatibility
rule](DEVELOPMENT_METHOD.md#current-runtime-compatibility) applies until that
implementation gap is addressed. Report any forced repeated confirmation as
that runtime limitation. An in-contract correction needs TASK authority and
applicable re-verification. Final acceptance of an earlier subject does not
approve a changed one. Additional contractual approvals remain applicable.

Every approval subject is named by its path, never by its id, because the decision binds the exact file that was fingerprinted. PLAN approval subjects are canonical `PLAN-*.md` records. Approval fingerprints and snapshots bind the parsed front matter and declared dependencies; the explanatory Markdown body does not grant authority. Baseline snapshots preserve the complete file for review.

## One decision for a concrete change

The owner decides on the presented execution scope, not on a quota of PLAN
files. The same decision should cover all plans and tasks that implement that
scope within its agreed bounds. Splitting, adding or switching plans alone
does not justify another owner question. A material change outside the decided
scope requires its own feasibility/impact proposal and one new decision.
Today's recording path still binds one exact PLAN fingerprint; it does not
yet provide shared coverage across plans. Do not copy an approval to another
subject or invent provenance to simulate that future capability.

This decision boundary applies when execution is requested. A planning-only
request authorizes preparation and planning checks, then ends with the plan
and findings; it does not require an owner decision to call plan authoring
complete. Execution readiness still requires the current decision, application
and TASK gate. Do not introduce a separate "planning complete" approval.

Before asking whether to proceed, the agent assesses feasibility and impact,
prepares the necessary scope and verification, runs preflight and strict
validation, and binds the reviewable proposal to the final fingerprint.
An explicit owner response such as "Proceed with that change" is the decision
when it clearly refers to that proposal. Preserve the actual words, channel
and reference and use `approval confirm` and `plan apply-decision` to record
and apply it. These commands materialize the same decision; they are not another
permission request. A bare request, unanswered question or added document is
not approval, and procedural recording does not authenticate identity.

Do not first ask for business approval and only afterwards prepare a different
PLAN for another approval. Ask again only for material new scope, impact,
assumptions, conditions or authority beyond what the owner reviewed. Ordinary
task refinement and described verification stay inside the decision; the
current runtime fingerprint exception must be named when it blocks this policy.
Do not reuse a confirmation for a different fingerprint or invent provenance.

One actual decision may be described in several process records; those labels
do not justify several owner questions. Only the scope actually presented and
decided is covered. The current validator requires a separate CHANGE-type
decision when a CHANGE record advances to APPROVED or later, so it cannot yet
use a PLAN decision reference for that state. Report this as a recording
incompatibility, not a new business approval requirement. Do not manufacture
another decision or falsely mark the CHANGE state as applied.

Keep historical approval for the original subject separate from current
authorization to execute the revision. A runtime `STALE` result means the record
does not authorize the current evaluated subject; it is not a retroactive
revocation of the old version's approval or verified observations. A new version
requires applicable verification and any high-risk approval of that version.

Historical snapshots still need integrity checks. Their normal replacement
does not require renewed approval of the old version. If strict validation
rejects a preserved historical decision, report the current validator's
limitation; do not delete the decision or ask the owner to approve history again.

## Routine PLAN confirmation

This is the everyday path, and it is the only human decision an agent may
transcribe on the owner's behalf; the signed flow below is imported with
`approval record` but never made by the agent. The owner reviews the concrete
proposal and replies by prompt. The agent transcribes that decision against
the fingerprint prepared for the unchanged proposal. The commands below are
agent bookkeeping, not instructions the owner must run:

```powershell
python scripts/harness.py fingerprint .harness/plans/PLAN-0001.md

# The owner reviews the proposal and replies, for example: "Proceed with this scope".

python scripts/harness.py approval confirm `
  --type PLAN `
  --subject .harness/plans/PLAN-0001.md `
  --decision APPROVED `
  --approver owner@example.com `
  --basis "Reviewed the plan and its tasks" `
  --confirm-fingerprint <fingerprint from above> `
  --confirmation-id HCONF-plan-0001 `
  --confirmation-channel <where the owner said it> `
  --confirmation-reference <what they said it in> `
  --authorized-action LOCAL_IMPLEMENTATION `
  --authorized-action LOCAL_TESTS `
  --authorized-action DOCUMENTATION `
  --acknowledge-procedural

python scripts/harness.py plan apply-decision --approval APR-0001
```

The confirmation fingerprint must match the plan as it stands, the confirmation
id must be unique and unused, an `APPROVED` decision must name at least one
`--authorized-action` and together they must cover every capability of every
TASK in the plan, and `--acknowledge-procedural` states on the record that this
proves provenance, not identity. The confirmation runs the plan preflight and
fails closed on any blocker; [Workflow](WORKFLOW.md) lists what it checks.
`plan apply-decision` additionally needs `state.active_plan` to name the plan
and the lifecycle to be `DECISION_READY`; see [Runtime gaps](RUNTIME_GAPS.md)
for the interim steps that satisfy those today. Editing bound fields afterwards
can make the decision non-current for the edited PLAN. The original decision
and snapshots remain history for their original subject; this does not make
all previously delivered work unapproved.

A procedural confirmation is limited to local, safe actions. A plan that
authorizes production, production data, destructive cleanup, or secret access
needs `CRYPTOGRAPHIC` assurance and the signed flow below.

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

Every status check re-verifies the signature, protected-ledger presence and ordering, exact subject fingerprint, dependency snapshots, decision status, and conditions. A changed subject, superseding decision, damaged snapshot, or invalid ledger makes the approval non-current.

Record reversal as a later protected decision (`REJECTED`, `REVISION_REQUIRED`, `DEFERRED`, or `REVOKED`). Never delete prior approvals or ledger entries. An approval permits only the named action on the exact subject; it does not imply another high-risk approval or execute anything by itself.
