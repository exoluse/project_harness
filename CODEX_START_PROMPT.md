# Codex Start Prompt

Follow [AGENTS.md](AGENTS.md) as the governing policy. Read it and this entry
once per session; a current supplied/read copy counts. Use its
[startup and routing rules](AGENTS.md#startup-and-context) to identify the
requested scope and read applicable detailed rules before acting. All shared
authority, documentation, ownership, verification and safety requirements apply.

## Model tiers

For each delegation, select the subagent model automatically from its
[model tier](docs/CONTEXT_EFFICIENCY.md#model-selection-and-delegation) through
the explicit spawn model, without asking the user: lightweight to
`gpt-5.6-luna`, standard to `gpt-5.6-terra`, advanced to `gpt-5.6-sol`. An
`agents.default_subagent_model` or agent role `config_file` model in
`.codex/config.toml` is the default for spawned agents; override it only when
the delegated work's tier differs. Keep strongest-tier judgments in the main
session; if its model is not suited to them, recommend a `/model` change to
the user. Update this mapping when available models change.

Last checked: 2026-09-18 against the [Codex models](https://learn.chatgpt.com/docs/models)
and [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).
