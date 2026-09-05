# Plan Hierarchy

Status: **decided on 2026-09-06, not yet implemented.** The runtime today knows
one level of PLAN and one `state.active_plan`. This document is the policy
decision and the specification the runtime change will implement, under
`harness.plan/v2` and `harness.state/v2`. Until that change lands, projects use
single-level PLANs exactly as `AGENTS.md` describes; nothing here weakens the
PLAN gate in the meantime.

## Why

A project of any size plans in more than one dimension at once. A web project
has back-end work, screens, infrastructure, and cross-cutting features such as
payment, each moving at its own pace with its own people. Today that forces a
choice between one large PLAN that must be re-approved on every change, and a
sequence of PLANs of which only one can be executable at a time. Neither fits
concurrent workstreams.

## Shape

A PLAN may have child PLANs. A child names its parent; a parent's list of
children is derived. The root of a tree is a `PLAN-*` record; every child
carries a category prefix the project declares, so the tree reads as the
project is organised:

```text
PLAN-0001  Acme storefront                 root   boundary approval
├─ API-001  Back-end API                    branch boundary approval
│  ├─ API-002  API sprint 1                 leaf   execution approval, active
│  └─ API-003  API sprint 2                 leaf   draft
├─ SCR-001  Screens                         branch boundary approval
│  └─ SCR-002  Web sprint 1                 leaf   execution approval, active
└─ PAY-001  Payment integration             leaf   execution approval, active
```

Every node is a `plan` record in `.harness/plans/`, written as Markdown with
strict front matter like today. Ids do not encode depth; the tree is defined by
`parent_plan_id` alone.

## Rules

1. **Branch or leaf.** A plan with children holds no TASKs; a plan with TASKs
   has no children. A root with TASKs and no children is a valid single-level
   plan and is what every existing project has. Mixing fails validation.
2. **Identifiers.** Root plans are `PLAN-NNNN`. Child plans are
   `<CATEGORY>-NNN`, where `CATEGORY` is two to eight capital letters declared in
   `project.json` under `plan_categories`, and numbering runs per category from
   `001`. TASK ids stay `TASK-NNNN` and remain global.
3. **Reserved prefixes.** A category may not be one of the record prefixes the
   harness already uses: `AC`, `APR`, `ART`, `CLM`, `CR`, `DSP`, `EVD`, `EVT`,
   `FUNC`, `HCONF`, `HOF`, `OI`, `PLAN`, `RCV`, `REQ`, `RES`, `SRC`, `TASK`,
   `VRD`. In particular `FUNC` names features, so a feature-oriented child plan
   takes another category such as `PAY` or `FEAT`.
4. **One parent, inside the subject.** A child plan carries
   `approval_subject.parent_plan_id`. It is part of what the owner approves and
   therefore part of the child's fingerprint: moving a plan under a different
   parent is a new decision.
5. **Children are derived.** A parent's `child_plan_refs` lives outside
   `approval_subject` and is rebuilt by `plan sync`. Adding, removing, or
   renumbering a child does not change the parent's fingerprint and does not
   invalidate the parent's approval.
6. **Containment.** A child stays inside its parent's boundary:
   - `requirement_refs` and `feature_refs` of the child are subsets of the
     parent's, when the parent lists any;
   - the child's `authorized_actions` are a subset of the parent's;
   - the parent's `excluded_actions` are a subset of the child's, so a child
     cannot un-exclude what an ancestor excluded;
   - when the category declares a `write_boundary`, every TASK under plans of
     that category has a `write_scope` inside it.
   Preflight reports a violation; the task gate fails closed on it.
7. **Approval per node.** Every plan in the tree is approved separately with
   the routine `approval confirm` flow and materialized with
   `plan apply-decision`. A branch approval is a **boundary approval**: it fixes
   scope and the authorized and excluded actions for everything beneath it. A
   leaf approval is an **execution approval**: it fixes the TASK list and
   verification strategy, as a PLAN approval does today.
8. **Independent invalidation.** Editing a node invalidates that node's
   approval only. Every descendant is non-executable until the node is
   re-approved; siblings and ancestors are unaffected. A parent is not listed in
   its children's `approval_dependencies`, so re-approving a parent never
   requires re-approving its children.
9. **Several active leaves.** `state.active_plans` maps each executable leaf to
   the `APR-*` that made it so. Any number of leaves may be active at once,
   under one active root. `state.current_plan` and `state.active_plan` keep
   naming the root and `state.active_decision` its decision.
10. **Task gate.** A TASK is executable when its plan is a leaf in
    `active_plans` with a current decision, every ancestor up to the root has a
    current PLAN approval whose id matches that plan's `decision_ref`, the
    TASK's capabilities are inside every ancestor's authorized actions and
    outside every ancestor's excluded actions, and the existing checks (plan
    membership, lifecycle state, `blocked_by`, `G0/G1`, claims) pass.
11. **Concurrency stays where it is.** Two active leaves whose TASKs touch the
    same path are coordinated by `write_scope` and claims exactly as concurrent
    writers are today. Hierarchy does not relax claim rules.
12. **Closing.** A leaf closes when its TASKs are done. A branch closes only
    when every child is `CLOSED` or `SUPERSEDED`. The project closure contract
    is evaluated against the root.
13. **Hotfix leaves.** An incident fix goes into its own leaf, for example
    `FIX-001` under the root, so its approval and re-approval never stale the
    sprint leaves. The sequence is in `docs/WORKFLOW.md`.

## Categories

`project.json` declares the categories a project uses. The set is the project's
own. A storefront might use `API`, `SCR`, `PAY`, and `INF`; a fintech site might
add `KYC` and `LEDGER`; an internal tool might use only `APP` and `OPS`; a
project that plans by team might use `BACKEND` and `FRONTEND`. The harness
recognises no category name. It checks only that a category is declared, is not
a reserved prefix, and is used consistently. Declaring a category is
configuration, not authority: it grants nothing and approves nothing.

```json
"plan_categories": {
  "API": {"title": "Back-end API", "write_boundary": ["api/", "tests/api/"]},
  "SCR": {"title": "Screens", "write_boundary": ["web/"]},
  "INF": {"title": "Infrastructure", "write_boundary": ["infra/"]},
  "PAY": {"title": "Payment integration"}
}
```

`write_boundary` is optional. When present it is an outer limit on the
`write_scope` of every TASK under that category, checked by preflight and the
task gate. Categories may be added at any time; removing one that has plans
fails validation.

## Project profiles

The categories a project needs follow from what kind of project it is, so the
harness does not fix them. It ships **profiles**: named seeds for
`plan_categories` that `init` copies into `project.json`. A profile is a
starting point, not a rule. After `init` the project renames, removes, or adds
categories freely, may end up with a set that matches no shipped profile, and
nothing later reads the profile again.

```powershell
python scripts/harness.py init --name "Acme storefront" --profile web
python scripts/harness.py init --name "Field app" --profile mobile
python scripts/harness.py init --name "Ledger sync" --profile data
python scripts/harness.py init --name "Parser library" --profile library
python scripts/harness.py init --name "Something else"                  # no categories yet
```

Profiles live in `.harness/templates/profiles/<name>.json`. The harness ships a
small set and a project may add its own before running `init`:

| Profile | Categories | Typical boundaries |
|---|---|---|
| `web` | `API` back-end API, `SCR` screens, `INF` infrastructure, `DB` schema and data | `api/`, `web/`, `infra/`, `db/` |
| `mobile` | `APP` client app, `API` back-end API, `INF` infrastructure | `app/`, `api/`, `infra/` |
| `data` | `PIPE` pipelines, `MODEL` models, `DASH` dashboards, `INF` infrastructure | `pipelines/`, `models/`, `dashboards/`, `infra/` |
| `library` | `CORE` source, `DOCS` documentation, `REL` release engineering | `src/`, `docs/`, `.github/` |

An `init` without `--profile` declares no categories; the project then has
single-level plans until it adds categories to `project.json`. A profile never
changes the approval policy, the five cryptographic boundaries, the closure
contract, or the execution mode; it only names how the project's plans are
organised. Feature-specific children such as `PAY-001` are added per project,
because they belong to one engagement rather than to a kind of project.

## Commands

The runtime change adds or extends these commands. Names follow the existing
CLI so the routine path stays recognisable.

```powershell
python scripts/harness.py new plan PLAN-0001 "Acme storefront"
python scripts/harness.py new plan API-001 "Back-end API" --parent PLAN-0001
python scripts/harness.py new plan API-002 "API sprint 1" --parent API-001
python scripts/harness.py new task TASK-0001 "Session API" --plan API-002 --capability LOCAL_IMPLEMENTATION

python scripts/harness.py plan sync PLAN-0001              # rebuild child_plan_refs down the tree
python scripts/harness.py report decision-package PLAN-0001 # the tree, one package
python scripts/harness.py fingerprint .harness/plans/API-002.md

# owner confirms the root, then each branch and leaf they want executable
python scripts/harness.py approval confirm --type PLAN --subject .harness/plans/API-002.md ...
python scripts/harness.py plan apply-decision --approval APR-0003   # adds API-002 to active_plans
```

`new task --plan` refuses a plan that has children. `new plan --parent` refuses
a parent that has TASKs, an undeclared category, a reserved prefix, and a
`PLAN-*` id for a child. `next` reports the tree and the next step for each
active leaf; `status` shows `active_plans` in full.

## What changes in the runtime

| Area | Change |
|---|---|
| `plan.schema.json` | `harness.plan/v2`: id pattern `^(PLAN-[0-9]{4,}|[A-Z]{2,8}-[0-9]{3,})$`, `approval_subject.parent_plan_id`, derived `child_plan_refs` |
| `state.schema.json` | `harness.state/v2`: `active_plans` object mapping plan id to `APR-*` |
| `project.schema.json` | optional `plan_categories` |
| `scaffold.py` | `init --profile <name>` seeds `plan_categories` from `.harness/templates/profiles/<name>.json`; ships `web`, `mobile`, `data`, `library` |
| `authoring.py` | `new plan --parent`, category and reserved-prefix checks, per-category numbering |
| `validation.py` | branch/leaf exclusivity, parent existence, containment, category declared |
| `gates.py` | ancestor chain check, `active_plans` membership, capability containment, write boundary |
| `lifecycle_mutations.py` | `apply-decision` updates `active_plans` for leaves and `active_plan` for the root; `plan sync` rebuilds children |
| `guidance.py`, `reporting.py` | tree-aware `next`, `status`, `decision-package` |
| tests | hierarchy, several active leaves, parent invalidation blocks descendants only, containment violations, reserved prefixes, profile seeding and `init` without a profile |

Existing `harness.plan/v1` records remain readable as single-level roots.

## What does not change

- PLAN approval stays procedural; the five cryptographic boundaries stay
  cryptographic.
- A user request still never substitutes for the owner's PLAN decision.
- Every TASK still points to exactly one plan and is listed by it.
- The Markdown body of a plan is still non-authoritative; only front matter is
  fingerprinted.
