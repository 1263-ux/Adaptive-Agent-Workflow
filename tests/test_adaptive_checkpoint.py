"""Exercise actual subprocess hooks, persisted work and the installer's commands."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/adaptive_checkpoint.py"
INSTALLER = ROOT / "scripts/install_workflow.py"


class OwnerLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="aaw project ")
        self.project = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def call(self, event, host="codex"):
        result = subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.project),
                                 "--host=" + host],
                                input=json.dumps(event), text=True, encoding="utf-8",
                                capture_output=True, check=True)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def note(self, state="active"):
        path = self.project / ".aaw/current.md"
        path.parent.mkdir(exist_ok=True)
        path.write_text(f"Status: {state}\nGoal: API report\nNext: inspect docs/findings.md\n"
                        "Skill: /skills/research/SKILL.md; executor: researcher-1\n",
                        encoding="utf-8")
        return path

    def test_specialist_work_arrives_before_production(self):
        out = self.call({"hook_event_name": "UserPromptSubmit", "prompt": "Research the API"})
        self.assertIn("inspect and use relevant professional Skills", out["hookSpecificOutput"]["additionalContext"])
        self.assertFalse((self.project / ".aaw/current.md").exists())

    def test_actual_child_prompt_gets_method_context_and_other_arguments_survive(self):
        self.note()
        original = {"prompt": "Gather API evidence", "subagent_type": "researcher", "model": "chosen"}
        out = self.call({"hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_input": original})
        body = out["hookSpecificOutput"]
        self.assertEqual(body["updatedInput"]["model"], "chosen")
        self.assertIn("/skills/research/SKILL.md", body["updatedInput"]["prompt"])
        self.assertIn("[AAW execution brief]", body["updatedInput"]["prompt"])
        self.assertNotIn("permissionDecision", body)
        self.assertIsNone(self.call({"hook_event_name": "PreToolUse", "tool_name": "Agent",
                                    "tool_input": body["updatedInput"]}))

    def test_codex_message_field_is_supported(self):
        out = self.call({"hook_event_name": "PreToolUse", "tool_name": "spawn_agent",
                         "tool_input": {"message": "Investigate", "agent_type": "explorer"}})
        self.assertIn("[AAW execution brief]", out["hookSpecificOutput"]["updatedInput"]["message"])

    def test_child_report_is_saved_without_restarting_child(self):
        self.assertIsNone(self.call({"hook_event_name": "SubagentStop", "session_id": "s1",
                                    "agent_id": "r1", "last_assistant_message": "docs/findings.md"}))
        files = list((self.project / ".aaw/runtime/handoffs").glob("*.json"))
        saved = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual(saved["reported_result"], "docs/findings.md")
        self.assertEqual(saved["meaning"], "worker report; awaiting owner inspection")

    def test_parent_gets_result_work_not_child_self_review(self):
        self.note()
        out = self.call({"hook_event_name": "PostToolUse", "tool_name": "Agent",
                         "tool_response": {"agent_id": "r1", "status": "running"}}, "claude-code")
        text = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("YOU, the owner", text)
        self.assertIn("not a\ncompleted deliverable", text)
        self.assertIn("docs/findings.md", text)
        self.assertNotIn("decision", out)

    def test_resume_reads_saved_progress_in_a_new_session(self):
        self.note()
        out = self.call({"hook_event_name": "SessionStart", "source": "resume", "session_id": "new"})
        self.assertIn("Next: inspect docs/findings.md", out["hookSpecificOutput"]["additionalContext"])

    def test_stop_only_continues_active_work_once(self):
        event = {"hook_event_name": "Stop", "stop_hook_active": False}
        self.assertIsNone(self.call(event))
        self.note()
        self.assertEqual(self.call(event)["decision"], "block")
        self.assertIn("Stop", self.call(event, "claude-code")["hookSpecificOutput"]["hookEventName"])
        self.assertIsNone(self.call({**event, "stop_hook_active": True}))
        for state in ("done", "paused", "blocked"):
            self.note(state)
            self.assertIsNone(self.call(event))

    def test_unrelated_tool_is_not_interrupted(self):
        self.assertIsNone(self.call({"hook_event_name": "PreToolUse", "tool_name": "Write"}))
        self.assertIsNone(self.call({"hook_event_name": "PostToolUse", "tool_name": "Bash"}))

    def test_init_and_show_preserve_existing_note(self):
        command = [sys.executable, str(SCRIPT), "--project", str(self.project)]
        subprocess.run(command + ["--init", "交付比较报告", "--next", "查阅专业 Skill"], check=True, capture_output=True)
        shown = subprocess.run(command + ["--show"], check=True, capture_output=True, text=True, encoding="utf-8")
        self.assertIn("查阅专业 Skill", shown.stdout)
        repeat = subprocess.run(command + ["--init", "Different goal"], capture_output=True)
        self.assertNotEqual(repeat.returncode, 0)
        self.assertIn("交付比较报告", (self.project / ".aaw/current.md").read_text(encoding="utf-8"))

    def test_install_merge_reinstall_and_real_configured_command(self):
        cfg = self.project / ".claude/settings.json"
        cfg.parent.mkdir()
        cfg.write_text(json.dumps({"permissions": {"deny": ["Bash(rm *)"]}, "hooks": {
            "Stop": [{"hooks": [{"type": "command", "command": "echo KEEP"}]}]}}), encoding="utf-8")
        command = [sys.executable, str(INSTALLER), "--project", str(self.project), "--host", "both"]
        subprocess.run(command, check=True, capture_output=True)
        first = cfg.read_text(encoding="utf-8")
        subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(first, cfg.read_text(encoding="utf-8"))
        data = json.loads(first)
        self.assertEqual(data["permissions"]["deny"], ["Bash(rm *)"])
        self.assertEqual(data["hooks"]["Stop"][0]["hooks"][0]["command"], "echo KEEP")
        self.note()
        for host, config_path in (("claude-code", cfg), ("codex", self.project / ".codex/hooks.json")):
            config = json.loads(config_path.read_text(encoding="utf-8"))
            handler = config["hooks"]["SessionStart"][-1]["hooks"][0]
            actual = [handler["command"], *handler["args"]] if "args" in handler else handler["command"]
            subdir = self.project / "nested"
            subdir.mkdir(exist_ok=True)
            result = subprocess.run(actual, shell=isinstance(actual, str), cwd=subdir,
                                    input=json.dumps({"hook_event_name": "SessionStart", "source": "resume"}),
                                    capture_output=True, text=True, encoding="utf-8", check=True)
            self.assertIn("docs/findings.md", json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"])
            package = self.project / (".agents" if host == "codex" else ".claude") / "skills/adaptive-agent-workflow"
            self.assertTrue((package / "SKILL.md").exists())
            self.assertTrue((package / "scripts/adaptive_checkpoint.py").exists())
            for ref in re.findall(r"references/[a-z-]+\.md", (package / "SKILL.md").read_text()):
                self.assertTrue((package / ref).is_file(), ref)

    def test_existing_project_note_can_be_selected(self):
        path = self.project / "docs/project/current.md"
        path.parent.mkdir(parents=True)
        path.write_text("Status: active\nNext: use existing project history\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.project),
                                 "--progress-file", "docs/project/current.md"],
                                input=json.dumps({"hook_event_name": "SessionStart"}),
                                capture_output=True, text=True, check=True)
        self.assertIn("use existing project history", json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"])
        self.assertFalse((self.project / ".aaw/current.md").exists())


if __name__ == "__main__":
    unittest.main()
