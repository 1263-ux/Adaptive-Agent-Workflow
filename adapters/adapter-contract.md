# Host Adapter Contract

## Purpose
Map generic workflow intent to mechanisms actually supported by a host. Keep the adapter thin; do not build a new Agent Runtime.

## Probe capabilities
| Capability | Verify |
|---|---|
| Skill discovery | Can installed Skills be listed/searched? |
| Skill inspection | Can body/resources be read on demand? |
| Skill mounting | Can a Skill be loaded into a specific Agent/task and unloaded? |
| Agent dispatch | How are child tasks created, awaited and collected? |
| Nested delegation | Can child Agents delegate? |
| Context isolation | Is child context actually independent? |
| Tool permissions | Are permissions inherited/restricted? |
| Workspace isolation | Are worktrees, sandboxes or isolated filesystems available? |
| Resume/handoff | What history, tools and state survive resume? |
| Budget | How are concurrency, turns, timeout and cumulative cost controlled? |

## Capability status
Use NATIVE, EMULATED, UNSUPPORTED or UNVERIFIED, with host/version evidence. Do not hide limitations behind a boolean.

## Principles
Host features are not portable by assumption. Role prompts do not create permission isolation. Skill discovery is not mounting; mounting is not authorization. If nested dispatch is unsupported, use top-level dispatch or a flat queue. Domain methods remain external.

## Current status
No executable adapter plugin is implemented. Host-specific Skill entry points and operational notes are provided for Codex and Claude Code; other hosts use the portable Skill. Native per-Agent mounting, nested delegation and permission isolation must still be verified against the installed host/version. See skills/adaptive-agent-workflow/references/host-adapters.md.
