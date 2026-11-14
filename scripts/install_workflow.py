#!/usr/bin/env python3
"""Install the complete AAW Skill and merge owner-loop hooks into a target project."""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import shlex
import shutil
import sys

SOURCE = Path(__file__).resolve().parents[1] / "skills/adaptive-agent-workflow"
EVENTS = {"SessionStart": None, "UserPromptSubmit": None,
          "PreToolUse": r"^(Agent|Task|spawn_agent)$",
          "PostToolUse": r"^(Agent|Task|spawn_agent|wait|wait_agent|TaskOutput)$",
          "SubagentStop": None, "Stop": None}
MARKER = "AAW owner loop"


def configuration(command: str, arguments: list[str] | None = None) -> dict:
    hooks = {}
    for event, matcher in EVENTS.items():
        group = {"hooks": [{"type": "command", "command": command,
                            "timeout": 10, "statusMessage": MARKER}]}
        if arguments is not None:
            group["hooks"][0]["args"] = arguments
        if matcher:
            group["matcher"] = matcher
        hooks[event] = [group]
    return {"hooks": hooks}


def merge(existing: dict, additions: dict) -> dict:
    # Replace our own current/legacy handlers; leave other hooks and settings intact.
    existing.setdefault("hooks", {})
    for event, groups in list(existing["hooks"].items()):
        kept = []
        for group in groups:
            handlers = [h for h in group.get("hooks", [])
                        if h.get("statusMessage") != MARKER
                        and "adaptive_checkpoint.py" not in h.get("command", "")]
            if handlers:
                kept.append({**group, "hooks": handlers})
        existing["hooks"][event] = kept
    for event, groups in additions["hooks"].items():
        existing["hooks"].setdefault(event, []).extend(groups)
    return existing


def install(project: Path, host: str, progress_file: str | None = None) -> Path:
    host_dir = ".agents" if host == "codex" else ".claude"
    target = project / host_dir / "skills/adaptive-agent-workflow"
    settings = project / (".codex/hooks.json" if host == "codex" else ".claude/settings.json")
    old_text = settings.read_text(encoding="utf-8") if settings.exists() else None
    data = json.loads(old_text) if old_text else {}
    # Copy the package, including its executable; ignore local bytecode.
    shutil.copytree(SOURCE, target, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    argv = [sys.executable, str(target / "scripts/adaptive_checkpoint.py"),
            "--host=" + host, "--project", str(project)]
    if progress_file:
        argv.extend(["--progress-file", progress_file])
    if host == "claude-code":
        additions = configuration(argv[0], argv[1:])  # Native exec form, no shell quoting.
    elif os.name == "nt":
        expression = "& " + " ".join("'" + arg.replace("'", "''") + "'" for arg in argv)
        encoded = base64.b64encode(expression.encode("utf-16-le")).decode("ascii")
        additions = configuration("powershell -NoProfile -NonInteractive -EncodedCommand " + encoded)
    else:
        additions = configuration(shlex.join(argv))
    data = merge(data, additions)
    settings.parent.mkdir(parents=True, exist_ok=True)
    if old_text is not None:
        backup = settings.with_name(settings.name + ".aaw-backup")
        if not backup.exists():
            backup.write_text(old_text, encoding="utf-8")
    settings.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ignore = project / ".gitignore"
    content = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    lines = [".aaw/runtime/", "*.aaw-backup", "__pycache__/", "*.pyc"]
    missing = [line for line in lines if line not in content.splitlines()]
    if missing:
        ignore.write_text(content.rstrip() + "\n\n# AAW local observations\n" +
                          "\n".join(missing) + "\n", encoding="utf-8")
    return settings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--host", choices=("codex", "claude-code", "both"), default="both")
    parser.add_argument("--progress-file", help="reuse an existing project working note")
    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        parser.error("--project must name an existing directory")
    try:
        for host in ("codex", "claude-code") if args.host == "both" else (args.host,):
            print(f"Installed {host}: {install(project, host, args.progress_file)}")
        print("Review/trust the changed hooks in the host. Existing project progress is untouched.")
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"AAW install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
