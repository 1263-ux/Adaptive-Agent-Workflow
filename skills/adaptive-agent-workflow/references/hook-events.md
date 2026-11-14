# Hook Events and Adaptive Checkpoints

## Contract

A hook event is a lifecycle signal that should cause the responsible Agent to re-observe the current task. The hook itself should remain deterministic, fast and side-effect-light.

### Supported logical events

| Logical event | Meaning | Required response |
|---|---|---|
| `owner_round_finished` | Main owner reaches a turn/round boundary | Review result, method fit, capability gaps and next action |
| `subtask_finished` | A sub-agent finishes a bounded task | Review output and hand off verified findings, artifacts, gaps and next action |

## Host mapping

| Host | Owner round | Subtask finished |
|---|---|---|
| Codex | `Stop` | `SubagentStop` |
| Claude Code | `Stop` | `SubagentStop` |

The mappings are semantically similar, not identical. Codex uses a continuation decision/reason. Claude Code supports additional context on Stop/SubagentStop.

Claude Code `TaskCompleted` is intentionally not used in the first prototype because its command-hook control is completion blocking, not a general non-blocking context injection. Use Stop/SubagentStop for adaptive review.

## Responsibilities

- **Hook:** detect event, apply recursion guard, inject a concise checkpoint prompt.
- **Owner Agent:** inspect evidence and decide whether to continue, discover capability, change method/team/scope or deliver.
- **Capability mechanism:** discover, inspect, select, load/install/mount only through actual host-supported mechanisms.
- **Host:** enforce tool permissions, project trust and workspace boundaries.

## Recursion guard

If the host reports `stop_hook_active: true`, the handler must return without another continuation. This prevents an endless review loop.

## Non-goals

- No automatic Skill installation or arbitrary code execution.
- No mandatory new Skill search on every checkpoint.
- No per-tool-call review.
- No custom task database or orchestration runtime.
- No claim that a reference read equals a Skill mounted into a child Agent.
