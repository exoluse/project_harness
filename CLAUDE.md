# Claude Code Adapter

Follow [AGENTS.md](AGENTS.md) as the governing policy. Read it and this adapter
once per session; a current supplied/read copy counts. Use its
[startup and routing rules](AGENTS.md#startup-and-context) to identify the
requested scope and read applicable detailed rules before acting. All shared
authority, documentation, ownership, verification and safety requirements apply.

The import below supplies the current policy with this adapter in every
session, so it stays in context after compaction:

@AGENTS.md

## Model tiers

Apply [model selection](docs/CONTEXT_EFFICIENCY.md#model-selection-and-delegation)
to reasoning and implementation. Resolve supported aliases or full model IDs
from the current tool and provider. Check their capability and effective model;
this adapter keeps no fixed family-to-tier ranking.

For delegation, use the Agent tool's `model` option when exposed and permitted.
Account for the subagent definition's `model` frontmatter and effective managed
or forced settings. An alias or `inherit` can resolve to the main session's
model; use it only when that model suits the work. Respect explicit pins and
tool restrictions under the shared selection rules.

If the main model is unsuitable, recommend that the user select a suitable model
with `/model`, following the shared capability-gap procedure. Do not assume that
a model listed in provider documentation is enabled for this account or client.

Last checked: 2026-09-29 against the Claude Code
[subagent model selection](https://code.claude.com/docs/en/sub-agents#choose-a-model)
and [model configuration](https://code.claude.com/docs/en/model-config) documentation.
Documentation reviewed; model switching and delegation were not exercised.
