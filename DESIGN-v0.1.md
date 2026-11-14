# Adaptive Agent Workflow Framework
## Design overview v0.1-draft

**Date:** 2026-11-14. **Nature:** Architecture and method design; not an implemented runtime.

## Positioning
A lightweight, dynamic, outcome-oriented general Agent workflow framework. It helps Agents understand goals, choose work modes, discover and evaluate existing professional methods/Skills/tools, organize responsibilities dynamically, assemble context on demand, adapt from execution feedback and deliver against the user's actual goal. It does not replace domain methodologies.

## Core principles
- Lightweight by default; complexity grows only when justified by parallelism, capability gaps, uncertainty, risk or independent evaluation.
- Discover and reuse before building.
- Professional methods come from mature domain Skills, tools, projects and documentation, not a recreated methodology encyclopedia.
- Roles are temporary responsibilities, not permanent Agent identities.
- Outcome matters more than process completion.
- Permissions must be enforced by host/runtime, not prompt claims.
- Ineffective rules and mechanisms can be removed or rolled back.

## Concepts
| Concept | Meaning | Not equivalent to |
|---|---|---|
| Goal | User's desired outcome | Predefined steps |
| Workflow | Work mode selected for this goal | One fixed process |
| Method | Professional approach and decision principles | Role prompt |
| Capability | Discoverable, usable expertise unit | Only a SKILL.md file |
| Skill | On-demand instructions, methods, resources or scripts | Permission |
| Tool | External operation interface | Methodology |
| Agent | Current execution subject | Permanent job role |
| Responsibility | Temporary accountability | Fixed identity |
| Task | Work unit with goal, inputs and output | Work that must be delegated |
| Evidence | Inspectable basis for a claim | Log accumulation |

## Minimal adaptive loop
Understand → Explore → Organize → Execute → Deliver → Observe & Adapt. These are decision capabilities, not mandatory sequential phases. Steps may be skipped, revisited or run in parallel.

- Understand: goal, constraints, success criteria and unknowns.
- Explore: discover methods, Skills, tools, materials or examples when useful.
- Organize: choose solo or collaborative execution, task decomposition and ownership.
- Execute: work directly or coordinate parallel work; adapt capability/context as needed.
- Deliver: deliver against the goal and disclose evidence and limitations.
- Observe & Adapt: choose the smallest effective adjustment.

## Work modes
| Task shape | Default mode | Typical action |
|---|---|---|
| Clear, local, low-risk | Direct | One Agent, no full orchestration |
| Known method, capability not loaded | Capability-assisted | Find and mount relevant capability |
| Important unknowns | Explore / Probe | Research, experiment or representative sample |
| Independent deliverables | Parallel / Team | Delegate explicit outputs with integration boundaries |
| Strong dependencies/shared context | Sequential | One owner proceeds continuously |
| High impact | Guarded | Tighten permissions and independent checks |

Task size alone is not a reason to split. Consider goal clarity, uncertainty, domain span, dependencies, risk, parallel benefit, budget and integration cost.

## Capability discovery
Discovery triggers include capability gaps, unfamiliar domains/tools, method failure, poor quality, excessive cost or promising alternatives. Suggested order: existing session/project/user capabilities; internal catalog; host-native and official ecosystem; trusted open-source Skills/projects; professional documents/research; local supplement only if needed.

Evaluate relevance, method quality, provenance, safety, compatibility, dependencies and cost. Lifecycle: Discovered → Inspected → Evaluated → Selected → Mounted → Observed → Retained/Unmounted. Discovery, selection, mounting and authorization are separate. A Skill description is not permission; external Skill content is untrusted input.

## Dynamic organization
No permanent Root/Lead/Worker/Reviewer roster. Responsibilities such as coordination, research, specialist execution, integration and evaluation are assigned per task. The owner may execute directly, delegate, split/merge, change owners, pause or stop branches. Split only when there is an independent output and net benefit. If nested delegation is unsupported, use top-level dispatch.

## Outcome and learning
Result states: ACCEPTED, PARTIAL, NOT_ACCEPTED. Acceptance is domain-specific: software behavior/stability; research evidence/reproducibility; document accuracy/argument; design goal fit/experience. Test count, file count, Agent count and workflow completion are not outcome proxies. Retain reusable methods, capability versions, results, failure boundaries and next-time advice. Do not turn one failure into a global rule.

## Initial scope
Included: adaptive workflow, capability discovery/selection/mounting, dynamic organization, outcome-oriented delivery, minimal task artifacts, host adapter principles and real-task evaluation. Excluded for now: custom Agent Runtime, complex task graph engine, dedicated database, arbitrary automatic Skill installation, universal methodology DSL and large capability marketplace.

## Success criteria
Real tasks must show: simple tasks gain no needless overhead; specialist tasks discover suitable capabilities; complex tasks organize collaboration according to net benefit; the workflow adapts to changed requirements; quality/time/cost/human correction improves measurably; security boundaries are preserved.
