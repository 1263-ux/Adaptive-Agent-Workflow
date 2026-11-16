# Acceptance Scorecard

A delivery is a claim plus the evidence that supports it. The scorecard is the shortest form that lets someone else check the claim without replaying the session.

## Form

One row per acceptance item, taken from the task brief:

| Item | Status | Evidence | Executor |
|---|---|---|---|
| what was to be true | PASS / WARN / FAIL | command actually run with its exit code, artifact path, or measured result | who ran it |

## Rules

- Evidence is a command and its result, or an artifact another person can open. "Tests pass" is not evidence; "`pytest -q` -> exit 0, 11 passed" is.
- Quote the command that actually ran, in the environment where it ran.
- Do not score an item you did not check. Mark it WARN and say why - an empty cell reads as PASS.
- WARN is honest, not a failure: an acceptable limitation, an unrun path, or a dependency that needs a real credential.
- FAIL stays on the scorecard. Do not remove a failing row by narrowing the acceptance criterion after the fact.
- Independence is a name, not a session id. A second Agent that only reports is not independent verification; a different executor running the check on the artifact is.
- Counts are not outcomes: test count, file count, Agent count and completed stages prove nothing on their own.

## When it is short

Small direct work needs no table. State in one line what was run, what it returned and what stayed unchecked. The scorecard exists to stop a vague "done", not to add paperwork to a one-line fix.

## Example

Numbers below are from one real run of this package; keep the shape and replace the values.

| Item | Status | Evidence | Executor |
|---|---|---|---|
| Handler returns a payload for all six events | PASS | `python -m unittest discover -s tests` -> exit 0, 17 tests OK | owner |
| Skill mirrors match the canonical package | PASS | `python scripts/sync_skills.py --check` -> exit 0, "mirrors are in sync" | owner |
| Runs on a cp936 console | PASS | same suite on Windows 11 / Python 3.14 / cp936, 17 tests OK | owner |
| A real host emits the events | WARN | not verified in a live host session; see docs/host-verification.md | owner |
