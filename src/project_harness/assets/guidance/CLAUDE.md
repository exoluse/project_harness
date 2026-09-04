# Claude Code Adapter

`AGENTS.md` is canonical. Follow its `USER_DIRECTED` execution model.

Run `python scripts/harness.py next` for the required next step and the command that performs it.

A newly initialized project may stay in discovery without PLAN/TASK records, and the user's request may authorize discovery/specification records directly. Before deliverable implementation, create or select a current PLAN and a TASK listed in that PLAN using `new plan`, `new task --plan`, and `plan activate`; those commands maintain the PLAN/TASK link, `state.current_plan`, and derived fields, so records are not hand-edited to satisfy a gate. The user's explicit request authorizes execution of that TASK; PLAN approval, claim, result, event, and evidence records remain unnecessary for routine work. Inspect the worktree first and preserve pre-existing changes.

Use claims and handoffs only when multiple writers are active. Treat the required PLAN as planning structure rather than human authorization. Create results or evidence only when coordination, audit, release, acceptance, or an asserted completion state needs them.

PLAN and TASK are Markdown files with canonical YAML-style front matter. Edit governed fields in the front matter; use the body only for explanatory notes. State, events, evidence, approvals, results, and reviews remain JSON.

Never self-authorize production, destructive work, secret access, production data changes, or final customer acceptance. Those boundaries use the cryptographic workflow in `docs/APPROVALS.md`.
