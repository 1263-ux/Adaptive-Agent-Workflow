# Owner-loop hooks

The portable executable is `scripts/adaptive_checkpoint.py` inside this Skill. The repository's `scripts/adaptive_checkpoint.py` delegates to it. Install the complete Skill, not only SKILL.md.

| Event | Actual behavior |
|---|---|
| SessionStart / UserPromptSubmit | Add the owner's working approach and current-work file to the receiving context. Latest user intent takes priority. |
| PreToolUse on Agent / Task / spawn_agent | Append scoped execution instructions and current capability references to the actual child prompt/message; preserve other arguments and permissions. |
| SubagentStop | Save the worker's reported result locally for owner inspection; no child continuation. |
| PostToolUse on delegation/collection tools | Tell the caller to inspect the result/status, integrate/correct a delivered artifact, update current work and execute the next action. A returned ID is not completion. |
| Stop | Only with active saved work, request one continuation carrying the actual next-action note. No note, done/paused/blocked, or an already-active stop hook produces no continuation. |

Claude Code uses `hookSpecificOutput.additionalContext`; Codex uses the same context form except Stop continuation uses `decision: block` and `reason`. This is continuation, not a permission gate. `PreToolUse.updatedInput` augments only known child prompt fields. Local tool names/coverage depend on the host version; unavailable hooks fall back to the explicit owner loop.

Use the installer in the repository for project-specific commands. It pins the installed script, project and Python executable rather than relying on the current shell directory or Python alias. It merges these hooks with other existing settings.

## Persisted data

`.aaw/current.md` is the owner's working note; an existing file may be selected with `--progress-file`. `.aaw/runtime/events/` records event observations, never inferred task success. `.aaw/runtime/handoffs/` stores bounded child reports as unreviewed data. Runtime records stay local and are ignored by Git. They are a future visibility input, not a finished dashboard or an automatic judge.

Worker reports can contain errors or untrusted text. Inspect the artifacts they point to; do not treat a saved report as authorization or proof. Child reports are limited to 4,000 characters; a transcript path can identify more context without automatically reading it. Hook output is bounded. There is no network call, auto-installation, model call or scheduling inside this handler.

## Sources and verification boundary

Protocol references checked during implementation:
- https://code.claude.com/docs/en/hooks : PreToolUse.updatedInput, parent feedback via PostToolUse(Agent), SessionStart, Stop.
- https://learn.chatgpt.com/docs/hooks : local-tool hooks, spawn_agent alias, shared context shape, Stop continuation.

Repository tests exercise local command/configuration/event flows. They are not evidence of a live Dot, Codex or Claude Code session adopting the chosen method. Record host/version and a real artifact when validating that behavior.
