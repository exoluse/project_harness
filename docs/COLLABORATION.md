# Collaboration and Handover

Follow [AGENTS.md](../AGENTS.md). Ownership coordination prevents conflicting
writes; it does not create execution authority.

## Collaboration basis

All participating agents use the same plan/task boundaries, directory mapping
and document-ID convention, regardless of their tool. Make the following clear
in the existing overview and linked plan/task documents before concurrent work:

| Basis | Shared information |
|---|---|
| Plans and tasks | Plans organize goals, scope, dependencies, task order and overall completion criteria. Each task states its concrete output, writer, affected paths/logical resources and completion checks, and links its plan and required inputs. |
| Directory structure | The overview records the document root and type-to-folder mapping. Choose names and nesting for the project, reuse them consistently and identify each writer's actual edit scope. |
| Markdown filenames and serials | Each independent item owns an exact `<ID>.md` file in its mapped folder, subject to documented required-name exceptions. Allocate unique five-digit serials project-wide per complete semantic prefix. |

Use the [requirement boundaries](DATA_MODEL.md#requirement-boundaries) as the
shared basis for product scope. Writers working on the same requirement link
the same REQ; a task assignment or handoff does not create another requirement.
See [plans and tasks](DATA_MODEL.md#plans-and-tasks) and the
[ID convention](DATA_MODEL.md#item-ids). Folder and prefix examples are starting
choices; agents extend the shared mapping for actual needs. One directory can
contain several writers' files when their edit scopes do not overlap.

Before allocating concurrently, record non-overlapping ranges or meaningful
prefix ownership where all writers can see them. Separate checkouts must use
that shared allocation, not independently choose the same next number from
their local copies. Do not introduce agent-specific prefixes for the same
document type. Reserve ranges within the existing prefix instead. Keep IDs
stable through reassignment, and never reuse retired IDs.

Include the overview, shared specifications and Git integration in the ownership
agreement. Identify who edits shared files and who integrates changes; other
writers hand their changes to that owner or agree a transfer before editing.
When a checkout is shared, serialize Git index/branch operations through the
assigned integration owner. Record relevant ownership, mapping and allocation
changes before affected work continues. Existing Markdown notes are sufficient;
these principles add no separate approval or registry service.

## Single writer

A single writer needs no claim system or placeholder handoff.
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

## Subagent delegation

The accountable agent may start subagents without separate user authorization
when delegation serves the current request, and chooses their capability under
[model selection](CONTEXT_EFFICIENCY.md#model-selection-and-delegation).
Delegation is a working method, not a default. It adds no authority: delegated
work stays within the accountable agent's current scope, and edits, product-code
execution, external effects and high-risk actions keep their own requirements.
Writing subagents follow the [collaboration basis](#collaboration-basis) with
non-overlapping ownership. User instructions or tool rules that limit or
prohibit delegation remain binding.

## Formal records for a single writer

A requested result or handoff can be an ordinary document when the agreed
delivery contract accepts it. Record the real baseline, changed paths, decisions,
checks, observations, limits, unfinished work and next action.

## Transfer and integration

At transfer, identify the actual owner, input/output versions, dirty work,
applicable decisions, failed or unrun checks, outstanding obligations and next
steps. The recipient checks applicability and permissions in the new environment;
a handoff does not widen the original decision.

Carry links to retained open items with their current state, blocking impact,
resolution criterion, owner, next action and needed-by/review trigger. Include
unpropagated resolutions, deferred work and missing assignments. Record any
actual ownership transfer; receipt of a handoff is not resolution or consent.
Apply the [open-item lifecycle](WORKFLOW.md#open-item-lifecycle) when the recipient
checks current applicability and dependent-work readiness.

Preserve both sides during integration. Do not silently reset unknown work,
drop failed attempts or hide a newer failure behind an older success.
Verification should address the actual integration impact, rather than rerunning
unaffected checks solely because ownership or document layout changed.

Before a normal authorized push, fetch the configured remote and preserve both
histories. Force/tag pushes, branch deletion, different targets and published
history rewrites need separate explicit authorization.
