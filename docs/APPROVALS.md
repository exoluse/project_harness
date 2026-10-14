# Approvals and Decisions

[AGENTS.md](../AGENTS.md) defines authority. Decisions are attributable human
actions concerning concrete scope. A filename, status or passing
tool check cannot create them.

## Who decides and who checks

The owner decides the implementation scope through a sufficiently concrete
direct request or a response to a proposal. The agent records the request or
decision basis and checks that each work item remains covered. It makes choices
within that authority, including explicitly delegated judgment, without inventing
an owner decision.

### Decision requests and delegated judgment

Before asking the owner, distinguish the choice from the authority needed to make it.

| Choice | Action |
|---|---|
| A commitment outside existing authority under the [material-change criteria](#material-changes) | Present the uncovered effect and obtain the owner's decision. |
| Judgment explicitly delegated for a stated subject and limits | Choose within those limits and record the choice and rationale where it belongs. |
| Routine implementation or work ordering within established commitments | Choose and proceed; update affected instructions without another approval. |

Record that the owner delegated judgment with the owning scope decision. State
the subject, allowed choices or constraints, exclusions and conditions for asking
again. Use the request and its context; do not invent broader authority from
phrases such as "use your judgment."

A new specification version or plan does not alone renew or end a delegation.
Check whether its subject and conditions still cover the proposed choice under
[coverage and currentness](#coverage-and-currentness). Ask only about an
uncovered or genuinely ambiguous effect. Delegation does not replace the specific
human decisions required by [high-risk controls](../AGENTS.md#high-risk-and-external-control).

## Preparing and recording one decision

A [clear implementation request](#clear-implementation-requests) supplies the
decision without a prior agent proposal. Establish the outcome and acceptance
criteria, affected components/paths/actions, data effects, exclusions,
feasibility, alternatives, material risk, dependencies, uncertainties and
verification. Identify the concrete scope by a stable
document version, commit or dated reference. Scale detail to the work and link
existing definitions. Present a proposal for a decision only where the current
request and existing decisions do not already cover the concrete action.

Note only that the work follows a user request or decision, next to its scope
or in a decision log. A note such as "Performed at the user's request" suffices.
No transcript, message ID or chat link is required for this note.
Keep the scope, constraints and resulting decisions in their owning sections.
Record technical rationale separately. Never invent a request, consent, dates
or signatures. Required approval and acceptance evidence still follows
[Security](SECURITY.md#five-high-risk-boundaries).

An explicit proceed response covers the unchanged presented implementation and
verification. One decision can cover multiple plans/tasks. One item can equally
carry several decisions taken at different times. Record each against the
sub-scope it covers under [plans and tasks](DATA_MODEL.md#plans-and-tasks)
rather than restating the item's overall mode. A supplied document,
issue or exploratory request alone is not approval of an unreviewed change.
Clarify only what remains ambiguous or materially undecided.

## Clear implementation requests

Treat a direct implementation/fix request as clear when all of these hold:

- The requested action and target can be identified from the request, session
  context and relevant project inputs; investigation alone is not the request.
- The intended result and a useful completion check can be stated without
  choosing a materially different outcome for the user.
- The necessary work fits the stated boundaries and existing decisions without
  requiring a material choice outside the agent's established authority or
  [delegated judgment](#decision-requests-and-delegated-judgment).

Clarity establishes intent and scope, not execution readiness. Check real
dependencies, ownership and required external permissions separately.

The user need not supply exact files, algorithms or test commands. Investigate
technical unknowns and choose routine details within scope. If a condition is
unresolved, ask only about the missing outcome, boundary or material choice;
continue independent authorized work. Do not require a fixed prompt template
or a second proceed response merely to restate a clear request.

## Material changes

Compare the proposed action with the actual authorized scope and conditions.
A change is material when it introduces or alters a commitment not already
covered by that decision in any of these areas:

- Intended behavior, deliverables or acceptance criteria.
- Public interfaces or compatibility relied on by users or other systems.
- Data collection, access, retention, migration or destructive effects.
- Security/privacy boundaries, external permissions or required controls.
- Spending, service dependencies, agreed resource limits or delivery promises.
- Assumptions or risks whose change invalidates the basis of the prior decision.

File count, code size, task splitting and implementation difficulty alone do
not make a change material. If the current request explicitly authorizes the
new effect, reuse it as the decision rather than asking again. Otherwise prepare
the before/after effect and obtain the owner's decision for affected work.
Specific high-risk/external controls still apply. Where impact is uncertain,
investigate first; clarify before performing the potentially uncovered effect.

| Situation | Assessment and action |
|---|---|
| Fix the identified calculation defect to match an existing expected result | Clear fix request; locate the implementation, make covered edits and verify the result. |
| Split an internal function while fixing that defect, preserving interfaces and accepted behavior | Routine implementation detail within scope; no renewed decision. |
| "Improve this" without a target outcome or usable context | Investigate what can be established and clarify the missing outcome before selecting one. |
| Change an API response format consumed by other systems during an internal fix | Material if compatibility change is not covered; present the effect and obtain a decision. |
| Add a paid service or send user data to a new provider | Check spending, data and external permissions; obtain any uncovered decision before the effect. |
| User explicitly requests a defined response-format migration | Use that request for the covered migration; assess dependencies and required controls without repeating approval. |

## Coverage and currentness

Before covered work begins, assess the actual outcome, actions, paths/data,
risk, constraints and checks against the decision. Confirm dependencies,
ownership and required external permissions.

Keep this readiness assessment once in the owning plan/work note, with the
request or decision basis, assessed scope/version and supporting evidence or
links. Tasks may inherit it through their parent link when the covered scope
and shared prerequisites are clear; no separate readiness record is required.
Before a selected item starts or resumes, check for changes and item-specific
dependencies or blockers. Record only those differences and any new assessment
needed, rather than repeating the shared checklist or unchanged confirmations.
Changed inputs, failed checks, ownership conflicts or unavailable permissions
reopen the affected assessment; an old ready label does not establish readiness.
Use [verification reuse](CONTEXT_EFFICIENCY.md#reuse-and-verification) to determine
which supporting checks remain applicable. Harness policy maintenance uses
the Git/conversation basis specified in [AGENTS](../AGENTS.md#harness-policy-maintenance).

Routine task splitting, reordering, plan switching, metadata edits and record
format changes do not create a new decision boundary. Material changes to
commitments, risk, assumptions, conditions or authority under the
[material-change criteria](#material-changes) need a prepared delta
and an actual owner decision before affected implementation.

Preserve prior versions and decisions as history. Changed outputs can limit
current applicability without making the past decision fictitious. Check
history integrity separately from current coverage; never widen an old
signature or copy evidence into a new PASS without assessment.

## Cancellation, withdrawal and resumption

Apply the latest attributable owner decision to its actual scope. Cancellation
ends the selected work; a pause leaves it pending; withdrawal removes the
specified permission. Identify affected work and its dependents. Continue other
work only when it remains authorized and outside the requested stop boundary.

1. Stop starting affected work. Use available authorized stop controls for work
   in progress; report an operation that cannot be stopped safely and its known
   effects. A stop request does not prove that an operation has stopped or that
   earlier effects have been undone.
2. In the existing plan or work note, note the owner's cancellation, pause or
   withdrawal. Record the affected scope and version, completed effects,
   unfinished work and any condition for resumption. Preserve earlier decisions,
   code, documents and evidence.
3. Cancellation, pause or withdrawal alone does not authorize deletion, rollback
   or data repair. Those actions retain their own scope and applicable
   [external controls](SECURITY.md).
4. Withdrawing a granted verification or acceptance result is a separate act
   from withdrawing a permission. Withdrawing such a result follows
   [verification and completion](WORKFLOW.md#verification-and-completion).
   Under that procedure, the overturned result is named, dependent work
   returns to its prior state, and the condition for restoring it is recorded.
   A decision that rested on the withdrawn result loses its basis and is
   reassessed under
   [coverage and currentness](#coverage-and-currentness).
5. Before resuming, check the current request, still-valid decisions, changed
   files/environment, dependencies and ownership. Reuse decisions that still
   cover the work. A clear resume request can itself supply the scope decision;
   clarify only uncovered scope or material changes. A withdrawn permission is
   usable again only when the current decision restores it and any required
   external control is satisfied. The old record alone cannot restore it.

For example, withdrawing deployment approval blocks further deployment work
and its dependents, while separately authorized development may continue. A request
to resume development does not itself restore deployment permission. A pause
of the whole project stops new work across that project.
