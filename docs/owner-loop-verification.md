# Local owner-loop verification

Scope: subprocess-level execution of the new hook implementation and installer, on Linux/Python in the editing environment. These are executed checks, not a live Codex, Claude Code or Dot model session.

Observed:
- Incoming task context directs specialist preparation before producing the specialist result.
- The actual child prompt/message gains the execution brief and saved capability reference; other arguments are preserved and no permission decision is added.
- SubagentStop writes an unreviewed handoff and returns no continuation.
- Delegation/collection return sends integration/next-action guidance to the caller, not back to the child; running/ID-only results are not declared completed.
- A new session receives the saved next action from the existing progress file.
- Only active saved work causes one Stop continuation; absent/done/paused/blocked work and recursive Stop do not.
- The initializer preserves existing progress. An existing project note can be reused without creating a duplicate.
- Installer re-run is idempotent for settings, preserves other hooks/permissions, and installs all referenced Skill files.
- Commands taken from the generated Codex and Claude settings were executed from a nested directory in a project path containing spaces. Both loaded the correct saved progress.

Command: `python -m unittest discover -s tests -v`.
Result: 21 tests passed. These assertions establish the behaviors listed above, not professional output quality or autonomous method selection.

Added in 0.5.0 and executed locally:
- `--dry-run` reports the planned settings, package and `.gitignore` changes and writes nothing; foreign hooks survive a real uninstall, and progress notes are left alone.
- `--codex-global` writes into `CODEX_HOME`, keeps a backup, preserves foreign hooks and unrelated keys, installs the command without `--project`, and restores the file on uninstall.
- A note owned by one session does not trigger a continuation in another session; the owning session still gets exactly one.
- A note longer than 6,000 characters reaches the model with an explicit truncation marker.
- Malformed hook input exits 0 with a message on stderr, so a broken event cannot block the host.
- Stored observations can be summarized and pruned; the skill tree no longer grows without a reader.

Windows / cp936 re-run (this revision): the suite was executed on Windows 11, Python 3.14, with the console default codec at cp936 and `PYTHONUTF8` unset. 21 tests passed. That required two handler fixes: stdout is reconfigured to UTF-8, and hook payloads are serialized as pure ASCII JSON, because a cp936 console emitted note text the parent process could not decode back.

Not executed here: native host event emission, native host event emission, model-driven Skill search/loading, MCP access and actual artifact improvement. No model credentials or third-party MCP servers were used.
