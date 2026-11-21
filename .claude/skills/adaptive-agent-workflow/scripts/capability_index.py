#!/usr/bin/env python3
"""Read-only local capability indexer, deterministic skill router, and rule extractor.

Zero external dependencies, zero network calls, zero LLM calls.
Scans local Skill directories (project, host mirrors, user home, optional sibling OAE
catalog) and builds `.aaw/runtime/capabilities.json` so the Owner does not have to
re-discover installed capabilities by hand every session.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any

MAX_MOUNTED_SKILLS = 2
SELF_SKILL_NAME = "adaptive-agent-workflow"
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "have",
    "will", "when", "then", "only", "used", "using", "use", "work", "task", "file",
    "files", "code", "make", "help", "please", "need", "want", "check", "run",
}


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


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse lightweight YAML frontmatter without requiring PyYAML."""
    lines = text.splitlines()
    meta: dict[str, Any] = {}
    body_start = 0
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                body_start = idx + 1
                header_lines = lines[1:idx]
                break
        else:
            header_lines = []
    else:
        # Fallback for legacy SKILL.md without leading --- fence (e.g. v0.6.0).
        header_lines = []
        for idx, line in enumerate(lines):
            if re.match(r"^[a-zA-Z0-9_-]+:\s*", line):
                header_lines.append(line)
                body_start = idx + 1
            else:
                break

    for raw in header_lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if value.startswith("[") and value.endswith("]"):
            items = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
            meta[key] = items
        else:
            meta[key] = value
    return meta, "\n".join(lines[body_start:])


def _list_field(meta: dict[str, Any], key: str) -> list[str]:
    val = meta.get(key)
    if isinstance(val, list):
        return [str(v).strip() for v in val if str(v).strip()]
    if isinstance(val, str) and val.strip():
        return [v.strip() for v in val.split(",") if v.strip()]
    return []


def tokenize(text: str) -> set[str]:
    ascii_words = {
        tok.lower()
        for tok in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]{1,}", text)
        if tok.lower() not in STOPWORDS and len(tok) >= 2
    }
    # Include 2-char CJK bigrams for Chinese prompt matching without external tokenizers.
    cjk_runs = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    cjk_tokens: set[str] = set()
    for run in cjk_runs:
        cjk_tokens.add(run)
        for idx in range(len(run) - 1):
            cjk_tokens.add(run[idx:idx + 2])
    return ascii_words | cjk_tokens


def skill_roots(project: Path, include_home: bool = True) -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = [
        ("project", project / "skills"),
        ("project-codex", project / ".agents/skills"),
        ("project-claude", project / ".claude/skills"),
    ]
    # Optional sibling open-agent-evals catalog if present next to the project.
    oae_dir = os.environ.get("AAW_OAE_DIR")
    if oae_dir:
        roots.append(("oae", Path(oae_dir).expanduser()))
    else:
        sibling_oae = project.parent / "open-agent-evals"
        if sibling_oae.is_dir():
            roots.append(("oae", sibling_oae))
    if include_home and os.environ.get("AAW_DISABLE_HOME_SCAN") != "1":
        home = Path.home()
        roots.extend([
            ("user-codex", home / ".agents/skills"),
            ("user-claude", home / ".claude/skills"),
        ])
    return roots


def preflight_tools(required_tools: list[str]) -> tuple[str, list[str]]:
    if not required_tools:
        return "READY", []
    missing = [tool for tool in required_tools if shutil.which(tool) is None]
    if missing:
        return "MISSING_TOOL", missing
    return "READY", []


def extract_distilled_rules(skill_md_path: Path, max_chars: int = 1200) -> str:
    """Extract compact executable rules/checklists from a SKILL.md for subagent inlining."""
    if not skill_md_path.is_file():
        return ""
    text = skill_md_path.read_text(encoding="utf-8", errors="replace")
    _, body = parse_frontmatter(text)
    lines = [line.rstrip() for line in body.splitlines()]
    picked: list[str] = []
    # Prefer sections titled Rules / Checklist / Verification / Workflow / Work the task.
    priority_re = re.compile(r"^#{1,3}\s+.*(rule|checklist|verif|workflow|work the task|gate|must|constraints|步骤|规则|验收)", re.I)
    in_priority = False
    for line in lines:
        if line.startswith("#"):
            in_priority = bool(priority_re.match(line))
            if in_priority:
                picked.append(line)
            continue
        if in_priority and line.strip():
            picked.append(line)
    if not picked:
        # Fallback: first non-empty lines of the body.
        picked = [line for line in lines if line.strip()][:20]
    joined = "\n".join(picked).strip()
    if len(joined) <= max_chars:
        return joined
    return joined[:max_chars].rstrip() + "\n[truncated: read full SKILL.md if needed]"


def scan_capabilities(project: Path, include_home: bool = True) -> dict[str, Any]:
    """Scan local Skill directories and produce a deduplicated capability manifest."""
    discovered: dict[str, dict[str, Any]] = {}
    for tier, root in skill_roots(project, include_home=include_home):
        if not root.is_dir():
            continue
        for skill_md in sorted(root.rglob("SKILL.md")):
            # Skip deeply nested vendor/node_modules/test fixtures.
            if any(part in {".git", "node_modules", "__pycache__", ".venv", "venv"} for part in skill_md.parts):
                continue
            try:
                text = skill_md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            meta, _ = parse_frontmatter(text)
            name = str(meta.get("name") or skill_md.parent.name).strip()
            if not name or name in discovered:
                continue
            required_tools = _list_field(meta, "requires_tools")
            status, missing_tools = preflight_tools(required_tools)
            entry = {
                "name": name,
                "description": str(meta.get("description") or "").strip(),
                "path": str(skill_md),
                "tier": tier,
                "triggers": _list_field(meta, "triggers"),
                "requires_tools": required_tools,
                "conflicts_with": _list_field(meta, "conflicts_with"),
                "host_support": _list_field(meta, "host_support") or ["codex", "claude-code"],
                "preflight": status,
                "missing_tools": missing_tools,
            }
            discovered[name] = entry

    cli_inventory = {
        tool: bool(shutil.which(tool))
        for tool in ("git", "python3", "python", "node", "npm", "pytest", "mvn", "cargo", "gh")
    }
    manifest = {
        "indexed_at": datetime.now(timezone.utc).isoformat(),
        "project": str(project),
        "max_mounted_skills": MAX_MOUNTED_SKILLS,
        "priority_order": ["user_latest_request", "domain_hard_gate_skill", "orchestration_skill"],
        "skills": list(discovered.values()),
        "cli_tools": {k: v for k, v in cli_inventory.items() if v},
    }
    return manifest


def write_capabilities_index(project: Path, include_home: bool = True) -> dict[str, Any]:
    manifest = scan_capabilities(project, include_home=include_home)
    out = project / ".aaw/runtime/capabilities.json"
    atomic_write(out, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def load_capabilities_index(project: Path, include_home: bool = True) -> dict[str, Any]:
    path = project / ".aaw/runtime/capabilities.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("skills"), list):
                return data
        except ValueError:
            pass
    return write_capabilities_index(project, include_home=include_home)


def match_skills(prompt: str, manifest: dict[str, Any], limit: int = MAX_MOUNTED_SKILLS) -> list[dict[str, Any]]:
    """Deterministically rank top-K domain skills for a user prompt."""
    if not prompt.strip():
        return []
    prompt_lower = prompt.lower()
    prompt_tokens = tokenize(prompt)
    scored: list[tuple[int, dict[str, Any]]] = []
    for skill in manifest.get("skills", []):
        name = str(skill.get("name", ""))
        if not name or name == SELF_SKILL_NAME:
            continue
        score = 0
        # Exact skill name mention is strongest signal.
        if name.lower() in prompt_lower:
            score += 10
        for trig in skill.get("triggers", []):
            if trig.lower() in prompt_lower:
                score += 6
        desc_tokens = tokenize(name + " " + str(skill.get("description", "")) + " " + " ".join(skill.get("triggers", [])))
        overlap = prompt_tokens & desc_tokens
        score += len(overlap) * 2
        if score >= 4:
            scored.append((score, skill))

    scored.sort(key=lambda item: (-item[0], item[1].get("name", "")))
    selected: list[dict[str, Any]] = []
    selected_names: set[str] = set()
    for score, skill in scored:
        if len(selected) >= limit:
            break
        conflicts = set(skill.get("conflicts_with", []))
        if conflicts & selected_names:
            continue
        selected.append({**skill, "match_score": score})
        selected_names.add(skill["name"])
    return selected


def format_router_notice(matches: list[dict[str, Any]], manifest: dict[str, Any]) -> str:
    if not matches:
        total = len([s for s in manifest.get("skills", []) if s.get("name") != SELF_SKILL_NAME])
        if total == 0:
            return ""
        return (f"\n[AAW capability router] {total} local domain Skill(s) indexed in "
                ".aaw/runtime/capabilities.json; none auto-matched this prompt (stay direct unless a gap appears).")
    lines = [
        f"\n[AAW capability router] Matched {len(matches)} domain Skill(s) "
        f"(budget max {MAX_MOUNTED_SKILLS}; precedence: user request > domain gate > orchestration):"
    ]
    for idx, skill in enumerate(matches, 1):
        status = skill.get("preflight", "READY")
        missing = skill.get("missing_tools") or []
        suffix = f" (missing CLI: {', '.join(missing)})" if missing else ""
        lines.append(f"  {idx}. {skill['name']} [{status}{suffix}] -> {skill['path']}")
    lines.append("Read the matched SKILL.md before specialist edits, or record SKIP_SKILL(<name>: <reason>) in current work.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".")
    parser.add_argument("--prompt", help="optional prompt to test deterministic skill routing")
    parser.add_argument("--no-home", action="store_true", help="skip scanning ~/.agents and ~/.claude")
    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()
    manifest = write_capabilities_index(project, include_home=not args.no_home)
    if args.prompt:
        matches = match_skills(args.prompt, manifest)
        print(json.dumps({"matches": matches}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
