# Local owner-loop verification

Scope: subprocess-level execution of the new hook implementation and installer, on Linux/Python in the editing environment. These are executed checks, not a live Codex, Claude Code or Dot model session.

Observed:
- Incoming task context directs specialist preparation before producing the specialist result.
- The actual child prompt/message gains the execution brief and saved capability reference; other arguments are preserved; the Claude Code response adds no permission decision, while Codex returns `permissionDecision: allow` with `updatedInput` (see the host verification permission boundary).
- SubagentStop writes an unreviewed handoff and returns no continuation.
- Delegation/collection return sends integration/next-action guidance to the caller, not back to the child; running/ID-only results are not declared completed.
- A new session receives the saved next action from the existing progress file.
- Only active saved work causes one Stop continuation; absent/done/paused/blocked work and recursive Stop do not. From v0.7.0, a paused note can still be blocked by the anti-cheat gate; it never receives the continuation.
- The initializer preserves existing progress. An existing project note can be reused without creating a duplicate.
- Installer re-run is idempotent for settings, preserves other hooks/permissions, and installs all referenced Skill files.
- Commands taken from the generated Codex and Claude settings were executed from a nested directory in a project path containing spaces. Both loaded the correct saved progress.

Command: `python -m unittest discover -s tests -v`.
Result: 41 tests passed (Windows 11, Python 3.14; the same suite runs on ubuntu-latest and windows-latest in CI). These assertions establish the behaviors listed above, not professional output quality or autonomous method selection.

Executed locally for v0.7.0:
- A staged change and an untracked new file both count toward the large-diff gate; `git add` no longer hides work from the gates.
- A staged test weakening is caught by the anti-cheat gate; `Test-Change:` in the note releases it deliberately.
- Repeated Stops on the same `Status: done` task write exactly one trace record; a different session writes its own.
- Two concurrent builders: stopping one with no correlating signal records `unattributed` and does not supersede the sibling; `Touched-Files` attributes it deterministically.
- `src/api` and `src/apiv2` do not conflict; the same path in another worktree is allowed.
- `Mounted-Skills` records requested and applied separately; an arbitrary file path is not inlined.
- A worker left active by another session is marked `stale` and stops blocking dispatch.

Not established by these tests: whether a live host delivers these events with the fields the handler expects, whether the router selects useful Skills, and whether the gates improve real work.

Added in 0.5.0 and executed locally:
- `--dry-run` reports the planned settings, package and `.gitignore` changes and writes nothing; foreign hooks survive a real uninstall, and progress notes are left alone.
- `--codex-global` writes into `CODEX_HOME`, keeps a backup, preserves foreign hooks and unrelated keys, installs the command without `--project`, and restores the file on uninstall.
- A note owned by one session does not trigger a continuation in another session; the owning session still gets exactly one.
- A note longer than 6,000 characters reaches the model with an explicit truncation marker.
- Malformed hook input exits 0 with a message on stderr, so a broken event cannot block the host.
- Stored observations can be summarized and pruned; the skill tree no longer grows without a reader.

Windows / cp936 re-run (v0.6.1 revision): the suite was executed on Windows 11, Python 3.14, with the console default codec at cp936 and `PYTHONUTF8` unset. 21 tests passed at that revision. That required two handler fixes: stdout is reconfigured to UTF-8, and hook payloads are serialized as pure ASCII JSON, because a cp936 console emitted note text the parent process could not decode back.

Not executed here: native host event emission, native host event emission, model-driven Skill search/loading, MCP access and actual artifact improvement. No model credentials or third-party MCP servers were used.
