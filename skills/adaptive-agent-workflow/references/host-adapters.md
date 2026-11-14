# Host Adapter Notes

Verify the installed host and version. These are conventions, not guarantees.

## Shared semantics
Discovery, inspection, loading, installation, mounting and authorization are distinct. A Skill cannot grant permissions.

## Codex
- Project Skills: .agents/skills/<skill-name>/SKILL.md
- User Skills: ~/.agents/skills/<skill-name>/SKILL.md
- Codex uses progressive disclosure: metadata for discovery, full instructions on selection, references/scripts on demand.
- Subagents inherit parent permissions, provider and MCP configuration. Custom Agent prompts do not create separate security boundaries.
- Do not assume a Skill can be injected into a particular child context unless the current interface supports it.

Official references:
- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://learn.chatgpt.com/docs/customization/overview

## Claude Code
- Project Skills: .claude/skills/<skill-name>/SKILL.md
- Skill metadata can be discovered before the full body is loaded.
- Subagents use host-specific agent definitions and isolated contexts. Tool permissions are configured by Claude Code, not by a Skill body.
- A Skill and subagent are different primitives: use a Skill for reusable instructions; use a subagent for isolated side work.
- Verify version/settings before assuming nested delegation or tool restrictions.

Official references:
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/sub-agents

## Other hosts
Use portable Agent Skills where supported; otherwise use the host's documented instruction mechanism. Mark unavailable features UNSUPPORTED or UNVERIFIED, use the smallest supported fallback, and never claim native support that was not verified.
