# Codex Start Prompt

Follow [AGENTS.md](AGENTS.md) as the governing policy. Read it and this entry
once per session; a current supplied/read copy counts. Use its
[startup and routing rules](AGENTS.md#startup-and-context) to identify the
requested scope and read applicable detailed rules before acting. All shared
authority, documentation, ownership, verification and safety requirements apply.

## In an adopting project

Codex loads the project's root `AGENTS.md`, which belongs to the project. It
reads `AGENTS.md` files from the project root down to the working directory and
has no documented import syntax. The root file therefore names the
[harness copy](docs/DATA_MODEL.md#project-instruction-files) and tells the
session to read the policy and this adapter there, such as
`harness/AGENTS.md` and `harness/CODEX_START_PROMPT.md`, before acting. It also
carries the project's entry content or routes to the file that holds it.

Codex stops adding instruction files once their combined size reaches a limit,
32 KiB by default (`project_doc_max_bytes`). A short root entry file stays well
under it, and the harness files are read on instruction instead.

Last checked: 2026-10-02 against the Codex
[AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
Documentation reviewed through fetched page summaries; loading was not exercised.

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
