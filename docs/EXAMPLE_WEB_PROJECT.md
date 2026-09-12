# Example: A Customer Web Project

This walkthrough maps the policy in `AGENTS.md` onto one concrete engagement. An
agency builds a public web site with member login, a product catalogue, and card
payment for a customer, runs it through acceptance, deploys it, and hands it
over. It adds no rules; it shows where each existing rule lands. Record ids and
commands are illustrative. At every point `python scripts/harness.py next` names
the actual step and the command that performs it.

Four roles appear:

| Role | Who | What they decide |
|---|---|---|
| Customer | the client organisation | supplies input, performs UAT, gives final acceptance |
| Project owner | the human lead or PM on the delivering side | approves every PLAN |
| Agents and developers | Codex, Claude Code, people | discovery, planning, implementation, verification |
| Operator or CI | a separately controlled account or pipeline | holds production credentials and performs deployments |

The customer and the project owner are different authorities. The owner's PLAN
confirmation is what lets development start; the customer's acceptance is a
cryptographic boundary at the end. Neither substitutes for the other.

## 1. Intake

Lifecycle: `OPPORTUNITY -> DISCOVERY -> CONTRACTED`

- Copy the harness into the project repository and run `init`. The project is
  in `DISCOVERY` with `current_plan: null`; no PLAN or TASK exists yet.
- Register what the customer supplied as it arrived. The RFP, meeting notes,
  the current site's URL, design mock-ups, and the brand guide become `SRC-*`
  and `ART-*` records with their authority marked (`raw`, `reference`,
  `contract`). Interpretation is recorded separately, so a later dispute can
  compare what was said with what was understood.
- The contract or statement of work is a `SRC-*` with contract authority. It is
  the reference for deciding whether a later request is in scope.
- Supplied HTML/JS mock-ups and office documents are registered but stay
  untrusted active content until a separate safe-execution decision.

```powershell
python scripts/harness.py init --name "Acme storefront"
python scripts/harness.py new source SRC-0001 "Acme RFP 2026-08-14"
python scripts/harness.py new artifact ART-0001 "Design mock-ups v3 (Figma export)"
python scripts/harness.py new source SRC-0002 "Signed SOW"
```

These records are authorized by the user's request alone; no approval is needed
to record what the customer said.

## 2. Requirements and specification

Lifecycle: `SPECIFYING`

- Write `REQ-*` records split into functional, non-functional, operational, and
  security requirements. For this site: member login, product search, card
  payment through the payment gateway, responsive layout, accessibility,
  page-load budget, personal-data handling.
- Write `FUNC-*` records per screen or capability, each with completion
  criteria. Every required criterion names the verification profiles it needs
  and the paths it binds. "Login form validation" might need `STATIC` and
  `BROWSER`; "checkout completes an order" needs `INTEGRATION` and `LIVE_ENV`.
- Anything undecided becomes an `OI-*` with a gate level. An unfinished design
  for the product page is a `G1` that blocks that page's tasks and nothing
  else. An unconfirmed domain name is a `G2` warning that work continues under.
- Questions for the customer sit in `OI-*` as `WAITING_EXTERNAL`. When the
  answer arrives it is registered as a new `SRC-*` and the item is resolved
  with explicit propagation targets.

```powershell
python scripts/harness.py new requirement REQ-0001 "Members authenticate with email and password"
python scripts/harness.py new requirement REQ-0002 "Card payment through the gateway"
python scripts/harness.py new feature FUNC-0001 "Login and session"
python scripts/harness.py new feature FUNC-0002 "Home page"
python scripts/harness.py new feature FUNC-0003 "Checkout"
# author each feature's requirement_refs and at least one completion criterion (AC-FUNC-0001-001, ...)
python scripts/harness.py new open-item OI-0001 "Product page design not yet approved by customer"
```

Still no PLAN. Specification does not need one.

## 3. Planning completion and execution readiness

### 3.1 Planning complete

Author the plan and pass the required planning checks. This milestone does not
require the owner to approve execution. The complete project order is shown in
the [HTML guide](HARNESS_POLICY_REPORT.html).

- Create one PLAN per milestone or sprint: "Sprint 1: authentication and home
  page", "Sprint 2: catalogue and cart", "Sprint 3: checkout and admin". Each
  PLAN declares its workstreams, verification strategy, authorized actions, and
  exclusions.
- Create the TASKs under the PLAN with `--plan`. Each declares its write scope
  (`web/`, `api/`) and locks. Routine TASKs use `LOCAL_IMPLEMENTATION`.
- Plan preflight checks the trace in both directions: every planned REQ has a
  realizing FUNC, every required criterion has an implementing TASK, and no
  TASK leaves the plan's declared boundary.
- `report decision-package` projects the plan, its tasks, requirements, and
  open items into one document for the owner to read.

```powershell
python scripts/harness.py new plan PLAN-0001 "Sprint 1: authentication and home page"
python scripts/harness.py new task TASK-0001 "Login form and session API" --plan PLAN-0001 `
  --feature FUNC-0001 --criterion AC-FUNC-0001-001 --capability LOCAL_IMPLEMENTATION
python scripts/harness.py new task TASK-0002 "Home page layout" --plan PLAN-0001 `
  --feature FUNC-0002 --criterion AC-FUNC-0002-001 --capability LOCAL_IMPLEMENTATION
# author the plan's requirement_refs, feature_refs, and verification_strategy,
# and each task's write_scope (api/auth, web/src/pages/home) and verification
python scripts/harness.py plan sync PLAN-0001
python scripts/harness.py validate --strict
python scripts/harness.py report decision-package PLAN-0001
```

For a planning-only request, report the plan, check results and open items and
stop here. Failed required checks mean the plan needs revision. The decision
package already includes the fingerprint; use it only while its inputs remain
unchanged.

### 3.2 Execution ready

When execution is requested, the owner decides once on that concrete scope.
The agent records the actual response against the reviewed fingerprint and
applies it. No separate approval of "planning complete" is required. Current
lifecycle application uses `DECISION_READY -> APPROVED` with the interim steps
below; these two milestones introduce no new runtime states.

```powershell
python scripts/harness.py approval confirm `
  --type PLAN --subject .harness/plans/PLAN-0001.md --decision APPROVED `
  --approver lead@agency.example --basis "Sprint 1 scope and tasks reviewed" `
  --confirm-fingerprint <fingerprint> --confirmation-id HCONF-plan-0001 `
  --confirmation-channel "sprint planning call" --confirmation-reference "2026-08-20 minutes" `
  --authorized-action LOCAL_IMPLEMENTATION --authorized-action LOCAL_TESTS --authorized-action DOCUMENTATION `
  --acknowledge-procedural
# interim (see RUNTIME_GAPS.md): set current_plan and active_plan in state.json,
# and the project is moved SPECIFYING -> PLANNING -> DECISION_READY with `transition --kind project`
python scripts/harness.py plan apply-decision --approval APR-0001
python scripts/harness.py transition --kind work_item --id TASK-0001 --to READY --agent codex --reason "approved scope ready to execute"
python scripts/harness.py gate task TASK-0001
```

The selected task is execution-ready only when its gate passes. A changed
governed PLAN/TASK fingerprint can invalidate current execution authority;
explanatory body edits alone do not. Ordinary task refinement is not a new
business decision, although the current runtime can force another fingerprint
confirmation. Preserve the original approval as history and report that limit.

With the plan hierarchy in [PLAN_HIERARCHY.md](PLAN_HIERARCHY.md) implemented,
this project would instead hold one root `PLAN-0001` for the whole engagement
and child plans such as `API-001` for the back end, `SCR-001` for screens, and
`PAY-001` for payment, each approved on its own and several executable at
once. Until then the sprint PLANs above are the shape to use.

## 4. Implementation

Lifecycle: `BUILDING`

- Move a TASK to `READY` and run its gate. Only now may files be edited, tests
  run, and commits made. The gate closes on `blocked_by`, an active `G0/G1`
  such as the unapproved product page design, or an overlapping claim.
- A single developer or agent works directly with no claim. When a front-end
  agent and a back-end agent work at the same time, each acquires a claim on
  non-overlapping paths and uses its own Git worktree.
- Commit explicit paths. Before push, fetch the configured remote, inspect
  divergence, and resolve conflicts without discarding either side. A normal
  push to the development branch is routine work under the applied PLAN
  decision; a force push or a push to another branch needs separate explicit
  authorization.
- When the customer asks to change the hero banner, distinguish an in-contract
  correction from changed requirements. For a material change, assess feasibility
  and impact, prepare its trace and plan, then obtain one proceed decision and
  record that same response as the PLAN decision. Task refinement alone needs
  no new business decision. Current fingerprint and reapplication limits remain
  documented in [Runtime gaps](RUNTIME_GAPS.md); do not bypass them or treat
  historical approvals as revoked.
- When work moves from one agent to another mid-task, the sender creates a
  handoff naming the changed files, what was verified and what was not, and the
  next action. The receiver acquires its own claim with that handoff.

```powershell
python scripts/harness.py transition --kind work_item --id TASK-0001 --to READY --agent codex --reason "PLAN-0001 approved"
python scripts/harness.py gate task TASK-0001

# concurrent writers only
python scripts/harness.py claim acquire --agent codex --task TASK-0001 --paths api/auth tests/api/auth
python scripts/harness.py claim acquire --agent claude --task TASK-0002 --paths web/src/pages/home

# implement, then:
python scripts/check_repo.py fast
git add -- api/auth tests/api/auth
git commit -m "Add session API and login validation"
git fetch --prune origin
git push
```

## 5. Verification

Lifecycle: `VERIFYING`

- Unit and integration test runs become `EVD-*` records with `STATIC` or
  `INTEGRATION` profiles, bound to the paths they exercised.
- End-to-end browser runs across the supported browsers and viewports produce
  `BROWSER` evidence.
- A staging deployment produces `LIVE_ENV` evidence. Staging is not production,
  so it needs no cryptographic approval. Keep the deploy credentials in CI, not
  in the agent's hands: an agent that reads the hosting key itself has crossed
  the `SECRET_ACCESS` boundary.
- For a release candidate, submit a `RES-*` and have a different reviewer record
  a `VRD-*`. Results are attempts, not votes; a later failed attempt cannot be
  hidden behind an earlier PASS.
- Keep the completion states distinct. A feature that passed unit tests is
  `STATIC_VERIFIED`, not done. Partial, unrun, or inconclusive checks are not
  PASS.

```powershell
python scripts/harness.py evidence record --agent codex `
  --claim-text "Checkout completes an order with the gateway test card" `
  --support AC-FUNC-0003-001 --profile LIVE_ENV `
  --method "Playwright suite against staging" --environment "staging.acme.example" `
  --expected "order confirmation page with order id" --actual "order confirmation page with order id" `
  --result VERIFIED --ambiguity-level NONE --binding web/src/checkout --binding api/orders

python scripts/harness.py gate feature FUNC-0003
```

## 6. Customer acceptance

Lifecycle: `CUSTOMER_ACCEPTANCE`

- The customer performs UAT on staging. Their feedback is registered as
  `SRC-*`; fixes go through `CR-*` or `OI-*` and back into the PLAN.
- An email saying "looks good" is input, not approval. Final acceptance is a
  `CUSTOMER_ACCEPTANCE` approval with `CRYPTOGRAPHIC` assurance, whose subject
  is the feature being accepted. The agent prepares the request; an authorized
  signer signs it and appends it to the protected ledger; the agent imports it
  and checks currentness. The agent never signs, installs, or infers it.

```powershell
$request = ".harness/decisions/accept-checkout.request.json"
python scripts/harness.py approval prepare --output $request `
  --type CUSTOMER_ACCEPTANCE --subject .harness/features/FUNC-0003.json --decision APPROVED `
  --approver sponsor@acme.example --basis "UAT sign-off on staging build 1.0.0-rc3" `
  --authorized-action CUSTOMER_ACCEPTANCE

# Human or broker only: sign and append to the protected ledger.

python scripts/harness.py approval record --request $request --signature "${request}.sig"
python scripts/harness.py approval check APR-0007
```

## 7. Production deployment

Lifecycle: `DEPLOYING`

- The release TASK carries a high-impact capability, and its
  `capability_approval_refs` must point at a current approval of the matching
  type. A missing, stale, or mismatched reference closes the task gate.
- Each high-risk action is approved separately. A release that ships new code
  and runs a schema migration needs both `PRODUCTION_DEPLOYMENT` and
  `PRODUCTION_DATA_CHANGE`; one does not imply the other.
- The approval does not deploy anything. The operator or CI performs the
  action and returns a receipt, which becomes `LIVE_ENV` evidence. The request
  basis names the exact target and the rollback plan.
- After the deploy, a production smoke run produces fresh `LIVE_ENV` evidence.
  Staging evidence does not carry over.

```powershell
python scripts/harness.py new task TASK-0012 "Deploy release 1.0.0 to production" --plan PLAN-0003 --capability PRODUCTION_DEPLOYMENT
python scripts/harness.py new change CR-0004 "Add orders.payment_reference column"
python scripts/harness.py new task TASK-0013 "Run migration 0007 on production" --plan PLAN-0003 --capability PRODUCTION_DATA_CHANGE

$deploy = ".harness/decisions/deploy-1.0.0.request.json"
python scripts/harness.py approval prepare --output $deploy `
  --type PRODUCTION_DEPLOYMENT --subject .harness/project.json --decision APPROVED `
  --approver lead@agency.example --basis "Release 1.0.0 to prod-eu; rollback is redeploy of 0.9.4" `
  --authorized-action PRODUCTION_DEPLOYMENT

$migrate = ".harness/decisions/migration-0007.request.json"
python scripts/harness.py approval prepare --output $migrate `
  --type PRODUCTION_DATA_CHANGE --subject .harness/changes/CR-0004.json --decision APPROVED `
  --approver lead@agency.example --basis "Additive column; reversible by dropping it" `
  --authorized-action PRODUCTION_DATA_CHANGE

# Human or broker only: sign both and append them to the protected ledger.

python scripts/harness.py approval record --request $deploy --signature "${deploy}.sig"
python scripts/harness.py approval record --request $migrate --signature "${migrate}.sig"
python scripts/harness.py gate task TASK-0012
```

## 8. Closure and maintenance

Lifecycle: `CLOSED -> MAINTAINING`

- The default closure criteria are `DELIVERY`, `HANDOVER`, and
  `MAINTENANCE_READINESS`, and each needs evidence. Delivery is the deployed
  release and its source; handover is documentation, accounts, domain, and
  infrastructure transferred to the customer; maintenance readiness is
  monitoring, backups, and the incident contact path.
- Closure also needs no active `G0/G1`, no outstanding claims, an active
  human-approved plan, and a closure-ready lifecycle state. `report completion`
  shows what is still missing without changing state. A cryptographic
  `PROJECT_CLOSURE` record is required only when the project's policy says so.
- Maintenance requests follow the same path as every other change: `SRC-*`,
  `CR-*`, a TASK in a PLAN, the owner's confirmation, implementation,
  verification, and a signed approval for anything that touches production.

```powershell
python scripts/harness.py report completion
```

## Where the cryptographic boundary lands on a web project

| What happens on the project | Approval type | Subject |
|---|---|---|
| Release to the production host | `PRODUCTION_DEPLOYMENT` | project |
| Schema migration, data backfill, bulk update on the live database | `PRODUCTION_DATA_CHANGE` | change |
| Dropping the legacy tables, deleting the old media bucket, retiring the previous site | `DESTRUCTIVE_ACTION` (task capability `DESTRUCTIVE_CLEANUP`) | change |
| Reading the hosting key, DNS credentials, payment-gateway secret, or OAuth client secret | `SECRET_ACCESS` | change |
| The customer's final sign-off | `CUSTOMER_ACCEPTANCE` | feature |

Each approval permits only the named action on the exact subject. Project
configuration cannot lower any of these to a procedural confirmation. The
subject paths above end in `.json` because that is the current format; after
[RECORD_FORMAT.md](RECORD_FORMAT.md) is implemented they end in `.md`.

## Traps this project will meet

- **A customer request is not execution authority.** "Just fix this now" is
  registered and classified, then becomes a TASK in a PLAN that the owner
  confirms. A hotfix is one TASK on the same path, not an exception to it;
  [WORKFLOW.md](WORKFLOW.md) gives the incident sequence.
- **A blocked design blocks only its screen.** The `G1` on the product page
  stops the product-page tasks. The payment API keeps going.
- **Staging green is not production verified.** After the release the
  `LIVE_ENV` evidence is taken again on production. Completion claims rest on
  current evidence for the environment they claim.
- **The owner's PLAN approval and the customer's acceptance are different
  decisions.** One starts the work; the other ends it. Recording either as the
  other is an invalid record, not a shortcut.
- **The harness is not a sandbox.** Keeping production credentials away from
  the agent and separating reviewers adversarially are jobs for CI or an
  external orchestrator. The harness records and gates those boundaries; it
  does not enforce them at the process level.

See [Workflow](WORKFLOW.md) for the generic path, [Human approval
operations](APPROVALS.md) for the signed flow, [Collaboration](COLLABORATION.md)
for claims and handoffs, and [Data model](DATA_MODEL.md) for the records used
here.
