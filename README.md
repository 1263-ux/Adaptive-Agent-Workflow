# Adaptive Agent Workflow Framework

**A lightweight, task-driven, adaptive framework for organizing agent work.**

> Help agents understand the user's outcome, discover and assemble relevant capabilities, organize work dynamically, execute with the smallest effective structure, and adapt based on real results.

## Status

Design baseline: **v0.1-draft**. This repository contains architecture and operating protocols, not a production runtime. Host-specific capabilities must be verified against the actual host and version.

## Start here

1. [Design overview](DESIGN-v0.1.md)
2. [Operating model](core/operating-model.md)
3. [Adaptive workflow](core/adaptive-workflow.md)
4. [Capability discovery and mounting](core/capability-discovery-and-mounting.md)
5. [Dynamic organization](core/dynamic-organization.md)
6. [Outcome, delivery and learning](core/outcome-and-learning.md)
7. [Host adapter contract](adapters/adapter-contract.md)
8. [Migration from the previous workflow](migration/from-v1.md)

## Core principles

- Lightweight by default; complexity grows only when the task justifies it.
- Discover and reuse before building.
- Professional methods are supplied by mature domain skills and tools, not recreated in this framework.
- Roles are temporary responsibilities, not permanent agent identities.
- Agent count, test count and process completion are not proxies for outcome quality.
- Permissions must be enforced by the host/runtime, never merely claimed by prompts.
- Every mechanism must be open to revision, simplification or removal.

## Related evaluation assets

The companion repository [open-agent-evals](https://github.com/1263-ux/open-agent-evals) maintains reusable Evaluation Packs, Method Assets, Experiment Records and Capability Profiles. This framework discovers and organizes work using those assets; the evaluation repository links back here as its execution framework. The two repositories are independently versioned and connected through asset IDs, versions and Git references.

## What this is not

- Not a universal fixed workflow.
- Not a mandatory multi-agent system.
- Not a replacement for professional software/game/research/design methodologies.
- Not a new agent runtime, task database or skills marketplace.
