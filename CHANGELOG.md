# Changelog

## 0.7.1 — 2026-11-21
- Fix frontmatter parsing of YAML block scalars (`description: >-`, `|`). The hand-rolled parser stored the literal `>-`, which erased the description and removed that Skill from routing; the maintainer's own `dev-system` Skill was affected.
- Fold common English suffixes (`screenshot`/`screenshots`, `review`/`reviewing`), split Skill names on `-`/`_`, and count a word from the Skill name as a strong signal. One description word still does not route; two do.
- Match Skill names and triggers on word boundaries. `cli` no longer fires on `click`, and `vision` no longer fires on `television`.
- Add function words to the stoplist so a single `is` or `what` cannot route a prompt.
- Document that cross-language routing requires declared triggers; the router does not translate.
- Router calibration on a fixed fixture: top-1 hit 14/21 → 16/21, negative false positives 2/10 → 0/10; with declared bilingual triggers, 21/21 and 0/10. Recorded in `open-agent-evals` as `exp-20261121-aaw-router-calibration`.
- Tests: 49.

## 0.7.0 — 2026-11-21
- Add `capability_index.py`: a read-only, zero-dependency local index of project/user Skills and CLI tools, written to `.aaw/runtime/capabilities.json`, and a deterministic Top-2 router injected on `UserPromptSubmit` with `READY` / `MISSING_TOOL` preflight. The router is unevaluated; no precision/recall data exists yet.
- Add 4-field dispatch contracts (`Role`, `Owned-Paths`, `Mounted-Skills`, `Acceptance`): role-aware briefs, physical inlining of indexed Skill rules, and blocking of overlapping builder paths in the same worktree. Overlap is compared by path component, and worktrees are compared after resolution.
- Add Stop gates: anti-cheat on deleted assertions and added skip markers, and a blind-verifier requirement for large diffs. Both cover staged, unstaged and untracked work; `Test-Change:` and `Verifier-Waiver:` release them. Stop uses `decision:block`, which works on every host version (`additionalContext` on Stop only exists from Claude Code 2.1.163).
- Add worker state to `.aaw/runtime/workers.json`: active/completed/superseded/stale/unattributed, `requested_skills` vs applied `mounted_skills`, and `interface_version`. A worker is never marked by guesswork: when several are active and nothing correlates the stop, it is recorded as `unattributed` and no sibling is superseded.
- Add one `aaw-trace@1` execution log record per finished task with a dedupe key; repeated Stops on the same task no longer duplicate the sample. The log is execution data, not evaluation evidence.
- Read reusable evaluation assets from `catalog.yaml` in `open-agent-evals` at a pinned commit instead of re-deriving them per task.
- Match Codex's observed flattened collaboration tool names as well as dotted names, and record the actual host name.
- Leave opaque Codex child messages unchanged rather than appending plaintext to an encrypted-looking token; child prompt injection for those messages remains unavailable.
- Fix the unquoted-colon `description` in `SKILL.md` frontmatter and validate it in CI.
- Tests: 31 protocol tests in the submitted bundle, 41 after adding gate, attribution, dedupe, path, trust and stale-worker coverage.
- Not done: live host verification of the gates, router calibration, and an `open-agent-evals` consumer for the trace log.

## 0.6.4 — 2026-11-17
- Recognize unmarked PowerShell encoded AAW commands during reinstall and uninstall, preserving unrelated hooks.
- Record matching `PreToolUse` invocations and correct the interpretation of missing event records.
- Emit `permissionDecision: allow` alongside `updatedInput` for Codex only, as required by the Codex 0.162.1 parser. This is a permission-decision field; its effect on real host approval has not been independently tested. Claude's output is unchanged. End-to-end child prompt rewriting remains unverified.

## 0.6.3 — 2026-11-16
- Widen the dispatch matchers to tolerate a namespace prefix: `(?:^|\.)(?:Agent|Task|spawn_agent)$` and the matching collection form, in the installer and both checked-in host configs. Codex dispatches as `collaboration.spawn_agent`, which an anchored alternation can never match.
- Record the first real Codex delegation in `docs/host-verification.md`: the child saw no injected brief and no `PreToolUse` record was written, keeping the prompt rewrite UNVERIFIED and separating hook matching from `updatedInput` support.

## 0.6.2 — 2026-11-16
- Record the Codex trust gate in `docs/host-verification.md`: an unapproved handler never runs, `codex exec` cannot approve it, and the terminal still prints `hook: <Event>` because another handler for that event fired.
- Upgrade the matrix with the first host-run evidence: `UserPromptSubmit` is NATIVE (real session ids in two records), while `SessionStart` stays UNVERIFIED with the reason stated.
- Warn on install that Codex approves hooks per handler slot, so interactive Codex must be opened once after handlers are added.

## 0.6.1 — 2026-11-16
- Add `--codex-global`: write `hooks.json` and the Skill package into `CODEX_HOME`, because Codex ignores a project-level `.codex/hooks.json`. The command omits `--project` so one global hook serves every project, the previous file is backed up, foreign hooks and unrelated keys survive, and `--uninstall --codex-global` restores it.
- Warn when `[features] hooks = true` is missing from `CODEX_HOME/config.toml`; without it Codex silently runs no handlers.
- Fix `sync_skills.py --check` failing right after the test suite wrote bytecode: the mirror inventory now ignores `__pycache__`/`*.pyc`, so check order no longer matters.
- Fix the installer printing unreadable paths on a cp936 console (stdout reconfigured to UTF-8, matching the handler).
- Fix `SKILL.md` pointing at `scripts/adaptive_checkpoint.py` in the project root, a path that exists only in this repository; it now names the installed package path, with a test that every script path named in `SKILL.md` exists in the package.
- Replace the stale example in `acceptance-scorecard.md` (it claimed 11 tests and an unrun Windows check) and scope its claim to the handler instead of the host.

## 0.6.0 — 2026-11-15
- Delete `core/`, `templates/`, `interfaces/`, `migration/` and `hooks/`: 13 files that nothing linked to. The task and capability templates contradicted the sizing rules they duplicated, so a model reading them would follow the wrong one.
- Preserve the one rule `core/` uniquely carried in `SKILL.md`: ask only when the answer would change the plan or the result.
- Link `research/` from the README instead of leaving the decision log and reference reading unreachable.
- Add `docs/host-verification.md`: host documentation versus what this package has observed, including that Codex hooks are opt-in behind `features.codex_hooks=true` and that `commandWindows`/`statusMessage` are undocumented keys.
- Add `--dry-run` and `--uninstall` to the installer, so installing into a real project can be inspected and reversed.
- Record first host evidence in `docs/host-verification.md`: Codex fires hooks only from `$CODEX_HOME/hooks.json` and ignored a project-level `.codex/hooks.json` on 0.162.1, while this package's Windows hook command was proven to return a correct payload.

## 0.5.0 — 2026-11-15
- Declare one normative source in the README; `core/`, `DESIGN-v0.1.md` and `research/` are marked historical drafts and are not installed.
- Rename the adapter "contract" to a host capability probe checklist and state that no adapter interface exists.
- Scope a working note to one session with an optional `Session:` line, so two sessions cannot claim the same Stop continuation.
- Surface note truncation with an explicit marker instead of dropping text past 6,000 characters silently.
- Give stored observations a reader: `--report` summarizes them and `--prune N` caps the directory, instead of growing unread records.
- Make hook output portable: stdout is reconfigured to UTF-8 and hook payloads are pure-ASCII JSON, so a cp936 console no longer corrupts them.
- Assert the constants the handler actually uses instead of duplicated prompt sentences, and cover session scoping, truncation, pruning and malformed input.
- Fix the suite on non-UTF-8 consoles: every subprocess call and file read now names its encoding.

## 0.4.0 — 2026-11-15
- Add a narrow risk gate: a short plan brief is required only for irreversible, externally visible, out-of-project or broad-rewrite work; inside those lines the owner still acts.
- Add topology selection criteria instead of a fixed topology, and require freezing the shared interface before parallel writes.
- Require reusing a warm collaborator for follow-up work on the module it already holds, with a fresh-context fallback when the host cannot resume.
- Make capability discovery one consolidated owner inventory plus a budget per further level, so children do not re-walk the ladder.
- Require an evidence-based acceptance scorecard for delivery; unchecked items are WARN, never PASS.
- Add `references/acceptance-scorecard.md` to the canonical Skill package.
- Reject fixed numeric dispatch budgets: call counts and line counts cannot be judged before the work exists, and they forbid legitimate single-owner isolation. Qualitative size hints stay in the topology table.

## 0.3.1 — 2026-11-15
- Replace the generic Stop-only reminder with owner entry/resume, capability-aware delegation and parent-side result integration.
- Append execution instructions and current capability references to actual child prompts without changing permissions.
- Save worker reports for owner inspection rather than restarting children to self-review.
- Read one project working note on resume; continue only active saved work at Stop.
- Add a project installer that copies the complete portable package, pins executable/project paths and preserves unrelated hooks/settings.
- Move executable ownership into the canonical Skill, keeping the root command as a compatibility entry point.
- Execute subprocess, persistence and installer scenarios locally; distinguish these from unperformed live-host task-quality tests.

## 0.2.0 — 2026-11-14
- Add installable project Skills for Codex and Claude Code.
- Add a portable canonical Skill.
- Add operational runtime guidance for work-mode selection, capability discovery, assembly, dynamic organization, adaptation and outcome delivery.
- Clarify discovery/loading/installation/mounting/authorization semantics.
- Add quickstart and host-specific capability notes.
- No custom Agent Runtime, scheduler or permission system is included.

## 0.1.0-draft — 2026-11-14
- Establish general-purpose, lightweight and outcome-oriented workflow positioning.
- Define adaptive workflow, capability discovery/mounting, dynamic organization and outcome learning.
- Add host adapter contract, capability record example, task/capability templates and migration notes.
- Design baseline only; no production runtime or host adapter was implemented.

## 0.2.1 — 2026-11-14
- Make skills/adaptive-agent-workflow the single manually maintained canonical Skill package.
- Bundle complete reference files in Codex and Claude Code Skill directories.
- Add a synchronizer and GitHub Actions drift check for generated host mirrors.
- Remove duplicate top-level operational references and the duplicate core runtime playbook.
- Add conditional safeguards for dependency cycles and stale results after requirement changes.
- Clarify that generated host copies must not be edited directly.

## 0.2.2 — 2026-11-14
- Make explicit user phase boundaries operational: preparation/design requests must not silently trigger product implementation.
- Add execution transparency behavior for requested reports and multi-owner/capability work.
- Require factual per-owner capability states and distinguish active participants from proposed roles.
- Add conditional team-organization guidance for capability ownership and phase separation.
- Extend runtime smoke tests for phase fidelity and execution transparency.

## 0.3.0 — 2026-11-14
- Add adaptive checkpoint hooks for main-owner Stop and sub-agent SubagentStop events in Codex and Claude Code.
- Add a shared standard-library Python handler with recursion protection and host-specific output protocols.
- Add hook event contract, setup/limitations documentation and behavioral tests.
- Extend CI to validate Skill mirrors, Python syntax, hook behavior and host hook JSON.
- Hooks prompt the responsible Agent to reassess results and capability fit; they do not autonomously install Skills or grant permissions.
