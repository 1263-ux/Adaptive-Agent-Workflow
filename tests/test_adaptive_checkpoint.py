"""Exercise actual subprocess hooks, persisted work and the installer's commands.

Behavior is asserted against the constants the handler actually uses, so rewording a
prompt does not break the suite; only a change in what gets injected where does.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/adaptive_checkpoint.py"
CANONICAL = ROOT / "skills/adaptive-agent-workflow/scripts/adaptive_checkpoint.py"
INSTALLER = ROOT / "scripts/install_workflow.py"


def load_canonical():
    spec = importlib.util.spec_from_file_location("aaw_checkpoint", CANONICAL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


aaw = load_canonical()


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

    def cli(self, *args, check=True):
        return subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.project),
                               *args], text=True, encoding="utf-8",
                               capture_output=True, check=check)

    def installer(self, *extra):
        return subprocess.run([sys.executable, str(INSTALLER), "--project", str(self.project),
                               "--host", "both", *extra], text=True, encoding="utf-8",
                              capture_output=True, check=True)

    def note(self, state="active", session=None):
        path = self.project / ".aaw/current.md"
        path.parent.mkdir(exist_ok=True)
        body = (f"Status: {state}" + "\n" + "Goal: API report" + "\n"
                + "Next: inspect docs/findings.md" + "\n"
                + "Skill: /skills/research/SKILL.md; executor: researcher-1" + "\n")
        if session:
            body += "Session: " + session + "\n"
        path.write_text(body, encoding="utf-8")
        return path

    def test_session_start_carries_the_owner_loop(self):
        out = self.call({"hook_event_name": "UserPromptSubmit", "prompt": "Research the API"})
        self.assertIn(aaw.OWNER_START, out["hookSpecificOutput"]["additionalContext"])
        self.assertFalse((self.project / ".aaw/current.md").exists())

    def test_actual_child_prompt_gets_brief_and_other_arguments_survive(self):
        self.note()
        original = {"prompt": "Gather API evidence", "subagent_type": "researcher", "model": "chosen"}
        out = self.call({"hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_input": original})
        body = out["hookSpecificOutput"]
        self.assertEqual(body["updatedInput"]["model"], "chosen")
        self.assertIn("/skills/research/SKILL.md", body["updatedInput"]["prompt"])
        self.assertIn(aaw.WORKER_BRIEF, body["updatedInput"]["prompt"])
        self.assertNotIn("permissionDecision", body)
        self.assertIsNone(self.call({"hook_event_name": "PreToolUse", "tool_name": "Agent",
                                    "tool_input": body["updatedInput"]}))

    def test_codex_message_field_is_supported(self):
        out = self.call({"hook_event_name": "PreToolUse", "session_id": "probe", "tool_name": "spawn_agent",
                         "tool_input": {"message": "Investigate", "agent_type": "explorer"}})
        self.assertIn(aaw.WORKER_BRIEF, out["hookSpecificOutput"]["updatedInput"]["message"])
        records = list((self.project / ".aaw/runtime/events").glob("*.json"))
        self.assertEqual(len(records), 1)
        record = json.loads(records[0].read_text(encoding="utf-8"))
        self.assertEqual((record["event"], record["session_id"], record["tool_name"]),
                         ("PreToolUse", "probe", "spawn_agent"))

    def test_child_report_is_saved_without_restarting_child(self):
        self.assertIsNone(self.call({"hook_event_name": "SubagentStop", "session_id": "s1",
                                    "agent_id": "r1", "last_assistant_message": "docs/findings.md"}))
        files = list((self.project / ".aaw/runtime/handoffs").glob("*.json"))
        saved = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual(saved["reported_result"], "docs/findings.md")
        self.assertIn("awaiting owner inspection", saved["meaning"])

    def test_parent_gets_result_work_not_child_self_review(self):
        self.note()
        out = self.call({"hook_event_name": "PostToolUse", "tool_name": "Agent",
                         "tool_response": {"agent_id": "r1", "status": "running"}}, "claude-code")
        text = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn(aaw.OWNER_RETURN, text)
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

    def test_stop_leaves_work_owned_by_another_session_alone(self):
        self.note(session="sess-A")
        event = {"hook_event_name": "Stop", "stop_hook_active": False}
        self.assertIsNone(self.call({**event, "session_id": "sess-B"}))
        self.assertEqual(self.call({**event, "session_id": "sess-A"})["decision"], "block")

    def test_truncated_note_says_so_instead_of_silently_dropping_text(self):
        path = self.project / ".aaw/current.md"
        path.parent.mkdir()
        path.write_text("Status: active\nGoal: big\nNext: x\n" + "padding " * 1200,
                        encoding="utf-8")
        out = self.call({"hook_event_name": "SessionStart", "session_id": "s"})
        self.assertIn("[truncated:", out["hookSpecificOutput"]["additionalContext"])

    def test_unrelated_tool_is_not_interrupted(self):
        self.assertIsNone(self.call({"hook_event_name": "PreToolUse", "tool_name": "Write"}))
        self.assertIsNone(self.call({"hook_event_name": "PostToolUse", "tool_name": "Bash"}))

    def test_init_records_session_and_preserves_existing_note(self):
        self.cli("--init", "交付比较报告", "--next", "查阅专业 Skill", "--session", "sess-A")
        note = (self.project / ".aaw/current.md").read_text(encoding="utf-8")
        self.assertIn("Session: sess-A", note)
        self.assertIn("查阅专业 Skill", self.cli("--show").stdout)
        self.assertEqual(self.cli("--init", "Another goal", check=False).returncode, 1)
        self.assertIn("交付比较报告", (self.project / ".aaw/current.md").read_text(encoding="utf-8"))

    def test_observations_can_be_reported_and_pruned(self):
        for index in range(5):
            self.call({"hook_event_name": "SubagentStop", "session_id": "s",
                       "agent_id": f"a{index}", "last_assistant_message": "done"})
        self.assertIn("5 records", self.cli("--report").stdout)
        self.assertIn("kept 2", self.cli("--prune", "2").stdout)
        self.assertIn("2 records", self.cli("--report").stdout)

    def test_malformed_event_does_not_break_the_host(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.project)],
                                input="not json", text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")

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
            for ref in re.findall(r"references/[a-z-]+\.md", (package / "SKILL.md").read_text(encoding="utf-8")):
                self.assertTrue((package / ref).is_file(), ref)

    def test_dry_run_reports_without_touching_the_project(self):
        cfg = self.project / ".claude/settings.json"
        cfg.parent.mkdir()
        cfg.write_text(json.dumps({"hooks": {"Stop": [{"hooks": [
            {"type": "command", "command": "echo KEEP"}]}]}}), encoding="utf-8")
        before = cfg.read_text(encoding="utf-8")
        result = self.installer("--dry-run")
        self.assertEqual(before, cfg.read_text(encoding="utf-8"))
        self.assertFalse((self.project / ".claude/skills/adaptive-agent-workflow").exists())
        self.assertFalse((self.project / ".gitignore").exists())
        self.assertIn("would", result.stdout)

    def test_uninstall_removes_only_its_own_handlers(self):
        cfg = self.project / ".claude/settings.json"
        cfg.parent.mkdir()
        cfg.write_text(json.dumps({"permissions": {"deny": ["Bash(rm *)"]}, "hooks": {
            "Stop": [{"hooks": [{"type": "command", "command": "echo KEEP"}]}]}}), encoding="utf-8")
        self.installer()
        self.assertIn(".aaw/runtime/", (self.project / ".gitignore").read_text(encoding="utf-8"))
        self.note()
        result = self.installer("--uninstall")
        data = json.loads(cfg.read_text(encoding="utf-8"))
        self.assertEqual(data["hooks"]["Stop"][0]["hooks"][0]["command"], "echo KEEP")
        self.assertEqual(data["permissions"]["deny"], ["Bash(rm *)"])
        self.assertNotIn("adaptive_checkpoint.py", cfg.read_text(encoding="utf-8"))
        self.assertFalse((self.project / ".claude/skills/adaptive-agent-workflow").exists())
        self.assertFalse((self.project / ".codex/hooks.json").exists())
        self.assertNotIn(".aaw/runtime/", (self.project / ".gitignore").read_text(encoding="utf-8"))
        self.assertTrue((self.project / ".aaw/current.md").exists())
        self.assertIn("Uninstalled", result.stdout)

    def test_skill_mentions_only_scripts_that_exist_in_the_package(self):
        package = ROOT / "skills/adaptive-agent-workflow"
        skill = (package / "SKILL.md").read_text(encoding="utf-8")
        mentioned = re.findall(r"scripts/[a-z_]+\.py", skill)
        self.assertTrue(mentioned)
        for relative in mentioned:
            self.assertTrue((package / relative).is_file(), relative)

    def test_mirror_inventory_ignores_generated_bytecode(self):
        spec = importlib.util.spec_from_file_location("aaw_sync", ROOT / "scripts/sync_skills.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        files = module.package_files(module.SOURCE)
        self.assertTrue(files)
        self.assertFalse([p for p in files if "__pycache__" in p.parts or p.suffix == ".pyc"])

    def test_codex_global_install_targets_codex_home_and_restores_it(self):
        home = self.project / "cxhome"
        home.mkdir()
        (home / "hooks.json").write_text(json.dumps({"note": "keep me", "hooks": {"Stop": [
            {"hooks": [{"type": "command", "command": "echo FOREIGN"}]}]}}), encoding="utf-8")
        (home / "config.toml").write_text("[features]\nhooks = true\n", encoding="utf-8")
        env = {**os.environ, "CODEX_HOME": str(home)}

        def run(*extra):
            return subprocess.run([sys.executable, str(INSTALLER), "--project", str(self.project),
                                   "--host", "codex", "--codex-global", *extra],
                                  text=True, encoding="utf-8", capture_output=True,
                                  check=True, env=env)

        run()
        installed = json.loads((home / "hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(installed["note"], "keep me")
        self.assertEqual(installed["hooks"]["Stop"][0]["hooks"][0]["command"], "echo FOREIGN")
        self.assertIn("UserPromptSubmit", installed["hooks"])
        session_hook = installed["hooks"]["SessionStart"][-1]["hooks"][0]["command"]
        self.assertNotIn("--project", session_hook)
        self.assertTrue((home / "skills/adaptive-agent-workflow/SKILL.md").exists())
        self.assertTrue((home / "hooks.json.aaw-backup").exists())
        self.assertFalse((self.project / ".codex/hooks.json").exists())

        run("--uninstall")
        restored = json.loads((home / "hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(restored["hooks"]), ["Stop"])
        self.assertEqual(restored["note"], "keep me")
        self.assertFalse((home / "skills/adaptive-agent-workflow").exists())

    def test_codex_global_refuses_the_claude_host(self):
        result = subprocess.run([sys.executable, str(INSTALLER), "--project", str(self.project),
                                 "--host", "claude-code", "--codex-global"],
                                text=True, encoding="utf-8", capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("codex", result.stderr.lower())

    def test_reinstall_removes_unmarked_windows_encoded_handler(self):
        import base64
        spec = importlib.util.spec_from_file_location("aaw_installer", INSTALLER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        def encoded(text):
            return "powershell -EncodedCommand " + base64.b64encode(text.encode("utf-16-le")).decode()
        old = {"type": "command", "command": encoded("& 'C:/skills/adaptive-agent-workflow/scripts/adaptive_checkpoint.py'")}
        foreign = {"type": "command", "command": encoded("& 'C:/other/script.py'")}
        existing = {"hooks": {"PreToolUse": [{"matcher": "old", "hooks": [old, foreign]}]}}
        merged = module.merge(existing, module.configuration("new-aaw"))
        groups = merged["hooks"]["PreToolUse"]
        self.assertEqual(groups[0]["hooks"], [foreign])
        self.assertEqual(groups[1]["hooks"][0]["command"], "new-aaw")
        self.assertEqual(module.strip(merged)["hooks"]["PreToolUse"][0]["hooks"], [foreign])

    def test_dispatch_matcher_tolerates_a_namespaced_tool_name(self):
        pattern = re.compile(r"(?:^|\.)(?:Agent|Task|spawn_agent)$")
        for name in ("Agent", "Task", "spawn_agent", "collaboration.spawn_agent", "mcp.Agent"):
            self.assertTrue(pattern.search(name), name)
        for name in ("Write", "spawn_agent_extra", "collaboration.read"):
            self.assertFalse(pattern.search(name), name)

    def test_existing_project_note_can_be_selected(self):
        path = self.project / "docs/project/current.md"
        path.parent.mkdir(parents=True)
        path.write_text("Status: active\nNext: use existing project history\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.project),
                                 "--progress-file", "docs/project/current.md"],
                                input=json.dumps({"hook_event_name": "SessionStart"}),
                                capture_output=True, text=True, encoding="utf-8", check=True)
        self.assertIn("use existing project history", json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"])
        self.assertFalse((self.project / ".aaw/current.md").exists())


if __name__ == "__main__":
    unittest.main()
