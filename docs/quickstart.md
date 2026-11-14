# Quickstart: use AAW in the project doing the work

Requires Python 3.10+ and a host that supports the documented hooks.

## Install or update

From the Adaptive-Agent-Workflow checkout:

```bash
git pull --ff-only origin main
python scripts/install_workflow.py --project /path/to/your/actual-project --host both
```

Use `--host codex` or `--host claude-code` for one host. On Windows, quote the project path, for example `--project "D:\Projects\My Project"`. Run the installer on the machine that runs the host: it selects that machine's Python executable and absolute project paths. Review/trust the updated hooks in the host, then start or resume a project session.

The installer copies the COMPLETE Skill, merges only AAW handlers into the existing settings, retains unrelated hooks/permissions, and backs up existing settings once. Re-running updates the managed package/handlers. It does not create or overwrite task progress, install third-party Skills, connect MCP servers or grant permissions.

For a project already tracking progress, append `--progress-file docs/project/current.md`. Otherwise continuing work uses `.aaw/current.md`. Claude Code installations use command+args exec form; Codex uses a shell command. Matchers and hook support still depend on the installed host version.

## Give the outcome, not a management checklist

Ask for the actual task and invoke Adaptive Agent Workflow through the host. The owner chooses a short plan and professional capability, produces a useful slice, inspects collaborators' results, updates current work and continues. A simple request stays direct.

The owner can initialize continuing work using its installed Skill script:

```bash
python .agents/skills/adaptive-agent-workflow/scripts/adaptive_checkpoint.py --project . --init "Deliver the requested outcome" --next "First concrete action"
```

For Claude Code substitute `.claude/skills/`. This is an agent action, not a form the user must fill. The owner then edits the note as work progresses and sets `Status: done`, `paused` or `blocked` when appropriate.

## What is persisted

- Current work: goal, next slice, actual capability/owner assignments, results and next action.
- `.aaw/runtime/handoffs/`: bounded worker reports awaiting owner inspection.
- `.aaw/runtime/events/`: host observations, not proof of task success.

Runtime records are local and Git-ignored. A future panel can read them, but no panel is included in this version.

## Verify installation

```bash
python -m unittest discover -s tests -v
python scripts/sync_skills.py --check
```

Local tests cover real subprocess commands, progress resume, prompt augmentation, parent feedback and merging settings. To check the host itself, use one real bounded delegation and inspect the child prompt, returned artifact and owner continuation. See [event semantics](../skills/adaptive-agent-workflow/references/hook-events.md).

For Dot or another host without these hooks, load the complete portable Skill and use its explicit owner loop/current-work note. Do not assume installing Codex/Claude settings activates a different host.
