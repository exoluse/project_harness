# Architecture

The harness separates project truth, live coordination, human decision assurance, protected cryptographic authority, and derived views. Keeping these stores distinct prevents a convenient agent-written file from becoming authenticated approval or acceptance.

```text
Customer and external inputs
  text, contract, document, storyboard, image, HTML/CSS/JS
                 |
                 v
Canonical project model (.harness in the repository)
  source -> requirement -> feature -> completion criterion
                 |                         |
                 v                         v
  open item/change -> plan -> work item -> evidence/result -> review
                 |                                      |
                 +------------------ gates -------------+

Live coordination                         Human decisions
<git-common-dir>/project-harness-runtime  procedural PLAN confirmation, or
  leases, inbox/outbox, acknowledgements    fixed config + signer + ledger
                 |                                      |
                 +--------------- CLI ------------------+
                                      |
                                      v
                             derived human views
                             HANDOFF.md, status, trace
```

## Canonical project records

Canonical data is stored as small JSON records under `.harness/`. JSON keeps the vendored CLI free of third-party runtime dependencies and lets every supported agent parse the same representation. `validate` enforces the JSON Schemas under `schemas/` with the dependency-free schema subset used by this distribution, then applies cross-record references, latest-attempt rules, bindings, and fingerprints.

The principal trace is:

```text
SRC-* -> REQ-* -> FUNC-* -> criterion ID -> TASK-*
                                      |        |
                                      v        v
                                   EVD-* <- RES-* -> VRD-*
```

Requirements retain acceptance criteria. Features turn them into implementable completion criteria. Each required criterion declares a verification plan, required profile, required bindings, and eligible evidence references. Work items declare which features and criteria they implement.

## Adaptive input convergence

There is no single mandatory input order:

- A customer requirement may produce functional design before a UI exists.
- A storyboard may produce candidate screens, actions, and features before the textual requirement is confirmed.
- HTML, CSS, or JavaScript may be registered later as an untrusted artifact and mapped to existing UI-dependent criteria.
- A complex or conflicting request remains an open item/change analysis instead of being guessed into the active baseline.

Dependency references determine which work blocks. The absence of UI is not a global stop unless a `G0` decision says it is.

## Fingerprints and currentness

Approved subjects expose fingerprinted fields. A human approval stores the exact subject fingerprint and immutable baseline snapshots of the subject and its declared approval dependencies. If the live subject or an approval dependency such as the assurance policy changes, the approval becomes stale.

Completion-criterion fingerprints cover the normative statement, verification plan, required profiles, and required bindings. Evidence must carry the current criterion fingerprint and current hashes for every required file/directory binding. Directory hashes are deterministic tree hashes.

Results bind the task fingerprint, plan fingerprint, base/head commit, exact changed-file states, and evidence fingerprints into a build fingerprint. Reviews bind both the result and build fingerprints. Gates use the numerically latest result for a task and the latest review of that result. Closure-grade integration additionally requires the result head to descend from its recorded base, the current integration HEAD to descend from the result head, and the committed path states to remain exact; an unrelated commit with the same tree is not accepted as integration.

## Human decision and authority plane

Project policy selects the minimum approval assurance. `PROCEDURAL` is supported only for `PLAN` and binds an explicit human confirmation to the exact fingerprint, decision, actions, and confirmation provenance. It is stored as repository provenance and does not authenticate the human against a same-privilege process; agents may prepare the command but must not execute it for the human.

Every other approval type remains `CRYPTOGRAPHIC`. Cryptographic approval verification does not accept repository or environment redirects for its trust root. The configuration location is fixed in code:

- Windows: `C:\ProgramData\ProjectHarness\authorities\<project-id>.json`
- POSIX: `/etc/project-harness/authorities/<project-id>.json`

That configuration is bound to the project ID and resolved repository root. It points outside the repository to a pinned SSH allowed-signers file and a protected decision-ledger directory. Every cryptographic approval status check re-verifies its signature, ledger presence, sequence, latest-decision status, subject fingerprint, and baseline snapshots. See [Human approval operations](APPROVALS.md).

## Live coordination plane

For a Git repository, claims, mailboxes, acknowledgements, handoff acceptances, ID allocation, and mutex data live under:

```text
<git-common-dir>/project-harness-runtime/
```

All linked worktrees therefore see the same active leases and inbox/outbox. Durable handoff/result/review records remain in `.harness/`; `HANDOFF.md` is only the latest rendered view.

Claims contain normalized path prefixes and case-normalized logical locks. Ancestor and descendant paths conflict. `**` is a workspace-exclusive path. Logical locks protect resources such as `database-schema`, `public-api`, or `release-manifest` even when their files differ.

## Git and no-Git modes

Git mode captures base/head commits and actual tracked, staged, and untracked changes. Separate worktrees plus the shared runtime enable parallel non-overlapping claims.

No-Git mode captures a full file-state snapshot, rejects changes outside the active claim, and permits only one active writer. It is useful for bootstrap coordination, but its result lacks the committed baseline required by task-dependency and project-closure assessment. Closure-grade integration therefore requires Git.

## Trust boundary

Agent IDs, reviewer IDs, and mailbox routing are procedural coordination fields. They prevent accidental self-review by label; they do not authenticate a process against a hostile same-privilege peer. Likewise, an agent that can replace the harness source can bypass a local invocation. Use an external orchestrator or protected CI runner, a protected harness version, distinct credentials, and OS-enforced authority files for adversarial or regulated enforcement.
