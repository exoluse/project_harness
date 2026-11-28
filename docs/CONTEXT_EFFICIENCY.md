# Context and Verification Efficiency

Follow [AGENTS.md](../AGENTS.md). Efficiency means reading and checking what
supports the current decision; it never permits omitting authority, dirty work,
failures, blockers or verification limits.

## Maintaining policy guidance

Keep always-needed boundaries and reading triggers in AGENTS.md. Maintain each
detailed rule in its owning document, using the entry map to locate it. Adapters
route to that policy and add only necessary tool-specific guidance. READMEs
explain purpose, getting started and representative examples for readers;
they do not maintain another detailed procedure or checklist.

When changing guidance, inspect the affected summaries, examples and links in
both README languages and relevant adapters. When shortening it, confirm that
each removed obligation remains in its owning rule and can be reached before
the affected action. Preserve incoming anchors, or repair their references in
the same change.
Do not achieve a shorter entry by making required detail optional or adding
another summary that readers must always load. Use the policy-maintenance
Git/diff trace; no separate review record or numeric length target is required.

### How guidance is written

An agent reads a rule immediately before the action it governs. Write guidance
to be scanned, not parsed.

- **One rule per sentence.** Split the sentence when a condition is attached.
- **Use verbs, not nominalizations.** "Check whether it still applies" carries
  more than "perform an applicability assessment" and costs less.
- **Keep the abstraction in the defined terms.** Terms such as material change
  or open item carry their definition; the sentences around them stay plain.
- **Break three or more conditions into a list.** This covers stacked clauses,
  not a single enumeration of items.
- **Keep a sentence under about 25 words.** A longer one usually holds two
  rules.

Lead each section with the rule it carries, then give its exceptions and the
reason. Split a section with subheadings or a table once it accumulates more
than about five rules. The number of rules decides this, not the length.

A spine rule that [AGENTS.md](../AGENTS.md) already carries needs no
restatement in a detailed document. That file is loaded in every session, so
the obligation is always reachable before the affected action. Restate it only
where the owning section changes what it means. This is a way to say the same
thing in less text, not permission to drop an obligation whose only statement
is here.

### Document checker

`node tools/check-docs.mjs [path ...]` checks that relative link targets exist,
that heading and HTML anchors resolve and that `Last checked:` dates are recent.
It needs Node and no packages, reads Markdown and writes nothing; a governed
project can point it at its own document root. In an adopting project, run it
from the [harness copy](DATA_MODEL.md#harness-copy), such as
`node harness/tools/check-docs.mjs project-docs`. The checker is an optional
way to supply part of the required
[document validation](DATA_MODEL.md#document-validation).
Verify the affected targets and anchors after changing guidance and before a
completion claim that relies on links. Use this checker or an equivalent tool
or manual check. Put the method, scope, result and limits in the commit
message, as policy maintenance does.

The generic link, anchor and date checks also apply to documents with semantic
paths. The checker does not enforce canonical-path identity, ordinary filename
syntax, unique logical ownership or overview coverage for those documents.
Review these under [document validation](DATA_MODEL.md#document-validation).

Its additional filename-ID diagnostics apply only to legacy `<ID>.md` or
`<ID>-<slug>.md` names. They detect duplicate filename IDs, missing body IDs,
missing descriptions, descriptions outside the former two-word syntax,
and unlinked ID-named files.
Repeated legacy ID-only headings can be reported in any scanned Markdown file.
These are legacy heuristics, not naming requirements for new path-based documents.
Established numbered files remain valid. `--allow-bare-ids` suppresses the
missing-description warning; the checker cannot distinguish old files from new ones.
Assess other legacy naming warnings against retained conventions before reporting a violation.

The legacy unlinked-file heuristic treats the unlinked document linking to the
most ID-named items as the overview. It exempts a lone scanned file.
It does not detect unlinked semantic-path documents or duplicate logical owners.
Scope scans where earlier records retain copies with the same legacy ID.

The checker reports link paths whose letter case differs from disk names.
GitHub matches paths case-sensitively even when a local filesystem does not.
Compare new link targets with tracked names, such as `git ls-files`.
A fragment matches an anchor as written or lowercased.
Hosts differ on HTML anchor case; lowercase anchors and links avoid that difference.

After changing the checker, run its regression tests with
`node --test tools/check-docs.test.mjs`. They write their fixtures to a
temporary directory, not to the repository.

A pass covers only the checks described above. Content, path conventions,
logical ownership, trace coverage and meaning still need their own review.
If the checker is unavailable or not used, perform the applicable checks by another method and state any gaps.
Required project, contract and CI checks retain their specified tools and scope.

### Dated tool facts

Model availability, selection options and tool configuration syntax change
outside this repository. Tool-specific details live in the adapters and the
[tool-level control snippets](SECURITY.md#tool-level-supporting-controls). Mark
each such passage with `Last checked: YYYY-MM-DD` and the official source it
was checked against. Recheck against that source in any of these cases:

- when the checker warns that the date is older than 90 days;
- when a model or tool release is known;
- before recommending the passage to an adopter.

Change the date only after actually checking; an unverified passage keeps its
old date. The date does not establish current model availability. Resolve
models under [model selection](#model-selection-and-delegation) instead of
keeping a fixed generation-to-tier mapping in policy.

## Reuse and verification

Reuse unchanged context and applicable evidence. Recheck when the subject,
criteria, dependencies, environment, authority or external requirements change.
Task splitting, ownership transfer or metadata edits alone do not justify
repeating unaffected product checks.

Use a known checked baseline with the recorded scope, criteria and results.
Confirm that its tested output and check evidence can be identified under
[verification and completion](WORKFLOW.md#verification-and-completion).
Inspect changes since that baseline, then check changed deliverables and their
affected references/dependencies. For Markdown, include modified text/links,
new owning paths, folder-convention changes and references to moved, renamed or removed targets.
Validate paths, anchors and logical ownership against the checked baseline and
subsequent changes under [path checks](DATA_MODEL.md#path-checks-and-verification-reuse).

Completion, handover or push requires reviewing evidence coverage and the actual
diff. It does not alone invalidate a successful check. Do not repeat
unaffected checks merely to restate their result. Rely on the original result
where it still applies, and state what the incremental check covers.

Broaden verification when any of these holds:

- a baseline is absent/unreliable;
- intervening changes are unknown;
- criteria or validation rules change;
- a failure suggests wider impact;
- project/CI controls require it.

Unchanged files are reusable only to the extent the baseline still covers them.
A scan of changed files alone cannot establish unique project-wide ownership
without reliable coverage of existing paths and definitions.

### Check scope and scheduling

Assign checks to the point where their evidence is needed, using the plan or
task that already owns verification. Reuse the baseline under the rules above.
Select checks under [claim-based verification](WORKFLOW.md#verification-and-completion).
Run a focused check for the changed outcome and likely or consequential failures
before costly broad coverage. A high pass count cannot compensate for a check
that does not observe the claimed behavior.

| Execution point | Default scope |
|---|---|
| Individual task | Changed behavior and affected dependencies, with targeted regression checks. |
| Integration of related tasks | Combined flows and shared regression checks on the integrated candidate. |
| Release or acceptance | The coverage and supported environments required by the delivery contract and project controls. |

Record the actual commands or planned check targets, environments, execution
point and reusable evidence. For costly checks, also state the concurrency limit
and known runtime/resource constraints. Use measured durations where available;
leave unknown cost explicit instead of inventing a budget. Do not copy a full
suite into every task solely because it appears in the project's command list.

Schedule checks before the completion claim or dependent action that requires
their result. Deferring an integrated check does not establish that result for
an individual task. Mandatory project, contract and CI checks retain their
required scope and timing.

Run resource-heavy suites one at a time unless adequate capacity for overlap
has been established. For long-running or memory-intensive checks, apply
[memory monitoring](#monitoring-available-memory). For repeated timeouts,
investigate product behavior, test reliability and resource contention before
choosing the rerun scope.
A focused rerun can test the diagnosis. The original failures stand until a
check of their scope passes; state what the later execution actually
establishes.

Once the relevant required checks pass, proceed with the work. Repeat or broaden
checks only when changed inputs, unresolved failures, uncertain evidence or
project controls justify it. Recording a result or handing off work alone does
not justify another full run.

## Monitoring available memory

Before starting long-running or memory-intensive work, check available memory
on the machine that will run it. If a job or container has a tighter limit,
check how much of its allowance remains. Compare available memory with the
expected peak. If demand is uncertain, start with a smaller batch when practical.

Keep sampling during execution, including while a single command is running.
Use host or runner metrics at intervals short enough to catch growing memory
pressure. Recheck before increasing concurrency or batch size. If the runner
exposes only job-level readings, state that limit when reporting memory pressure.

If memory is too low for the work ahead or readings show growing pressure,
reduce concurrency or batch size. Defer a run that still cannot fit. If
pressure persists during a run you started for this task, pause or stop it at
a safe point. Start or resume when a fresh reading shows enough memory for
the adjusted workload.

## Model selection and delegation

Use the strongest suitable reasoning model currently available for definition,
analysis, design, planning and consequential decisions. This applies to compact
work and to reasoning discovered during implementation. Select implementation
models by difficulty and failure impact once the governing behavior is settled.
The accountable agent is the session that received the request and reports its result.

### Work and capability

| Tier | Typical work | Handling |
|---|---|---|
| Strongest available | Problem and requirement definition; analysis and root-cause diagnosis; design and planning; substantive review; authority, scope, risk and open-item decisions; planning completion, verification interpretation, handover and closure judgments | The accountable agent retains decisions and final conclusions. Substantive delegated reasoning or drafting uses the same capability tier. |
| Advanced | Difficult implementation of settled designs, such as complex algorithms, concurrency, performance-sensitive changes or integration across components | Use the strongest model when the implementation difficulty requires it. Review against the governing design and checks. |
| Standard | Ordinary feature implementation, bounded fixes and tests using established behavior and contracts | Review the output against the defined outcome and checks. |
| Lightweight | Simple, low-risk edits with a prescribed approach; mechanical checks and file location; factual extraction and recording of settled decisions or observed results, without interpretation | Keep the assignment bounded and verify its result. A higher tier checks any value it derives, such as a date or an estimate. Interpretation returns to the strongest tier. |

Assess implementation complexity, coupling, uncertainty and failure impact.
File count or task length alone does not determine the tier. Requirements,
designs and plans are reasoning work even when delivered as Markdown; a later
review does not justify drafting them with a weaker model.

When implementation exposes a need for analysis, design, planning or a material
decision, return that part to the strongest tier before dependent edits continue.
A delegated agent returns the question with its evidence. Once resolved, bounded
implementation can resume at the appropriate tier. Routine coding choices within
settled behavior remain with the implementer.

### Selecting available models

Resolve concrete models when first needed in a session; adapters describe the
tool-specific selection mechanism. Do not hard-code model generations into tiers.

1. Check the models and selection options exposed by the current tool or client.
   Respect explicit model pins, provider restrictions, access and agreed budgets.
   A provider's public catalog alone does not establish availability here.
2. Use current capability descriptions and applicable project evidence to match
   models to the work. Consult official documentation when that basis is missing
   or a known release changes it. Names, release dates and prices alone do not
   establish reasoning capability; do not invent model IDs or a `latest` alias.
3. Use supported aliases when their effective model is suitable and no explicit
   version pin applies. Account for inherited defaults and tool restrictions;
   request only model and reasoning settings the actual interface supports.
4. Reuse the selection basis while it remains current. Reassess when availability,
   capabilities, constraints or task difficulty change, or a selection fails.
   No repeated catalog search is required. A
   [project model roster](#project-model-roster), where kept, records this basis.

The accountable agent selects implementation and subagent models without another
approval within those constraints. State a material substitution and its basis
in the commit message when later work relies on it. Do not silently
replace a required strong model with a weaker default. A supported alternative
may be used only when it meets the work's capability and constraint requirements.

### Project model roster

A project may designate which models each tier uses. Keep this roster in the
[project entry](DATA_MODEL.md#suggested-information), which every session reads
first. Where a roster exists, it is the selection basis for the steps above.

For each tier, record:

- the permitted models, by the identifiers the tool accepts;
- whether the tier runs as the main session or through delegation;
- the basis, such as provider descriptions or project evidence, with its date.

Before listing a model, confirm with a short run that the tool and account
accept it. A model shown in a client's model list can still be refused.

Select only from the roster. An unlisted model, or a tier below what the work
requires, needs the project owner's decision. A roster change is a project
decision, recorded where the roster lives.

Pin the main session to a strongest-tier model through tool configuration; the
adapters give the setting. Reassess the roster in any of these cases:

- a model or tool release is known;
- a listed model fails or is refused;
- project results show a tier's work falling short.

### Accountability and tool limits

The user or tool configuration selects the main session model. Before
strongest-tier work, check that model:

- where a roster exists, compare the effective model with its strongest tier,
  when the tool reports the model;
- otherwise, assess it against current capability descriptions.

A weaker model may not recognize its own gap. The roster and a configuration
pin are the dependable controls; this check is a backstop.

If the main model cannot meet the reasoning requirement, state the gap and
recommend a suitable model change through the client's supported control. Do
not claim to have switched models without tool evidence. Continue independent
work that the current model can handle; leave the affected judgment pending
when no suitable model is available.

Whether and how to delegate follows
[subagent delegation](COLLABORATION.md#subagent-delegation). Delegation is optional;
model selection does not require creating subagents or changing saved settings.

Delegated output is evidence for what it actually checked; it creates no
authority, completion or PASS. A lower tier never lowers required checks,
completion criteria, decisions or security boundaries.

Do not claim cost, performance or token savings without measuring them. A
measurement records the actual method, workload and limitations; comparisons
need comparable scope.
