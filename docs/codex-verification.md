# Verifying the Codex hooks for real

The installer can place hooks correctly; only a real session proves Codex runs them. This page is the procedure, the evidence to collect and what each outcome means.

## 0. Prerequisites

- `codex --version` is 0.114 or newer (hooks are experimental from that line).
- `$env:USERPROFILE\.codex\config.toml` contains, at the top level:

  ```toml
  [features]
  hooks = true
  ```

  Without it Codex runs no handlers and reports nothing. The installer warns when the line is missing.
- The model endpoint is reachable. SessionStart fires before the model is called, so a failing call still proves hook wiring - but a complete session needs the network.

## 1. Install globally

Run from this repository. `--project` names the project you will test in; in global mode the hook does not pin it, the handler resolves each session from the event.

```powershell
cd D:\新建文件夹\aaw\Adaptive-Agent-Workflow-main
python scripts\install_workflow.py --project "D:\path\to\your-project" --host codex --codex-global --dry-run
python scripts\install_workflow.py --project "D:\path\to\your-project" --host codex --codex-global
```

Expect: the target is `%USERPROFILE%\.codex\hooks.json`, six events are listed, and `hooks.json.aaw-backup` appears next to it.

## 2. Prove the handler independently of the host

This removes the host from the equation. Run it before blaming Codex:

```powershell
'{"hook_event_name":"SessionStart","session_id":"manual","source":"startup"}' |
  python "$env:USERPROFILE\.codex\skills\adaptive-agent-workflow\scripts\adaptive_checkpoint.py" --host=codex --project "D:\path\to\your-project"
```

Expect a single line of JSON containing `hookSpecificOutput.additionalContext`, and a new file under `<project>\.aaw\runtime\events\`. If this fails, the problem is the handler or the paths, not the host.

## 3. Run a real Codex session

Work inside the project so both the event `cwd` and the process cwd resolve there:

```powershell
cd "D:\path\to\your-project"
codex exec "Reply with exactly: HOOKPROBE"
```

Interactive `codex` works too and exercises more events. Do **not** create `.aaw\current.md` with `Status: active` for the first run: the Stop hook would then ask Codex to continue, which is a different behaviour under test.

## 4. Collect two independent signals

| Signal | Where | What it proves |
|---|---|---|
| Codex prints `hook: SessionStart` (and similar lines) | Codex terminal output | the host ran a handler for that event |
| A record appears in `.aaw\runtime\events\` | `--report` or the directory | this package's handler ran and parsed the host payload |

```powershell
python "$env:USERPROFILE\.codex\skills\adaptive-agent-workflow\scripts\adaptive_checkpoint.py" --project "D:\path\to\your-project" --report
```

Copy the `--report` output verbatim - the record fields (`event`, `observed_at`, `meaning`) are the evidence.

## 5. Reading the outcome

| Observed | Conclusion |
|---|---|
| Both signals | Codex integration verified for the events that fired |
| `hook:` line but no record | Codex ran something, our command failed; re-run step 2 and compare the command in `hooks.json` |
| Record but no `hook:` line | handler was invoked by something other than the session under test; check for a second hooks file |
| Neither | hooks disabled (`features.hooks`), Codex older than 0.114, or the global file was not the one read |

`SessionStart` alone is a legitimate result for `codex exec`. `Stop` and `SubagentStop` need an interactive session or a delegation.

## 6. One deliberate continuation test (optional)

Only after the wiring is proven: create a note in the project and run again.

```powershell
python "$env:USERPROFILE\.codex\skills\adaptive-agent-workflow\scripts\adaptive_checkpoint.py" --init "probe" --next "say OK" --session manual --project "D:\path\to\your-project"
```

The Stop handler answers with `{"decision": "block", "reason": ...}` for the note's session and stays silent for any other. Then set `Status: done` in the note so the next run stops normally.

## 7. Roll back

```powershell
python scripts\install_workflow.py --project "D:\path\to\your-project" --host codex --codex-global --uninstall
```

Foreign hooks and unrelated keys survive; the package copy under `CODEX_HOME\skills` is removed. `hooks.json.aaw-backup` is left in place for manual comparison.

## 8. Then update the record

Copy the result into [host verification](host-verification.md): replace the UNVERIFIED row with the event list that fired, the Codex version and the platform. Keep the rows that did not fire as UNVERIFIED rather than assuming them.
