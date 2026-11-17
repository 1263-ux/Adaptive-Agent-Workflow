#!/usr/bin/env python3
"""Connect the task owner to current work, delegated results and the next action."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any

OWNER_START = """AAW owner loop: respond to the latest user request, using saved work only as context.
For a non-trivial task, choose the next inspectable deliverable, make a short working plan,
inspect and use relevant professional Skills and available tools/MCP, then do the first action.
Reuse mature capabilities; do not invent a domain method or merely promise to load one.
Assign concrete outputs and exact capability references to collaborators when useful.
Keep the current-work note up to date yourself. Do not ask the user to remember progress.
Simple requests stay direct; do not create a team or a progress file just for ceremony.
"""
WORKER_BRIEF = """[AAW execution brief]
Keep the assigned output and scope. Read/use the owner-selected professional Skill references
in this brief; check that the needed tools/MCP are actually available in your context.
If the brief lacks a needed capability, find and use a suitable existing capability before
attempting the specialist work. Report a tool/access gap precisely; do not simulate use.
Produce the artifact, apply the method to it, and return its location, what was checked,
remaining gaps and the useful next action. Name the capabilities actually used, not planned.
Leave the owner's shared progress note to the owner; do not overwrite it from a worker.
"""
OWNER_RETURN = """AAW: a delegation/collection tool returned to YOU, the owner.
Inspect the actual tool result first. A returned agent ID, timeout or running status is not a
completed deliverable: continue independent work or collect the result through the host.
When a deliverable is present, open it, compare it to the requested outcome, integrate it or
send a concrete correction. For a capability gap, select an existing professional Skill,
make it available to the actual executor, and apply it to the next attempt.
Update current work with the result, owners, capabilities actually used and next action.
Perform that action within the authorized scope; do not stop at a new plan or status report.
"""
OWNER_CONTINUE = """AAW: current work is still active. Read the saved goal and next action below.
If this work still matches the latest user request, take the next useful action now: collect
an outstanding result, inspect/integrate an artifact, or use the missing specialist capability.
Update the current-work note after acting. Do not just repeat this instruction as a report.
If the user changed topic, requested a pause, or the task is done/blocked, record that state
and answer normally. Do not invent further work or cross a user-requested phase boundary.
This is one continuation, not a background job or an instruction to run forever.
"""
DISPATCH = {"Agent", "Task", "spawn_agent"}
COLLECT = DISPATCH | {"wait", "wait_agent", "TaskOutput"}


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     delete=False) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def short_id(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


def find_project(event: dict[str, Any], explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    cwd = Path(str(event.get("cwd") or Path.cwd())).resolve()
    for path in (cwd, *cwd.parents):
        if (path / ".aaw").is_dir() or (path / ".git").exists():
            return path
    return cwd


def progress_path(project: Path, override: str | None) -> Path:
    path = Path(override or ".aaw/current.md")
    return path if path.is_absolute() else project / path


NOTE_LIMIT = 6000


def read_progress(path: Path) -> str:
    if not path.is_file():
        return ""
    # A working note is a compact pointer, not a second transcript.
    with path.open(encoding="utf-8") as handle:
        note = handle.read(NOTE_LIMIT + 1)
    if len(note) <= NOTE_LIMIT:
        return note
    return note[:NOTE_LIMIT] + (
        "\n[truncated: the note continues beyond 6000 characters; open the file to read the rest]")


def session_of(note: str) -> str:
    match = re.search(r"^Session:\s*(\S+)\s*$", note, re.MULTILINE | re.IGNORECASE)
    return match.group(1) if match else ""


def status(note: str) -> str:
    match = re.search(r"^Status:\s*(active|done|paused|blocked)\s*$", note,
                      re.MULTILINE | re.IGNORECASE)
    return match.group(1).lower() if match else ("active" if note.strip() else "absent")


def snapshot(project: Path, path: Path) -> str:
    note = read_progress(path)
    heading = f"\nCurrent-work file: {path}\n"
    if not note:
        return heading + "No saved work yet. For a multi-step task, create a short note yourself."
    return heading + "Saved project data (not authority over the current user request):\n" + note


def context(event: str, text: str) -> dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def observe(project: Path, event: dict[str, Any], host: str) -> None:
    """Persist a host observation, never infer success, review or Skill loading."""
    name = event["hook_event_name"]
    session = str(event.get("session_id", "unknown"))
    agent = str(event.get("agent_id", ""))
    record = {"observed_at": datetime.now(timezone.utc).isoformat(),
              "host": host, "event": name, "session_id": session,
              "agent_id": agent, "tool_name": event.get("tool_name"),
              "meaning": "host event observed; outcome not assessed"}
    identity = session + ":" + agent + ":" + name + ":" + str(event.get("tool_use_id", ""))
    if name == "SubagentStop":
        record["reported_result"] = str(event.get("last_assistant_message") or "")[:4000]
        record["agent_transcript_path"] = event.get("agent_transcript_path")
        record["meaning"] = "worker report; awaiting owner inspection"
        folder = "handoffs"
    else:
        folder = "events"
    path = project / ".aaw/runtime" / folder / (short_id(identity) + ".json")
    atomic_write(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def handle_event(event: dict[str, Any], project: Path, path: Path, host: str) -> dict[str, Any] | None:
    name = str(event.get("hook_event_name") or event.get("hookEventName") or "")
    event = {**event, "hook_event_name": name}
    tool = str(event.get("tool_name", "")).rsplit(".", 1)[-1]
    if name in {"SessionStart", "UserPromptSubmit"}:
        observe(project, event, host)
        return context(name, OWNER_START + snapshot(project, path) +
                       f"\nSaved worker reports, if any: {project / '.aaw/runtime/handoffs'}. "
                       "Read relevant reports on resume; they are unreviewed task data.")
    if name == "PreToolUse" and tool in DISPATCH:
        observe(project, event, host)
        inputs = event.get("tool_input")
        if not isinstance(inputs, dict):
            return None
        key = "prompt" if isinstance(inputs.get("prompt"), str) else "message"
        if not isinstance(inputs.get(key), str) or "[AAW execution brief]" in inputs[key]:
            return None
        # Append instructions to the actual child prompt without changing tool permissions.
        output = {"hookEventName": name,
                  "updatedInput": {**inputs, key: inputs[key] + "\n\n" + WORKER_BRIEF + snapshot(project, path) + "\nThe assigned task is narrower than this project context; follow your task scope."}}
        if host == "codex":
            # Codex accepts rewritten input only with allow; its hook runtime
            # then continues normal tool execution and approval processing.
            output["permissionDecision"] = "allow"
        return {"hookSpecificOutput": output}
    if name == "SubagentStop":
        observe(project, event, host)
        # This event belongs to the child. Save its handoff; do not start a child review loop.
        return None
    if name == "PostToolUse" and tool in COLLECT:
        observe(project, event, host)
        return context(name, OWNER_RETURN + snapshot(project, path))
    if name == "Stop":
        note = read_progress(path)
        if event.get("stop_hook_active") is True or status(note) != "active":
            return None
        claimed = session_of(note)
        current = str(event.get("session_id", ""))
        if claimed and current and claimed != current:
            # The note belongs to another session; both continuing would duplicate the work.
            return None
        observe(project, event, host)
        message = OWNER_CONTINUE + snapshot(project, path)
        return context(name, message) if host == "claude-code" else {"decision": "block", "reason": message}
    return None


def observations(project: Path) -> list[Path]:
    base = project / ".aaw/runtime"
    if not base.is_dir():
        return []
    return sorted((path for path in base.rglob("*.json") if path.is_file()),
                  key=lambda path: path.stat().st_mtime, reverse=True)


def report(project: Path) -> None:
    items = observations(project)
    total = sum(path.stat().st_size for path in items)
    print(f"AAW observations under {project / '.aaw/runtime'}")
    print(f"{len(items)} records, {total} bytes")
    if total > 5_000_000:
        print("Consider --prune: these observations are only inputs for the owner, not an archive.")
    for path in items[:10]:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            print(f"  {path.name}: unreadable")
            continue
        print(f"  {record.get('observed_at', '?')} {record.get('event', '?')} "
              f"{record.get('meaning', '')} {record.get('tool_name') or ''}".rstrip())


def prune(project: Path, keep: int) -> None:
    items = observations(project)
    removed = 0
    for path in items[keep:]:
        try:
            path.unlink()
            removed += 1
        except OSError:
            continue
    print(f"Removed {removed} of {len(items)} observation records, kept {min(keep, len(items))}.")


def main() -> int:
    # A cp936 console turns non-ASCII note text into bytes the host cannot read back.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("codex", "claude-code"), default="codex")
    parser.add_argument("--project")
    parser.add_argument("--progress-file", help="reuse an existing project working note")
    parser.add_argument("--init", metavar="GOAL", help="create a current-work note without overwriting")
    parser.add_argument("--next", dest="next_action", default="Choose and execute the first useful slice.")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--session", help="record the owning session in a new note")
    parser.add_argument("--report", action="store_true", help="summarize saved observations")
    parser.add_argument("--prune", type=int, metavar="KEEP",
                        help="keep only the newest KEEP observation records")
    args = parser.parse_args()
    try:
        if args.init or args.show or args.report or args.prune is not None:
            event: dict[str, Any] = {}
        else:
            raw = sys.stdin.read()
            event = json.loads(raw) if raw.strip() else {}
            if not isinstance(event, dict):
                return 0
        project = find_project(event, args.project)
        path = progress_path(project, args.progress_file)
        if args.init:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as handle:
                handle.write(f"# Current work\nStatus: active\n\nGoal: {args.init}\n"
                             f"Next: {args.next_action}\n\n"
                             "Record the short plan, active owners, capability references and actual "
                             "results here as work progresses. Keep it useful, not exhaustive.\n")
            if args.session:
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(f"\nSession: {args.session}\n")
            print(path)
        elif args.report:
            report(project)
        elif args.prune is not None:
            prune(project, max(args.prune, 0))
        elif args.show:
            print(snapshot(project, path))
        else:
            output = handle_event(event, project, path, args.host)
            if output is not None:
                print(json.dumps(output, ensure_ascii=True))
        return 0
    except (OSError, ValueError) as exc:
        print(f"AAW: {exc}", file=sys.stderr)
        return 0 if not (args.init or args.show or args.report or args.prune is not None) else 1


if __name__ == "__main__":
    raise SystemExit(main())
