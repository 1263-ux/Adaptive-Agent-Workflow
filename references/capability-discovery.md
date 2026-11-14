# Capability Discovery Playbook

Use when a task benefits from specialist methods, a capability gap exists, the domain/tooling is unfamiliar, the current method underperforms, or the user explicitly asks for exploration.

## Triggers
- A necessary Skill or tool is missing.
- The domain or method is unfamiliar.
- Current quality is below the user's target.
- The approach is too slow, costly or unreliable.
- A promising alternative may materially improve the result.
- The user explicitly requests research or exploration.

Do not search by default for every task. First check whether current capabilities suffice.

## Search sequence
1. Current conversation/session capabilities and user-provided resources.
2. Project-local and team Skills/catalogs.
3. Host-native Skills, tools and official integrations.
4. Official repositories and documentation.
5. Trusted maintained specialist repositories and open Skills.
6. Professional literature, standards and examples.
7. Create a local supplement only for a demonstrated gap.

Search for the concrete subproblem and expected output, not merely a broad domain label.

## Candidate decision
For each serious candidate, briefly answer:
- What problem does it solve and what method/expertise does it provide?
- Why does it fit, and when does it not apply?
- What are its source, version and license?
- What tools, permissions, runtime or dependencies does it require?
- Are there scripts, network calls, install hooks, credential access or file side effects?
- Does it conflict with another selected method?
- Is a representative probe needed?

Review proportionally. Familiar low-risk capabilities need a light check. New or consequential capabilities need deeper inspection. Executable, networked, credentialed or destructive behavior requires code inspection and actual authorization/sandbox controls.

## Selection and composition
Prefer mature upstream capability over rewriting it. Combine complementary methods, sequence dependent methods, and resolve conflicts through applicability analysis or a small experiment. Do not load overlapping Skills without a reason. Preserve source and version/commit; prefer references or pinning over copying third-party Skill bodies.

## Mounting semantics
"Mount" means making the selected capability available to the responsible execution context through a mechanism the host actually supports.

Distinguish:
- Discovered: metadata/source found.
- Inspected: instructions/dependencies reviewed.
- Selected: chosen for this task.
- Loaded: instructions read into a context.
- Installed: files placed in a host-recognized persistent location.
- Mounted: host/runtime confirms availability in the intended context.
- Authorized: required tool/resource permissions are actually granted.

A Skill cannot grant permissions. If the host cannot dynamically mount to a child Agent, pass a reference or scoped instructions in its task brief. If only manual loading is supported, state that. Do not claim installation or mounting when only reading occurred.
