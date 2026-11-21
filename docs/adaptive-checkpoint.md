# Owner-loop execution support (v0.7.0)

The former Stop-only reminder has been replaced by a connected owner loop:

**Read current work → discover and route capability → equip the executor → produce a slice → return results to the owner → update and perform the next action.**

The implementation and [portable event contract](../skills/adaptive-agent-workflow/references/hook-events.md) are maintained inside the canonical Skill. [Install it into the actual work project](quickstart.md), not just the workflow repository.

SessionStart indexes locally installed Skills and CLI tools into `.aaw/runtime/capabilities.json`; UserPromptSubmit matches the prompt against that index and injects the top candidates with `READY` / `MISSING_TOOL` preflight. Both also bring in current work. PreToolUse on delegation appends a scoped execution brief, inlines the rules of up to two indexed `Mounted-Skills`, records the worker, and blocks overlapping builder `Owned-Paths` in the same worktree. SubagentStop saves a report without restarting the child. PostToolUse on delegation/collection returns actionable feedback to the caller. Stop requests one continuation only for active saved work; done, paused, blocked and absent work do not loop.

A newly spawned agent ID is not a finished artifact. The owner checks whether the returned work is ready, then opens and integrates/corrects the actual result. Updating progress and selecting the next action are owner responsibilities, not user chores.

The working note is maintained by the agent; hook observations and child reports are saved by code. No code path claims that a Skill was used, that an MCP worked, or that an output was accepted merely because an event occurred. An unresolved `Mounted-Skills` entry is reported as not mounted, and a worker the stop event cannot be matched to is recorded as `unattributed` rather than assigned by guess.

## Enforcement, and its limits

v0.7 adds two host-enforced Stop gates and one dispatch gate. They are guardrails for a cooperating operator, not a security boundary:

- **Dispatch block** (`PreToolUse`): denies a second builder whose `Owned-Paths` overlap an active builder in the same worktree. Paths are compared by component; worktrees are compared after resolution. Active workers from another session or older than `AAW_WORKER_TTL_HOURS` (default 12) are marked `stale` first, so a crashed child cannot block forever.
- **Anti-cheat** (`Stop`): the uncommitted work (staged, unstaged and untracked) is scanned for deleted assertions and added skip markers in test files. `Test-Change: <reason>` in the note releases it deliberately.
- **Large-diff verifier** (`Stop`): active work above 3 files or 100 changed lines without a completed, attributed blind verifier for the same diff hash gets a `[AAW VERIFIER GATE]`. `Verifier-Waiver: <reason>` releases it.

Stop decisions use `{"decision":"block","reason":...}` on both hosts. `hookSpecificOutput.additionalContext` on Stop exists only from Claude Code 2.1.163, so it is not the only path. Gates run only when a current-work note exists. A diff scan that fails is reported to the owner instead of being treated as a clean tree.

This is not a runtime: no model calls, no background scheduler, no database, no automatic installation. State is three JSON files and one append-only log under Git-ignored `.aaw/runtime/`. Existing host permissions remain in force. In Claude Code auto mode, changed delegation inputs can require the host to re-evaluate the call; this integration does not override that permission decision.

## Execution log

When the note reaches `Status: done`, Stop appends one `aaw-trace@1` record to `.aaw/runtime/eval-trace.jsonl`. The key is `session_id` plus diff hash, so repeated Stops on the same finished task do not duplicate it, and worker counts are scoped to the session.

This is a raw execution log, not an evaluation result. It says that a verifier ran, not that the work was good; it covers one task in one project, not a controlled comparison. Turning it into evidence requires an experiment record in `open-agent-evals` with a pack, version, conditions, runs and `replay_status`.

## Working from more than one session

A note may carry a `Session: <id>` line. When it does, only that session is asked to continue at Stop; another session in the same project leaves the note alone instead of duplicating the slice. Without the line the note stays shared, which is the intended behavior for one session per project.

Note text is read up to 6,000 characters. Anything beyond is cut with an explicit truncation marker rather than dropped silently, so the model can tell that it is not seeing everything.

## Observations

`--report` prints the newest records with a total size and `--prune N` keeps only the newest N. Nothing reads these files automatically: they are owner inputs, not evidence of quality, and they are Git-ignored.

Test report: [local execution verification](owner-loop-verification.md). Real Dot/Codex/Claude task-quality effects are not established by local protocol tests.
