# Codex Start Prompt

Follow [AGENTS.md](AGENTS.md) as the governing policy. Read it and this entry
once per session; a current supplied/read copy counts. Use its
[startup and routing rules](AGENTS.md#startup-and-context) to identify the
requested scope and read applicable detailed rules before acting. All shared
authority, documentation, ownership, verification and safety requirements apply.

## Model tiers

Apply [model selection](docs/CONTEXT_EFFICIENCY.md#model-selection-and-delegation)
to reasoning and implementation. Resolve models from the current session's
supported choices; use the official model guidance to assess capability when
needed. This adapter keeps no fixed generation-to-tier mapping.

For delegation, use an explicit spawn model when the tool exposes and permits
that override. Account for `agents.default_subagent_model` and any agent role's
`config_file` settings. Follow the actual tool's inheritance and override rules;
an inherited or configured model must still suit the assigned work. Respect
explicit pins and tool restrictions under the shared selection rules.

The main model is selected through the client's model control, or `/model` in
an interactive CLI session. Apply the shared capability-gap procedure when it
is unsuitable; recommending a change does not perform one.

Last checked: 2026-09-29 against the [Codex models](https://learn.chatgpt.com/docs/models),
[subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents)
and [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).
Documentation reviewed; model switching and delegation were not exercised.
