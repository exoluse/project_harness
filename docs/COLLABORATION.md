# Collaboration and Handover

Follow [AGENTS.md](../AGENTS.md). Ownership coordination prevents conflicting
writes; it does not create execution authority.

## Collaboration basis

All participating agents share the same plan/task boundaries, directory mapping,
ID convention and allocation arrangement, regardless of their tool. Before
concurrent work, make these clear in the existing overview and linked plan/task
documents:

- [plans and tasks](DATA_MODEL.md#plans-and-tasks), with each task's writer and
  actual edit scope;
- the document root and [folder mapping](DATA_MODEL.md#folders-by-document-kind);
- the [ID format table](DATA_MODEL.md#item-ids) and the
  [allocation arrangement](DATA_MODEL.md#allocation-and-validation-reuse).

Writers on the same requirement link the same REQ; a task assignment or handoff
does not create another requirement. One directory can contain several writers'
files when their edit scopes do not overlap. Do not introduce agent-specific
prefixes for the same document type.

Include the overview (root and [area overviews](DATA_MODEL.md#area-overviews)
when used), shared specifications and Git integration in the ownership
agreement. Identify who edits shared files and who integrates changes; other
writers hand their changes to that owner or agree a transfer before editing.
When a checkout is shared, serialize Git index/branch operations through the
assigned integration owner. Record relevant ownership, mapping and allocation
changes before affected work continues. Existing Markdown notes are sufficient;
these principles add no separate approval or registry service.

When each writer uses a separate worktree or clone on their own branch,
integrates through reviewed merges, and a designated
[external work tracker](DATA_MODEL.md#external-work-trackers)
owns assignment, that arrangement satisfies the ownership agreement: the
tracker assignee and the branch identify the writer, and whoever merges a
change is its integration owner. Shared documents such as the overview and
contracts may then change through the same reviewed merge; no separate owner
table is needed in the overview. Record the arrangement once in the overview.
Writers sharing one checkout or one allocation record still need the explicit
assignments above.

## Concurrent writers

Agree owners and non-overlapping paths and logical resources before concurrent
editing. Prefer isolated worktrees when practical. Shared project notes or the
team's coordination tool can record ownership, baseline, scope and status; a
tool that owns assignment or status follows [external work trackers](DATA_MODEL.md#external-work-trackers).

Do not edit another writer's active scope. Account for shared schemas, generated
files, migrations and other logical collisions even if filenames differ.
Resolve ownership and integration order explicitly. Each writer still needs
applicable authority and real prerequisites for their own work. Under branch
isolation this rule applies at merge: resolve conflicts preserving both sides
and never overwrite the other change silently.

Concurrency is bounded by the checkout, not only by the writer. In one working
tree, keep one writing participant active at a time: their edits, and any
command that rewrites files, merge into a single uncommitted state that no one
can attribute afterwards. Read-only work — review, analysis, search and checks
that write nothing into the tree — may run alongside it. Give each concurrent
writer a separate worktree or clone with its own working directory and index.
Separate branch names within one checkout do not isolate uncommitted changes.
The ownership agreement above still applies at merge.

### Coordination waits

Identify the awaited input, responsible owner and affected dependent work in
the existing task/plan or open item. Keep unaffected, authorized work moving
when its ownership, ID allocation, contracts, inputs and permissions are ready.
Use the shared assignments; a wait never authorizes taking over another
writer's scope or making an unrecorded allocation.

| Awaited item | Work that waits |
|---|---|
| Ownership or ID allocation | Work requiring that unresolved assignment or new allocation. Existing independently assigned work may continue. |
| Shared contract or integration output | Consumers that require its unresolved content or version. Work with independent ready inputs may continue. |
| Progress-summary update | Reflection in the shared document follows its owner; already covered independent work need not wait solely for that edit. Missing decisions or assignments are not mere summary updates. |
| Git integration turn | The queued integration operation and work requiring its result. Independent work may continue without concurrent shared-index/branch operations or unauthorized shared-file edits. |

Record pending shared updates once with the owner and needed-by point in the
existing handoff/task note. Apply [summary currentness](DATA_MODEL.md#summary-ownership-and-updates)
before a decision, dependent start/resumption, handoff or completion claim
relies on the summary. Surface blockers promptly; pending reflection cannot
hide a failure, change actual readiness or establish integration success.

## Subagent delegation

The accountable agent may start subagents without separate user authorization
when delegation serves the current request, and chooses their capability under
[model selection](CONTEXT_EFFICIENCY.md#model-selection-and-delegation).
Delegation is a working method, not a default. It adds no authority: delegated
work stays within the accountable agent's current scope, and edits, product-code
execution, external effects and high-risk actions keep their own requirements.
Writing subagents follow the [collaboration basis](#collaboration-basis) with
non-overlapping ownership, including the one-writer limit per working tree in
[concurrent writers](#concurrent-writers): where subagents share a checkout,
run one writing subagent at a time and use read-only subagents for parallel
work. User instructions or tool rules that limit or prohibit delegation remain
binding.

## Transfer and integration

At transfer, identify the actual owner, objective and stopping point,
input/output versions, dirty work, completed work and changed paths, applicable
decisions, checks run with their results, failed or unrun checks, limits,
outstanding obligations and next action. Apply
[current-state updates](WORKFLOW.md#updating-current-work-state) before the
receiver relies on the entry pointers. A Markdown handoff is sufficient when
the delivery contract accepts it.

The recipient checks applicability and permissions in the new environment. A
handoff or a Git transfer does not by itself establish current permissions,
decision provenance or protected credentials, and it does not widen the
original decision.

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

Stage by explicit path. A whole-tree or whole-directory stage takes whatever
else the checkout holds, including work that was already there and files
outside the item's declared scope, and the resulting commit no longer shows who
changed what. Stage the paths the work actually changed, confirm the staged set
before committing, and leave another writer's uncommitted files unstaged,
uncommitted and unreverted, handing them back under
[concurrent writers](#concurrent-writers). Where a tool stages automatically,
inspect the staged set and unstage what the item did not change.
