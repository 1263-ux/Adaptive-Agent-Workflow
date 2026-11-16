# Host verification

What a host **documents** is not what this package has **observed**. Keep the two apart; the package only relies on the first column until someone fills the second.

## Sources checked

- Claude Code hooks reference: <https://code.claude.com/docs/en/hooks> (events, `settings.json` schema, stdin JSON, `hookSpecificOutput`, exit codes).
- Codex hooks: <https://learn.chatgpt.com/docs/hooks>, `openai/codex` PR #9691 and `codex-rs/hooks`. Configured in `.codex/hooks.json` or `[hooks]` in `config.toml`.

## Status vocabulary

`NATIVE` / `EMULATED` / `UNSUPPORTED` / `UNVERIFIED`, from [the probe checklist](../adapters/host-capability-probe.md).

## Matrix

| What the package relies on | Claude Code | Codex | Observed here |
|---|---|---|---|
| SessionStart / resume context | documented | documented; `matcher` filters `source` (`startup`, `resume`, `clear`, `compact`, `fork`) | no |
| UserPromptSubmit | documented | documented | no |
| PreToolUse rewrites the child prompt (`updatedInput`) | documented | `PreToolUse` documented; whether the input can be rewritten is UNVERIFIED | no |
| PostToolUse returns work to the owner | documented | documented | no |
| SubagentStop saves a handoff | documented | documented | no |
| Stop continuation and its recursion guard | documented (`stop_hook_active`) | `Stop` documented; a `stop_hook_active` field is UNVERIFIED | no |
| Windows command form | documented | `commandWindows` is not in the documented schema - UNVERIFIED | no |

## Two failures that look exactly like silence

1. **Codex hooks are opt-in.** The handlers only fire with `features.codex_hooks=true` (`codex -c features.codex_hooks=true`); without it nothing runs and nothing errors.
2. **Unknown keys are ignored, not rejected.** `commandWindows` and `statusMessage` are not in the documented Codex schema. A config carrying them can look installed while the Windows branch never executes.

## Turning UNVERIFIED into evidence

- Run one bounded real task in the host, then read `adaptive_checkpoint.py --report`. If the six events are absent from `.aaw/runtime/events/`, the wiring is not firing - that is a host/config finding, not a model behaviour finding.
- Record host, version, platform and a short `--report` excerpt in the matrix above.
- Keep one row per capability. A green row for delegation does not make mounting, isolation or method quality green.

## What a passing verification is not

One successful delegation proves the event fired and the payload parsed. It does not prove that capability mounting works, that a child context is isolated, or that the delivered artifact is better. Those need the task-level comparison, not a hook log.


## Evidence collected on this machine

Host: Windows 11, `codex-cli 0.162.1`, `claude 2.1.220`. One Codex session completed and returned its answer after reconnects; later runs were blocked by the endpoint. Hook evidence below does not depend on model completion.

| Observation | Result | How it was produced |
|---|---|---|
| Codex fires SessionStart hooks from `$CODEX_HOME/hooks.json` | **NATIVE** | Ran `codex exec` in a project whose global `~/.codex/hooks.json` holds an unrelated hook. Codex logged `hook: SessionStart` / `hook: SessionStart Completed`. |
| Codex loads a project-level `.codex/hooks.json` | **NOT LOADED** | Same project, `CODEX_HOME` pointed at an isolated directory holding only `auth.json` and a `config.toml` with `[features] hooks = true`. Codex logged no hook line and this package's handler wrote nothing. |
| This package's Windows hook command works | **NATIVE** | Fed a real `SessionStart` payload into the encoded command from the installed `hooks.json`; the handler returned a correct `hookSpecificOutput.additionalContext`. |
| `UserPromptSubmit` | **NATIVE** | Two real sessions wrote records carrying host session ids (01a1e4ea-..., 01a1e4e7-...), not the manual probe id. |
| `SessionStart` | **NATIVE** | After restoring the original handler, a real Codex session recorded SessionStart with session id `01a1e4f1-404c-7662-8f50-c0d6e3dcfa3f`; see the confirmation below. |
| `PreToolUse`, `PostToolUse`, `SubagentStop`, `Stop` | UNVERIFIED | No delegation or tool loop was exercised. |
| Claude Code hooks | UNVERIFIED | Not exercised yet. |

## What the third row implies for installation

The package currently installs Codex hooks into `<project>/.codex/hooks.json`. On the host above that file was ignored, so the Codex half of the integration is inert as shipped: the handlers are correct, the location is not. The working location is `$CODEX_HOME/hooks.json`, which is shared with every other project and may already contain unrelated hooks.

Two consequences follow, and the second is why this is not simply a one-line change:

1. Project-scoped install cannot work for Codex as documented; the hook must be merged into the global file.
2. A global merge touches configuration outside the project, so it needs an explicit opt-in, a backup, and an uninstall that restores the previous file - the same treatment the Claude Code settings already receive.

Until that exists, treat the Codex integration as UNVERIFIED in practice even though its commands are proven correct.
## Update: the global Codex location

The installer now supports `--codex-global`: it writes `hooks.json` and the Skill package into `CODEX_HOME`, omits `--project` from the command so the handler resolves the project from the event, keeps a backup of the previous file, preserves every foreign hook and unrelated key, and `--uninstall --codex-global` restores the file and removes the package.

Live firing from that location is observed for both `UserPromptSubmit` and `SessionStart` (see the records below). The earlier `hook: SessionStart` lines could not be attributed to this package because an unrelated global hook fires on the same event.

## Alternatives worth evaluating

Claude Code ships a plugin mechanism that installs hooks together with skills and agents in one command. If it fits the target hosts, it replaces hand-merging `settings.json` - and removes most of the uninstall problem this repository solves by hand.

## Codex global probe: 2026-11-16

Windows, `codex-cli 0.162.1`, `[features] hooks = true`; test project was `C:\Users\chenfeng\AppData\Local\Temp\aaw-codex-verification`. The original AAW SessionStart handler remained unverified: earlier `codex exec` runs printed `hook: SessionStart`, but the only SessionStart record below was generated by an explicit manual invocation (`session_id: manual`). An unrelated herdr SessionStart hook was also configured, so that terminal line alone cannot attribute execution to AAW.

With the AAW SessionStart command temporarily replaced by a logging probe, the first `codex exec` printed one SessionStart pair but created no probe log. The interactive hook review showed SessionStart: 2 installed, 1 active, 1 needing review; the probe was marked modified and required trust. After explicitly trusting that probe, a new `codex exec` printed two SessionStart pairs and the probe recorded 385 bytes of stdin. Its JSON contained `session_id`, `transcript_path`, `cwd`, `hook_event_name: SessionStart`, `model`, `permission_mode`, and `source: startup`. This establishes the probe received a host payload after trust; it does not establish that the restored AAW SessionStart command is trusted or has run. The probe was removed and the original hooks file restored immediately after capture.

The installed AAW `UserPromptSubmit` handler did record two real host events during these runs; other event behavior remains unverified. The raw report after the probe run was:

```text
AAW observations under C:\Users\chenfeng\AppData\Local\Temp\aaw-codex-verification\.aaw\runtime
3 records, 770 bytes
  2026-11-16T15:12:28.453180+00:00 UserPromptSubmit host event observed; outcome not assessed
  2026-11-16T15:09:27.923011+00:00 UserPromptSubmit host event observed; outcome not assessed
  2026-11-16T14:58:18.783734+00:00 SessionStart host event observed; outcome not assessed
```

The first earlier model request ultimately returned `HOOKPROBE` after reconnects; the hook evidence does not depend on model completion. The second probe command changes the trusted command, so restoring the original does not itself prove its trust state.

### What the trust gate teaches

1. **`hook: <Event>` is an event-level signal, never a handler-level one.** Some handler for the event ran; nothing says which. Only this package's own records, or a probe that logs, settle attribution.
2. **Trust is tracked per handler slot**, as `[hooks.state.'<file>:<event>:<group>:<handler>']` in `config.toml`. After approval this host carries seven entries, including both `session_start:0:0` (the unrelated hook) and `session_start:1:0` (this package). Adding a second handler to an event therefore creates a new slot that needs its own approval, and `codex exec` cannot give it.
3. **A hook can be installed correctly and still never run.** The installer writes a valid file; only the interactive UI can approve it. That is why the installer now warns instead of reporting success.
4. **A logging probe separates three states that look identical from outside**: not invoked, invoked with no payload, invoked with a payload. Here it reported 385 bytes, whose shape (`session_id`, `cwd`, `hook_event_name`, `source`) is exactly what the handler reads.

## Restored SessionStart confirmation: 2026-11-16

With the original AAW command restored, `codex exec --skip-git-repo-check` on Windows with `codex-cli 0.162.1` created a `SessionStart` record at `2026-11-16T15:20:00.469095+00:00`, with session ID `01a1e4f1-404c-7662-8f50-c0d6e3dcfa3f`, matching the real host session. It also recorded `UserPromptSubmit` for that session. This verifies these two events for this configuration; it does not establish later event behavior or task quality.

```text
AAW observations under C:\Users\chenfeng\AppData\Local\Temp\aaw-codex-verification\.aaw\runtime
5 records, 1302 bytes
  2026-11-16T15:20:02.207471+00:00 UserPromptSubmit host event observed; outcome not assessed
  2026-11-16T15:20:00.469095+00:00 SessionStart host event observed; outcome not assessed
  2026-11-16T15:12:28.453180+00:00 UserPromptSubmit host event observed; outcome not assessed
  2026-11-16T15:09:27.923011+00:00 UserPromptSubmit host event observed; outcome not assessed
  2026-11-16T14:58:18.783734+00:00 SessionStart host event observed; outcome not assessed
```
