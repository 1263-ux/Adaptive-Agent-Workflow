import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "adaptive_checkpoint.py"


def invoke(payload):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )


class AdaptiveCheckpointTests(unittest.TestCase):
    def test_codex_stop_requests_owner_review(self):
        result = invoke({"hook_event_name": "Stop", "stop_hook_active": False})
        data = json.loads(result.stdout)
        self.assertEqual(data["decision"], "block")
        self.assertIn("main task owner", data["reason"])
        self.assertIn("capability gap", data["reason"])

    def test_codex_subagent_stop_requests_handoff_review(self):
        result = invoke({
            "hook_event_name": "SubagentStop",
            "agent_type": "researcher",
            "stop_hook_active": False,
        })
        data = json.loads(result.stdout)
        self.assertEqual(data["decision"], "block")
        self.assertIn("researcher", data["reason"])
        self.assertIn("handoff", data["reason"])

    def test_recursive_stop_is_suppressed(self):
        for event_name in ("Stop", "SubagentStop"):
            result = invoke({"hook_event_name": event_name, "stop_hook_active": True})
            self.assertEqual(result.stdout, "")

    def test_unrelated_event_is_ignored(self):
        result = invoke({"hook_event_name": "PostToolUse"})
        self.assertEqual(result.stdout, "")

    def test_claude_stop_uses_additional_context(self):
        result = invoke({
            "hook_event_name": "Stop",
            "stop_hook_active": False,
            "_host": "claude-code",
        })
        data = json.loads(result.stdout)
        self.assertEqual(data["hookSpecificOutput"]["hookEventName"], "Stop")
        self.assertIn("main task owner", data["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__":
    unittest.main()
