"""Regression checks for audit boundaries, privacy, and schema inventory."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from audit_config import inventory, tomllib


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_nested_inventory_never_emits_config_values_or_writes(self):
        self.write("AGENTS.md", "PRIVATE_INSTRUCTIONS")
        self.write("packages/api/AGENTS.md", "NESTED_PRIVATE")
        self.write(".mcp.json", json.dumps({"mcpServers": {"example": {
            "command": "SECRET_COMMAND", "args": ["SECRET_ARGUMENT"],
            "env": {"TOKEN": "SECRET_VALUE"}, "url": "SECRET_ENDPOINT",
        }}}))
        self.write("node_modules/example/.mcp.json", "ignore me")
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        report = inventory(self.root)
        output = json.dumps(report)
        for value in ("PRIVATE_INSTRUCTIONS", "NESTED_PRIVATE", "SECRET_COMMAND",
                      "SECRET_ARGUMENT", "SECRET_VALUE", "SECRET_ENDPOINT", "ignore me"):
            self.assertNotIn(value, output)
        paths = [row["path"] for row in report["artifacts"]]
        self.assertIn("packages/api/AGENTS.md", paths)
        self.assertNotIn("node_modules/example/.mcp.json", paths)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        self.assertEqual(report["findings"], [])

    def test_broken_external_and_looping_links_are_not_read(self):
        external = Path(self.temp.name) / "external"
        external.mkdir()
        (external / "config.toml").write_text("SECRET_EXTERNAL", encoding="utf-8")
        (self.root / ".codex").symlink_to(external, target_is_directory=True)
        skills = self.root / ".claude/skills"
        skills.mkdir(parents=True)
        (skills / "broken").symlink_to("missing", target_is_directory=True)
        (skills / "loop").symlink_to("loop", target_is_directory=True)
        original = Path.read_text

        def checked_read(path, *args, **kwargs):
            self.assertTrue(path.resolve().is_relative_to(self.root))
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", checked_read):
            report = inventory(self.root)
        codes = {finding["code"] for finding in report["findings"]}
        self.assertTrue({"external-link-not-read", "broken-link", "unreadable-or-link-loop"} <= codes)
        self.assertNotIn("SECRET_EXTERNAL", json.dumps(report))

    def test_jsonc_duplicate_keys_and_bad_shapes_need_attention(self):
        self.write(".vscode/mcp.json", '{// keep comments\n"servers": {},}')
        self.write(".mcp.json", '{"mcpServers": {}, "mcpServers": {}}')
        self.write(".gemini/settings.json", '{"mcpServers": []}')
        self.write(".cursor/mcp.json", '{"mcpServers": {"bad": null}}')
        self.write(".codex/config.toml", '[mcp_servers.a]\ncommand = "SECRET"\ncommand = "OTHER"')
        report = inventory(self.root)
        codes = {finding["code"] for finding in report["findings"]}
        toml_status = "parse-error" if tomllib else "manual-parse-required-toml-use-python-3.11"
        self.assertTrue({"manual-parse-required-json-or-jsonc", "duplicate-key",
                         "invalid-server-map-shape", "invalid-server-entry-shape",
                         toml_status} <= codes)
        self.assertNotIn("SECRET", json.dumps(report))

    def test_schema_variants_and_valid_aliases(self):
        self.write(".codex/config.toml", '[mcp_servers.docs]\nurl = "https://example.com"')
        self.write("opencode.json", '{"mcp":{"servers":{"docs":{"type":"remote","disabled":true}}}}')
        self.write("packages/legacy/opencode.json", '{"mcp":{"servers":{"type":"local","enabled":false}}}')
        self.write(".agents/skills/review/SKILL.md", "---\nname: review\n---\n")
        self.write(".agents/skills/review/assets/example.bin", "asset")
        dest = self.root / ".claude/skills"
        dest.mkdir(parents=True)
        (dest / "review").symlink_to("../../.agents/skills/review", target_is_directory=True)
        report = inventory(self.root)
        expected = [] if tomllib else [{"path": ".codex/config.toml", "code": "manual-parse-required-toml-use-python-3.11"}]
        self.assertEqual(report["findings"], expected)
        containers = {r["path"]: r.get("container") for r in report["artifacts"]}
        if tomllib:
            self.assertEqual(containers[".codex/config.toml"], "mcp_servers")
        self.assertEqual(containers["opencode.json"], "mcp.servers")
        self.assertIn("possible V1", containers["packages/legacy/opencode.json"])
        self.assertEqual(len(report["potential_skill_collisions"]), 1)
        self.assertEqual(inventory(self.root), report)

    def test_non_json_constants_and_non_object_roots(self):
        self.write(".mcp.json", '{"mcpServers": NaN}')
        self.write("opencode.json", "[]")
        codes = {finding["code"] for finding in inventory(self.root)["findings"]}
        self.assertIn("manual-parse-required-json-or-jsonc", codes)
        self.assertIn("invalid-root-shape", codes)

    def test_copilot_bare_maps_and_gemini_non_mcp_settings(self):
        self.write(".github/mcp.json", '{"docs":{"type":"http","url":"SECRET_ENDPOINT"}}')
        self.write(".gemini/settings.json", '{"context":{"fileName":"AGENTS.md"},"theme":"Default"}')
        report = inventory(self.root)
        self.assertEqual(report["findings"], [])
        rows = {row["path"]: row for row in report["artifacts"]}
        self.assertIn("bare server map", rows[".github/mcp.json"]["container"])
        self.assertEqual(rows[".gemini/settings.json"]["servers"], [])
        self.assertNotIn("SECRET_ENDPOINT", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
