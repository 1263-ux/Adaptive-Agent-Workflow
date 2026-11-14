#!/usr/bin/env python3
"""Emit a lightweight Adaptive Agent Workflow checkpoint for supported host hooks."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

CHECKPOINT = """Adaptive Agent Workflow checkpoint — one concise review is required before continuing.

1. Inspect the actual result of the just-finished work. What was delivered, and what evidence supports it?
2. Is the current method and capability set still sufficient for the next step?
3. If there is a real capability gap, actively discover and inspect suitable existing Skills/methods; select and load only what is useful into the responsible context. Do not search or load Skills just to satisfy this checkpoint.
4. If the method, owner, team, scope or task topology is no longer suitable, make the smallest effective adjustment.
5. Continue when the current approach is adequate. If this was a sub-agent, return a factual handoff to the owner: output locations, findings, capability states, gaps and next action.

Be precise: distinguish available, discovered, inspected, selected, loaded, installed, mounted and authorized. Never report a planned capability as loaded or mounted. Respect the user's current project phase; this checkpoint does not authorize a phase transition.
"""


def main() -> int:
    raw = sys.stdin.read()
    try:
        event: dict[str, Any] = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0

    name = str(event.get("hook_event_name") or event.get("hookEventName") or "")
    if name not in {"Stop", "SubagentStop"}:
        return 0

    # Prevent a continuation prompt from recursively triggering itself.
    if event.get("stop_hook_active") is True:
        return 0

    if name == "Stop":
        role = "main task owner"
        target = "Review the whole task round and decide whether to continue, adapt, or deliver."
    else:
        role = "sub-agent"
        agent_type = event.get("agent_type") or event.get("agent_type_name") or "unnamed"
        target = (
            f"Review your own work as sub-agent ({agent_type}) and prepare a factual handoff "
            "for the parent owner. Do not expand scope or create more agents unless explicitly useful."
        )

    message = f"{CHECKPOINT}\nCurrent event: {name}. Current participant: {role}. {target}"
    is_claude = (
        str(event.get("source") or "").lower() == "claude-code"
        or event.get("_host") == "claude-code"
        or bool(os.environ.get("CLAUDE_PROJECT_DIR"))
    )

    if is_claude:
        output = {
            "hookSpecificOutput": {
                "hookEventName": name,
                "additionalContext": message,
            }
        }
    else:
        # Codex Stop/SubagentStop use a continuation reason, not additionalContext.
        output = {
            "decision": "block",
            "reason": message,
        }

    sys.stdout.write(json.dumps(output, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
