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

Inspect before writing, and reverse it when you stop:

```bash
python scripts/install_workflow.py --project "/path/to/your/actual-project" --host both --dry-run
python scripts/install_workflow.py --project "/path/to/your/actual-project" --host both --uninstall
```

Uninstall removes only AAW handlers and the two AAW `.gitignore` lines. Other hooks, permissions, generic ignore entries (such as `__pycache__/`), `.aaw/` progress and runtime records stay where they are.

Codex loads hooks from `CODEX_HOME/hooks.json` only, so install it globally:

```bash
python scripts/install_workflow.py --project "/path/to/your/actual-project" --host codex --codex-global
```

The global file is shared with every project, so the handler is installed without `--project` and resolves the project from the event. A backup of the previous `hooks.json` is written next to it, foreign hooks and unrelated keys are preserved, and `--uninstall --codex-global` restores it.

Codex hooks are also opt-in upstream: without `[features] hooks = true` in `CODEX_HOME/config.toml` the handlers never run and nothing reports the failure. The installer warns when that line is missing (see [host verification](host-verification.md)).

## Give the outcome, not a management checklist

Ask for the actual task and invoke Adaptive Agent Workflow through the host. The owner chooses a short plan and professional capability, produces a useful slice, inspects collaborators' results, updates current work and continues. A simple request stays direct.

The owner can initialize continuing work using its installed Skill script:

```bash
python .agents/skills/adaptive-agent-workflow/scripts/adaptive_checkpoint.py --project . --init "Deliver the requested outcome" --next "First concrete action" --session <id>

Add `--session <id>` when one project is worked from more than one session: only the session named in the note may claim the Stop continuation, so two terminals cannot run the same slice. Omit it for a single-session project.
```

For Claude Code substitute `.claude/skills/`. This is an agent action, not a form the user must fill. The owner then edits the note as work progresses and sets `Status: done`, `paused` or `blocked` when appropriate.

## What is persisted

- Current work: goal, next slice, actual capability/owner assignments, results and next action.
- `.aaw/runtime/handoffs/`: bounded worker reports awaiting owner inspection.
- `.aaw/runtime/events/`: host observations, not proof of task success.

Runtime records are local and Git-ignored. `--report` summarizes them and `--prune N` keeps the newest N; there is no panel and no background process reading them.

## Verify installation

```bash
python -m unittest discover -s tests -v
python scripts/sync_skills.py --check
```

Local tests cover real subprocess commands, progress resume, prompt augmentation, parent feedback and merging settings. To check the host itself, use one real bounded delegation and inspect the child prompt, returned artifact and owner continuation. See [event semantics](../skills/adaptive-agent-workflow/references/hook-events.md).

For Dot or another host without these hooks, load the complete portable Skill and use its explicit owner loop/current-work note. Do not assume installing Codex/Claude settings activates a different host.
