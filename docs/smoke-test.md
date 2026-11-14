# Real-host owner-loop check

Use the installed project package in the actual host. Record host/version and inspect real artifacts rather than marking a prompt checklist complete.

1. Give one bounded specialist task. The owner reads project context, chooses a suitable available Skill/method and tools, makes a short plan and starts work in that turn.
2. Delegate one independent output. Inspect the actual child prompt: it should carry the output, selected capability reference and scoped execution instructions.
3. Let the child finish. Its result should be saved under `.aaw/runtime/handoffs/`. The child should not be restarted just to self-review.
4. Collect the result in the parent. The owner should open the artifact, integrate or correct it, update current work and perform the next useful action. A returned agent ID or running status is not a delivered artifact.
5. Resume a new session. It should receive the existing current-work note and inspect the saved artifacts instead of asking the user to reconstruct progress.
6. Mark the task done, paused or blocked in the working note. Stop should not request another continuation. A simple direct task without a note should not be forced through this loop.

Also check an explicit design-only request, a missing MCP tool and a requirement change. The owner should adapt within the user's scope, not claim missing capabilities or ask for approval at every internal step.

Local protocol/installer checks are in [owner-loop-verification.md](owner-loop-verification.md). This document is a live-host procedure, not a claim that those host runs have already happened.
