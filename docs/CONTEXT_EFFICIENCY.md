# Context and Token Efficiency

This policy reduces repeated context without weakening approval, safety, or
verification gates. `AGENTS.md` contains the compact invariant set;
`harness.py next` selects the current path; detailed documents and records are
loaded only when that path requires them.

## Routing

| Condition | Required context and checks |
|---|---|
| New agent session | Current `AGENTS.md` once, tool adapter, then `next` |
| Policy-only maintenance | Edit the authorized policy text directly; no init, project records, execution PLAN or fingerprint approval request. Follow-up requests retain that scope unless the user explicitly expands it. |
| `NEEDS_INIT` | For read-only/status work, report it without initialization. If the requested work needs governed project records: `git status --short`, `init`, `next`, then `doctor` |
| Discovery/specification | The supplied sources and only the records being authored |
| Planning | Current requirement/feature, PLAN/TASK, preflight blockers, then `validate --strict`; a planning-only request ends with the plan and findings, without an execution approval request |
| Execution readiness | Current prepared scope and fingerprint, actual owner decision, decision application and TASK gate; distinct from planning completion |
| Stage readiness or iteration planning | Only the relevant stage contract in `DEVELOPMENT_METHOD.md` and that scope's inputs, deliverables, criteria and open items |
| Requirement, PLAN or deliverable revision | `DEVELOPMENT_METHOD.md` change classification/cycle, the prior basis and affected references; `WORKFLOW.md` **Changing an approved plan** when approval becomes stale |
| `NEEDS_PLAN_APPROVAL` | `WORKFLOW.md` section **The path as it runs today** and `RUNTIME_GAPS.md` item 4; prepare one decision package, and transcribe only an actual owner decision |
| Execution/resume | Current PLAN/TASK, accepted handoff if any, `git status --short`, `validate --strict`, and `gate task` |
| Concurrent writers | Current claims and `COLLABORATION.md`; skip claims for one writer |
| High-risk action | `APPROVALS.md`, `SECURITY.md`, and `doctor` authority status |
| Release/handoff/result/push | Relevant evidence plus `check_repo.py`; report verification tiers separately |
| Reset or hotfix | Only the matching section of `WORKFLOW.md` |

`status` is a full dump for investigation. It is not a routine substitute for
`next`. Do not load README, all schemas, all canonical records, or all policy
documents merely to orient a session. Re-read a file when its hash or Git state
changed, the current decision references a new version, or a failed command
requires its detail.

## Measurement

Before measuring, remove avoidable duplication in the agent workflow:

- A decision package's fingerprint need not be fetched again just for display
  when its subject and dependencies are unchanged. Check strict-validation
  warnings separately if the package does not include them.
- Reuse an unchanged check for coincident policy checkpoints only when its
  scope and freshness satisfy both. Keep the mandatory checks built into
  decision recording, application, mutation and task gates.
- Keep governed meaning in canonical fields and rationale in prose. Reference
  the same criterion or decision instead of maintaining independent copies.
- Do not turn optional CHANGE approvals, results, reviews, handoffs or
  concurrent claims into routine single-agent requirements.
- Assess evidence applicability before rerunning checks. Report runtime
  currentness limits separately from an actual need to reverify the product.
- Report completion of the requested scope. A `next` suggestion to add a TASK
  after all tasks finish is not a new request.

These rules do not claim that the CLI shares validation results across commands
or that runtime duplication has been removed.

When an agent or wrapper exposes usage metadata, measure without storing prompt
content or secrets:

- input, output, cached, and total model tokens;
- tool-output characters and truncated outputs;
- paths and hashes of context files read;
- repeated reads of an unchanged hash;
- commands and human decision turns from request to passing task gate;
- tokens before the first implementation edit;
- tokens spent recovering from stale decisions, wrong guidance, or failed
  manual record edits.

Derived indicators:

```text
startup overhead = tokens through the first actionable `next`
governance ratio = pre-implementation governance tokens / total task tokens
repeat ratio = tokens from unchanged repeated context / total input tokens
gate efficiency = tokens and commands from completed PLAN to passing task gate
```

Do not put raw prompts, secrets, credentials, protected approval material, or
customer data in telemetry. Aggregate measurements are operational evidence,
not proof that implementation or acceptance passed.

## Initial targets

- routine resumed-session startup: at most 1,500 input tokens;
- after a complete PLAN is authored: one consolidated human decision and at
  most five machine steps to a passing task gate;
- governance ratio for a medium routine change: at most 25 percent;
- unchanged-context repeat ratio: at most 10 percent;
- no reduction in task-gate, dirty-worktree, blocker, approval, or verification
  enforcement.

These are baseline targets, not release claims. Benchmark cold and resumed
sessions separately across read-only investigation, a small fix, a medium
feature, concurrent work, and a high-risk preparation. Report medians and the
slowest case; do not average away a fail-closed or blocked path.

## Policy non-regression checklist

An efficiency change is invalid if any answer below becomes no:

- Does deliverable implementation still require the current fingerprint-bound
  PLAN decision, a listed TASK, applied decision, and passing task gate?
- Are dirty user/unknown paths and active claims still preserved?
- Are task refinement and ordering distinguished from changed agreements,
  with feasibility and impact presented before one owner proceed decision that
  is recorded as the PLAN approval, rather than a second decision afterwards?
- Are materially changed scope/impact/conditions distinguished from routine
  refinement, and any extra current-runtime fingerprint requirement named
  explicitly without bypassing its gate or inventing consent?
- Is prior-version approval and verification history preserved separately from
  the change decision and current verification of the revision?
- Are production deployment/data, destructive action, credential access, and
  final acceptance still cryptographically human-approved?
- Are partial, failed, stale, ambiguous, and unrun verification kept from PASS?
- Does reset still require the explicit request, visible dry run, retained
  snapshot, and preserved human-decision runtime?
- Are policy documents still unable to grant runtime authority or weaken
  code-enforced gates?
- Do stage contracts remain explicit and revisable, with changed requirements,
  plans and deliverables propagated to current authority and verification?

Use this checklist when changing `AGENTS.md`, adapters, prompts, or routing
documents. Token reduction is accepted only after the checklist remains green.

## Runtime status and remaining work

The audited CLI detours are removed: `next` distinguishes draft completeness,
owner decision, decision application and scope completion. Complete CLI authoring
and application no longer require manual state-pointer edits. Explicit shared
scope works across single-level plans and preserves legacy fingerprint semantics.
See [Runtime gaps](RUNTIME_GAPS.md) for fixes and their regression coverage.

Category/parent hierarchy, wider Markdown record migration and optional usage
metadata remain separate work. When adapters lack real token counts, continue
to label character-based estimates as estimates. These designs do not add
routine approval steps and do not authorize their own runtime implementation.
