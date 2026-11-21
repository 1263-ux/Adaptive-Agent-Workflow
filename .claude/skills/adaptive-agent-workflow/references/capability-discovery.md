# Capability Discovery, Routing & Verified Mounting

Orchestration cannot substitute for domain capability, and relying on models to remember to search for Skills fails in practice. Make discovery automatic, mounting bounded, and loading verifiable.

## Automated Local Indexing & Push Routing

- **`SessionStart`** runs `scripts/capability_index.py` (read-only, zero network, zero LLM calls) to scan project `skills/`, `.agents/skills/`, `.claude/skills/`, user-level host Skill folders, optional sibling `open-agent-evals`, and local CLI tools, writing `.aaw/runtime/capabilities.json`.
- **`UserPromptSubmit`** deterministically matches the prompt against indexed `name`, `triggers`, and `description` fields, checks `requires_tools` preflight (`READY` vs. `MISSING_TOOL`), and pushes the Top-K candidates directly into the owner's context.
- **Explicit waiver:** If a matched Skill is intentionally not used, record `SKIP_SKILL(<name>: <reason>)` in `.aaw/current.md`.

## Mounting Budget & Conflict Precedence

Mounting too many Skills causes context bloat and contradictory rules:

- **Hard budget:** Mount at most **2 domain Skills** per task or worker.
- **Precedence order:** `latest user request > domain hard-gate Skill > orchestration Skill`.
- **Optional frontmatter metadata:** Skills may declare `triggers: [...]`, `requires_tools: [...]`, `conflicts_with: [...]`, and `host_support: [...]` in YAML frontmatter (always quote `description` if it contains `:`, or use a block scalar such as `description: >-`).
- **Triggers are the routing contract.** The router matches a prompt against the Skill name and declared triggers, plus description words as corroboration (two or more). A prompt that shares no token with a Skill cannot match it, and the router does not translate: a Chinese request needs Chinese triggers on an English-described Skill. Declare the words users actually type, in every language the task accepts.

## 7-Tier Search Ladder (When Local Index Has a Proven Gap)

1. Current session / user resources
2. Project-local and team Skills (`.aaw/runtime/capabilities.json`)
3. Host-native Skills and official integrations
4. Official repositories and documentation
5. Trusted, maintained open-source Skills (inspect scripts, network, credentials, and install hooks; pin commit SHA)
6. Domain literature, standards, and reference implementations
7. Local minimal supplement—only for a proven gap

## Reusable Evaluation and Method Assets

When the task needs an evaluation standard, a regression gate, or a method that outlives this session, read the asset catalog in `1263-ux/open-agent-evals` before writing your own. Pin the read to a commit, not a moving branch.

- Read `catalog.yaml` and select by `kind` (`evaluation-pack`, `method-asset`, `experiment-record`, `capability-profile`), `domain`, `status` and `applicability`. Open an asset's `path` only when its entry fits the task; the catalog is deliberately thin.
- Treat `proposed` and `experimental` as unproven. A `verified` method is bound by its declared conditions, not by the headline claim. An experiment's `confidence` and `replay_status` travel with any number taken from it.
- Do not fork a pack, rubric or method into this repository. Cite its id and version. When an asset does not fit, record the gap as a new experiment rather than editing the asset locally.
- Local discovery and the remote catalog are different things: the index answers "what is installed here", the catalog answers "what evidence exists". Do not treat an indexed Skill as a verified method.

Current pin: `open-agent-evals@6fd1875d5dcff17a7f82bf2146e4d8fab4f5c774` (`catalog.yaml`). Bump it deliberately; asset ids and versions carry the meaning, not the catalog file.

## 7 Orthogonal Lifecycle States

Never claim a state that did not happen:

`Discovered -> Inspected -> Selected -> Loaded -> Installed -> Mounted -> Authorized`

- **Physical inlining for subagents:** Because subagents frequently ignore bare file-path pointers, `PreToolUse` resolves up to 2 `Mounted-Skills:` entries **that exist in `capabilities.json`** and splices their distilled rules into the subagent prompt. An arbitrary file path is never inlined; unresolved entries are reported in the brief as not mounted.
- **Authorization boundary:** A Skill never grants permissions; host runtime settings remain the sole permission authority.

## Execution Log, Not Evaluation Evidence

When `.aaw/current.md` reaches `Status: done`, `Stop` appends one record per task to `.aaw/runtime/eval-trace.jsonl` (`schema: aaw-trace@1`: host, session, roles used, mounted Skills, verifier coverage, unattributed workers, dead-ends logged, diff size, test-tampering count). A dedupe key prevents repeated Stops on the same finished task from inflating the count.

This is a **raw execution log**. It is not an evaluation result and must not be read as one:

- It records that a verifier ran, not that the work was good.
- It covers one task in one project, not a controlled comparison.
- Turning it into evidence requires an experiment record in `open-agent-evals` with a pack, version, conditions, runs and `replay_status`.

Write to this log freely; cite it as evidence only after that aggregation exists.
