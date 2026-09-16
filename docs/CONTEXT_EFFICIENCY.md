# Context and Verification Efficiency

Follow [AGENTS.md](../AGENTS.md). Efficiency means reading and checking what
supports the current decision; it never permits omitting authority, dirty work,
failures, blockers or verification limits.

## Startup and routing

Read the current policy and applicable adapter once per session. Identify the
user's objective, stopping point and existing decisions, then inspect relevant
project notes, input versions and dirty work. Read only the material needed
for the current scope.

| Need | Read next |
|---|---|
| Find current feature/work scope | Project overview index, then the relevant unit and linked shared specifications; see [document organization](DATA_MODEL.md#document-organization). |
| Stage readiness or requirements/design recovery | Relevant section of [Development method](DEVELOPMENT_METHOD.md). |
| Scope decision or material change | [Approvals](APPROVALS.md) and the actual proposal/decision. |
| Work sequence, completion or transition | Relevant section of [Workflow](WORKFLOW.md). |
| Concurrent ownership or handover | [Collaboration](COLLABORATION.md) and current ownership notes. |
| High-risk action | [Security](SECURITY.md) and applicable external requirements. |
| Records left by the retired runtime | [Former runtime records](WORKFLOW.md#former-runtime-records). |

Use targeted searches for additional detail. Do not load all policies, records,
schemas or the entire README for routine orientation.

Keep entry prompts/adapters short: point to the governing policy and relevant
sections, adding tool-specific instructions only where useful. A policy already
read or supplied in the current session need not be reread through each link.
The linked rules remain binding; shortening the entry text does not make them
optional or require loading every linked document at startup.

## Reuse and verification

Reuse unchanged context and applicable evidence. Recheck when the subject,
criteria, dependencies, environment, authority or external requirements change.
Task splitting, ownership transfer or metadata edits alone do not justify
repeating unaffected product checks.

Use a known checked baseline with the recorded scope, criteria and results.
Inspect changes since that baseline, then check changed deliverables and their
affected references/dependencies. For Markdown, include modified text/links,
new IDs, mapping changes and references to moved, renamed or removed targets.
Validate new definitions against the verified project-wide ID allocation basis
under [allocation reuse](DATA_MODEL.md#allocation-and-validation-reuse).

Completion, handover or push requires reviewing evidence coverage and the actual
diff. It does not alone invalidate a successful check. After adding a check
receipt to a note, inspect that edit and any links/IDs it introduces; do not
repeat unaffected checks merely to record their result again. Preserve the
original result and identify what the incremental check covers.

Broaden verification when a baseline is absent/unreliable, intervening changes
are unknown, criteria or validation rules change, a failure suggests wider
impact, or project/CI controls require it. Unchanged files are reusable only to
the extent the baseline still covers them. A scan of changed files alone does
not prove project-wide uniqueness without a reliable allocation baseline.

Run checks appropriate to the actual deliverable. For documents, review content,
format and links. For product changes, run the relevant product checks and
required project/CI validation. A compile pass or a skipped test does not
establish the intended product behavior.

Classify a failure by its real effect, retain the original result and report
the limitation. Do not silence a required check or hide new failures to save
time.

## Progress and handoff notes

Retain the objective/stopping point, input/output versions, actual decision
bounds, ownership and dirty work, completed work, current failures and remaining
obligations. State the next action and what would unblock affected work.

Do not invent performance or token savings. If measuring efficiency, record the
actual method, workload and limitations; comparisons need comparable scope.
Historical reports remain observations of their original runtime and workload,
not current performance guarantees.
