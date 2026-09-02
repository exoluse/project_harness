# Claude Code Adapter

`AGENTS.md` is canonical. Follow its `USER_DIRECTED` execution model.

Every project requires a current PLAN and every change requires a TASK listed in that PLAN. The user's explicit request authorizes execution of that TASK; PLAN approval, claim, result, event, and evidence records remain unnecessary for routine work. Inspect the worktree first and preserve pre-existing changes.

Use claims and handoffs only when multiple writers are active. Treat the required PLAN as planning structure rather than human authorization. Create results or evidence only when coordination, audit, release, acceptance, or an asserted completion state needs them.

Never self-authorize production, destructive work, secret access, production data changes, or final customer acceptance. Those boundaries use the cryptographic workflow in `docs/APPROVALS.md`.
