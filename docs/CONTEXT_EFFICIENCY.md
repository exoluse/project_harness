# Context and Verification Efficiency

Follow [AGENTS.md](../AGENTS.md). Efficiency means reading and checking what
supports the current decision; it never permits omitting authority, dirty work,
failures, blockers or verification limits.

## Startup and routing

Read the current policy and applicable adapter once per session. Identify the
user's objective, stopping point and existing decisions, then inspect relevant
project notes, input versions and dirty work. There is no mandatory `next`,
`doctor`, initialization or full-record scan.

| Need | Read next |
|---|---|
| Stage readiness or requirements/design recovery | Relevant section of [Development method](DEVELOPMENT_METHOD.md). |
| Scope decision or material change | [Approvals](APPROVALS.md) and the actual proposal/decision. |
| Work sequence, completion or transition | Relevant section of [Workflow](WORKFLOW.md). |
| Concurrent ownership or handover | [Collaboration](COLLABORATION.md) and current ownership notes. |
| High-risk action | [Security](SECURITY.md) and applicable external requirements. |
| Optional CLI diagnosis | Current command help and the matching legacy finding in [Runtime gaps](RUNTIME_GAPS.md). |

Use targeted searches for additional detail. Do not load all policies, records,
schemas or the entire README for routine orientation.

## Reuse and verification

Reuse unchanged context and applicable evidence. Recheck when the subject,
criteria, dependencies, environment, authority or external requirements change.
Task splitting, ownership transfer or metadata edits alone do not justify
repeating unaffected product checks.

Run checks appropriate to the actual deliverable. For documents, review content,
format and links. For product changes, run the relevant product checks and
required project/CI validation. Optional bundled tooling can add information,
but its compile pass or absent-test skip is not product verification.

Classify a failure by its real effect, retain the original result and report
the limitation. Do not silence a required check or hide new failures to save
time. A legacy format limitation does not by itself revoke a valid decision.

## Progress and handoff notes

Retain the objective/stopping point, input/output versions, actual decision
bounds, ownership and dirty work, completed work, current failures and remaining
obligations. State the next action and what would unblock affected work.

Do not invent performance or token savings. If measuring efficiency, record the
actual method, workload and limitations; comparisons need comparable scope.
Historical reports remain observations of their original runtime and workload,
not current performance guarantees.
