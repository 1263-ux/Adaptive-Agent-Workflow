#!/usr/bin/env python3
"""Synchronize host-specific Skill mirrors from the canonical package."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "adaptive-agent-workflow"
TARGETS = [
    ROOT / ".agents" / "skills" / "adaptive-agent-workflow",
    ROOT / ".claude" / "skills" / "adaptive-agent-workflow",
]


def package_files(base: Path) -> set[Path]:
    return {
        path.relative_to(base)
        for path in base.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    }


def check_target(target: Path) -> list[str]:
    errors: list[str] = []
    source_files = package_files(SOURCE)
    target_files = package_files(target) if target.exists() else set()

    for rel in sorted(source_files - target_files):
        errors.append(f"{target.relative_to(ROOT)}: missing {rel.as_posix()}")
    for rel in sorted(target_files - source_files):
        errors.append(f"{target.relative_to(ROOT)}: unexpected {rel.as_posix()}")
    for rel in sorted(source_files & target_files):
        if not filecmp.cmp(SOURCE / rel, target / rel, shallow=False):
            errors.append(f"{target.relative_to(ROOT)}: out of sync {rel.as_posix()}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if generated host Skill mirrors differ from the canonical package",
    )
    args = parser.parse_args()

    if not SOURCE.is_dir():
        print(f"Canonical Skill package not found: {SOURCE}", file=sys.stderr)
        return 2

    if args.check:
        errors = [error for target in TARGETS for error in check_target(target)]
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("Codex and Claude Code Skill mirrors are in sync.")
        return 0

    for target in TARGETS:
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SOURCE, target)
        print(f"Synced {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
