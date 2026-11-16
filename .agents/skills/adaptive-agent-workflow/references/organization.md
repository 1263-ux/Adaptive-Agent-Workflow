# Dynamic Organization

## Principle
Organize around work and outputs, not permanent Agent titles. There is no required Root → Lead → Worker → Reviewer hierarchy. The current owner may execute directly, delegate or change the organization as evidence emerges.

## Respect project phases
A project may need separate preparation and production phases. If the user asks to establish the system first, organize only the preparation work: capability research, Skill discovery, team design, workflow, environment checks and acceptance planning. Do not silently start product implementation. Production roles may be proposed, but must be clearly distinguished from active participants.

## Delegate only for a reason
Delegate when an independent inspectable output exists and there is a real benefit: distinct expertise, parallel time savings, context isolation or independent evaluation. Do not delegate merely because a task is large or has many steps.

Judge net benefit, not size. Delegation is a poor trade when the whole change stays inside the owner context, when several short edits would sit behind a coordination round-trip, or when each child would need the same reading pass the owner already did. Splitting three related files across three children is the canonical failure: three partial views, one integration cost, no parallel gain. Keep the work and do it.

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

| Situation | Default | Why |
|---|---|---|
| Goal clear, a handful of files, low risk | Direct | Coordination cost exceeds any parallel gain |
| Unknowns decide the design | Research-first or Probe-first | One inspected answer replaces several guesses |
| Independent modules sharing a boundary | Parallel with a frozen interface | Parallelism pays only when the contract holds still |
| Shared context, one artifact built in steps | Sequential | Handoffs would re-read the same context |
| High impact, expensive to reverse | Builder plus independent verifier | The producer own claim is the weakest evidence |

Selection is provisional: move to a stronger topology when evidence shows the current one failing, and back to Direct when it is not needed.

## Freeze the shared interface before parallel writes
Before dispatching parallel work that touches a shared boundary, the owner defines the part others depend on - type definitions, API signatures, schema, file layout, naming - and passes it in every brief. Children fill their own scope but do not redefine the boundary. When the boundary must change, the owner changes it once, tells every active child and reconciles the results. A contract that lives only in the owner head is not a contract.

## Reuse a warm collaborator
A collaborator holds context the owner does not. When follow-up work belongs to the same module - a failing test, a review correction, an extension of the same artifact - return it to the collaborator that produced it. Start a new one when the responsibility actually changes: a different module, an independent verifier, or isolation from a context that has gone wrong. If the host cannot resume a collaborator, carry its paths, decisions and constraints into the new brief and say that a fresh context is in use.

## Handoff
Preserve goal/current state, verified findings, decisions, completed artifact locations, blockers/risks, and next action/acceptance. Do not copy entire chat histories unless needed.

## Shared state and dependency cycles
Before concurrent writes, use host-enforced isolation, separate worktrees/sandboxes, a single-writer policy or explicit file ownership. Prompt-only boundaries are not enforcement.

When tasks form a dependency cycle, the accountable owner should break the cycle deliberately: clarify the true dependency, introduce a minimal interface/stub or provisional artifact, or rescope/reorder the tasks. Do not let agents wait on one another indefinitely. A stub is a temporary coordination device, not a requirement for ordinary tasks.

## Requirement changes and stale results
When a requirement or task baseline changes, the owner should mark affected work as superseded and communicate the new target. Late results from superseded work must not overwrite newer artifacts. Use host-enforced branch/worktree/version checks where available; otherwise require the owner to inspect and explicitly integrate late results. Do not impose version bookkeeping on simple sequential work.

## Restructure and review
Split, merge, reassign, pause, resume or stop tasks as needed. Preserve useful completed work and mark superseded outputs. If nested delegation is unsupported, use flat dispatch. Review effort matches risk; independent review should inspect actual artifacts. A different session ID alone does not prove independence.
