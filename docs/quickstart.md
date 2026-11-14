# Quickstart

## Codex
This repository includes a project Skill at .agents/skills/adaptive-agent-workflow/SKILL.md. Open the repository in Codex and check the host's Skill selector/discovery. If it does not appear, verify the path and refresh the host according to its current documentation.

## Claude Code
This repository includes a project Skill at .claude/skills/adaptive-agent-workflow/SKILL.md. Open the repository in Claude Code and invoke it or let the host match the task.

## Other hosts
Use skills/adaptive-agent-workflow/SKILL.md as the portable canonical copy. Install it in the host's documented Skill location if supported; otherwise expose its instructions using the documented mechanism.

## Smoke prompts
- "Fix this small local bug." Expected: direct execution, no unnecessary team.
- "Explore suitable mature Skills for this unfamiliar task before committing to an approach." Expected: capability discovery before commitment.
- "Build these independent components in parallel." Expected: bounded outputs and explicit integration boundaries.
- "The current method is not achieving the target. Diagnose why and adapt." Expected: cause analysis before adding rules or repeating the same attempt.

This framework does not guarantee every host feature. See adapters/host-adapters.md.
