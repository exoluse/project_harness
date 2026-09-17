# Context and Verification Efficiency

Follow [AGENTS.md](../AGENTS.md). Efficiency means reading and checking what
supports the current decision; it never permits omitting authority, dirty work,
failures, blockers or verification limits.

## Startup and routing

Use the [startup and routing rules](../AGENTS.md#startup-and-context) as the
single entry map. Find project scope through the overview, then the owning
items and relevant shared specifications. Use targeted searches for linked
detail; do not load all policies, records or the entire README for orientation.
Reuse current supplied/read copies. A summary or link does not substitute for
reading an applicable rule before its action or completion claim.

## Maintaining policy guidance

Keep always-needed boundaries and reading triggers in AGENTS.md. Maintain each
detailed rule in its owning document, using the entry map to locate it. Adapters
route to that policy and add only necessary tool-specific guidance. READMEs
explain purpose, getting started and representative examples for readers;
they do not maintain another detailed procedure or checklist.

When changing guidance, inspect the affected summaries, examples and links in
both README languages and relevant adapters. When shortening it, confirm that
each removed obligation remains in its owning rule and can be reached before
the affected action. Preserve incoming anchors or repair their references.
Do not achieve a shorter entry by making required detail optional or adding
another summary that readers must always load. Use the policy-maintenance
Git/diff trace; no separate review record or numeric length target is required.

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

Apply the [verification requirements](../AGENTS.md#verification-and-exceptional-paths)
to the chosen scope. A compile pass or skipped test does not establish intended
product behavior. Retain failures and their actual impact; efficiency cannot
justify hiding results or silencing required checks.

## Model selection and delegation

Match model capability to the consequence of a wrong judgment, not to file
count or task length. This policy defines capability tiers only; adapters map
them to concrete models. The accountable agent is the session that received the
request and reports its result.

| Tier | Typical work | Handling |
|---|---|---|
| Strongest available | Classifying request clarity, material changes, high-risk effects and unknown dispositions; planning completion checks; inferring intent during reverse engineering; resolving open items; completion, handover and closure claims | Keep with the accountable agent. |
| Standard | Bounded implementation or document drafting within a defined scope; code search and summaries | The accountable agent reviews the output against the scope and criteria before relying on it. |
| Lightweight | Mechanical scans such as link/anchor, ID collision, filename and format checks; locating files | The accountable agent interprets the reported result and its impact. |

For each delegation, the accountable agent selects the tier and model itself;
the user need not choose or approve the model. The accountable agent keeps the
strongest-tier judgments above. A delegated agent that meets an authority, scope,
design or safety judgment returns it with its evidence instead of deciding.
Whether and how to delegate follows [subagent delegation](COLLABORATION.md#subagent-delegation).

Delegated output is evidence for what it actually checked; it creates no
authority, completion or PASS. A lower tier never lowers required checks,
completion criteria, decisions or security boundaries. The user or tool
configuration selects the main session model; the agent may recommend a change
when the judgment risk of the next stage changes, but does not stop covered work
for it. Do not claim cost or token savings without the
[measurement described below](#progress-and-handoff-notes).

## Progress and handoff notes

Retain the objective/stopping point, input/output versions, actual decision
bounds, ownership and dirty work, completed work, current failures and remaining
obligations. State the next action and what would unblock affected work.
For retained open items, link their current state, owner, next action,
needed-by/review trigger and resolution or closure evidence. Reassess the
affected items at the [lifecycle review points](WORKFLOW.md#review-escalation-and-reopening),
without copying the full item history into each progress note.

Do not invent performance or token savings. If measuring efficiency, record the
actual method, workload and limitations; comparisons need comparable scope.
Historical reports remain observations of their original runtime and workload,
not current performance guarantees.
