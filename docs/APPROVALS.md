# Human Approval Operations

Routine implementation uses the PLAN approval workflow. It requires a current PLAN, a TASK listed in it, and the current human PLAN decision materialized by `plan apply-decision` before execution.

Cryptographic approval is reserved for five high-risk boundaries:

| Approval type | Subject | Required assurance |
|---|---|---|
| `PRODUCTION_DEPLOYMENT` | project | `CRYPTOGRAPHIC` |
| `PRODUCTION_DATA_CHANGE` | change | `CRYPTOGRAPHIC` |
| `DESTRUCTIVE_ACTION` | change | `CRYPTOGRAPHIC` |
| `SECRET_ACCESS` | change | `CRYPTOGRAPHIC` |
| `CUSTOMER_ACCEPTANCE` | feature | `CRYPTOGRAPHIC` |

PLAN records are mandatory once execution is prepared, while initial discovery may have none. PLAN approval is mandatory before execution. `CHANGE`, `EXCEPTION`, and `PROJECT_CLOSURE` approvals remain optional process records. `PLAN-0001` in this repository is historical; `state.current_plan` identifies its successor.

PLAN approval subjects are canonical `PLAN-*.md` records. Approval fingerprints and snapshots bind the parsed front matter and declared dependencies; the explanatory Markdown body does not grant authority. Baseline snapshots preserve the complete file for review.

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
