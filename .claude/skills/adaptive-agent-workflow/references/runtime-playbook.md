# Owner execution loop

## Default behavior

The user gives the outcome. The owner supplies the short plan, suitable methods, actual executor/tool setup, first useful deliverable, integration and next action. The owner keeps working within the authorized scope rather than asking the user to manage each step.

For simple work, do it directly. For specialist work, inspect the relevant available Skills/tool inventory before producing the specialist result. Familiar, working capabilities are reused; external discovery is for an actual gap, not a ritual. Exploration and executable probes are valid work, not something blocked until a full plan is written.

## From capability to actual work

A capability assignment is concrete: “use `<path or pinned source>`, apply `<method relevant to this output>`, use `<available tools>`, produce `<artifact>`.” The executor reads the selected instructions in its own context and uses the method. If a needed MCP tool is unavailable, fix/replace that dependency within authorization or state the blocker. Do not merely rename an ordinary worker as a specialist.

Skill discovery can be delegated. The investigator returns a usable source, requirements and recommendation; the producer receives that capability and applies it. Do not stop at collecting Skill links. If no suitable Skill exists, use a documented professional method and say so, rather than inventing a Skill to fill a slot.

## Work in deliverable slices

Choose a slice that answers the next important question or produces something inspectable. The team and method may change between slices. Prepare only the next necessary work, not a complete future organization chart.

When a member returns, distinguish “started/running” from “delivered.” Open the result when available. Decide whether to integrate it, correct a specific gap, replace the method/capability, or collect more evidence. Then perform the next action, not just describe it. Shared edits still use isolation or a single writer; task changes supersede affected old work.

## One working note, maintained by the owner

Use an existing project note or `.aaw/current.md`. No per-agent dossiers or mandatory tables. Keep the current goal, short plan/current slice, capability references and actual owners, artifact locations, decisions, next action and blocker. Only the accountable owner edits this shared note; workers return handoffs.

The optional hook reads `Status: active` / `done` / `paused` / `blocked`. Without a status line, a nonempty existing note is considered active. Keep the note concise; hook context includes at most 6,000 characters, and the owner can read the full file when needed. Carry forward what is true, not the full chat.

Example, not a required form:

```text
Status: active
Goal: deliver a usable source-cited technical comparison.
Current slice: resolve the two disputed API behaviors before writing recommendations.
Method/capability: selected research Skill at <real path>; read by researcher A.
Tools: available web search and official documentation; no private connector needed.
Result: docs/evidence.md contains the checked cases; one case is still unresolved.
Next: owner opens those cases, resolves the missing evidence, writes the comparison.
```

## Worked sequence

User asks for a specialist report. The owner reads the relevant writing/research Skill and checks available source tools, writes a three-line plan, then assigns evidence gathering with the precise capability reference. The worker reads it and returns source-backed findings. The owner opens them, fixes unsupported claims, applies the writing method to produce the report, saves its path and next step in current work, and delivers it. A missing source triggers a focused search, not a new framework or a request for the user to supervise research.

The same loop works for code, design, research and other outcomes; domain acceptance comes from the task and chosen professional method. A user-requested design-only phase remains design-only. Internal method changes do not create extra approval ceremonies.

## Host connection

Startup/resume reads current work. Delegation receives execution instructions and current capability references. A child stop saves a report; it does not make the child repeatedly self-review. The parent receives result-oriented guidance when a delegation/collection tool returns. Only active saved work can request one Stop continuation. Completing/pausing/blocking the note stops continuation.

Hooks carry context and record observed events; they do not prove method quality, Skill use or MCP readiness. Actual execution and inspected artifacts do. There is no background worker in this package.
