# Hook Events & Runtime Contracts

The portable Python hook (`scripts/adaptive_checkpoint.py` + `scripts/capability_index.py`) connects real host lifecycle events to `.aaw/current.md` and `.aaw/runtime/` with zero network calls, zero LLM calls, and zero auto-installation.

## Supported Events

1. **`SessionStart` / `UserPromptSubmit`**
   - `SessionStart` refreshes `.aaw/runtime/capabilities.json` (read-only local Skill & CLI scan).
   - `UserPromptSubmit` runs deterministic Top-2 Skill routing and injects `[AAW capability router]` with `READY / MISSING_TOOL` preflight status alongside `OWNER_START` and `.aaw/current.md` (truncated at 6,000 chars with an explicit marker).
2. **`PreToolUse`** (matches `Agent`, `Task`, `spawn_agent`, including namespaced/flattened Codex forms)
   - Parses optional dispatch contract fields (`Role: scout|builder|verifier`, `Owned-Paths:`, `Mounted-Skills:`, `Worktree:`).
   - **Conflict block:** Blocks concurrent `builder` dispatches whose `Owned-Paths` overlap in the same worktree (`permissionDecision: deny` on Claude Code, `decision: block` on Codex). Overlap is compared by path components, so `src/api` and `src/apiv2` are distinct; worktrees are compared after resolution.
   - **Role-aware briefs:** Injects `SCOUT_BRIEF` for explicit `scout`, isolated `VERIFIER_BRIEF` (without builder prose) for explicit `verifier`, and `WORKER_BRIEF` for `builder`/default.
   - **Physical Skill inlining:** Inlines distilled rules for up to 2 `Mounted-Skills` entries that resolve to indexed Skills. Arbitrary paths are rejected and named in the brief.
   - Records active worker metadata in `.aaw/runtime/workers.json`, including `session_id`, `requested_skills` and applied `mounted_skills` separately. Workers left active by a previous session, or older than `AAW_WORKER_TTL_HOURS` (default 12), are marked `stale` before conflict checks.
3. **`SubagentStop`**
   - Saves truncated worker report (4,000 chars) + parsed structured envelope (`Status`, `Touched-Files`, `Skills-Applied`, `Interface-Status`, `Dead-Ends`) to `.aaw/runtime/handoffs/`.
   - **Attribution:** The host does not correlate a stop event with its dispatch. The handler matches by `agent_id` if known, else a single active worker, else the `Touched-Files` envelope. With several active workers and no signal, the worker is recorded as `unattributed` and the handler does **not** guess: no sibling supersede and no out-of-bounds attribution.
   - Checks staged, unstaged and untracked files against a builder's `Owned-Paths` and flags `out_of_bounds_files`.
   - If `Interface-Status: BROKEN` on an attributed worker, increments `interface_version` and marks active sibling workers `superseded`. Never restarts the child.
4. **`PostToolUse`** (matches dispatch and collection tools)
   - Returns control to the owner (`OWNER_RETURN`) and appends `[AAW SUPERSEDED WARNING]` if any sibling workers were invalidated by an interface change.
5. **`Stop`**
   - All Stop decisions use `{"decision":"block","reason":...}`. `hookSpecificOutput.additionalContext` on Stop exists only from Claude Code 2.1.163, so it is not relied on.
   - **Anti-cheat gate:** Inspects the uncommitted work (staged, unstaged and untracked) on test files; blocks if assertions were deleted or `@skip` / `xfail` / `.skip(` markers were added. A deliberate change is released by `Test-Change: <reason>` in the note.
   - **Large-diff verifier gate:** When `Status: active` and the work exceeds thresholds (`AAW_VERIFIER_MAX_FILES=3` or `AAW_VERIFIER_MAX_LINES=100`) without a completed attributed `verifier` for that diff hash, injects `[AAW VERIFIER GATE]`. `Verifier-Waiver: <reason>` releases it.
   - **Single continuation:** Continues once when `Status: active` and `stop_hook_active` is false (respecting `Session:` ownership). Gates run only when a current-work note exists.
   - **Execution log:** When `Status: done`, appends one `aaw-trace@1` JSONL record per task to `.aaw/runtime/eval-trace.jsonl`; repeated Stops with the same session and diff hash do not duplicate it.

## Local Persistence

- `.aaw/current.md` — Owner-maintained working note (`Status`, `Goal`, `Next`, `Dead-Ends`, optional `Session`).
- `.aaw/runtime/capabilities.json` — Read-only local Skill & CLI index.
- `.aaw/runtime/workers.json` — Worker roster (`active` / `completed` / `superseded` / `unattributed` / `stale`), `interface_version`, per-worker `attribution`, `requested_skills` and applied `mounted_skills`. Capped at 500 records.
- `.aaw/runtime/events/` & `.aaw/runtime/handoffs/` — Raw observations and structured worker handoffs.
- `.aaw/runtime/eval-trace.jsonl` — One `aaw-trace@1` execution log record per finished task.
- `.aaw/runtime/eval-trace-state.json` — Dedupe keys for the trace log (last 200).
