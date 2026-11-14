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
Result: 11 tests passed. These assertions establish the behaviors listed above, not professional output quality or autonomous method selection.

Not executed here: Windows process execution, native host event emission, model-driven Skill search/loading, MCP access and actual artifact improvement. No model credentials or third-party MCP servers were used.
