# Changelog

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
