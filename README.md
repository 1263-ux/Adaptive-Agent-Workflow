# Adaptive Agent Workflow Framework

**A lightweight, task-driven, adaptive framework for organizing agent work.**

> Help agents understand the user's outcome, discover and assemble relevant capabilities, organize work dynamically, execute with the smallest effective structure, and adapt based on real results.

## Status

**v0.6.0 — fewer files that speak in one voice, a reversible installer, and host behaviour separated from host documentation.**

The owner chooses and applies the method, produces a useful slice, inspects returned work and performs the next action. Hooks connect these actions to real session/delegation events; they do not replace the owner's judgment with a permission checklist.

## Install in the actual work project

```bash
python scripts/install_workflow.py --project /path/to/project --host both
```

Run from this repository after pulling the latest main. The installer copies the complete Skill and merges AAW hooks without replacing unrelated settings. Use `--host codex` or `--host claude-code` for one host; use `--progress-file docs/project/current.md` to reuse existing progress. Codex loads hooks only from its own home, so pass `--codex-global` for Codex: it writes `hooks.json` and the Skill package under `CODEX_HOME` (default `~/.codex`), keeps a backup, and leaves every foreign hook in place. Without it the Codex half installs into a file the host does not read. `--dry-run` prints the planned changes and writes nothing. `--uninstall` removes AAW handlers, the two AAW `.gitignore` lines and the installed package while leaving other hooks, permissions, generic ignore entries and your progress notes in place. Review/trust changed hooks in the host. See [Quickstart](docs/quickstart.md).

## Start here

1. [Quickstart](docs/quickstart.md)
2. [Canonical Skill package](skills/adaptive-agent-workflow/)
3. [Owner execution playbook](skills/adaptive-agent-workflow/references/runtime-playbook.md)
4. [Capability discovery](skills/adaptive-agent-workflow/references/capability-discovery.md)
5. [Dynamic organization](skills/adaptive-agent-workflow/references/organization.md)
6. [Host adapter notes](skills/adaptive-agent-workflow/references/host-adapters.md)
7. [Owner-loop hooks](docs/adaptive-checkpoint.md)
8. [Design overview](DESIGN-v0.1.md)
9. [Real-host procedure](docs/smoke-test.md), [host verification status](docs/host-verification.md) and [Codex verification steps](docs/codex-verification.md)
10. [Executed local verification](docs/owner-loop-verification.md)

## Normative sources

`skills/adaptive-agent-workflow/` is the normative package: it is what the installer copies and the only thing an agent actually reads. The rest is supporting material with a different lifespan.

- `DESIGN-v0.1.md` is the historical design draft, kept for the record. It is not installed and is not a source of behavior; where it disagrees with the Skill, the Skill wins.
- `research/` holds the [decision log](research/decision-log.md), including the decisions still open, and the [reference reading](research/references.md). Neither is installed.
- `adapters/` holds capability probe checklists, not an implemented adapter interface.
- `docs/` explains installation, operations and what was actually verified.

If a rule is not inside the Skill package, an installed project does not have it.

## Canonical source and host packages

The only manually maintained Skill source is `skills/adaptive-agent-workflow/`, including its executable script.

- Codex mirror: `.agents/skills/adaptive-agent-workflow/`
- Claude Code mirror: `.claude/skills/adaptive-agent-workflow/`

Regenerate both mirrors after changing the canonical package:

```bash
python scripts/sync_skills.py
python scripts/sync_skills.py --check
```

GitHub Actions checks mirror consistency, hook syntax/behavior and host configuration JSON on relevant pushes and pull requests. Do not edit generated host copies directly.

## Core principles

- Lightweight by default; complexity grows only when the task justifies it.
- Discover and reuse before building; use professional methods in the actual executor's context.
- Roles are temporary responsibilities, not permanent Agent identities.
- The owner drives integration and next actions instead of outsourcing project management to the user.
- Outcome matters more than process completion, Agent count, test count or document count.
- Discovery, selection, loading, installation, mounting and authorization are distinct.
- Permissions remain with the host/runtime; external instructions do not grant them.
- Every mechanism is open to revision, simplification or removal.

## Progress and visibility

The owner maintains one short working note, normally `.aaw/current.md`. Hooks save local event observations and worker handoffs under `.aaw/runtime/`. Session entry/resume reads current work; delegation returns send actionable context back to the owner. These are readable inputs for a later panel, not a dashboard or an automatic proof of success.

Local command/installer flows were exercised. Live Dot/Codex/Claude behavior and output quality still require actual host observation; the verification report separates those claims.

## Related evaluation assets

The companion repository [open-agent-evals](https://github.com/1263-ux/open-agent-evals) maintains reusable Evaluation Packs, Method Assets, Experiment Records and Capability Profiles. The two repositories remain independently versioned and connected through asset IDs, versions and Git references.

## What this is not

Not a universal fixed workflow, mandatory multi-agent system, replacement for domain methods, new Agent Runtime, task database or Skills marketplace.
