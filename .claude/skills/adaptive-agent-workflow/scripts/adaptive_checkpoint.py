#!/usr/bin/env python3
"""Connect the task owner to current work, delegated results, capability routing and anti-laziness gates."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import capability_index as cap_idx
except ImportError:  # pragma: no cover - fallback if copied standalone
    cap_idx = None

OWNER_START = """AAW owner loop: respond to the latest user request, using saved work only as context.
For a non-trivial task, stay direct on the hot cache by default; delegate only for a context
firewall (Scout), worktree-isolated parallel builds (Builder), or blind diff audit (Verifier).
Inspect and use matched professional Skills and available tools/MCP before specialist edits.
Reuse mature capabilities; do not invent a domain method or merely promise to load one.
Assign concrete outputs, role, owned_paths and exact capability references to collaborators.
Keep the current-work note (including Dead-Ends) up to date yourself.
Simple requests stay direct; do not create a team or a progress file just for ceremony.
"""
WORKER_BRIEF = """[AAW execution brief]
Keep the assigned output and scope. Read/use the owner-selected professional Skill references
in this brief; check that the needed tools/MCP are actually available in your context.
If the brief lacks a needed capability, find and use a suitable existing capability before
attempting the specialist work. Report a tool/access gap precisely; do not simulate use.
Produce the artifact, apply the method to it, and return its location, what was checked,
remaining gaps, any Dead-Ends hit, and the useful next action. Name capabilities actually used.
Leave the owner's shared progress note to the owner; do not overwrite it from a worker.
"""
SCOUT_BRIEF = """[AAW execution brief]
Role: scout (read-only context firewall).
Do NOT edit repository files. Gather evidence, locate root causes or constraints, and return a
compact handoff (<500 words) with exact file paths, verified facts, Dead-Ends, and open risks.
Leave the owner's shared progress note to the owner.
"""
VERIFIER_BRIEF = """[AAW execution brief]
Role: verifier (blind, read-only adversarial audit).
Do NOT edit repository files and do NOT trust builder rationalizations. Inspect only the acceptance
criteria, frozen interface, actual git diff/artifacts, and real command exit codes.
Flag any weakened or skipped tests as FAIL. Return PASS / WARN / FAIL per acceptance item with
commands run, exit codes, and concrete defects.
"""
OWNER_RETURN = """AAW: a delegation/collection tool returned to YOU, the owner.
Inspect the actual tool result first. A returned agent ID, timeout or running status is not a
completed deliverable: continue independent work or collect the result through the host.
When a deliverable is present, open it, compare it to the requested outcome, integrate it or
send a specific correction. Record any Dead-Ends so later steps never retry disproved paths.
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
NOTE_LIMIT = 6000
DEFAULT_VERIFIER_MAX_FILES = 3
DEFAULT_VERIFIER_MAX_LINES = 100
TEST_FILE_RE = re.compile(r"(?:^|/)(?:test_[^/]+|[^/]+_test|[^/]+\.spec|[^/]+\.test)\.[a-z0-9]+$|(?:^|/)tests?/", re.I)
TEST_SKIP_ADD_RE = re.compile(
    r"^\+.*(?:\b(?:skip|skipIf|skipUnless|xfail)\b|\.skip\s*\(|@Disabled\b|@Ignore\b|unittest\.skip)",
    re.I,
)
ASSERT_REMOVE_RE = re.compile(r"^-(?!-).*(?:\bassert\b|assertEqual|assertTrue|assertFalse|expect\s*\()", re.I)


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


def read_progress(path: Path) -> str:
    if not path.is_file():
        return ""
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


def workers_path(project: Path) -> Path:
    return project / ".aaw/runtime/workers.json"


def load_workers(project: Path) -> dict[str, Any]:
    path = workers_path(project)
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("workers"), list):
                return data
        except ValueError:
            pass
    return {"interface_version": 1, "workers": []}


def save_workers(project: Path, data: dict[str, Any]) -> None:
    atomic_write(workers_path(project), json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def parse_dispatch_contract(text: str, inputs: dict[str, Any]) -> dict[str, Any]:
    """Extract optional lightweight role/contract fields from subagent dispatch inputs."""
    role_raw = ""
    role_match = re.search(r"(?:^|\n)\s*Role\s*:\s*(scout|builder|verifier)\b", text, re.I)
    if role_match:
        role_raw = role_match.group(1).lower()
    else:
        hint = str(inputs.get("subagent_type") or inputs.get("agent_type") or "").lower()
        if any(tok in hint for tok in ("scout", "explore", "research")):
            role_raw = "scout"
        elif any(tok in hint for tok in ("verif", "review", "audit")):
            role_raw = "verifier"
        else:
            role_raw = "builder"

    owned_paths: list[str] = []
    owned_match = re.search(r"(?:^|\n)\s*Owned-Paths\s*:\s*(.+)$", text, re.I | re.M)
    if owned_match:
        owned_paths = [p.strip().strip("`") for p in re.split(r"[,;]", owned_match.group(1)) if p.strip()]

    mounted_skills: list[str] = []
    skill_match = re.search(r"(?:^|\n)\s*(?:Mounted-Skills|Skills?)\s*:\s*(.+)$", text, re.I | re.M)
    if skill_match:
        raw_skills = [s.strip().strip("`") for s in re.split(r"[,;]", skill_match.group(1)) if s.strip()]
        mounted_skills = [s for s in raw_skills if s.lower() != "none"]

    worktree_match = re.search(r"(?:^|\n)\s*Worktree\s*:\s*(\S+)", text, re.I)
    worktree = worktree_match.group(1).strip() if worktree_match else ""

    return {
        "role": role_raw,
        "explicit_role": bool(role_match),
        "owned_paths": owned_paths,
        "mounted_skills": mounted_skills,
        "worktree": worktree,
    }


def _path_parts(value: str) -> tuple[str, ...]:
    text = value.replace("\\", "/").strip()
    if text.endswith("*"):
        text = text.rstrip("*").rstrip("/")
    return tuple(part for part in PurePosixPath(text).parts if part not in ("", "."))


def paths_overlap(a: str, b: str) -> bool:
    """True when one path equals the other or is a directory prefix of it.

    Components are compared, so `src/api` and `src/apiv2` do not overlap. A
    false block stops legitimate dispatch, which is the expensive error here.
    """
    parts_a, parts_b = _path_parts(a), _path_parts(b)
    if not parts_a or not parts_b:
        return False
    shortest = min(len(parts_a), len(parts_b))
    return parts_a[:shortest] == parts_b[:shortest]


def resolve_worktree(project: Path, value: str) -> str:
    if not value:
        return ""
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = project / candidate
    try:
        return str(candidate.resolve())
    except OSError:
        return str(candidate)


def detect_owned_path_conflicts(project: Path, roster: dict[str, Any],
                                owned_paths: list[str], worktree: str) -> list[str]:
    if not owned_paths:
        return []
    conflicts: list[str] = []
    current_worktree = resolve_worktree(project, worktree)
    for worker in roster.get("workers", []):
        if worker.get("status") != "active" or worker.get("role") != "builder":
            continue
        if current_worktree != resolve_worktree(project, str(worker.get("worktree") or "")):
            continue
        for existing_path in worker.get("owned_paths", []):
            for new_path in owned_paths:
                if paths_overlap(existing_path, new_path):
                    conflicts.append(
                        f"{new_path} overlaps active builder {worker.get('worker_id', '?')} ({existing_path})"
                    )
    return conflicts


def expire_stale_workers(roster: dict[str, Any], session_id: str) -> None:
    """Release workers a dead session left behind; a crashed child must not block forever."""
    try:
        ttl_hours = float(os.environ.get("AAW_WORKER_TTL_HOURS", "12"))
    except ValueError:
        ttl_hours = 12.0
    now = datetime.now(timezone.utc)
    for worker in roster.get("workers", []):
        if worker.get("status") != "active":
            continue
        worker_session = str(worker.get("session_id") or "")
        if session_id and worker_session and worker_session != session_id:
            worker.update(status="stale", stale_reason="session-changed", completed_at=now.isoformat())
            continue
        try:
            dispatched = datetime.fromisoformat(str(worker.get("dispatched_at")))
        except ValueError:
            continue
        if (now - dispatched).total_seconds() > ttl_hours * 3600:
            worker.update(status="stale", stale_reason="ttl", completed_at=now.isoformat())


MAX_WORKER_RECORDS = 500


def trim_workers(roster: dict[str, Any]) -> None:
    workers = roster.get("workers", [])
    if len(workers) <= MAX_WORKER_RECORDS:
        return
    active = [worker for worker in workers if worker.get("status") == "active"]
    history = [worker for worker in workers if worker.get("status") != "active"]
    roster["workers"] = active + history[-(MAX_WORKER_RECORDS - len(active)):]


def select_worker_for_stop(roster: dict[str, Any], envelope: dict[str, Any],
                           agent_id: str) -> tuple[dict[str, Any] | None, str]:
    """Choose which active worker a SubagentStop belongs to.

    The host does not correlate a stop event with the dispatch that started it,
    so this is attribution, not identity. Ambiguity must stay visible instead of
    being resolved into a confident wrong answer.
    """
    active = [worker for worker in roster.get("workers", []) if worker.get("status") == "active"]
    if not active:
        return None, "none"
    if agent_id:
        known = [worker for worker in active if worker.get("agent_id") == agent_id]
        if len(known) == 1:
            return known[0], "agent-id"
    if len(active) == 1:
        return active[0], "single"
    touched = [item.strip() for item in str(envelope.get("touched_files") or "").split(",") if item.strip()]
    if touched:
        scores = [
            (sum(1 for item in touched for owned in worker.get("owned_paths", [])
                 if paths_overlap(item, owned)), worker)
            for worker in active
        ]
        best = max(score for score, _ in scores)
        winners = [worker for score, worker in scores if score == best and score > 0]
        if len(winners) == 1:
            return winners[0], "touched-files"
    return active[0], "ambiguous"


def resolve_inline_skills(project: Path, requested: list[str]) -> tuple[list[str], list[str], str]:
    """Inline distilled rules for up to MAX_MOUNTED_SKILLS *indexed* Skills.

    A dispatch prompt is model-authored text. Only capabilities already present
    in capabilities.json may be inlined; an arbitrary path in `Mounted-Skills:`
    must never become prompt content.
    """
    if not requested or cap_idx is None:
        return [], list(requested), ""
    manifest = cap_idx.load_capabilities_index(project)
    by_name = {str(skill.get("name", "")).lower(): skill for skill in manifest.get("skills", [])}
    by_path = {
        str(Path(skill["path"]).resolve()): skill
        for skill in manifest.get("skills", [])
        if skill.get("path") and Path(skill["path"]).is_file()
    }
    applied: list[str] = []
    rejected: list[str] = []
    chunks: list[str] = []
    for item in requested:
        if len(applied) >= cap_idx.MAX_MOUNTED_SKILLS:
            rejected.append(item)
            continue
        entry = by_name.get(item.lower())
        candidate: Path | None = Path(entry["path"]) if entry else None
        if candidate is None:
            try:
                resolved = Path(item).expanduser()
                if not resolved.is_absolute():
                    resolved = project / resolved
                resolved = resolved.resolve()
            except (OSError, ValueError):
                resolved = None
            if resolved is not None and str(resolved) in by_path:
                candidate = resolved
                entry = by_path[str(resolved)]
        if candidate is None or not candidate.is_file():
            rejected.append(item)
            continue
        rules = cap_idx.extract_distilled_rules(candidate)
        if not rules:
            rejected.append(item)
            continue
        label = candidate.parent.name if candidate.name == "SKILL.md" else candidate.name
        applied.append(label)
        tier = (entry or {}).get("tier", "unknown")
        chunks.append(f"\n[AAW mounted skill: {label} ({candidate}, tier={tier})]\n{rules}")
    return applied, rejected, "\n".join(chunks)


def git_run(project: Path, *args: str) -> str | None:
    if not (project / ".git").exists():
        return None
    try:
        proc = subprocess.run(
            ["git", *args], cwd=project, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=3, check=False,
        )
        return proc.stdout if proc.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


MAX_UNTRACKED_SCANNED = 200


def _untracked_files(project: Path) -> list[str]:
    listing = git_run(project, "ls-files", "--others", "--exclude-standard")
    return [line.strip() for line in (listing or "").splitlines() if line.strip()]


def _line_count(path: Path) -> int:
    try:
        with path.open("rb") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def git_diff_metrics(project: Path) -> dict[str, Any]:
    """Inspect uncommitted work: staged, unstaged and untracked.

    `git diff` alone sees neither staged changes nor new files, so a single
    `git add` would leave every gate here blind. Diff against HEAD (or the
    index when the repository has no commit yet) and count untracked files
    separately.
    """
    empty: dict[str, Any] = {
        "is_git": False, "scan_error": "", "files": [], "file_count": 0,
        "changed_lines": 0, "diff_hash": "", "test_tampering": [], "untracked": [],
    }
    if not (project / ".git").exists():
        return empty
    has_head = git_run(project, "rev-parse", "--verify", "HEAD") is not None
    diff_args = ["diff", "HEAD"] if has_head else ["diff", "--cached"]
    numstat = git_run(project, *diff_args, "--numstat")
    if numstat is None:
        return {**empty, "is_git": True, "scan_error": "git diff failed"}

    files: list[str] = []
    changed_lines = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added, deleted, filepath = parts[0], parts[1], parts[2]
        files.append(filepath)
        if added.isdigit():
            changed_lines += int(added)
        if deleted.isdigit():
            changed_lines += int(deleted)

    untracked = _untracked_files(project)
    for name in untracked[:MAX_UNTRACKED_SCANNED]:
        if name in files:
            continue
        files.append(name)
        changed_lines += _line_count(project / name)

    diff_text = git_run(project, *diff_args, "--unified=0") or ""
    fingerprint = diff_text + "\n" + "\n".join(sorted(untracked))
    diff_hash = short_id(fingerprint) if fingerprint.strip() else ""

    tampering: list[str] = []
    current_file = ""
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
            continue
        if not current_file or not TEST_FILE_RE.search(current_file):
            continue
        if TEST_SKIP_ADD_RE.match(line):
            tampering.append(f"{current_file}: added skip/ignore marker ({line[:80]})")
        elif ASSERT_REMOVE_RE.match(line):
            tampering.append(f"{current_file}: removed assertion ({line[:80]})")

    return {
        "is_git": True,
        "scan_error": "",
        "files": files,
        "file_count": len(files),
        "changed_lines": changed_lines,
        "diff_hash": diff_hash,
        "test_tampering": tampering[:5],
        "untracked": untracked,
    }


def parse_handoff_envelope(message: str) -> dict[str, Any]:
    """Parse structured fields from a worker's final message when present."""
    envelope: dict[str, Any] = {}
    for field, key in (
        ("Status", "status"),
        ("Interface-Status", "interface_status"),
        ("Skills-Applied", "skills_applied"),
        ("Dead-Ends", "dead_ends"),
        ("Touched-Files", "touched_files"),
    ):
        match = re.search(rf"(?:^|\n)\s*{field}\s*:\s*(.+)$", message, re.I | re.M)
        if match:
            envelope[key] = match.group(1).strip()
    return envelope


TRACE_SCHEMA = "aaw-trace@1"
MAX_TRACE_KEYS = 200


def append_eval_trace(project: Path, session_id: str, host: str, note: str,
                      metrics: dict[str, Any]) -> bool:
    """Append one execution trace per finished task.

    A trace is an execution log, not an evaluation result. It carries a schema
    id and a dedupe key because a `Status: done` note stays done: without the
    key, every later Stop would append an identical record and inflate any
    downstream sample count.
    """
    state_path = project / ".aaw/runtime/eval-trace-state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            state = {}
    except (OSError, ValueError):
        state = {}
    keys = [str(key) for key in state.get("keys", []) if isinstance(key, str)]
    trace_key = f"{session_id or 'unknown'}:{metrics.get('diff_hash') or short_id(note)}"
    if trace_key in keys:
        return False

    roster = load_workers(project)
    all_workers = roster.get("workers", [])
    workers = [w for w in all_workers if session_id and w.get("session_id") == session_id]
    if not workers:
        workers = all_workers
    roles = sorted({str(worker.get("role", "builder")) for worker in workers})
    mounted = sorted({skill for worker in workers for skill in worker.get("mounted_skills", [])})
    verifier_ran = any(
        worker.get("role") == "verifier" and worker.get("status") == "completed"
        for worker in workers
    )
    dead_ends = re.findall(r"(?:^|\n)\s*Dead-Ends?\s*:\s*(.+)$", note, re.I | re.M)
    trace = {
        "schema": TRACE_SCHEMA,
        "trace_key": trace_key,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "host": host,
        "session_id": session_id,
        "status": status(note),
        "worker_count": len(workers),
        "roles_used": roles,
        "skills_mounted": mounted,
        "verifier_ran": verifier_ran,
        "unattributed_workers": len([w for w in workers if w.get("status") == "unattributed"]),
        "dead_ends_logged": len([d for d in dead_ends if d.strip() and d.strip().lower() != "none"]),
        "diff_files": metrics.get("file_count", 0),
        "diff_lines": metrics.get("changed_lines", 0),
        "diff_scan_error": metrics.get("scan_error", ""),
        "test_tampering": len(metrics.get("test_tampering") or []),
    }
    trace_path = project / ".aaw/runtime/eval-trace.jsonl"
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(trace, ensure_ascii=False) + "\n")
    keys.append(trace_key)
    atomic_write(state_path, json.dumps({"keys": keys[-MAX_TRACE_KEYS:]}, ensure_ascii=False) + "\n")
    return True


def observe(project: Path, event: dict[str, Any], host: str, extra: dict[str, Any] | None = None) -> None:
    """Persist a host observation, never infer success, review or Skill loading."""
    name = event["hook_event_name"]
    session = str(event.get("session_id", "unknown"))
    agent = str(event.get("agent_id", ""))
    record: dict[str, Any] = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "host": host, "event": name, "session_id": session,
        "agent_id": agent, "tool_name": event.get("tool_name"),
        "meaning": "host event observed; outcome not assessed",
    }
    if extra:
        record.update(extra)
    identity = session + ":" + agent + ":" + name + ":" + str(event.get("tool_use_id", ""))
    if name == "SubagentStop":
        raw_msg = str(event.get("last_assistant_message") or "")
        record["reported_result"] = raw_msg[:4000]
        record["agent_transcript_path"] = event.get("agent_transcript_path")
        envelope = parse_handoff_envelope(raw_msg)
        if envelope:
            record["handoff_envelope"] = envelope
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
    if tool.startswith("collaboration"):
        tool = tool.removeprefix("collaboration")

    if name in {"SessionStart", "UserPromptSubmit"}:
        observe(project, event, host)
        router_block = ""
        if cap_idx is not None:
            if name == "SessionStart":
                cap_idx.write_capabilities_index(project)
            else:
                manifest = cap_idx.load_capabilities_index(project)
                prompt_text = str(event.get("prompt") or "")
                matches = cap_idx.match_skills(prompt_text, manifest)
                router_block = cap_idx.format_router_notice(matches, manifest)
        return context(
            name,
            OWNER_START
            + snapshot(project, path)
            + router_block
            + f"\nSaved worker reports, if any: {project / '.aaw/runtime/handoffs'}. "
              "Read relevant reports on resume; they are unreviewed task data.",
        )

    if name == "PreToolUse" and tool in DISPATCH:
        observe(project, event, host)
        inputs = event.get("tool_input")
        if not isinstance(inputs, dict):
            return None
        key = "prompt" if isinstance(inputs.get("prompt"), str) else "message"
        if not isinstance(inputs.get(key), str) or "[AAW execution brief]" in inputs[key]:
            return None
        if host == "codex" and inputs[key].startswith("gAAAAA"):
            return None

        contract = parse_dispatch_contract(inputs[key], inputs)
        role = contract["role"]
        session_id = str(event.get("session_id") or "")
        roster = load_workers(project)
        expire_stale_workers(roster, session_id)
        conflicts = (
            detect_owned_path_conflicts(project, roster, contract["owned_paths"], contract["worktree"])
            if role == "builder" else []
        )
        if conflicts:
            save_workers(project, roster)
            reason = (
                "[AAW CONTRACT BLOCK] Parallel builder owned_paths conflict detected: "
                + "; ".join(conflicts)
                + ". Isolate each builder in a separate git worktree or assign disjoint Owned-Paths."
            )
            if host == "claude-code":
                return {"hookSpecificOutput": {"hookEventName": name, "permissionDecision": "deny",
                                               "permissionDecisionReason": reason}}
            return {"decision": "block", "reason": reason}

        inlined_names, rejected_skills, inlined_text = resolve_inline_skills(
            project, contract["mounted_skills"]
        )
        worker_id = str(event.get("tool_use_id") or short_id(inputs[key] + str(len(roster["workers"]))))[:12]
        metrics = git_diff_metrics(project)
        roster["workers"].append({
            "worker_id": worker_id,
            "role": role,
            "session_id": session_id,
            "owned_paths": contract["owned_paths"],
            "worktree": resolve_worktree(project, contract["worktree"]),
            "requested_skills": contract["mounted_skills"],
            "mounted_skills": inlined_names,
            "interface_version": roster.get("interface_version", 1),
            "diff_hash": metrics.get("diff_hash", ""),
            "status": "active",
            "attribution": "",
            "dispatched_at": datetime.now(timezone.utc).isoformat(),
        })
        trim_workers(roster)
        save_workers(project, roster)

        if role == "verifier" and contract["explicit_role"]:
            brief = VERIFIER_BRIEF + "\nDo not rely on builder narration; inspect the diff and acceptance criteria directly."
        elif role == "scout" and contract["explicit_role"]:
            brief = SCOUT_BRIEF + snapshot(project, path)
        else:
            brief = (
                WORKER_BRIEF
                + snapshot(project, path)
                + "\nThe assigned task is narrower than this project context; follow your task scope."
            )
        if inlined_text:
            brief += "\n" + inlined_text
        if rejected_skills:
            brief += (
                "\n[AAW notice] Not mounted (not an indexed Skill or unreadable): "
                + ", ".join(rejected_skills)
                + ". Only Skills present in .aaw/runtime/capabilities.json can be inlined; "
                  "record a capability gap instead of pointing at arbitrary files."
            )
        active_builders = [w for w in roster["workers"] if w.get("status") == "active" and w.get("role") == "builder"]
        if role == "builder" and len(active_builders) >= 2 and not contract["worktree"]:
            brief += "\n[AAW notice] Multiple builders are active concurrently without git worktree isolation; stay strictly inside Owned-Paths."

        output: dict[str, Any] = {
            "hookEventName": name,
            "updatedInput": {**inputs, key: inputs[key] + "\n\n" + brief},
        }
        if host == "codex":
            output["permissionDecision"] = "allow"
        return {"hookSpecificOutput": output}

    if name == "SubagentStop":
        raw_msg = str(event.get("last_assistant_message") or "")
        envelope = parse_handoff_envelope(raw_msg)
        roster = load_workers(project)
        agent_id = str(event.get("agent_id", ""))
        matched_worker, attribution = select_worker_for_stop(roster, envelope, agent_id)
        out_of_bounds: list[str] = []
        if matched_worker is not None:
            matched_worker["attribution"] = attribution
            matched_worker["completed_at"] = datetime.now(timezone.utc).isoformat()
            if attribution == "ambiguous":
                # Several workers were active and nothing correlated the stop to
                # one of them. Do not guess: no agent id, no sibling supersede,
                # no file attribution.
                matched_worker["status"] = "unattributed"
            else:
                matched_worker["status"] = "completed"
                if envelope.get("interface_status", "").upper() == "BROKEN":
                    roster["interface_version"] = int(roster.get("interface_version", 1)) + 1
                    for sibling in roster["workers"]:
                        if sibling is not matched_worker and sibling.get("status") == "active":
                            sibling["status"] = "superseded"
                if matched_worker.get("role") == "builder" and matched_worker.get("owned_paths"):
                    metrics = git_diff_metrics(project)
                    for changed in metrics.get("files", []):
                        if not any(paths_overlap(changed, owned) for owned in matched_worker["owned_paths"]):
                            out_of_bounds.append(changed)
                    matched_worker["out_of_bounds_files"] = out_of_bounds
            save_workers(project, roster)
        extra: dict[str, Any] = {"worker_attribution": attribution}
        if out_of_bounds:
            extra["out_of_bounds_files"] = out_of_bounds
        observe(project, event, host, extra=extra)
        return None

    if name == "PostToolUse" and tool in COLLECT:
        observe(project, event, host)
        roster = load_workers(project)
        superseded = [w["worker_id"] for w in roster.get("workers", []) if w.get("status") == "superseded"]
        extra_warn = ""
        if superseded:
            extra_warn = (
                f"\n[AAW SUPERSEDED WARNING] Workers {', '.join(superseded)} ran against an older "
                f"interface version (current v{roster.get('interface_version', 1)}). Discard stale outputs."
            )
        return context(name, OWNER_RETURN + extra_warn + snapshot(project, path))

    if name == "Stop":
        note = read_progress(path)
        current_status = status(note)
        metrics = git_diff_metrics(project)
        if current_status == "done" and note.strip():
            append_eval_trace(project, str(event.get("session_id", "")), host, note, metrics)
            return None
        if event.get("stop_hook_active") is True:
            return None
        if not note.strip():
            # Gates belong to AAW-managed work. An unrelated conversation in the
            # same project must not be blocked by a pre-existing diff.
            return None

        scan_notice = ""
        if metrics.get("scan_error"):
            scan_notice = (
                f"\n[AAW NOTICE] Diff scan failed ({metrics['scan_error']}); "
                "anti-cheat and large-diff gates could not evaluate."
            )

        # Anti-cheat gate: block if tests were silently weakened/skipped in uncommitted diff.
        if metrics["test_tampering"] and not re.search(r"(?im)^\s*Test-Change\s*:\s*\S", note):
            msg = (
                "[AAW ANTI-CHEAT GATE] Detected weakened or skipped tests in git diff:\n- "
                + "\n- ".join(metrics["test_tampering"])
                + "\nRestore the assertions. If the test change is deliberate, record "
                  "`Test-Change: <reason>` in the current-work note before stopping."
            )
            observe(project, event, host, extra={"gate": "anti_cheat"})
            return {"decision": "block", "reason": msg}

        # Large-diff blind verifier gate (only when active work has large uncommitted changes).
        try:
            max_files = int(os.environ.get("AAW_VERIFIER_MAX_FILES", DEFAULT_VERIFIER_MAX_FILES))
            max_lines = int(os.environ.get("AAW_VERIFIER_MAX_LINES", DEFAULT_VERIFIER_MAX_LINES))
        except ValueError:
            max_files, max_lines = DEFAULT_VERIFIER_MAX_FILES, DEFAULT_VERIFIER_MAX_LINES
        if current_status == "active":
            claimed = session_of(note)
            current = str(event.get("session_id", ""))
            if claimed and current and claimed != current:
                return None
            roster = load_workers(project)
            verifier_covered = any(
                w.get("role") == "verifier" and w.get("status") == "completed"
                and w.get("attribution") != "ambiguous"
                and (not metrics["diff_hash"] or w.get("diff_hash") == metrics["diff_hash"])
                for w in roster.get("workers", [])
            )
            waived_verifier = re.search(r"(?im)^\s*Verifier-Waiver\s*:\s*\S", note)
            gate_note = ""
            if (metrics["file_count"] > max_files or metrics["changed_lines"] > max_lines) \
                    and not verifier_covered and not waived_verifier:
                gate_note = (
                    f"\n[AAW VERIFIER GATE] Uncommitted work touches {metrics['file_count']} files "
                    f"({metrics['changed_lines']} lines) with no completed blind Verifier for diff "
                    f"{metrics['diff_hash']}. Dispatch a read-only `Role: verifier`, or record "
                    "`Verifier-Waiver: <reason>` in the note if an independent check is not warranted."
                )
            observe(project, event, host)
            message = OWNER_CONTINUE + scan_notice + gate_note + snapshot(project, path)
            # decision:block works on every host version; hookSpecificOutput
            # additionalContext on Stop only exists from Claude Code 2.1.163.
            return {"decision": "block", "reason": message}
    return None


def observations(project: Path) -> list[Path]:
    base = project / ".aaw/runtime"
    if not base.is_dir():
        return []
    return sorted(
        (path for path in base.rglob("*.json")
         if path.is_file() and path.name not in {"capabilities.json", "workers.json"}),
        key=lambda path: path.stat().st_mtime, reverse=True,
    )


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
    parser.add_argument("--workers", action="store_true", help="show active/completed worker roster")
    parser.add_argument("--capabilities", action="store_true", help="refresh and show indexed capabilities")
    parser.add_argument("--prune", type=int, metavar="KEEP",
                        help="keep only the newest KEEP observation records")
    args = parser.parse_args()
    cli_mode = bool(args.init or args.show or args.report or args.workers
                    or args.capabilities or args.prune is not None)
    try:
        if cli_mode:
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
                             f"Next: {args.next_action}\n"
                             "Dead-Ends: none\n\n"
                             "Record the short plan, active owners, capability references and actual "
                             "results here as work progresses. Keep it useful, not exhaustive.\n")
            if args.session:
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(f"\nSession: {args.session}\n")
            print(path)
        elif args.report:
            report(project)
        elif args.workers:
            print(json.dumps(load_workers(project), ensure_ascii=False, indent=2))
        elif args.capabilities:
            manifest = cap_idx.write_capabilities_index(project) if cap_idx else {"skills": []}
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
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
        return 0 if not cli_mode else 1


if __name__ == "__main__":
    raise SystemExit(main())
