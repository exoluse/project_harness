# Human Approval Operations

Routine implementation does not use this workflow. An explicit user request is sufficient for ordinary development, tests, commits, fetch, conflict resolution, and a normal push to the configured upstream.

Cryptographic approval is reserved for five high-risk boundaries:

| Approval type | Subject | Required assurance |
|---|---|---|
| `PRODUCTION_DEPLOYMENT` | project | `CRYPTOGRAPHIC` |
| `PRODUCTION_DATA_CHANGE` | change | `CRYPTOGRAPHIC` |
| `DESTRUCTIVE_ACTION` | change | `CRYPTOGRAPHIC` |
| `SECRET_ACCESS` | change | `CRYPTOGRAPHIC` |
| `CUSTOMER_ACCEPTANCE` | feature | `CRYPTOGRAPHIC` |

`PLAN`, `CHANGE`, `EXCEPTION`, and `PROJECT_CLOSURE` may remain as historical/process records, but they are not routine execution authority in `USER_DIRECTED` mode. `PLAN-0001` in this repository is one such bootstrap history record.

## Protected authority

The authority config is fixed outside the repository:

- Windows: `C:\ProgramData\ProjectHarness\authorities\<project-id>.json`
- POSIX: `/etc/project-harness/authorities/<project-id>.json`

It identifies the project and repository root, a pinned SSH allowed-signers file, a signature namespace, the permitted high-risk approval types, and a protected append-only decision ledger. The coding-agent account must not be able to modify the config, signer list, private key, ledger, or authoritative verifier.

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
