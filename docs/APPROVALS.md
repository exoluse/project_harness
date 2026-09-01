# Human Approval Operations

Human approval is distinct from agent execution authority. `.harness/project.json` declares the minimum assurance for each approval type. A repository approval is current only when its exact subject/dependency fingerprint, decision, conditions, authorized/excluded actions, attestation, latest-decision position, and immutable baseline snapshots all agree.

Two assurance levels are supported:

- `PROCEDURAL` is eligible only for `PLAN`. It records an explicit confirmation ID, channel, reference, approver label, exact fingerprint, and decision payload. It is useful for ordinary local project planning, but it is provenance rather than cryptographic identity authentication.
- `CRYPTOGRAPHIC` verifies an allowed human SSH signer, a fixed external authority configuration, the exact signed request in a protected append ledger, and the latest protected authority sequence.

An agent may prepare a decision package or copyable command. It must not run `approval confirm` on the human's behalf, invent confirmation provenance, sign with a human key, install a ledger entry, or infer approval from conversation or repository text. There is no procedural or unauthenticated production, production-data, exception, customer-acceptance, change, or project-closure mode.

## Supported approval subjects

| Approval type | Canonical subject kind | Assurance |
|---|---|---|
| `PLAN` | plan | policy-selected `PROCEDURAL` or `CRYPTOGRAPHIC` |
| `CUSTOMER_ACCEPTANCE` | feature | `CRYPTOGRAPHIC` |
| `PROJECT_CLOSURE` | project | `CRYPTOGRAPHIC` |
| `CHANGE` | change | `CRYPTOGRAPHIC` |
| `PRODUCTION_DEPLOYMENT` | project | `CRYPTOGRAPHIC` |
| `PRODUCTION_DATA_CHANGE` | change | `CRYPTOGRAPHIC` |
| `EXCEPTION` | change | `CRYPTOGRAPHIC` |

The recommended policy keeps the safe default cryptographic and opts only plan approval into procedural confirmation:

```json
{
  "policy": {
    "approval_assurance": {
      "default": "CRYPTOGRAPHIC",
      "by_type": {
        "PLAN": "PROCEDURAL"
      }
    }
  }
}
```

Missing legacy policy fails closed to `CRYPTOGRAPHIC`. The default cannot be lowered to `PROCEDURAL`, and no non-`PLAN` override may select it. Include `.harness/project.json` in a plan's `approval_dependencies` so changing the assurance policy invalidates the plan fingerprint and its approval.

## Procedural plan confirmation

Run preflight and print the exact current fingerprint:

```powershell
python scripts/harness.py validate --strict
python scripts/harness.py gate plan PLAN-0001
python scripts/harness.py report decision-package PLAN-0001
$planFingerprint = python scripts/harness.py fingerprint .harness/plans/PLAN-0001.json
```

The project owner reviews the decision package and personally runs the confirmation. The fingerprint must be copied from the immediately preceding command, the decision must be explicit, and an approved plan must list every authorized action rather than relying on an empty action list:

```powershell
python scripts/harness.py approval confirm `
  --type PLAN `
  --subject .harness/plans/PLAN-0001.json `
  --decision APPROVED `
  --approver owner@example.com `
  --basis "Reviewed the exact plan, risks, and verification boundaries" `
  --confirm-fingerprint $planFingerprint `
  --confirmation-id HCONF-PLAN-0001 `
  --confirmation-channel TERMINAL `
  --confirmation-reference "direct owner confirmation" `
  --authorized-action LOCAL_IMPLEMENTATION `
  --authorized-action LOCAL_TESTS `
  --authorized-action DOCUMENTATION `
  --excluded-action PRODUCTION_DEPLOYMENT `
  --excluded-action PRODUCTION_DATA_CHANGE `
  --excluded-action EXTERNAL_WRITE `
  --acknowledge-procedural
```

`--acknowledge-procedural` states that this record does not authenticate the human against a same-privilege process. `HCONF-*` must identify one real confirmation and cannot be reused for a different decision payload. Channel and reference must describe the actual confirmation; they are not authority tokens. For `APPROVED_WITH_CONDITIONS`, provide matching `--condition` and `--condition-ref OI-*` values.

Procedural plans are code-limited to `LOCAL_IMPLEMENTATION`, `LOCAL_TESTS`, and `DOCUMENTATION`. A plan or confirmation containing any other authorized action requires `CRYPTOGRAPHIC` plan assurance. In addition, a task with `PRODUCTION_DEPLOYMENT`, `PRODUCTION_DATA_CHANGE`, `EXTERNAL_WRITE`, or `DESTRUCTIVE_CLEANUP` must declare a current cryptographic approval in `capability_approval_refs`; plan approval alone never authorizes those actions. Every condition on a referenced high-impact approval must be fully resolved before the capability gate opens. `HUMAN_PRIVATE_KEY_ACCESS` is never an agent capability.

Capture the returned `APR-*`, verify it, and then explicitly apply it to the active plan and lifecycle state:

```powershell
python scripts/harness.py approval check APR-0001
python scripts/harness.py gate plan PLAN-0001 --require-approval
python scripts/harness.py plan apply-decision --approval APR-0001
```

Applying a decision is idempotent state materialization; it does not create or upgrade approval authority. Any subject or approval-dependency change requires a new fingerprint and a new human decision.

## Cryptographic external-authority workflow

The authority configuration contains an allowlist of approval types. Both the project assurance policy and external authority mapping must allow a cryptographic request.

### 1. Establish the external authority

The configuration path is fixed and cannot be redirected by an agent or environment variable:

- Windows: `C:\ProgramData\ProjectHarness\authorities\<project-id>.json`
- POSIX: `/etc/project-harness/authorities/<project-id>.json`

For a Windows project `MYPROJ`, an administrator can use a protected layout such as:

```text
C:\ProgramData\ProjectHarness\
  authorities\MYPROJ.json
  trust\MYPROJ.allowed_signers
  ledgers\MYPROJ\
```

The private key belongs in a separate human-only or signing-service location, never under the repository or these public verification directories.

An example authority configuration is:

```json
{
  "schema": "harness.authority/v1",
  "project_id": "MYPROJ",
  "authority_id": "myproj-owner-authority-v1",
  "repository_root": "C:\\workspace\\my-project",
  "protection": "OS_ACL_OR_EXTERNAL_BROKER",
  "signature_namespace": "project-harness",
  "allowed_signers_path": "C:\\ProgramData\\ProjectHarness\\trust\\MYPROJ.allowed_signers",
  "allowed_signers_sha256": "<lowercase sha256 of the allowed-signers file>",
  "decision_ledger_path": "C:\\ProgramData\\ProjectHarness\\ledgers\\MYPROJ",
  "approval_types": [
    "PLAN",
    "CUSTOMER_ACCEPTANCE",
    "PROJECT_CLOSURE",
    "CHANGE",
    "PRODUCTION_DEPLOYMENT",
    "PRODUCTION_DATA_CHANGE",
    "EXCEPTION"
  ]
}
```

The resolved `repository_root` must match the project being checked. The allowed-signers and ledger paths must resolve outside that repository.

An OpenSSH allowed-signers entry binds the exact value passed as `--approver` to the namespace:

```text
owner@example.com namespaces="project-harness" ssh-ed25519 AAAAC3... project-owner
```

Compute and pin its digest in the authority configuration:

```powershell
$signers = "C:\ProgramData\ProjectHarness\trust\MYPROJ.allowed_signers"
(Get-FileHash -LiteralPath $signers -Algorithm SHA256).Hash.ToLowerInvariant()
```

Apply OS ACLs or an external approval broker so that:

- the coding-agent account can read the authority config, allowed signers, and ledger but cannot modify them;
- only the human owner/approval broker can use the private key;
- only the protected installer can append request/signature pairs to the ledger;
- existing ledger entries cannot be rewritten or deleted by agents;
- the harness code used by the authoritative CI/gate is protected from project writers.

The repository initializer writes `.harness/templates/authority-config.example.json` as documentation only. Copying it into the repository does not establish authority.

Verify discovery of the external trust root:

```powershell
python scripts/harness.py doctor
```

`human_approval_authority.state` must be `READY` before preparing a cryptographic request. It may remain unavailable when a plan legitimately uses procedural assurance; that does not authorize any cryptographic approval type.

### 2. Preflight and prepare one decision request

First run the relevant preflight. For a plan:

```powershell
python scripts/harness.py validate --strict
python scripts/harness.py gate plan PLAN-0001
python scripts/harness.py report decision-package PLAN-0001
```

Use the decision package as the single consolidated review surface before choosing a decision. It includes the exact fingerprint, coverage, open items, action limits, preflight outcome, and authority readiness; it is not itself an approval.

Prepare the exact decision request inside the repository. This example explicitly authorizes code/test edits and excludes production deployment:

```powershell
$request = ".harness/decisions/PLAN-0001.request.json"
python scripts/harness.py approval prepare `
  --output $request `
  --type PLAN `
  --subject .harness/plans/PLAN-0001.json `
  --decision APPROVED `
  --approver owner@example.com `
  --basis "Reviewed consolidated plan, scope, schedule, risks, and verification" `
  --authorized-action LOCAL_IMPLEMENTATION `
  --authorized-action LOCAL_TESTS `
  --authorized-action DOCUMENTATION `
  --excluded-action PRODUCTION_DEPLOYMENT `
  --ttl-minutes 60
```

The CLI reads the current protected ledger, allocates the next authority sequence, binds the subject fingerprint, and writes an expiring request. Serialize request preparation/signing: two concurrently prepared requests can claim the same next sequence and create a detectable ledger fork.

For `APPROVED_WITH_CONDITIONS`, add at least one matching pair:

```powershell
--condition "Customer must supply the final accessibility copy" `
--condition-ref OI-0012
```

The condition reference remains enforceable until the open item has a complete propagated resolution.

### 3. Human inspection and SSH signing

The human owner must inspect the request itself, including:

- `project_id`, `authority_id`, sequence, decision ID, and expiry;
- approval type, subject ID/path, and subject fingerprint;
- decision, basis, conditions, and open-item references;
- authorized and excluded actions.

Sign the unchanged request with the protected private key and configured namespace:

```powershell
$privateKey = "C:\ProtectedKeys\MYPROJ-owner-ed25519"
ssh-keygen -Y sign -f $privateKey -n project-harness $request
```

OpenSSH writes `${request}.sig`. Any byte change to the JSON after signing invalidates the signature.

### 4. Install the signed decision in the protected append ledger

This is an external privileged operation by the human owner or approval broker. The project CLI intentionally has no elevated ledger-install command.

The protected installer rechecks the request and signature, confirms that the sequence and decision ID are unused, then appends the exact bytes. One deterministic naming pattern is:

```powershell
$ledger = "C:\ProgramData\ProjectHarness\ledgers\MYPROJ"
$decision = Get-Content -LiteralPath $request -Raw | ConvertFrom-Json
$ledgerName = "{0:D10}-{1}.request.json" -f [int]$decision.authority_sequence, $decision.decision_id
$ledgerRequest = Join-Path $ledger $ledgerName
$ledgerSignature = Join-Path $ledger "${ledgerName}.sig"

Copy-Item -LiteralPath $request -Destination $ledgerRequest
Copy-Item -LiteralPath "${request}.sig" -Destination $ledgerSignature
```

Every ledger request filename must end with `.request.json`, and its adjacent signature must be the same path plus `.sig`. Preserve prior files. The harness re-verifies every ledger signature and detects conflicting sequence or decision-ID forks.

On platforms with an approval broker, perform the same append atomically through the broker rather than granting the coding-agent process write permission.

### 5. Import the protected decision into the project

After installation, import the exact repository request/signature pair:

```powershell
python scripts/harness.py approval record --request $request --signature "${request}.sig"
```

The command succeeds only if the signature is valid, the exact pair exists in the protected ledger, the request has not expired, the external authority allows the type, the subject fingerprint is current, and the request is the latest protected decision for its type/subject. It creates `APR-*` plus immutable snapshots under `.harness/baselines/APR-*/`.

Capture the returned approval ID, then check it and the corresponding gate:

```powershell
python scripts/harness.py approval check APR-0001
python scripts/harness.py gate plan PLAN-0001 --require-approval
python scripts/harness.py plan apply-decision --approval APR-0001
```

Subsequent status checks re-verify the external signer file, its pinned digest, the entire protected ledger, latest sequence, current subject fingerprint, and baseline snapshot hashes. Approval import is not a one-time trust shortcut.

The request TTL bounds how long a signed request may be imported. Once imported, passage of that request expiry alone does not expire the approval; a later protected decision, a changed subject/dependency fingerprint, a damaged snapshot, or invalid external authority makes it non-current.

`approval check` exits `0` only for `CURRENT`. A `STALE` or `SUPERSEDED` decision exits with the stale status code (`3`); other non-current decisions are blocked. Scripts must inspect the exit code and must not treat a printed historical approval as current authority.

## Supersede, reject, or revoke

Record a later `REJECTED`, `REVISION_REQUIRED`, `DEFERRED`, or `REVOKED` decision at the assurance required for that type. A procedural plan uses a new direct confirmation and unique `HCONF-*`; a cryptographic decision uses the same prepare/sign/install/import workflow. The latest repository decision for the type/subject controls and an invalid latest record does not fall back to an older approval; cryptographic decisions additionally require the latest protected authority sequence.

Never delete an old approval or ledger entry to represent reversal. The ordered decision history is part of the evidence.

## Operational boundary

A current plan decision approves only the actions written into that exact decision. An empty action list grants nothing. Plan approval does not imply customer acceptance, production deployment, production data change, exception handling, or project closure. Those use their own exact subjects, cryptographic approval types, capabilities, and gates.

Procedural approval never authenticates a human identity. SSH approval authenticates the protected decision flow only when the config, signer key, ledger, and authoritative harness execution are outside agent write authority. Neither mode makes agent aliases cryptographic identities, and neither can prevent a same-privilege process from modifying an unprotected local checkout; use protected CI/external orchestration for that boundary.
