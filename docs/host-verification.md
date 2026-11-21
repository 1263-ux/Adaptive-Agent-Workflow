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
| Stop gates via `{"decision":"block","reason":...}` | documented | documented | no |
| `additionalContext` on Stop | documented from 2.1.163; unsupported earlier (docs still inconsistent) | not used by this package | no |
| Windows command form | documented | `commandWindows` is not in the documented schema - UNVERIFIED | no |

v0.7.0 uses `decision:block` for every Stop gate precisely because `additionalContext` on Stop is version-dependent. The gates are still UNVERIFIED here in the sense that no live session has been observed returning them.

## Two failures that look exactly like silence

1. **Codex hooks are opt-in.** The handlers only fire with `features.codex_hooks=true` (`codex -c features.codex_hooks=true`); without it nothing runs and nothing errors.
2. **Unknown keys are ignored, not rejected.** `commandWindows` and `statusMessage` are not in the documented Codex schema. A config carrying them can look installed while the Windows branch never executes.

## Turning UNVERIFIED into evidence

- Run one bounded real task in the host, then read `adaptive_checkpoint.py --report`. An absent record does not by itself establish why a hook did not run: check the installed handler version, matching, trust, execution errors, and the host event separately.
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

## Real Codex delegation: 2026-11-16

On Windows with `codex-cli 0.162.1`, a `codex exec --skip-git-repo-check -c features.multi_agent=true` session (`01a1e4fc-5f3f-78b2-95d7-762e8bc65916`) invoked `collaboration.spawn_agent`; the child returned `PROBE_CHILD` and reported no extra instructions in its task prompt. The AAW report held SessionStart and UserPromptSubmit for that run but no PreToolUse record, and the terminal showed no PreToolUse hook line. A separate delegation in the desktop session likewise reported no injected text and produced no AAW PreToolUse record. The prompt rewrite therefore stays **UNVERIFIED** here: these observations do not isolate hook matching, hook invocation, or host support for `updatedInput`. The call was namespaced `collaboration.spawn_agent` while the configured matcher was `^(Agent|Task|spawn_agent)$`; the string the host matches on was not captured, so a mismatch was a hypothesis, not an established cause.

### The matching fix, and the two variables it separates

The shipped matcher was an anchored alternation, which cannot match a namespaced name. It is now `(?:^|\.)(?:Agent|Task|spawn_agent)$` for `PreToolUse`, and the matching form with the collection tools for `PostToolUse`, in the installer and in both checked-in host configs. This is a strict superset: every name that matched before still matches.

The fix also replaces argument with observation. If a delegation now writes a `PreToolUse` record, its `tool_name` field holds the exact string the host matches on. A missing record alone does not distinguish host event emission from trust, matching, handler errors or an older handler that did not record this event.

Two variables stay separate and should be reported separately:

1. **Does the hook fire** for a namespaced dispatch tool? (matcher and event emission)
2. **Does the host honour `hookSpecificOutput.updatedInput`?** Documented for Claude Code, unverified for Codex. A hook that fires proves only the first.

Until a `PreToolUse` record exists and a child reports the injected brief, the prompt-rewrite mechanism remains UNVERIFIED on Codex however correct the matcher looks.

## Codex delegation follow-up

On Windows with Codex 0.162.1 and the widened matcher, a real delegation displayed `hook: PreToolUse Failed`; `PostToolUse` recorded `spawn_agent`. The earlier handler did not record PreToolUse at all, so an absent record was not evidence of absent host emission. The handler now records matching PreToolUse events before producing its response. A record establishes invocation, not that Codex accepted `updatedInput` or that a child received the brief. The failure cause and prompt rewrite remain unverified.

## Codex PreToolUse protocol follow-up

Codex `rust-v0.162.1` validates `updatedInput` only when accompanied by `permissionDecision: allow`; without it, its parser reports `PreToolUse hook returned updatedInput without permissionDecision:allow`. Its hook runtime passes rewritten input to tool dispatch; the effect on real approval and sandbox paths has not been independently tested. The Codex response now uses this required combination; Claude's response remains unchanged. This fixes the response format, not a demonstrated end-to-end delegation rewrite. A separately trusted logging wrapper was not invoked for a real `collaboration.spawn_agent` call on this host, so neither its payload nor a rewritten prompt was observed. The upstream [spawn_agent PreToolUse issue](https://github.com/openai/codex/issues/49736) reports a similar host limitation. Continue to treat delivery of the brief through this event as unverified.

## Codex rewrite permission boundary

For matching dispatch calls, the Codex handler now returns `hookSpecificOutput.permissionDecision: "allow"` together with `updatedInput`. This field is emitted only for Codex; the Claude Code response does not include a permission decision. The [Codex 0.162.1 output parser](https://github.com/openai/codex/blob/rust-v0.162.1/codex-rs/hooks/src/engine/output_parser.rs) rejects `updatedInput` without `allow`. The [0.162.1 hook runtime](https://github.com/openai/codex/blob/rust-v0.162.1/codex-rs/core/src/hook_runtime.rs) returns the rewritten input to [tool dispatch](https://github.com/openai/codex/blob/rust-v0.162.1/codex-rs/core/src/tools/registry.rs), which then calls the tool. This source inspection is version-specific, not a live proof that every approval and sandbox path remains unchanged; the field is a permission decision and its security effect in actual sessions and other versions remains unverified. In particular, a real approval-required delegation and end-to-end rewrite have not been demonstrated. Review this behavior before relying on it as a permission boundary.

## Codex flattened tool names and opaque input

On Windows with `codex-cli 0.162.1`, a trusted catch-all PreToolUse logging probe captured one real shell call and one real multi-agent delegation in the same session. Their `tool_name` values were `Bash` and `collaborationspawn_agent`; a subsequent wait was `collaborationwait_agent`. The earlier matcher and handler accepted dotted names but missed these flattened names. The spawn event's `tool_input.message` began with `gAAAAA` and was an opaque token rather than the child task text. The handler now records these flattened events and leaves such Codex messages unchanged, because appending plaintext could corrupt the token. A record proves handler invocation, not successful prompt rewriting. The plain-message rewrite is locally tested; real delivery of a brief into an opaque child task remains unverified.

With the updated installer and handler installed and trusted, a second real Codex 0.162.1 session (`01a1e99c-5173-7981-8817-1acb427e48bb`) emitted `PreToolUse Completed` and recorded `PreToolUse` and `PostToolUse` with `tool_name: collaborationspawn_agent`. This verifies the event matching and recording on that host, not delivery of an injected brief.
