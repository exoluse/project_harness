# Collaboration and Handover

Follow [AGENTS.md](../AGENTS.md). Ownership coordination prevents conflicting
writes; it does not create execution authority.

## Single writer

A single writer needs no claim system, runtime attempt or placeholder handoff.
Inspect dirty files before writing and preserve user/unknown changes. Use a
concise task list and progress notes sufficient to explain what was changed
and what remains.

## Concurrent writers

Agree owners and non-overlapping paths and logical resources before concurrent
editing. Prefer isolated worktrees when practical. Shared project notes or the
team's coordination tool can record ownership, baseline, scope and status.

Do not edit another writer's active scope. Account for shared schemas, generated
files, migrations and other logical collisions even if filenames differ.
Resolve ownership and integration order explicitly. Each writer still needs
applicable authority and real prerequisites for their own work.

Use subagents only when the user or applicable higher-level instructions
authorize delegation. This document does not itself request parallel agents.

## Formal records for a single writer

A requested result or handoff can be an ordinary document when the agreed
delivery contract accepts it. Record the real baseline, changed paths, decisions,
checks, observations, limits, unfinished work and next action. No prospective or
retrospective CLI claim is required under current policy.

If the optional legacy `result submit` or `handoff create` command is selected,
its implemented claim and attempt checks still apply. Do not fabricate a claimed
past run to satisfy them. Use a truthful document handoff if accepted; otherwise
resolve the chosen process's requirements before claiming formal completion.

## Transfer and integration

At transfer, identify the actual owner, input/output versions, dirty work,
applicable decisions, failed or unrun checks, outstanding obligations and next
steps. The recipient checks applicability and permissions in the new environment;
a handoff does not widen the original decision.

Preserve both sides during integration. Do not silently reset unknown work,
drop failed attempts or hide a newer failure behind an older success.
Verification should address the actual integration impact, rather than rerunning
unaffected checks solely because ownership or document layout changed.

Before a normal authorized push, fetch the configured remote and preserve both
histories. Force/tag pushes, branch deletion, different targets and published
history rewrites need separate explicit authorization.
