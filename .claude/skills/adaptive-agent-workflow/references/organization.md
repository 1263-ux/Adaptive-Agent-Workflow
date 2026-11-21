# Dynamic Organization & Collaboration Contracts

Organize around inspectable outputs and net ROI—never permanent org charts (`Root -> Lead -> Worker -> Reviewer`).

## Single-Agent Default vs. Multi-Agent ROI

A single owner riding a warm prompt cache is faster and cheaper for ~80% of tasks. Do **not** split work just because a task is large; splitting pays cold-start reading cost, breaks KV-cache locality, and imposes a manager tax on the owner.

Delegate **only** in three positive-ROI modes:

1. **Scout (`Role: scout`) — Context Firewall:** Read-only exploration across noisy logs, large unfamiliar directories, or broad web research. Protects the owner's context window by returning a distilled `<500`-word brief (`file paths`, `verified facts`, `Dead-Ends`, `open risks`).
2. **Worktree Builder (`Role: builder`) — Orthogonal Parallelism:** Independent modules with a **frozen interface** and **disjoint `Owned-Paths`**. When running 2+ builders concurrently, isolate each builder in its own `git worktree` (`Worktree: <path>`) so test runners, build caches, and `.git/index.lock` do not contend.
3. **Blind Verifier (`Role: verifier`) — Cognitive De-biasing:** Read-only adversarial check on high-impact or large diffs (default threshold: `>3` files or `>100` changed lines). The verifier sees **only** acceptance criteria, frozen interfaces, actual diffs/artifacts, and command exit codes—never the builder's rationalization.

## 4-Field Dispatch Contract

Include these lightweight fields in every subagent dispatch prompt so `PreToolUse` can enforce boundaries and inline mounted Skills:

```text
Role: scout | builder | verifier
Owned-Paths: src/api/, tests/api/
Mounted-Skills: refactor-gate
Worktree: ../wt-api   # required when 2+ builders run concurrently
Acceptance: pytest tests/api -q (exit 0), no weakened assertions
```

- **Overlap blocking:** `PreToolUse` registers active workers in `.aaw/runtime/workers.json` and blocks concurrent `builder` dispatches whose `Owned-Paths` overlap in the same worktree. Paths are compared by component (`src/api` and `src/apiv2` do not conflict). Active workers left by a previous session or older than `AAW_WORKER_TTL_HOURS` are marked `stale` and stop blocking.
- **Attribution is not identity:** the host does not tell a `SubagentStop` which dispatch it belongs to. The handler uses `agent_id` when known, then a single active worker, then `Touched-Files`. With concurrent workers and no signal it records `unattributed` and withholds supersede and out-of-bounds judgments rather than blaming the wrong worker.
- **Warm collaborator reuse:** Reuse a warm collaborator already holding a module (`workers.json`) for follow-up fixes instead of cold-starting a duplicate worker.
- **Offload evaluation to scripts:** Let deterministic tests, linters, and `git diff` gates do 80% of verification so the owner remains a player-coach, not a pure PM.

## Interface Breakage, Superseding & Dead-Ends

- **Structured handoff envelope:** Workers return compact fields when applicable (`Status:`, `Touched-Files:`, `Skills-Applied:`, `Interface-Status: OK|BROKEN`, `Dead-Ends:`).
- **Superseding stale siblings:** If a builder reports `Interface-Status: BROKEN`, `SubagentStop` increments `interface_version` in `.aaw/runtime/workers.json` and marks active sibling workers `superseded`. `PostToolUse` warns the owner to discard stale outputs before integrating.
- **Negative memory (`Dead-Ends`):** Record disproved approaches in `.aaw/current.md` under `Dead-Ends:` so neither warm retries nor fresh sessions repeat failed paths.
