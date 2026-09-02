# Project Agent Harness

Project Agent Harness is a repository-native control plane for projects performed by humans and AI agents. It connects customer input, requirements, feature contracts, plans, approvals, bounded work, evidence, changes, delivery, and maintenance without treating an agent's claim as human authorization.

Codex, Claude Code, and other agents use the same JSON records and command surface. They may alternate through an exact handoff or work in separate Git worktrees with non-overlapping claims.

## What the harness enforces

- The lifecycle is adaptive: inputs may arrive in different orders, while every implementation path converges on traceable requirements and completion evidence.
- The trace is `source -> requirement -> feature -> completion criterion -> work item -> result/evidence -> review`.
- `G0`-`G3` open items stay active until their resolution is complete and propagated. Blocking gates fail closed.
- Required criteria declare verification profiles and file or directory bindings. Missing, ambiguous, partial, failed, stale, or unrelated evidence cannot complete them.
- Plan and human approval records are bound to canonical SHA-256 fingerprints. A changed subject invalidates the affected approval.
- Approval assurance is policy-driven. A project may allow explicit `PROCEDURAL` confirmation for `PLAN`, while production, external, exception, customer-acceptance, closure, and other high-risk decisions remain `CRYPTOGRAPHIC` through the fixed external SSH authority and protected ledger.
- Procedural plans are limited to local implementation, local tests, and documentation. High-impact task capabilities require explicit current cryptographic approval references in addition to plan approval.
- Claims prevent overlapping path or logical-resource writers. Git common-directory leases and mailboxes coordinate separate worktrees.
- A handoff records exact changed-file states and must be accepted explicitly. A submitted result is terminal for that work attempt and releases its claim.
- The latest result attempt and its latest review determine task readiness; an older PASS cannot hide a newer failed or incomplete attempt.
- `IMPLEMENTED`, `STATIC_VERIFIED`, `INTEGRATION_VERIFIED`, `BROWSER_VERIFIED`, `LIVE_ENV_VERIFIED`, `CUSTOMER_ACCEPTED`, and `CLOSED` remain distinct.

## Lifecycle

The state vocabulary covers the whole customer project:

```text
OPPORTUNITY -> DISCOVERY -> CONTRACTED -> SPECIFYING -> PLANNING
-> DECISION_READY -> APPROVED -> BUILDING -> VERIFYING
-> CUSTOMER_ACCEPTANCE -> DEPLOYING -> CLOSED -> MAINTAINING
```

This is not a forced waterfall. For example, backend specification can continue while a missing storyboard blocks only the UI-dependent criteria and tasks. A later storyboard, image, HTML, CSS, or JavaScript bundle is registered as an untrusted source/artifact, impact-assessed, and incorporated through a new version where needed.

See [Project workflow](docs/WORKFLOW.md) for the gate-by-gate sequence.

## Initialize a project

From this harness repository, initialize another repository with the supported script entrypoint:

```powershell
python scripts/harness.py init C:\workspace\my-project --project-id MYPROJ --name "My Project"
Set-Location C:\workspace\my-project
git init
git add .
git commit -m "Initialize project harness"
```

The generated project vendors the dependency-free Python runtime under `.harness/tooling/`, copies the enforced schemas, shared agent policies, start prompts, and operator documentation, and therefore runs its own `scripts/harness.py` without installing this package. A generated project can initialize another equally self-contained project.

`init --force` is a repair operation, not a reset. It requires the supplied project ID and name to match the existing canonical project record exactly, preserves `project.json`, `state.json`, and all project records, and refreshes only the distributed runtime plus missing scaffold files. Use governed lifecycle and change commands for project metadata changes.

Before recording a cryptographic human approval, an administrator must establish the external authority and ledger described in [Human approval operations](docs/APPROVALS.md). A project whose policy permits procedural `PLAN` assurance can approve a plan without that trust root, but the project owner must personally run the exact confirmation; an agent cannot do so on the owner's behalf.

## Daily commands

Run these from an initialized project root:

```powershell
python scripts/harness.py doctor
python scripts/harness.py status
python scripts/harness.py validate --strict
python scripts/harness.py trace REQ-0001
python scripts/harness.py report decision-package PLAN-0001
python scripts/harness.py report completion
python scripts/check_repo.py fast
python scripts/check_repo.py full
```

`scripts/check_repo.py` defaults to `full`. The `fast` tier provides short contract-focused feedback; only `full` runs the entire test discovery. Both tiers compile code, run their declared tests, and finish with strict harness validation. The script executes only fixed repository checks. Verification strings stored in plans, results, or handoffs are records; the harness does not execute mutable project JSON as commands.

`report decision-package` assembles the plan fingerprint, preflight, requirement-feature-criterion-task coverage, workstreams, action boundaries, unresolved items, configured assurance readiness, and available decisions for one consolidated human review. `report completion` keeps feature gates, technical closure preflight, and fully authorized closure separate; it exits blocked until authorized closure truly passes.

For a policy that permits procedural plan assurance, the human owner first copies the current fingerprint from `fingerprint`, checks the exact decision and action boundaries, and personally runs `approval confirm`. The acknowledgment records provenance only; it is not cryptographic identity authentication. Apply the returned decision explicitly before task work starts:

```powershell
$planFingerprint = python scripts/harness.py fingerprint .harness/plans/PLAN-0001.json
python scripts/harness.py approval confirm --type PLAN --subject .harness/plans/PLAN-0001.json --decision APPROVED --approver owner@example.com --basis "Reviewed the exact plan" --confirm-fingerprint $planFingerprint --confirmation-id HCONF-PLAN-0001 --confirmation-channel TERMINAL --confirmation-reference "direct owner confirmation" --authorized-action LOCAL_IMPLEMENTATION --authorized-action LOCAL_TESTS --authorized-action DOCUMENTATION --excluded-action PRODUCTION_DEPLOYMENT --acknowledge-procedural
python scripts/harness.py approval check APR-0001
python scripts/harness.py plan apply-decision --approval APR-0001
```

Do not reuse a fingerprint after any approval dependency changes. Use the cryptographic prepare/sign/install/import workflow for assurance levels or approval types that do not permit procedural confirmation.

## Codex and Claude Code flow

The coordinator dispatches an approved, startable task:

```powershell
python scripts/harness.py dispatch --task TASK-0001 --to-agent claude --issued-by coordinator --instructions "Implement the declared criteria only"
python scripts/harness.py mailbox list --box inbox --agent claude
```

The worker acquires the exact write scope, then chooses one terminal path for the attempt:

```powershell
python scripts/harness.py claim acquire --agent claude --task TASK-0001 --paths src/example.py tests/test_example.py

# Continue the same task in Codex. This writes HOF-0001 and releases the Claude claim.
python scripts/harness.py handoff create --claim CLM-0001 --from-agent claude --to-agent codex --task TASK-0001 --summary "Implementation ready for continuation" --changed-file src/example.py --changed-file tests/test_example.py --verification "python -m unittest tests.test_example::PASS" --unverified "Browser behavior not exercised" --next-action "Inspect the diff and continue TASK-0001"

# Codex accepts the exact handoff state while acquiring its new claim.
python scripts/harness.py claim acquire --agent codex --task TASK-0001 --paths src/example.py tests/test_example.py --handoff HOF-0001
```

Alternatively, the worker submits a result:

```powershell
python scripts/harness.py result submit --claim CLM-0002 --agent codex --summary "Task implementation complete" --changed-file src/example.py --changed-file tests/test_example.py --verification "python -m unittest tests.test_example::PASS" --evidence EVD-0001 --limitation "No production deployment performed"
python scripts/harness.py mailbox list --box outbox --agent codex
python scripts/harness.py review record --result RES-0001 --reviewer claude --decision PASS --basis "Diff and declared checks independently reviewed" --check "python -m unittest tests.test_example"
```

`result submit` releases the claim. Further edits require a new startable attempt and a new claim. Reviewer names are procedural provenance, not cryptographic identities; use an external orchestrator or protected CI identity boundary when hostile same-privilege separation matters. See [Collaboration](docs/COLLABORATION.md).

## Git boundary

No-Git mode can serialize one claim and detect changes from a full workspace snapshot, so it is useful for early coordination. It cannot produce the committed base/head evidence required by dependency and project-closure gates. Use a Git repository, commits, and isolated worktrees for closure-grade integration and parallel writers.

## Sources of truth

- Canonical project records: `.harness/`
- Shared live leases and agent mailboxes in Git projects: `<git-common-dir>/project-harness-runtime/`
- Cryptographic human approval authority on Windows: `C:\ProgramData\ProjectHarness\authorities\<project-id>.json`
- Cryptographic human approval authority on POSIX: `/etc/project-harness/authorities/<project-id>.json`
- Human-readable current handoff view: `HANDOFF.md`

The external authority configuration, allowed signers, private keys, and decision ledger for `CRYPTOGRAPHIC` assurance must not be stored in or made writable from the project repository. A repository `PROCEDURAL` plan confirmation is intentionally weaker provenance and must never be described as authenticated human identity.

The current CLI has no built-in production executor. It governs capability and approval records; a separately controlled deployment/messaging/data adapter must perform any authorized external action and return evidence.

## Documentation

- [Constitution](docs/CONSTITUTION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Project workflow](docs/WORKFLOW.md)
- [Human approval operations](docs/APPROVALS.md)
- [Codex and Claude Code collaboration](docs/COLLABORATION.md)
- [Data model](docs/DATA_MODEL.md)
- [Security boundaries](docs/SECURITY.md)

The repository implements the shared protocol; merely detecting both CLIs is not proof that a live Codex/Claude two-model session has been exercised.
