# Owner-loop hooks

Install the complete Skill and event wiring into the work project with `python scripts/install_workflow.py --project /path/to/project --host both`.

The executable source is `skills/adaptive-agent-workflow/scripts/adaptive_checkpoint.py`. The root script is a compatibility entry point. The [event contract](../skills/adaptive-agent-workflow/references/hook-events.md) and [setup guide](../docs/quickstart.md) describe the current behavior.

SubagentStop records the child's handoff; the parent's delegation/collection return is where integration work is requested. Startup/resume carries the current-work note. The handlers do not install Skills or grant tool permissions.
