# Adaptive Agent Workflow Framework

**A lightweight, task-driven, adaptive framework for organizing agent work.**

> Help agents understand the user's outcome, discover and assemble relevant capabilities, organize work dynamically, execute with the smallest effective structure, and adapt based on real results.

## Status

**v0.2.1 — canonical Skill package with generated host mirrors; no custom Agent Runtime.**

## Start here

1. [Quickstart](docs/quickstart.md)
2. [Canonical Skill package](skills/adaptive-agent-workflow/)
3. [Runtime playbook](skills/adaptive-agent-workflow/references/runtime-playbook.md)
4. [Capability discovery and mounting](skills/adaptive-agent-workflow/references/capability-discovery.md)
5. [Dynamic organization](skills/adaptive-agent-workflow/references/organization.md)
6. [Host adapter notes](skills/adaptive-agent-workflow/references/host-adapters.md)
7. [Design overview](DESIGN-v0.1.md)
8. [Runtime smoke tests](docs/smoke-test.md)

## Canonical source and host packages

The only manually maintained Skill source is `skills/adaptive-agent-workflow/`.

- Codex mirror: `.agents/skills/adaptive-agent-workflow/`
- Claude Code mirror: `.claude/skills/adaptive-agent-workflow/`

Regenerate both mirrors after changing the canonical package:

```bash
python scripts/sync_skills.py
```

Check for drift without modifying files:

```bash
python scripts/sync_skills.py --check
```

GitHub Actions checks mirror consistency on relevant pushes and pull requests. Do not edit generated host copies directly.

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

## Related evaluation assets

The companion repository [open-agent-evals](https://github.com/1263-ux/open-agent-evals) maintains reusable Evaluation Packs, Method Assets, Experiment Records and Capability Profiles. The two repositories are independently versioned and connected through asset IDs, versions and Git references.

## What this is not

- Not a universal fixed workflow.
- Not a mandatory multi-agent system.
- Not a replacement for professional software/game/research/design methodologies.
- Not a new Agent Runtime, task database or Skills marketplace.
