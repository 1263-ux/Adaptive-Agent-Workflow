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
          # Codex also emits flattened names such as collaborationspawn_agent.
          "PreToolUse": r"(?:^|\.|^collaboration)(?:Agent|Task|spawn_agent)$",
          "PostToolUse": r"(?:^|\.|^collaboration)(?:Agent|Task|spawn_agent|wait|wait_agent|TaskOutput)$",
          "SubagentStop": None, "Stop": None}
MARKER = "AAW owner loop"
GITIGNORE_HEADER = "# AAW local observations"
GITIGNORE_ADDED = [".aaw/runtime/", "*.aaw-backup", "__pycache__/", "*.pyc"]
GITIGNORE_REMOVED = [".aaw/runtime/", "*.aaw-backup"]


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


def is_aaw_handler(handle: dict) -> bool:
    command = handle.get("command", "")
    if handle.get("statusMessage") == MARKER or "adaptive_checkpoint.py" in command:
        return True
    if "-EncodedCommand " in command:
        try:
            encoded = command.split("-EncodedCommand ", 1)[1].split()[0]
            command = base64.b64decode(encoded, validate=True).decode("utf-16-le")
        except (ValueError, UnicodeError, IndexError):
            return False
        return "adaptive-agent-workflow" in command and "adaptive_checkpoint.py" in command
    return False


def keep_foreign(groups: list) -> list:
    """Keep every handler that is not ours, including unrelated hooks in shared groups."""
    kept = []
    for group in groups:
        handlers = [handle for handle in group.get("hooks", []) if not is_aaw_handler(handle)]
        if handlers:
            kept.append({**group, "hooks": handlers})
    return kept


def strip(existing: dict) -> dict:
    """Remove every AAW handler and leave the rest of the settings untouched."""
    hooks = existing.get("hooks")
    if not isinstance(hooks, dict):
        return existing
    for event, groups in list(hooks.items()):
        kept = keep_foreign(groups) if isinstance(groups, list) else []
        if kept:
            hooks[event] = kept
        else:
            hooks.pop(event, None)
    if not hooks:
        existing.pop("hooks", None)
    return existing


def merge(existing: dict, additions: dict) -> dict:
    existing = strip(existing)
    existing.setdefault("hooks", {})
    for event, groups in additions["hooks"].items():
        existing["hooks"].setdefault(event, []).extend(groups)
    return existing


def codex_home() -> Path:
    value = os.environ.get("CODEX_HOME")
    return Path(value).expanduser() if value else Path.home() / ".codex"


def paths(project: Path, host: str, global_codex: bool = False) -> tuple[Path, Path]:
    if host == "codex" and global_codex:
        # Codex only loads hooks from its own home, and a global hook must not pin one project.
        home = codex_home()
        return home / "skills/adaptive-agent-workflow", home / "hooks.json"
    host_dir = ".agents" if host == "codex" else ".claude"
    settings = project / (".codex/hooks.json" if host == "codex" else ".claude/settings.json")
    return project / host_dir / "skills/adaptive-agent-workflow", settings


def warn_about_codex_trust() -> None:
    config = codex_home() / "config.toml"
    text = config.read_text(encoding="utf-8") if config.exists() else ""
    if "hooks = true" not in text:
        print("WARNING: Codex hooks are opt-in. Without [features] hooks = true in "
              f"{config} the handlers never run, and nothing reports the failure.", file=sys.stderr)
    print("WARNING: Codex approves hooks per handler slot. Open interactive Codex once and approve "
          "the new entries, or they are skipped silently; codex exec cannot approve them.",
          file=sys.stderr)


def hook_config(project: Path, host: str, target: Path, progress_file: str | None,
                global_codex: bool = False) -> dict:
    argv = [sys.executable, str(target / "scripts/adaptive_checkpoint.py"), "--host=" + host]
    if not global_codex:
        # A global hook serves every project, so the handler resolves the project from the event.
        argv.extend(["--project", str(project)])
    if progress_file:
        argv.extend(["--progress-file", progress_file])
    if host == "claude-code":
        return configuration(argv[0], argv[1:])  # Native exec form, no shell quoting.
    if os.name == "nt":
        expression = "& " + " ".join("'" + arg.replace("'", "''") + "'" for arg in argv)
        encoded = base64.b64encode(expression.encode("utf-16-le")).decode("ascii")
        return configuration("powershell -NoProfile -NonInteractive -EncodedCommand " + encoded)
    return configuration(shlex.join(argv))


def ignore_lines(project: Path) -> tuple[list[str], list[str]]:
    ignore = project / ".gitignore"
    content = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    return content, [line for line in GITIGNORE_ADDED if line not in content.splitlines()]


def install(project: Path, host: str, progress_file: str | None = None,
            dry_run: bool = False, global_codex: bool = False) -> Path:
    target, settings = paths(project, host, global_codex)
    old_text = settings.read_text(encoding="utf-8") if settings.exists() else None
    data = merge(json.loads(old_text) if old_text else {},
                 hook_config(project, host, target, progress_file, global_codex))
    content, missing = ignore_lines(project)
    if global_codex:
        warn_about_codex_trust()
    if dry_run:
        state = "would create" if old_text is None else "would merge into"
        print(f"[{host}] {state} {settings}; events: {', '.join(sorted(data['hooks']))}")
        print(f"[{host}] would copy the Skill package to {target}")
        if global_codex:
            print(f"[{host}] project .gitignore untouched; add .aaw/runtime/ to each "
                  "project that should ignore its own notes")
        else:
            print(f"[{host}] .gitignore: " + (", ".join(missing) if missing else "already complete"))
        return settings
    # Copy the package, including its executable; ignore local bytecode.
    shutil.copytree(SOURCE, target, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    settings.parent.mkdir(parents=True, exist_ok=True)
    if old_text is not None:
        backup = settings.with_name(settings.name + ".aaw-backup")
        if not backup.exists():
            backup.write_text(old_text, encoding="utf-8")
    settings.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if missing and not global_codex:
        ignore = project / ".gitignore"
        ignore.write_text(content.rstrip() + "\n\n# AAW local observations\n" +
                          "\n".join(missing) + "\n", encoding="utf-8")
    return settings


def uninstall(project: Path, host: str, dry_run: bool = False,
              global_codex: bool = False) -> Path:
    target, settings = paths(project, host, global_codex)
    old_text = settings.read_text(encoding="utf-8") if settings.exists() else None
    data = strip(json.loads(old_text)) if old_text else {}
    content, _ = ignore_lines(project)
    kept = [line for line in content.splitlines()
            if line not in GITIGNORE_REMOVED and line.strip() != GITIGNORE_HEADER]
    removed = 0 if global_codex else len(content.splitlines()) - len(kept)
    if dry_run:
        print(f"[{host}] would remove {target}")
        print(f"[{host}] would remove AAW handlers from {settings}"
              + ("" if old_text else " (not present)"))
        print(f"[{host}] .gitignore: " + (f"would remove {removed} AAW line(s)" if removed else "nothing to remove"))
        return settings
    if target.exists():
        shutil.rmtree(target)
    if old_text is not None:
        if data:
            settings.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            settings.unlink()
    if removed:
        (project / ".gitignore").write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
    return settings


def main() -> int:
    # A cp936 console turns the reported absolute paths into unreadable bytes.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--host", choices=("codex", "claude-code", "both"), default="both")
    parser.add_argument("--progress-file", help="reuse an existing project working note")
    parser.add_argument("--dry-run", action="store_true", help="show the planned changes only")
    parser.add_argument("--uninstall", action="store_true",
                        help="remove AAW hooks, .gitignore lines and the installed package")
    parser.add_argument("--codex-global", action="store_true",
                        help="Codex loads hooks only from CODEX_HOME; write hooks.json and the "
                             "Skill package there instead of into the project")
    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        parser.error("--project must name an existing directory")
    if args.codex_global and args.host == "claude-code":
        parser.error("--codex-global applies to the codex host only")
    try:
        for host in ("codex", "claude-code") if args.host == "both" else (args.host,):
            scoped = args.codex_global and host == "codex"
            if args.uninstall:
                where = uninstall(project, host, args.dry_run, scoped)
                print(f"{'Would uninstall' if args.dry_run else 'Uninstalled'} {host}: {where}")
            else:
                where = install(project, host, args.progress_file, args.dry_run, scoped)
                print(f"{'Would install' if args.dry_run else 'Installed'} {host}: {where}")
        if args.uninstall:
            print("Progress notes and .aaw/runtime records were left in place; remove .aaw yourself if unwanted.")
        else:
            print("Review/trust the changed hooks in the host. Existing project progress is untouched.")
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"AAW install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
