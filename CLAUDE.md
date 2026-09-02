# Claude Code Adapter

`AGENTS.md` is canonical. Follow its `USER_DIRECTED` execution model.

For an explicit user request, ordinary development, tests, commits, fetch, conflict resolution, and a normal push to the configured upstream do not require a plan, task, claim, result, event, or evidence record. Inspect the worktree first and preserve pre-existing changes.

Use claims and handoffs only when multiple writers are active. Treat plans as reference material. Create results or evidence only when coordination, audit, release, acceptance, or an asserted completion state needs them.

Never self-authorize production, destructive work, secret access, production data changes, or final customer acceptance. Those boundaries use the cryptographic workflow in `docs/APPROVALS.md`.
