#!/usr/bin/env python3
"""Compatibility entry point; executable source lives in the portable Skill."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "skills" /
                      "adaptive-agent-workflow" / "scripts" / "adaptive_checkpoint.py"),
                   run_name="__main__")
