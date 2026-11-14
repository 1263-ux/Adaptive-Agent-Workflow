# Adaptive Checkpoint Hook Prototype

This folder documents the host hook prototype. The executable handler is `scripts/adaptive_checkpoint.py`.

- Codex config: `.codex/hooks.json`
- Claude Code config: `.claude/settings.json`
- Design and limitations: `docs/adaptive-checkpoint.md`
- Logical event contract: `skills/adaptive-agent-workflow/references/hook-events.md`

The hook is a trigger, not an autonomous Skill installer. It injects a short checkpoint instruction; the Agent performs the actual review and decides whether capability discovery or team changes are needed.

Install/enable hooks only after reviewing and trusting the project configuration in the host.
