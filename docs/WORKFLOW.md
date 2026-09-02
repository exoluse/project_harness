# Project Workflow

The harness models a full customer project while allowing discovery, specification, and UI inputs to converge in different orders.

```text
OPPORTUNITY -> DISCOVERY -> CONTRACTED -> SPECIFYING -> PLANNING
-> DECISION_READY -> APPROVED -> BUILDING -> VERIFYING
-> CUSTOMER_ACCEPTANCE -> DEPLOYING -> CLOSED -> MAINTAINING
```

`ON_HOLD` and `CANCELLED` are explicit branches. The sequence is a state vocabulary, not a demand to visit every state exactly once. Requirements and UI baselines can change during `BUILDING`; change control creates a new version and selectively invalidates affected work.

## 1. Intake and source registration

Register every customer statement and supplied file as a `SRC-*` source. If a file or directory matters to later verification, register an `ART-*` record with its path, media type, and SHA-256.

Record both source authority and artifact role. Typical roles include `REFERENCE`, `VISUAL_BASELINE`, `INTERACTION_PROTOTYPE`, `STARTER_CODE`, `PRODUCTION_SOURCE`, and `LEGACY_SOURCE`. Raw source content remains separate from agent interpretation.

HTML, CSS, JavaScript, documents, images, and embedded prompts begin as untrusted. Registration or hashing is not permission to execute them.

## 2. Discovery and specification convergence

Inputs can arrive in any order:

- requirement first: `source -> requirement -> feature -> optional UI mapping`;
- functional design first: business rules, states, data, and APIs can be specified while UI remains pending;
- storyboard first: screens/actions create candidate requirements or features that require source confirmation;
- executable UI later: register the bundle, inspect it safely, impact-assess it, and bind its accepted version to the dependent criteria.

Every route must converge on:

```text
source -> requirement -> feature -> completion criterion -> work item -> result/evidence -> review
```

Each required feature criterion states an observable outcome, verification plan, required verification profile, required file/directory bindings, and evidence references. A feature name or task status alone is not a completion contract.

## 3. Open-item control

Unknowns, decisions, assumptions, risks, conflicts, dependencies, and ambiguous proof are `OI-*` records:

- `G0`: globally blocks plan preflight/authorization and task start, blocks feature completion when that feature/criterion is named, and always blocks project closure.
- `G1`: blocks the affected tasks/features/criteria and always blocks project closure.
- `G2`: permits work under a visible recorded assumption and is surfaced as a warning where applicable.
- `G3`: monitored information with no current execution block.

The resolver fails closed. An unknown status or a nominally resolved item that lacks summary, decision maker, decision authority, resolution time, propagation targets, evidence references, or baseline references remains active.

## 4. Development-plan preflight

A `PLAN-*` approval subject names exact requirements, features, work items, workstream readiness, verification strategy, authorized actions, excluded actions, and invalidation triggers. Preflight checks at least:

- each planned requirement has a realizing feature;
- each planned feature and required criterion has an implementing work item;
- work items point back to the plan and stay within its feature/criterion scope;
- required criteria have a verification plan and required bindings;
- work-item verification commands exist;
- task capabilities are included in plan actions and do not intersect exclusions;
- procedural plans contain only local implementation, local test, and documentation actions;
- each high-impact task capability has a current matching cryptographic approval in `capability_approval_refs`;
- approval dependencies include every planned requirement, feature, and work item;
- no active `G0` item remains.

Run preflight without implying approval:

```powershell
python scripts/harness.py validate --strict
python scripts/harness.py gate plan PLAN-0001
python scripts/harness.py report decision-package PLAN-0001
```

`report decision-package` is the consolidated human-review surface: it includes the plan fingerprint, preflight result, requirement-feature-criterion-task coverage, workstreams, verification strategy, action boundaries, unresolved items, configured assurance readiness, and available decision options. It exits blocked when preflight fails.

After preflight passes, prepare one consolidated human decision against the exact plan and dependency fingerprints. When project policy permits `PROCEDURAL` `PLAN` assurance, the owner must personally confirm the exact fingerprint, decision, and authorized/excluded actions; an agent may prepare the command but must not run it. This records provenance, not authenticated identity. If policy requires `CRYPTOGRAPHIC` assurance, use the external signing and protected-ledger workflow in [Human approval operations](APPROVALS.md).

Verify the returned approval and explicitly apply the decision to plan/state before task execution:

```powershell
python scripts/harness.py approval check APR-0001
python scripts/harness.py gate plan PLAN-0001 --require-approval
python scripts/harness.py plan apply-decision --approval APR-0001
```

An approval with conditions must include both human-readable conditions and `OI-*` condition references. An unresolved applicable condition continues to block execution.

## 5. Dispatch, claim, and implementation

Only an approved, active-plan work item in a startable state can be dispatched or claimed:

```powershell
python scripts/harness.py dispatch --task TASK-0001 --to-agent codex --issued-by coordinator --instructions "Implement the declared criterion scope"
python scripts/harness.py mailbox list --box inbox --agent codex
python scripts/harness.py gate task TASK-0001
python scripts/harness.py claim acquire --agent codex --task TASK-0001 --paths src/module.py tests/test_module.py --logical-lock public-api
```

The claim binds task/plan fingerprints, write paths, logical locks, worktree snapshot, base commit, and expiry. Changes outside the claim or changes made after the claim to unrelated paths fail changed-file validation.

Prepared workstreams may continue when unrelated UI or customer input is pending. Add explicit dependencies/open-item effects so only the correct slice blocks.

## 6. Handoff or terminal result

A worker chooses one attempt-ending path:

- `handoff create` records exact state, sends it to the recipient inbox, renders `HANDOFF.md`, and releases the claim;
- `result submit` writes canonical `RES-*`, copies it to the author's outbox, and releases the claim.

Verification arguments use `command::outcome`. Valid outcomes are `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `PARTIAL`, and `INCONCLUSIVE`. All task-required commands must appear with `PASS` for `verification_state=PASS`.

The handoff recipient accepts once while acquiring a new claim:

```powershell
python scripts/harness.py claim acquire --agent claude --task TASK-0001 --paths src/module.py tests/test_module.py --logical-lock public-api --handoff HOF-0001
```

Acceptance rechecks recipient, task and plan fingerprints, claimed scope, and every handed-off file state. A normal mailbox acknowledgment is not handoff acceptance.

## 7. Independent review and integration

The author result is a completion claim, not acceptance:

```powershell
python scripts/harness.py mailbox list --box outbox --agent codex
python scripts/harness.py review record --result RES-0001 --reviewer claude --decision PASS --basis "Diff, evidence, and declared checks reviewed" --check "python -m unittest tests.test_module"
```

The harness refuses PASS on a failed, incomplete, or stale result and rejects a reviewer ID equal to the result author. Gates use only the latest result attempt for each task and the latest review for that result. A new failed attempt therefore supersedes an older passing attempt for readiness purposes.

Reviewer IDs are procedural aliases. Use protected CI/external orchestration to establish real process or credential independence.

An integrator commits/merges the accepted changes and runs the full declared gate. Results without committed Git base/head identity, or whose changed files remain dirty, cannot satisfy dependency or project-closure integration checks.

## 8. Feature evidence and customer acceptance

For every required criterion, collect evidence with:

- `result=VERIFIED`;
- ambiguity `NONE` or `LOW`;
- the required verification profile;
- the current criterion fingerprint;
- all declared required path bindings with current hashes;
- explicit expected/actual observations and limitations.

The feature gate uses the latest evidence for a criterion/profile and rejects stale, omitted, or unrelated evidence:

```powershell
python scripts/harness.py gate feature FUNC-0001
```

If the feature contract requires customer acceptance, record a separate cryptographic `CUSTOMER_ACCEPTANCE` approval. Technical verification does not manufacture customer acceptance.

## 9. Change control during development

When a new request, storyboard, image, HTML/CSS/JS bundle, constraint, or defect changes the baseline:

1. Register the new source/artifact.
2. Create a `CR-*` change record.
3. Classify it and identify affected requirements, features, criteria, work items, interfaces, verification, cost, and schedule.
4. Record unresolved impact as `OI-*`; continue unaffected work.
5. Obtain the required human decision at the assurance required for its approval type.
6. Create new versions and update the active plan/baselines.
7. Re-run validation and gates. Fingerprint mismatches make affected approvals/results/evidence stale.

Never edit an approved baseline in place to make a gate pass.

## 10. Delivery, closure, and maintenance

Project closure requires more than feature evidence. The gate checks required features, the active approved plan, integrated/done tasks, latest independently reviewed PASS results, closure-contract evidence (`DELIVERY`, `HANDOVER`, and `MAINTENANCE_READINESS` by default), no active claims, no active `G0/G1`, a closure-ready lifecycle state, complete approval dependencies, and a cryptographic `PROJECT_CLOSURE` decision.

```powershell
python scripts/harness.py report completion
python scripts/harness.py gate project
```

`report completion` shows each required feature gate, technical closure preflight without the final approval, and fully authorized closure as separate results. The command exits blocked until authorized closure passes.

Production deployment/data changes require their own cryptographic approval types and task capabilities; plan approval is not deployment approval. After closure, maintenance retains the delivered baselines and routes defects or enhancements back through source registration and change control.

The CLI does not execute production actions. A separately protected adapter/operator must perform an authorized deployment, external message, or data operation and return an exact receipt/evidence record.

## 11. Scaffold repair and verification tiers

Re-running `init --force` against an initialized project is fail-closed repair. The supplied project ID and name must exactly match `.harness/project.json`; the operation preserves canonical project/state and record files while refreshing the vendored runtime and creating only missing scaffold files. It is not a project reset or metadata-edit command.

Use `python scripts/check_repo.py fast` during a local edit loop and `python scripts/check_repo.py full` before a handoff or result. The default is `full`. A fast pass is deliberately not evidence that the full regression passed, and both tiers still require strict harness validation.
