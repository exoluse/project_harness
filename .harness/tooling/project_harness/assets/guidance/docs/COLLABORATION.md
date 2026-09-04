# Collaboration

## Claims are concurrency control

A claim is needed only while multiple writers can edit concurrently. It is not routine execution authority, human approval, or a prerequisite for a single-agent task.

Before concurrent work:

```powershell
git status --short
python scripts/harness.py mailbox list --box inbox --agent <agent-id>
python scripts/harness.py claim acquire --agent <agent-id> --task TASK-0001 --paths <path> [<path> ...]
```

Use separate Git worktrees, non-overlapping paths, and non-overlapping logical locks. The runtime under `<git-common-dir>/project-harness-runtime/` makes claims visible across linked worktrees. Do not edit another active claim's files.

## Handoff

Use a handoff only when ownership of in-progress work moves between agents. It records exact changed files, file states, verification, limits, risks, and the next action, then releases the sender's claim. The receiver accepts it while acquiring its own claim.

```powershell
python scripts/harness.py handoff create --claim CLM-0001 --from-agent codex --to-agent claude --task TASK-0001 --summary "Continue implementation" --changed-file src/example.py --verification "python -m unittest::PASS" --next-action "Review and continue"
python scripts/harness.py claim acquire --agent claude --task TASK-0001 --paths src/example.py --handoff HOF-0001
```

## Results and reviews

Results are on-demand audit objects. Use one when a task attempt needs independent review, immutable build lineage, a release gate, or a formal handback. A routine commit does not require one.

When a result is used, its latest attempt controls that audited workflow. A newer failed or incomplete attempt cannot be hidden by an older PASS. Reviewer IDs are provenance strings, not cryptographic identities; hostile separation needs protected CI or an external orchestrator.

## Dirty work and recovery

Unowned dirty paths remain `USER_OR_UNKNOWN`. Never reset, clean, delete, or overwrite them to satisfy a claim. Recovery may abandon a stale lease after its structured checks, but it does not take ownership of dirty files.

No-Git claims serialize writers but cannot prove committed lineage. Use Git and isolated worktrees for parallel work or release-grade integration.
