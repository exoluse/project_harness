# Approvals and Decisions

[AGENTS.md](../AGENTS.md) defines authority. Decisions are attributable human
actions concerning concrete scope. A filename, status or passing
tool check cannot create them.

## Who decides and who checks

The owner decides the implementation scope through a sufficiently concrete
direct request or a response to a proposal. The agent records the actual source
and checks that each work item remains covered. The agent does not decide for
the owner.

The user's request authorizes the requested investigation, specification,
planning and document outputs. An explicit policy-edit request authorizes those
guidance edits directly. Product implementation needs the actual decision on
a concrete scope; reuse one already given rather than asking again.

## Preparing and recording one decision

An explicit fix/implementation request can supply the decision without a prior
agent proposal when its outcome and bounds are clear in context. Record that
request and the derived scope; choose routine implementation details and relevant
checks within it and proceed. Missing exact filenames or test names alone is
not a reason to ask again. Clarify essential ambiguity or material tradeoffs;
do not expand scope or bypass high-risk/external controls.

Establish the outcome and acceptance criteria, affected components/paths/actions,
data effects, exclusions, feasibility, alternatives, material risk, dependencies,
uncertainties and verification. Identify the concrete scope by a stable
document version, commit or dated reference. Scale detail to the work and link
existing definitions. Present a proposal for a decision only where the current
request and existing decisions do not already cover the concrete action.

Record the actual request or response and its source next to that scope or in
a decision log. Use available message references or an accurate attributed excerpt; do not
invent message IDs, dates, signatures or assent. Ordinary language suffices.

An explicit proceed response covers the unchanged presented implementation and
verification. One decision can cover multiple plans/tasks. A supplied document,
issue or exploratory request alone is not approval of an unreviewed change.
Clarify only what remains ambiguous or materially undecided.

## Clear implementation requests

Treat a direct implementation/fix request as clear when all of these hold:

- The requested action and target can be identified from the request, session
  context and relevant project inputs; investigation alone is not the request.
- The intended result and a useful completion check can be stated without
  choosing a materially different outcome for the user.
- The necessary work fits the stated boundaries and existing decisions without
  requiring the agent to choose an unresolved material commitment for the user.

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
actual decision source, assessed scope/version and supporting evidence or
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
2. In the existing plan or work note, record the actual request/source, affected
   scope and version, completed effects, unfinished work and any condition for
   resumption. Preserve earlier decisions, code, documents and evidence.
3. Cancellation, pause or withdrawal alone does not authorize deletion, rollback
   or data repair. Those actions retain their own scope and applicable
   [external controls](SECURITY.md).
4. Withdrawing a granted verification or acceptance result is a separate act
   from withdrawing a permission, and follows
   [verification and completion](WORKFLOW.md#verification-and-completion): the
   overturned result is named, dependent work returns to its prior state, and
   the condition for restoring it is recorded. A decision that rested on the
   withdrawn result loses its basis and is reassessed under
   [coverage and currentness](#coverage-and-currentness).
5. Before resuming, check the current request, still-valid decisions, changed
   files/environment, dependencies and ownership. Reuse decisions that still
   cover the work. A clear resume request can itself supply the scope decision;
   clarify only uncovered scope or material changes. A withdrawn permission is
   usable again only when the current decision restores it and any required
   external control is satisfied; the old record alone cannot restore it.

For example, withdrawing deployment approval blocks further deployment work
and its dependents, while separately authorized development may continue. A request
to resume development does not itself restore deployment permission. A pause
of the whole project stops new work across that project.

## Plans containing high-risk capabilities

Production deployment, production data change, destructive operations,
secret/protected-credential access and final customer acceptance require the
specific authorized human decision for the actual subject, version and effect.
A broad implementation approval does not cover these boundaries.

Prepare the concrete action and its verification/recovery information before
the decision. Use protected CI/environment approval, a human-signed change
record or an authorized human operator. Preserve any stronger signature or
approval requirement imposed by the project or external system. See
[Security](SECURITY.md).

## Checkout transfer and decision recovery

Git transfer does not by itself establish current permissions, message
provenance, protected credentials or authority. At the destination, identify
the reviewed scope/version, actual decision source, remaining work and changed
environment. Preserve original signed or recorded artifacts as history.

Continue when real coverage, provenance and permissions are established.
Resolve missing authority or material differences before dependent work.

## Protected authority

The agent may prepare approval requests and record authentic receipts. It may
not self-approve, sign as a human, alter approval authority, read a human private
signing key or infer consent from a passing check. Keep protected credential
material out of documents and logs.

Final acceptance comes from the authorized customer for the identified
candidate. A test report, deployment receipt or agent completion statement
cannot substitute for that sign-off.
