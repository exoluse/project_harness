# Security

The harness is a coordination and gate engine, not a sandbox. Mutable repository data cannot authenticate a human or protect itself from a same-privilege process.

## Authority boundary

Discovery may begin without PLAN/TASK placeholders. Before executable work, a current PLAN and TASK require a direct human PLAN decision that `plan apply-decision` has materialized. An explicit user request is not approval and cannot authorize routine development operations, commits, fetch, conflict resolution, or a normal push. Cryptographic human approval is code-forced for:

- production deployment;
- production data changes;
- destructive operations;
- secret or protected-credential access;
- final customer acceptance.

Project configuration cannot lower these categories to procedural assurance. `HUMAN_PRIVATE_KEY_ACCESS` is never an agent capability. PLAN confirmation, exceptions, ordinary changes, and project-closure bookkeeping are not cryptographic execution permits unless separately configured.

## Trust locations

| Store | Purpose |
|---|---|
| Repository | code, plans, optional records, reviewable provenance |
| Git common runtime | transient claims, mutexes, mailboxes |
| Protected external authority | signer allowlist, private-key boundary, append decision ledger |
| Protected CI/orchestrator | hostile separation and regulated enforcement |

Windows authority config: `C:\ProgramData\ProjectHarness\authorities\<directory>-<root-digest>.json`

POSIX authority config: `/etc/project-harness/authorities/<directory>-<root-digest>.json`

The name is derived from the repository root the configuration is bound to; `doctor` reports the exact path.

## Operational rules

- Never put tokens, cookies, passwords, connection strings, private keys, or protected authority files in records, logs, evidence, results, or handoffs.
- Inspect untrusted code and documents before execution; do not combine them with secrets or production credentials.
- Commands stored in mutable records are declarative and are never auto-executed.
- Before a high-risk action, verify exact scope, target environment, current cryptographic approval, conditions, and rollback/reconciliation needs.
- Approval does not execute the action. A separately controlled operator or adapter performs it and returns a receipt when evidence is needed.
- Same-string reviewer checks are procedural only. Use protected CI or external orchestration for genuine adversarial separation.
