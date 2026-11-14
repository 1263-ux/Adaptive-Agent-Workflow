# Runtime Smoke Test

Use these scenarios after installing the project Skill in a supported host. Record host/version and whether behavior was native, manual fallback or unsupported.

## 1. Direct task stays direct
Prompt: "Fix this small, local typo/bug in the current project."
Expected:
- Agent understands the requested outcome.
- No unnecessary research, team creation or long planning artifact.
- It makes the change and performs proportionate verification.
- It reports the result and any limitation.

## 2. Explicit capability exploration
Prompt: "Before choosing an approach, explore mature Skills or specialist methods for this unfamiliar task and recommend what to use."
Expected:
- Agent identifies a concrete capability gap.
- Searches available sources using host-supported tools.
- Inspects candidate source, method, dependencies, license and safety.
- Explains the selection briefly.
- Does not claim installation/mounting unless it happened.

## 3. Dynamic organization
Prompt: "Implement these two independent deliverables in parallel, then integrate them."
Expected:
- Agent confirms independent outputs and integration boundaries.
- Uses host-supported delegation only when available.
- Establishes workspace/write isolation or a single-writer plan.
- Integrates and verifies actual artifacts.
- Does not create a fixed role hierarchy.

## 4. Method failure adaptation
Prompt: "The current approach is not meeting the quality target. Diagnose the cause and change the smallest thing likely to improve the outcome."
Expected:
- Agent identifies the failure category before retrying.
- Considers missing capability, wrong method, execution issue, unclear goal, environment and organization.
- Changes method/team/scope/context only as justified.
- Checks whether the change improved the result.

## 5. Handoff and continuation
Prompt: "Hand this task to another agent/member and have them continue."
Expected:
- Handoff includes goal, current state, verified findings, artifact paths, blockers and next action.
- Receiving member can inspect source artifacts.
- No claim of isolated permissions unless host enforces them.

## 6. Outcome-based delivery
Prompt: "Deliver the requested result and tell me what is actually complete."
Expected:
- Acceptance is based on the user goal and task-specific criteria.
- Evidence is proportionate to important claims.
- Incomplete items and limitations are disclosed.
- Test count, agent count and process completion are not used as success proxies.

## Pass criteria

The Skill is useful if:
- Simple tasks do not gain noticeable process overhead.
- Capability discovery happens when it materially helps.
- Team creation is justified by independent outputs or other clear benefits.
- The Agent adapts after failure rather than blindly repeating.
- Delivery quality and clarity improve without misleading capability claims.

A checklist pass is not proof of production effectiveness. Compare actual task outcomes, time, cost and human corrections against a baseline.
