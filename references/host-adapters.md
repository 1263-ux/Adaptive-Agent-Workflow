# Host Adapter Notes

This file describes host patterns, not guarantees. Verify the installed host and version before relying on a capability.

## Common semantics
Discovery, inspection, loading, installation, mounting and authorization are different operations. A Skill cannot grant permission.

## Codex
- Project Skills are conventionally stored under .agents/skills/<skill-name>/SKILL.md.
- User Skills are conventionally stored under ~/.agents/skills/<skill-name>/SKILL.md.
- Codex progressively discloses Skills: metadata is available for discovery; full instructions load when selected; references/scripts are accessed only when needed.
- Subagents use Codex-supported mechanisms and inherit parent permissions, provider and MCP configuration. A custom Agent prompt does not create a separate security boundary.
- Do not assume a Skill can be forcibly injected into a child context unless the current interface supports it. Pass a reference or scoped instructions in the task prompt when needed.

Official references:
- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://learn.chatgpt.com/docs/customization/overview

## Claude Code
- Project Skills are conventionally stored under .claude/skills/<skill-name>/SKILL.md.
- Skill metadata can be discovered before the full body is loaded; invoked Skills load instructions on demand.
- Subagents use host-specific agent definitions and isolated contexts. Tool availability and permissions are configured by Claude Code, not by a Skill body.
- A Skill and a subagent are different primitives: use a Skill for reusable instructions; use a subagent for isolated side work.
- Verify the current version and settings before assuming nested delegation, tool restrictions or lifecycle behavior.

Official references:
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/sub-agents

## Other hosts
Use portable Agent Skills format where supported. Otherwise expose the Skill through the host's documented mechanism.

If dynamic Skill search, per-Agent mounting, nested delegation, isolated workspaces or resumable handoff is unavailable:
1. Mark it UNSUPPORTED or UNVERIFIED.
2. Use the smallest supported fallback.
3. Do not claim native support.
4. Keep permission enforcement in the host/runtime.
