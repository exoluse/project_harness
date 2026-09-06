# Claude Code Adapter

`AGENTS.md` is canonical and is not loaded automatically. Read its current
repository copy once per session, then run `python scripts/harness.py next` and
use its state to load only the referenced records or policy section. Re-read an
unchanged file only when evidence shows that it changed during the session.

At `NEEDS_PLAN_APPROVAL`, the current `next` output is wrong: read only **The
path as it runs today** in `docs/WORKFLOW.md` and item 4 of
`docs/RUNTIME_GAPS.md`. PLAN approval, task gates, dirty-work preservation, and
the five cryptographic boundaries remain mandatory.
