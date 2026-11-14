# Adaptive Checkpoint Hooks

## Purpose

The hook prototype makes capability reassessment recur during execution. It does not make decisions or install Skills. It injects a short checkpoint instruction at the end of a main turn and when a sub-agent stops.

**Hook triggers observation; the responsible Agent decides; the host performs supported loading/authorization.**

## Events configured

| Logical moment | Codex event | Claude Code event | Behavior |
|---|---|---|---|
| Main owner finishes a turn/round | Stop | Stop | Ask the owner to inspect results, reassess methods/capabilities/team, then continue, adapt or deliver |
| Sub-agent finishes | SubagentStop | SubagentStop | Ask the sub-agent to review its output and provide a factual handoff |

We intentionally do not hook every tool call. Tool-level hooks would create noise and context overhead. We also do not use Claude Code TaskCompleted in this prototype: that event's command-hook control is designed to block completion, not inject a non-blocking adaptive review. Stop/SubagentStop provide the required context/continuation behavior.

## What happens at a checkpoint

The injected instruction asks the Agent to:
1. Inspect the actual output and evidence.
2. Decide whether current methods and capabilities remain adequate.
3. Discover/inspect/load a specialist Skill only if a real gap or better option exists.
4. Change owner, team, task topology or scope only when useful.
5. Continue when the current approach is adequate.
6. Give the parent owner a factual handoff when the event belongs to a sub-agent.

A checkpoint does not mean a new Skill must be loaded every time.

## Recursion and cost controls

- The handler exits silently when the host sets `stop_hook_active: true`, preventing repeated continuation loops.
- The handler is standard-library Python and performs no network access, installation, file writes or Skill execution.
- Hook timeout is 10 seconds; normal execution should be nearly instantaneous.
- The checkpoint is deliberately short and does not read full transcripts.
- Hook trust/approval is controlled by the host.

## Codex setup

The repository includes `.codex/hooks.json`. Open the repository in Codex, inspect the project hooks with `/hooks`, and explicitly review/trust the definitions before use. Project hooks load only when the project is trusted.

The Codex commands use `python3` on Unix-like systems and `python` on Windows. The Claude Code commands use `python` with the project-directory variable. Ensure the selected launcher points to Python 3; adjust the command in the relevant host configuration if your environment uses a different launcher.

Codex Stop/SubagentStop continuation uses a hook `decision: block` with a reason that becomes the next continuation prompt. It is not the same output protocol as Claude Code.

Official reference: https://learn.chatgpt.com/docs/hooks

## Claude Code setup

The repository includes `.claude/settings.json`. Open the project in Claude Code and review/trust the project settings/hooks when prompted. The command uses `python`; ensure Python 3 is available as `python` on PATH. If not, change it to your local Python launcher.

Claude Code Stop/SubagentStop hooks inject `hookSpecificOutput.additionalContext`. They do not block task completion in this configuration.

Official reference: https://code.claude.com/docs/en/hooks

## Limitations

- This hook does not discover Skills itself. It prompts the Agent to perform discovery through the host's available Skill/search tools.
- It cannot guarantee per-subagent Skill injection. The Agent must use native host support or pass scoped instructions in the task brief.
- It cannot prove that a Skill is mounted. The Agent must report the actual state.
- Codex's Stop hook continues the turn with a new prompt; Claude Code adds context to the continuing conversation. The user experience is similar, not identical.
- Host versions and local settings may affect hook support. Verify in the host UI/logs after installation.

## Test

Run:

```bash
python -m unittest discover -s tests -v
```

The tests validate event mapping, output shape, recursion guard and unrelated-event no-op behavior. They do not replace an end-to-end test in the actual Codex and Claude Code hosts.
