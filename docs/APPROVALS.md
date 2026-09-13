# Approvals and Decisions

[AGENTS.md](../AGENTS.md) defines authority. Decisions are attributable human
actions concerning concrete scope. A filename, fingerprint, status or passing
tool check cannot create them.

## Who decides and who checks

The owner decides on the presented implementation scope. The agent prepares
the proposal, records the actual response and checks that each work item remains
covered. The agent does not decide for the owner.

The user's request authorizes the requested investigation, specification,
planning and document outputs. An explicit policy-edit request authorizes those
guidance edits directly. Product implementation needs the actual decision on
a concrete scope; reuse one already given rather than asking again.

## Preparing and recording one decision

Present the outcome and acceptance criteria, affected components/paths/actions,
data effects, exclusions, feasibility, alternatives, material risk, dependencies,
uncertainties and verification. Identify the reviewed proposal by a stable
document version, commit or dated reference.

Record the actual response and its source next to that proposal or in a decision
log. Use available message references or an accurate attributed excerpt; do not
invent message IDs, dates, signatures or assent. No special phrase, typed hash,
APR record or user-run command is required.

An explicit proceed response covers the unchanged presented implementation and
verification. One decision can cover multiple plans/tasks. A supplied document,
issue or exploratory request alone is not approval of an unreviewed change.
Clarify only what remains ambiguous or materially undecided.

## Coverage and currentness

Before covered work begins, assess the actual outcome, actions, paths/data,
risk, constraints and checks against the decision. Confirm dependencies,
ownership and required external permissions.

Routine task splitting, reordering, plan switching, metadata edits and record
format changes do not create a new decision boundary. Material changes to
commitments, risk, assumptions, conditions or authority need a prepared delta
and an actual owner decision before affected implementation.

Preserve prior versions and decisions as history. Changed outputs can limit
current applicability without making the past decision fictitious. Check
history integrity separately from current coverage; never widen an old
signature or copy evidence into a new PASS without assessment.

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

There is no mandatory bundled-runtime signed PLAN under the current operating
policy. If a legacy CLI action is deliberately used, its implementation can
still require both a signed PLAN and matching action approvals. Those checks
are unchanged; this document does not authorize bypassing them.

## Checkout transfer and decision recovery

Git transfer does not by itself establish current permissions, message
provenance, protected credentials or authority. At the destination, identify
the reviewed scope/version, actual decision source, remaining work and changed
environment. Preserve original signed or recorded artifacts as history.

Continue when real coverage, provenance and permissions are established.
Resolve missing authority or material differences before dependent work.
A missing local CLI marker alone is not a new human decision requirement for
ordinary document-based work.

Legacy runtime decisions may bind repository roots and protected local markers.
Do not forge or manually install markers, replay a different decision as if it
were the original, or rewrite signed snapshots. See the explicitly legacy
[checkout finding](RUNTIME_GAPS.md#b8-checkout-transfer) if using that tool.

## Protected authority

The agent may prepare approval requests and record authentic receipts. It may
not self-approve, sign as a human, alter approval authority, read a human private
signing key or infer consent from a passing check. Keep protected credential
material out of documents and logs.

Final acceptance comes from the authorized customer for the identified
candidate. A test report, deployment receipt or agent completion statement
cannot substitute for that sign-off.

## Legacy signed-flow reference

The bundled CLI and its approval schemas retain their implemented behavior.
No migration or compatibility is implied by this policy change. For historical
command procedures, consult the
[pre-transition approvals snapshot](archive/runtime-required-policy/docs/APPROVALS.md.txt)
as legacy tool documentation only. Inspect current help and real prerequisites
before a scoped use; never follow archived instructions as current authority.
