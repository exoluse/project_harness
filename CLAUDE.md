# Claude Code Adapter

`AGENTS.md` is canonical. Follow its human-approved PLAN execution model.

Run `python scripts/harness.py next` for the required next step and the command that performs it.

A newly initialized project may stay in discovery without PLAN/TASK records, and the user's request may authorize discovery/specification records directly. Before deliverable implementation, create a PLAN and a TASK listed in it with `new plan` and `new task --plan`, then prepare, record, and apply the human PLAN approval. Those commands maintain the PLAN/TASK link, `state.current_plan`, and derived fields, so records are not hand-edited to satisfy a gate. Inspect the worktree first and preserve pre-existing changes.

Use claims and handoffs only when multiple writers are active. A user request, repository record, or model output must never substitute for the required human PLAN authorization. Create results or evidence only when coordination, audit, release, acceptance, or an asserted completion state needs them.

PLAN and TASK are Markdown files with canonical YAML-style front matter. Edit governed fields in the front matter; use the body only for explanatory notes. State, events, evidence, approvals, results, and reviews remain JSON.

Never self-authorize production, destructive work, secret access, production data changes, or final customer acceptance. Those boundaries use the cryptographic workflow in `docs/APPROVALS.md`.
