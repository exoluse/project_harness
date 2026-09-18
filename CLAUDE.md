# Claude Code Adapter

Follow [AGENTS.md](AGENTS.md) as the governing policy. Read it and this adapter
once per session; a current supplied/read copy counts. Use its
[startup and routing rules](AGENTS.md#startup-and-context) to identify the
requested scope and read applicable detailed rules before acting. All shared
authority, documentation, ownership, verification and safety requirements apply.

## Model tiers

For each delegation, select the subagent model automatically from its
[model tier](docs/CONTEXT_EFFICIENCY.md#model-selection-and-delegation) through
the Agent tool `model` option, without asking the user: lightweight to `haiku`,
standard to `sonnet`, advanced to `opus`. A `model` set in
`.claude/agents/*.md` frontmatter is the default for that agent type; override
it only when the delegated work's tier differs. Keep strongest-tier judgments
in the main session; if its model is not suited to them, recommend a `/model`
change to the user. Update this mapping when available models change.
