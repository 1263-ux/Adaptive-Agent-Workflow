# Owner-loop execution support (v0.3.1)

The former Stop-only reminder has been replaced by a connected owner loop:

**Read current work → select and apply capability → equip the executor → produce a slice → return results to the owner → update and perform the next action.**

The implementation and [portable event contract](../skills/adaptive-agent-workflow/references/hook-events.md) are maintained inside the canonical Skill. [Install it into the actual work project](quickstart.md), not just the workflow repository.

SessionStart/UserPromptSubmit bring in current work. PreToolUse on delegation appends a scoped execution brief and capability references to the child prompt. SubagentStop saves a report without restarting the child. PostToolUse on delegation/collection returns actionable feedback to the caller. Stop requests one continuation only for active saved work; done, paused, blocked and absent work do not loop.

A newly spawned agent ID is not a finished artifact. The owner checks whether the returned work is ready, then opens and integrates/corrects the actual result. Updating progress and selecting the next action are owner responsibilities, not user chores.

The working note is maintained by the agent; hook observations and child reports are saved by code. No code path claims that a Skill was used, that an MCP worked, or that an output was accepted merely because an event occurred.

No new permission gates, task database, model calls or background scheduler are added. Existing host permissions remain in force. In Claude Code auto mode, changed delegation inputs can require the host to re-evaluate the call; this integration does not override that permission decision.

Test report: [local execution verification](owner-loop-verification.md). Real Dot/Codex/Claude task-quality effects are not established by local protocol tests.
