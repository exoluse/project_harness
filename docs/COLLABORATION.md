# Codex, Claude Code, and Multi-Agent Collaboration

Agents are assigned bounded task roles rather than permanent powers. Codex may implement and Claude Code may review, or the direction may be reversed. A coordinator owns dispatch and an integrator owns shared merges/full gates when the plan says so.

The protocol supports safe alternating or parallel work. It does not claim that two installed CLIs have actually completed a live cross-model session.

## Shared runtime

In a Git repository, all worktrees resolve the same live coordination root:

```text
<git-common-dir>/project-harness-runtime/
  leases/
  mailboxes/inbox/<agent>/
  mailboxes/outbox/<agent>/
  mailboxes/acks/<agent>/
  handoff-acceptances/
```

Claims, mailbox copies, acknowledgements, and handoff acceptance are runtime coordination, not committed project truth. Durable `HOF-*`, `RES-*`, and `VRD-*` records remain under `.harness/`. `HANDOFF.md` is a rendered current view.

In no-Git mode the runtime falls back to `.harness/runtime/`, only one active claim is permitted, and a full workspace snapshot detects out-of-claim changes. Because no-Git results have no committed base/head identity, they cannot satisfy dependency or project-closure integration checks.

## Dispatch and inbox

The coordinator can dispatch only a task whose task-start gate passes:

```powershell
python scripts/harness.py dispatch `
  --task TASK-0001 `
  --to-agent claude `
  --issued-by coordinator `
  --instructions "Implement only the declared feature and criterion scope"
```

The recipient reads and optionally acknowledges its mailbox:

```powershell
python scripts/harness.py mailbox list --box inbox --agent claude
python scripts/harness.py mailbox ack --box inbox --agent claude --id DSP-0001
```

Acknowledgment only hides the item from the default listing. It does not approve the plan, start work, acquire ownership, or accept a handoff.

## Acquire a claim

Before writing, re-run the task gate and acquire a subset of the work item's declared scope:

```powershell
python scripts/harness.py gate task TASK-0001
python scripts/harness.py claim acquire `
  --agent claude `
  --task TASK-0001 `
  --paths src/service.py tests/test_service.py `
  --logical-lock public-api `
  --ttl-minutes 120
```

The lease binds:

- agent and work item;
- task and active-plan fingerprints;
- normalized path prefixes and logical locks;
- base commit and exact worktree;
- acquisition snapshot and expiry;
- required verification commands.

Overlapping path ancestors/descendants or logical locks conflict across all linked worktrees. Dirty paths inside the request must have been explicitly acknowledged by the work item or an exact handoff; unowned dirty work remains `USER_OR_UNKNOWN`.

Refresh a current claim before expiry:

```powershell
python scripts/harness.py claim refresh CLM-0001 --agent claude --ttl-minutes 120
```

## Sequential handoff

```text
approved TASK -> sender claim -> bounded edits/checks -> HOF record
-> sender claim released -> recipient exact-state acceptance/new claim
-> continuation or independent review
```

The sender declares every actual changed path and at least one exact `command::outcome`:

```powershell
python scripts/harness.py handoff create `
  --claim CLM-0001 `
  --from-agent claude `
  --to-agent codex `
  --task TASK-0001 `
  --summary "API slice implemented; integration still pending" `
  --changed-file src/service.py `
  --changed-file tests/test_service.py `
  --verification "python -m unittest tests.test_service::PASS" `
  --unverified "No browser or production execution" `
  --risk "Shared consumer has not been integration-tested" `
  --next-action "Inspect the diff, accept HOF-0001, and run the integration test"
```

Handoff creation stores file hashes/states, copies the record to the recipient inbox, updates `HANDOFF.md`, and releases the sender's claim. It is terminal for that claim.

The recipient must accept the handoff while acquiring a fresh claim:

```powershell
python scripts/harness.py claim acquire `
  --agent codex `
  --task TASK-0001 `
  --paths src/service.py tests/test_service.py `
  --logical-lock public-api `
  --handoff HOF-0001
```

Acceptance is allowed exactly once. It rejects the wrong recipient/task, stale task or plan fingerprints, paths outside the new claim, or any changed handed-off file state.

## Terminal worker result

When an attempt is ready for review rather than continuation, submit a result:

```powershell
python scripts/harness.py result submit `
  --claim CLM-0002 `
  --agent codex `
  --summary "TASK-0001 implementation complete" `
  --changed-file src/service.py `
  --changed-file tests/test_service.py `
  --verification "python -m unittest tests.test_service::PASS" `
  --evidence EVD-0001 `
  --limitation "Production deployment not performed"
```

Submission writes canonical `RES-*`, copies it to the author's outbox, records task/plan/build/evidence fingerprints, and releases the claim. It is terminal for that attempt. The author cannot continue editing under the released claim; new work requires a startable new attempt and claim.

Read results from the producing agent's outbox:

```powershell
python scripts/harness.py mailbox list --box outbox --agent codex
python scripts/harness.py mailbox ack --box outbox --agent codex --id RES-0001
```

## Latest-attempt review

A result is a claim, not acceptance. A differently named reviewer records an explicit verdict:

```powershell
python scripts/harness.py review record `
  --result RES-0001 `
  --reviewer claude `
  --decision PASS `
  --basis "Reviewed current diff, evidence bindings, and test output" `
  --check "python -m unittest tests.test_service"
```

Valid verdicts are `PASS`, `CHANGES_REQUIRED`, `REJECTED`, and `INCONCLUSIVE`. PASS is refused if result verification is failed/incomplete or its task, plan, changed files, evidence, or build fingerprint is stale.

Readiness always uses the numerically latest `RES-*` for the task and then the latest `VRD-*` for that result. Consequences:

- an older PASS cannot compensate for a newer FAIL or incomplete result;
- reviewing an old attempt does not approve a newer attempt;
- changing a bound result file/evidence invalidates its review/currentness;
- task dependencies and project closure require a current latest PASS plus committed Git integration.

## Parallel worktrees

For true parallel writes:

1. Create one Git worktree/branch per writer.
2. Define disjoint work items, path scopes, and logical locks.
3. Acquire claims; shared Git-common-dir leases expose conflicts across worktrees.
4. Submit exact handoffs/results and independent reviews.
5. Give a designated integrator the shared files/merge logical locks.
6. Commit the integration and run the plan's full verification gate.

Formatters, generated clients, lockfiles, migrations, schema registries, public APIs, and release manifests often touch shared state even when the initial source paths differ. Model them with a common logical lock or serialize them.

## Expiry and recovery

Do not silently steal an expired lease. Inspect processes, worktree, diff, outbox, and possible external side effects, then record recovery:

```powershell
python scripts/harness.py claim recover CLM-0001 --agent coordinator --reason "Owner process ended; diff and external effects inspected"
```

Recovery marks the old claim abandoned. It does not automatically take ownership; acquire a new claim after resolving dirty-path ownership.

## Identity boundary

Agent strings such as `codex`, `claude`, or `reviewer-2` are normalized routing/provenance labels. The local harness prevents accidental same-label self-review, but a same-privilege process can choose another label. When independent review is a security/compliance property, an external orchestrator must authenticate agent processes, isolate credentials/worktrees, control the harness version, and attest who ran each review.

Human approval uses a separate cryptographic external authority; it does not turn agent IDs into authenticated identities.
