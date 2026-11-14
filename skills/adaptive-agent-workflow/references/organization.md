# Dynamic Organization

## Principle
Organize around work and outputs, not permanent Agent titles. There is no required Root → Lead → Worker → Reviewer hierarchy. The current owner may execute directly, delegate or change the organization as evidence emerges.

## Respect project phases
A project may need separate preparation and production phases. If the user asks to establish the system first, organize only the preparation work: capability research, Skill discovery, team design, workflow, environment checks and acceptance planning. Do not silently start product implementation. Production roles may be proposed, but must be clearly distinguished from active participants.

## Delegate only for a reason
Delegate when an independent inspectable output exists and there is a real benefit: distinct expertise, parallel time savings, context isolation or independent evaluation. Do not delegate merely because a task is large or has many steps.

## Make capability ownership explicit when relevant
For multi-owner or specialist work, each active participant should have:
- Responsibility and concrete output.
- Skills/tools actually available or loaded.
- Any capability gap and discovery task.
- Whether downstream delegation is needed.
- Status and blocker.

Do not invent participants or report planned capabilities as mounted. If the host cannot isolate or load capabilities per child Agent, state the limitation and use the supported fallback.

## Minimal task brief
For ordinary work, pass only Goal, Output, Inputs, Constraints and Acceptance. Add dependencies, owner, write scope, baseline/version, budget and integration plan only when needed.

## Topologies
Direct, Sequential, Research-first, Probe-first, Parallel and Hybrid are all valid. Choose and change topology as the task evolves.

## Handoff
Preserve goal/current state, verified findings, decisions, completed artifact locations, blockers/risks, and next action/acceptance. Do not copy entire chat histories unless needed.

## Shared state and dependency cycles
Before concurrent writes, use host-enforced isolation, separate worktrees/sandboxes, a single-writer policy or explicit file ownership. Prompt-only boundaries are not enforcement.

When tasks form a dependency cycle, the accountable owner should break the cycle deliberately: clarify the true dependency, introduce a minimal interface/stub or provisional artifact, or rescope/reorder the tasks. Do not let agents wait on one another indefinitely. A stub is a temporary coordination device, not a requirement for ordinary tasks.

## Requirement changes and stale results
When a requirement or task baseline changes, the owner should mark affected work as superseded and communicate the new target. Late results from superseded work must not overwrite newer artifacts. Use host-enforced branch/worktree/version checks where available; otherwise require the owner to inspect and explicitly integrate late results. Do not impose version bookkeeping on simple sequential work.

## Restructure and review
Split, merge, reassign, pause, resume or stop tasks as needed. Preserve useful completed work and mark superseded outputs. If nested delegation is unsupported, use flat dispatch. Review effort matches risk; independent review should inspect actual artifacts. A different session ID alone does not prove independence.
