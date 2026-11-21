# Capability Discovery

## When to discover
Discover when a necessary capability is missing, the domain/tooling is unfamiliar, quality is poor, the current approach is too slow or costly, a better alternative may materially improve the outcome, or the user explicitly asks for exploration. Skip when existing capabilities suffice.

One consolidated inventory is the owner job. Check what the session, the project and the host already expose in one pass, then pass the confirmed references into every brief. Children do not walk the ladder again for a gap the inventory already answered - that spends a second context to rediscover the first one.

## Where to search
1. Current session and user-provided resources.
2. Project-local and team Skills/catalogs.
3. Host-native Skills and official integrations.
4. Official repositories and documentation.
5. Trusted maintained specialist repositories and open Skills.
6. Professional literature, standards and examples.
7. A local supplement only for a demonstrated gap.

Budget, not a count cap. Each further level must name the gap it closes and the gain it is expected to produce; stop when the next level costs more than the answer is worth. A fixed search quota fails the same way - the expensive levels are exactly where a real gap gets closed.

Search for the concrete subproblem and expected output, not a broad domain label.

## Evaluate proportionally
For a candidate, determine its purpose, method, applicability, source/version/license, dependencies, compatibility, cost and risks. Inspect scripts, network/file access, credential handling and install hooks. Familiar low-risk capabilities need a light check; new, consequential or executable capabilities need deeper inspection and actual authorization/sandbox controls.

## Select and compose
Prefer mature upstream capabilities over rewriting them. Combine complementary methods, sequence dependent methods and resolve conflicts through applicability analysis or a small experiment. Avoid loading overlapping Skills without a reason. Preserve source/version/commit and prefer references or pinning over copying third-party Skill bodies.

## Reusable evaluation and method assets

When the task needs an evaluation standard, a regression gate, or a method that outlives this session, read the asset catalog in `1263-ux/open-agent-evals` before writing your own. Pin the read to a commit, not a moving branch.

- Read `catalog.yaml` and select by `kind` (`evaluation-pack`, `method-asset`, `experiment-record`, `capability-profile`), `domain`, `status` and `applicability`. Open an asset's `path` only when its entry fits the task; the catalog is deliberately thin.
- Treat `proposed` and `experimental` as unproven. A `verified` method is bound by its declared conditions, not by the headline claim. An experiment's `confidence` and `replay_status` travel with any number taken from it.
- Do not fork a pack, rubric or method into this repository. Cite its id and version. When an asset does not fit, record the gap as a new experiment rather than editing the asset locally.

Current pin: `open-agent-evals@5b956779efe3c1673b69f45bad102153efe2ae79` (`catalog.yaml`). Bump it deliberately; the asset ids and versions carry the meaning, not the catalog file.

## Distinguish lifecycle states
- Discovered: metadata/source found.
- Inspected: instructions/dependencies reviewed.
- Selected: chosen for this task.
- Loaded: instructions read into a context.
- Installed: files placed in a host-recognized persistent location.
- Mounted: host/runtime confirms availability in the intended context.
- Authorized: required tool/resource permissions are actually granted.

A Skill cannot grant permissions. If the host cannot mount to a child Agent, pass a reference or scoped instructions in its task brief. Never claim a state that did not occur.
