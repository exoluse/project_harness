# Context and Token Efficiency

This policy reduces repeated context without weakening approval, safety, or
verification gates. `AGENTS.md` contains the compact invariant set;
`harness.py next` selects the current path; detailed documents and records are
loaded only when that path requires them.

## Routing

| Condition | Required context and checks |
|---|---|
| New agent session | Current `AGENTS.md` once, tool adapter, then `next` |
| `NEEDS_INIT` | For read-only/status work, report it without initialization. If the requested work needs governed project records: `git status --short`, `init`, `next`, then `doctor` |
| Discovery/specification | The supplied sources and only the records being authored |
| Planning | Current requirement/feature, PLAN/TASK, preflight blockers, then `validate --strict` |
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

## Runtime work still required

Policy routing alone cannot remove the current CLI detours. The implementation
order remains:

1. Fix `docs/RUNTIME_GAPS.md` items 1 through 5 and 7, with one CLI end-to-end
   test from `init` to task gate and re-approval.
2. Make `next` authoritative at approval and decision-application states.
3. Add complete CLI authoring options so normal preflight does not require
   manual schema-driven edits.
4. Implement `harness.plan/v2` leaf approvals so one task change does not stale
   unrelated executable work.
5. Add privacy-preserving usage metadata when an adapter provides real token
   counts; otherwise label character-based estimates as estimates.

These changes touch runtime code, schemas, or tests and therefore require an
approved PLAN/TASK. This document authorizes none of them by itself.
