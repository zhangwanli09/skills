"""Check that clean checkouts can reproduce every advertised filesystem scenario."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from setup_fixture import EVAL_DIR, prepare, snapshot


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / "isolated runs"

    def test_declared_inputs_create_the_advertised_scenarios(self):
        cases = json.loads((EVAL_DIR / "evals.json").read_text())["evals"]
        for case in cases:
            with self.subTest(eval_id=case["id"]):
                self.assertTrue(case["files"])
                for name in case["files"]:
                    self.assertTrue((EVAL_DIR.parent / name).is_file(), name)
                metadata = prepare(case["id"], self.workspace)
                project = Path(metadata["project"])
                git_root = subprocess.check_output(
                    ["git", "-C", str(project), "rev-parse", "--show-toplevel"], text=True
                ).strip()
                self.assertEqual(Path(git_root).resolve(), project.resolve())
                self.assertIn(str(project), metadata["prompt"])
                self.assertNotIn("{{project}}", metadata["prompt"])
                self.assertTrue(Path(metadata["working_directory"]).is_dir())
                initial = json.loads(Path(metadata["initial_state_file"]).read_text())
                self.assertEqual(snapshot(project), initial["project"])
                clients = (project / "CLIENTS.md").read_text()
                for name in ("Codex", "Claude Code", "Cursor", "Gemini CLI", "Copilot", "OpenCode"):
                    self.assertIn(name, clients)

                if case["id"] == 1:
                    package = project / ".claude/skills/review"
                    self.assertEqual((package / "assets/example.bin").read_bytes(), b"\x00\xff\x10")
                    self.assertTrue((package / "references/checklist.md").is_file())
                    self.assertTrue((package / "scripts/check.py").is_file())
                    if os.name != "nt":
                        self.assertTrue(os.access(package / "scripts/check.py", os.X_OK))
                elif case["id"] == 2:
                    source = (project / ".agents/skills/review/SKILL.md").read_bytes()
                    divergent = (project / ".claude/skills/review/SKILL.md").read_bytes()
                    self.assertNotEqual(source, divergent)
                    editor = json.loads((project / ".vscode/mcp.json").read_text())
                    self.assertEqual(editor["servers"]["locked"]["env"]["TOKEN"], "${input:token}")
                    self.assertTrue(editor["servers"]["locked"]["sandboxEnabled"])
                    legacy = json.loads((project / "opencode.json").read_text())
                    self.assertFalse(legacy["mcp"]["docs"]["enabled"])
                else:
                    broken, external = (project / ".claude/skills" / name for name in ("broken", "external"))
                    self.assertTrue(broken.is_symlink())
                    self.assertFalse(broken.exists())
                    self.assertTrue(external.is_symlink())
                    target = external.resolve()
                    self.assertFalse(target.is_relative_to(project))
                    self.assertTrue(target.is_relative_to(Path(metadata["run_directory"])))
                    self.assertTrue((target / "SKILL.md").is_file())
                    self.assertEqual(Path(metadata["working_directory"]), project / "packages/api")
                    self.assertIn("// Preserve", (project / "opencode.jsonc").read_text())
                    servers = json.loads((project / ".mcp.json").read_text())["mcpServers"]
                    self.assertEqual(servers["process"]["args"], ["scripts/server with spaces.js", "--flag", "a b"])
                    self.assertEqual(servers["http"]["type"], "http")
                    self.assertEqual(servers["legacy"]["type"], "sse")

    def test_each_run_is_independent_including_external_sentinels(self):
        for eval_id in (1, 2, 3):
            with self.subTest(eval_id=eval_id):
                first = prepare(eval_id, self.workspace)
                second = prepare(eval_id, self.workspace)
                self.assertNotEqual(first["project"], second["project"])
                first_project, second_project = Path(first["project"]), Path(second["project"])
                expected = snapshot(second_project)
                (first_project / "AGENTS.md").write_text("Only this run was changed.\n")
                self.assertEqual(snapshot(second_project), expected)
                if eval_id == 3:
                    first_target = (first_project / ".claude/skills/external").resolve()
                    second_target = (second_project / ".claude/skills/external").resolve()
                    self.assertNotEqual(first_target, second_target)
                    before = snapshot(second_target)
                    (first_target / "SKILL.md").write_text("Changed test sentinel.\n")
                    self.assertEqual(snapshot(second_target), before)

    def test_setup_cli_works_outside_the_checkout(self):
        completed = subprocess.run(
            [sys.executable, str(EVAL_DIR / "setup_fixture.py"), "--eval-id", "1",
             "--workspace", str(self.workspace)],
            cwd=self.temp.name, check=True, capture_output=True, text=True,
        )
        metadata = json.loads(completed.stdout)
        saved = json.loads(Path(metadata["metadata_file"]).read_text())
        self.assertEqual(saved["project"], metadata["project"])
        self.assertEqual(saved["prompt"], metadata["prompt"])
        self.assertTrue(Path(metadata["outputs"]).is_dir())

    def test_failed_setup_does_not_leave_partial_projects(self):
        for method, error in (("setup_fixture.subprocess.run", FileNotFoundError("Git unavailable")),
                              ("setup_fixture.Path.symlink_to", OSError("Symlinks unavailable"))):
            with self.subTest(method=method):
                with patch(method, side_effect=error):
                    with self.assertRaises(OSError):
                        prepare(3, self.workspace)
                self.assertEqual(list(self.workspace.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
