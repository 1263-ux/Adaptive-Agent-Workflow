# Adaptive Agent Workflow Framework

**A lightweight, task-driven, adaptive framework for organizing agent work.**

> Help agents understand the user's outcome, discover and assemble relevant capabilities, organize work dynamically, execute with the smallest effective structure, and adapt based on real results.

## Status

**v0.2.0 — usable Skill package; no custom Agent Runtime.**

The repository now includes executable Agent Skills for Codex and Claude Code, plus a portable canonical Skill. It is intended to guide real task execution through host-native mechanisms. It does not implement its own scheduler, permission system, task database or Skill marketplace.

## Start here

1. [Quickstart](docs/quickstart.md)
2. [Portable Skill](skills/adaptive-agent-workflow/SKILL.md)
3. [Codex project Skill](.agents/skills/adaptive-agent-workflow/SKILL.md)
4. [Claude Code project Skill](.claude/skills/adaptive-agent-workflow/SKILL.md)
5. [Design overview](DESIGN-v0.1.md)
6. [Runtime playbook](core/runtime-playbook.md)
7. [Capability discovery and mounting](references/capability-discovery.md)
8. [Dynamic organization](references/organization.md)
9. [Host adapter notes](references/host-adapters.md)

## Core principles

- Lightweight by default; complexity grows only when the task justifies it.
- Discover and reuse before building.
- Professional methods are supplied by mature domain Skills and tools, not recreated in this framework.
- Roles are temporary responsibilities, not permanent Agent identities.
- Outcome matters more than process completion.
- Agent count, test count and document count are not proxies for quality.
- Discovery, selection, loading, installation, mounting and authorization are distinct.
- Permissions must be enforced by the host/runtime, never merely claimed by prompts.
- Every mechanism is open to revision, simplification or removal.

## Operating loop

Understand → Explore (when useful) → Organize (when useful) → Execute → Deliver → Observe & Adapt.

These are decision capabilities, not mandatory sequential phases. Simple tasks may go directly to execution. Complex or unfamiliar tasks can explore, form teams and revisit earlier decisions.

## Host support

- **Codex:** project Skill under `.agents/skills/`.
- **Claude Code:** project Skill under `.claude/skills/`.
- **Other hosts:** use the portable Skill and the host's documented installation/invocation mechanism.

See [host adapter notes](references/host-adapters.md). Host capabilities must be verified against the actual host/version. The framework does not create permissions or guarantee dynamic per-agent mounting.

## Related evaluation assets

The companion repository [open-agent-evals](https://github.com/1263-ux/open-agent-evals) maintains reusable Evaluation Packs, Method Assets, Experiment Records and Capability Profiles. The two repositories are independently versioned and connected through asset IDs, versions and Git references.

## What this is not

- Not a universal fixed workflow.
- Not a mandatory multi-agent system.
- Not a replacement for professional software/game/research/design methodologies.
- Not a new Agent Runtime, task database or Skills marketplace.
