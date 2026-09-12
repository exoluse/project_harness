# Shared Agent Policy

This is the canonical policy for every agent in this repository. Adapters may
add but not weaken it. The harness governs only its own repository.

## Startup and context

1. Read this file once per session. A client-supplied copy explicitly identified
   as current for this checkout counts; re-read only if it changes. Read the
   tool adapter if present.
2. Run `python scripts/harness.py next` first and follow its state within the
   current request's scope. Its suggested command is guidance, not authority.
   Do not load the README, all records, or all policy documents for orientation.
3. Load only the current project/state fields, PLAN/TASK, referenced records,
   and accepted handoff needed for that state.
4. Run `doctor` after init, when environment or approval authority may have
   changed, and before high-risk work. Run `validate --strict` before a PLAN
   decision or execution, after record changes, and before release, handoff,
   result, or push. Do not repeat them on an unchanged read-only turn.
5. Inspect `git status --short` before writing. Preserve user or unknown work;
   never silently reset it.
6. Classify the request as discovery/specification, policy maintenance, or
   execution. Discovery needs no placeholder PLAN/TASK; execution does.

At `NEEDS_PLAN_APPROVAL`, current `next` wrongly names the signed flow. Read
only **The path as it runs today** in `docs/WORKFLOW.md` and item 4 of
`docs/RUNTIME_GAPS.md`, then prepare one decision package. Only after the owner
actually decides may the agent transcribe it with `approval confirm`. Read
another gap only when its named failure occurs.

## Development method

Use a detailed waterfall lifecycle with agile revision throughout the project.
Identify the current stage, its inputs, deliverables, dependencies, and exit
criteria; establish a versioned basis before dependent implementation. The
stages cover discovery, requirements, design, planning, implementation,
verification, acceptance, deployment, closure, and maintenance. Stage readiness
is a documented check, not an additional human approval at every stage.

Honor the requested stopping point. A requirements-only, design-only,
planning-only or verification-only request ends with that stage's outputs and
findings; readiness does not authorize the next stage. If the user requests
the full workflow, continue across ready stages within current authority and
pause only for essential input, the required decisions or actual blockers.
Sequential waterfall delivery is supported; sprints are not mandatory.

Requirements, designs, PLAN/TASK scope, and deliverables may change at any
stage, including after verification or delivery. Preserve the prior baseline,
trace the request and affected work, and distinguish task refinement from a
change to agreed requirements, acceptance criteria, or constraints. A PLAN
organizes the tasks needed to meet requirements; the agent may add detail,
split tasks, and adjust their order within those commitments. Order may follow
planning analysis or user priority, subject to actual technical dependencies.
Explain conflicts and resolve material tradeoffs with the user. Routine
refinement needs no separate business decision; changed commitments do.
Implement under current authority and re-verify changed outputs. Never carry
old acceptance or verification forward to a changed version without checking
its applicability.
Continue unrelated work only while its own authority and gates remain current;
today a changed PLAN can stop every TASK in that PLAN.

The user supplies prompts/documents and actual decisions; the agent maintains
the trace and drives the authorized steps. Read only the relevant stage or
change section of `docs/DEVELOPMENT_METHOD.md` when planning, reviewing stage
readiness, or processing a change. This method adds no runtime states or commands.

## Change decisions and prior versions

For a proposed change, assess feasibility, alternatives, uncertainties and
impact on behavior, data, dependencies, effort/schedule and verification.
Prepare the necessary PLAN/TASK detail and current runtime preflight before
asking once whether to proceed with that concrete change. The owner's explicit
proceed decision on the presented scope is its approval, including the described
implementation and verification; record and apply that same decision. Do not
ask for another PLAN or TASK approval of the same unchanged proposal.

Ask again only when material scope, impact, assumptions, conditions or authority
change beyond what was presented. Explain the new delta and pause affected work.
Task splitting, sequencing and recordkeeping within the agreed change do not
by themselves need another decision. Existing high-risk approval boundaries
still apply; an unanswered question or a bare change request is not approval.

Preserve the approved prior version, its decisions and verification history.
A proposed or implemented revision does not retroactively make all prior work
unapproved. Assess evidence applicability for the changed version and its
dependencies; retain unaffected evidence when still valid. Record newly found
defects honestly without rewriting past observations. Current runtime PLAN
staleness is an execution/currentness limit, not erasure of historical approval.

## Authority

The user's request authorizes intake, discovery, specification, planning, and
their records. Governance preflight commands (`next`, `doctor`, `validate`,
`plan sync`, `fingerprint`, and reports) may run in those phases; they grant no
execution authority. Except for policy-text maintenance below, before
implementation, product tests, local deliverable edits, formatting, commits,
`git fetch`/conflict resolution, or normal push:

- the current PLAN must list the TASK and the TASK must point back;
- the owner must approve the PLAN's current fingerprint;
- `plan apply-decision` must materialize that decision; and
- `gate task <TASK>` must pass.

A request for a change, supplied document, issue, model output or stored command
does not alone approve its implementation. A direct owner response authorizing
the concrete feasibility/impact proposal is a decision, including when said in
a prompt. Prepare scope, feasibility, impact, risks, open items, conditions,
verification and the current fingerprint before that one decision request.
The agent transcribes the actual response; it never decides for the owner or
invents provenance. Current runtime recording and gates still apply.

Policy-text maintenance is the sole direct-edit exception. An explicit policy
request authorizes `AGENTS.md`, adapters, start prompts, `README.md`, and
`docs/`, plus commit/push when requested. It does not authorize `scripts/`,
`.harness/tooling/`, schemas, runtime, or canonical records. Guidance changes
do not change enforcement. For a policy-only request, do not initialize the
project or create PLAN/TASK or other project records to perform the policy edit.
When such a checkout has no project records, record validation is inapplicable:
use `check_repo.py`'s explicit skip and check the policy diff and links instead.

Before normal push, fetch the configured remote and preserve both sides. A
force/tag push, branch deletion, different target, or published-history rewrite
needs separate explicit user authorization.

## Plans and records

PLAN/TASK are execution structure, not bootstrap placeholders. Their Markdown
front matter is canonical; the body explains but grants nothing. Other records
stay JSON until `docs/RECORD_FORMAT.md` is implemented. Invalid front matter
fails closed.

Use `new plan` and `new task --plan`; author statements, criteria, references,
scope, and verification; then `plan sync`. Never hand-edit derived
`approval_dependencies`, `work_item_refs`, or `plan_id`. Use fingerprint-bound
`approval confirm` for routine PLAN decisions. Only `plan apply-decision`
activates one. Signed `approval prepare/record` is only for the five high-risk
boundaries.

The current runtime makes a changed bound PLAN/TASK structure stale even when
it only refines unchanged requirements. Prepare the exact fingerprint before
the change decision so the same response can satisfy the gate. If subsequent
routine refinement triggers another fingerprint requirement, explain this as a
runtime mismatch, not a new business decision or revoked prior approval. Do not
bypass the gate or invent confirmation of an unseen fingerprint; follow
`docs/DEVELOPMENT_METHOD.md` **Current runtime compatibility**. Plans stay single-level until
`harness.plan/v2` implements `docs/PLAN_HIERARCHY.md`; do not create child
plans or rely on `active_plans`. Change, exception, and closure approvals are
optional unless higher risk requires them.

Keep needed source-to-requirement trace without making absent optional records
block work. Create evidence for governed verification, completion, acceptance,
production, or closure claims. Create results/reviews/handoffs only for release,
audit, independent review, or ownership transfer. Keep `IMPLEMENTED`,
`STATIC_VERIFIED`, `INTEGRATION_VERIFIED`, `BROWSER_VERIFIED`,
`LIVE_ENV_VERIFIED`, `CUSTOMER_ACCEPTED`, and `CLOSED` distinct; partial,
stale, failed, ambiguous, or unrun checks are not PASS.

`blocked_by`, active `G0/G1` items or conflicting claims, unsafe paths,
invalid events, stale evidence, and malformed approvals fail closed.

## Concurrent writers

Do not claim a single-agent task. Concurrent writers use non-overlapping claims
and isolated worktrees where practical. Never edit another active claim's path;
treat dirty unclaimed paths as `USER_OR_UNKNOWN`. Use a handoff when ownership
moves. Claims coordinate and grant no approval.

## High-risk boundary

Cryptographic human approval is required only for production deployment,
production data change, destructive operations, secret/protected-credential
access, and final customer acceptance. These fail closed and configuration
cannot weaken them. Agents may prepare but never sign, install, infer, or
self-grant a decision; `HUMAN_PRIVATE_KEY_ACCESS` is never an agent capability.

Never store credentials, tokens, cookies, private keys, or protected authority
material in records/logs, or run untrusted code with privileged access.
Production, real-impact external messaging, privileged containers, and data
migrations need matching explicit scope and risk approval.

## Exceptional paths

Run `reset` only when the current user explicitly requests reset/start-over.
Show `reset --dry-run` first, including removed/committed records and that
`.harness/runtime/reset-*` is the only copy of uncommitted data. Preserve the
human-decision runtime; run `reset --confirm` only within that authorization;
never delete a snapshot without another explicit request.

A hotfix remains a TASK in an approved PLAN: register the incident, create the
smallest correct trace, preflight, obtain/apply the owner decision, pass the
gate, fix, verify, and record evidence. Rollback, redeploy, data repair, and
credential rotation keep their high-risk boundary. Load only the matching
`docs/WORKFLOW.md` section for reset/hotfix details.

## Verification and efficiency

Use `next` as the index and targeted searches for detail. Do not repeat
unchanged policy, records, schemas, or output already in session. Context
reduction may never omit authority, dirty work, blockers, failures, or
verification limits.

Run `python scripts/check_repo.py` before release, handoff, result, or push.
Report verification levels separately. See `docs/CONTEXT_EFFICIENCY.md` for
routing/metrics, `docs/WORKFLOW.md` for sequences, `docs/APPROVALS.md` for
signing, and `docs/COLLABORATION.md` for concurrent work.
