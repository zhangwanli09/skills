#!/usr/bin/env python3
"""Read-only inventory of standard project agent paths; Python 3.9+, no deps.

Only paths, schema/field names and structural statuses are emitted. Configuration
values and parser exception messages are deliberately omitted. This is not a
client schema validator, YAML validator, secret scanner or MCP connection check.
"""

import argparse
import json
import os
from pathlib import Path
import sys
try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None


FILES = {
    "AGENTS.md": "instructions",
    "AGENTS.override.md": "instructions",
    "CLAUDE.md": "instructions",
    "CLAUDE.local.md": "instructions",
    ".claude/CLAUDE.md": "instructions",
    ".claude/AGENTS.md": "instructions",
    "GEMINI.md": "instructions",
    ".github/copilot-instructions.md": "instructions",
    ".cursorrules": "legacy-instructions",
    ".mcp.json": "mcp-json",
    ".github/mcp.json": "mcp-copilot",
    ".cursor/mcp.json": "mcp-json",
    ".gemini/settings.json": "mcp-json",
    ".vscode/mcp.json": "mcp-vscode",
    ".codex/config.toml": "mcp-toml",
    "opencode.json": "mcp-opencode",
    "opencode.jsonc": "mcp-opencode",
}
SKILLS = (
    ".agents/skills", ".claude/skills", ".cursor/skills", ".codex/skills",
    ".gemini/skills", ".github/skills", ".opencode/skills", "skills",
)
RULES = (".cursor/rules", ".claude/rules", ".github/instructions")
CONTAINERS = (".agents", ".claude", ".cursor", ".codex", ".gemini", ".github", ".opencode", ".vscode")
SKIP = {
    ".git", "node_modules", "vendor", ".venv", "venv", "__pycache__",
    "dist", "build", "coverage", ".next", ".cache",
    ".agents", ".claude", ".cursor", ".codex", ".gemini", ".github",
    ".opencode", ".vscode", "skills",
}


class DuplicateKey(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey()
        result[key] = value
    return result


def reject_constant(_value):
    raise ValueError()


def mcp_server_map(config, kind, filename):
    container = {"mcp-toml": "mcp_servers", "mcp-vscode": "servers",
                 "mcp-opencode": "mcp"}.get(kind, "mcpServers")
    servers = config.get(container, {})
    if (filename == ".mcp.json" or kind == "mcp-copilot") and "mcpServers" not in config and config:
        # Bare maps are accepted by Copilot but not every .mcp.json consumer.
        servers = config
        container = "bare server map (verify consuming client)"
    if kind == "mcp-opencode" and isinstance(servers, dict):
        # V1 can legally name a server 'servers'; inspect its entry shape.
        candidate = servers.get("servers")
        if isinstance(candidate, dict) and not isinstance(candidate.get("type"), str):
            servers = candidate
            container = "mcp.servers"
        elif servers:
            container = "mcp (possible V1; verify installed version)"
    return container, servers


def inventory(project):
    root = Path(project).resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError()
    artifacts, findings = [], []

    def relative(path):
        return path.relative_to(root).as_posix()

    def issue(path, code):
        findings.append({"path": relative(path), "code": code})

    def inspect(path, kind):
        """Resolve before reading, including symlinks in parent components."""
        row = {"path": relative(path), "kind": kind}
        try:
            target = path.resolve(strict=True)
            if not target.is_relative_to(root):
                issue(path, "external-link-not-read")
                row["status"] = "external-link-not-read"
            else:
                row["status"] = "present"
                if path.is_symlink():
                    row["target"] = relative(target)
        except FileNotFoundError:
            if not path.is_symlink():
                return None
            issue(path, "broken-link")
            row["status"] = "broken-link"
        except (OSError, RuntimeError):
            issue(path, "unreadable-or-link-loop")
            row["status"] = "unreadable-or-link-loop"
        artifacts.append(row)
        return row

    def config(path, row):
        if path.suffix == ".toml" and tomllib is None:
            row["status"] = "manual-parse-required-toml-use-python-3.11"
            issue(path, row["status"])
            return
        try:
            raw = path.read_text(encoding="utf-8")
            data = (tomllib.loads(raw) if path.suffix == ".toml" else
                    json.loads(raw, object_pairs_hook=unique_object,
                               parse_constant=reject_constant))
        except DuplicateKey:
            row["status"] = "duplicate-key"
            issue(path, row["status"])
            return
        except (ValueError, UnicodeError, OSError):
            # JSONC may be valid for a client; do not claim it is invalid JSONC.
            row["status"] = ("parse-error" if path.suffix == ".toml" else
                             "manual-parse-required-json-or-jsonc")
            issue(path, row["status"])
            return
        if not isinstance(data, dict):
            row["status"] = "invalid-root-shape"
            issue(path, row["status"])
            return
        row["container"], servers = mcp_server_map(data, row["kind"], path.name)
        if not isinstance(servers, dict):
            issue(path, "invalid-server-map-shape")
            row["status"] = "invalid-server-map-shape"
            return
        row["servers"] = []
        for name, entry in sorted(servers.items()):
            if not isinstance(entry, dict):
                issue(path, "invalid-server-entry-shape")
                row["servers"].append({"name": name, "status": "invalid-shape"})
                continue
            # Never include values, even for commands, URLs, or transport type.
            row["servers"].append({"name": name, "fields": sorted(entry)})

    def skill_entries(path, scope):
        try:
            if not path.is_dir():
                issue(path, "expected-directory")
                return
            entries = sorted(path.iterdir())
            for entry in entries:
                if entry.name.startswith("."):
                    continue
                if not entry.is_dir() and not entry.is_symlink():
                    continue
                skill = inspect(entry, "skill-folder")
                if not skill or skill["status"] != "present":
                    continue
                entrypoint = entry / "SKILL.md"
                marker = inspect(entrypoint, "skill-entrypoint")
                if not marker or marker["status"] != "present" or not entrypoint.is_file():
                    issue(entry, "no-readable-skill-entrypoint-or-grouped-directory")
                    continue
                skill["folder_name"] = entry.name
                skill["scope"] = scope
        except OSError:
            issue(path, "unreadable-directory")

    def walk_error(error):
        issue(Path(error.filename), "unreadable-directory")

    for directory, dirs, _files in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(directory)
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not d.startswith("."))
        for folder in CONTAINERS:
            path = base / folder
            if path.is_symlink():
                inspect(path, "linked-config-directory")
        for filename, kind in FILES.items():
            path = base / filename
            row = inspect(path, kind)
            if not row or row["status"] != "present":
                continue
            if not path.is_file():
                issue(path, "expected-file")
            elif kind.startswith("mcp-"):
                config(path, row)
        for folder in SKILLS:
            path = base / folder
            kind = "distribution-skills" if folder == "skills" else "discovery-skills"
            row = inspect(path, kind)
            if row and row["status"] == "present":
                skill_entries(path, relative(base))
        for folder in RULES:
            inspect(base / folder, "scoped-rules")

    groups = {}
    for row in artifacts:
        if "folder_name" in row:
            groups.setdefault((row["scope"], row["folder_name"]), []).append(row["path"])
    collisions = [paths for paths in groups.values() if len(paths) > 1]
    return {
        "scope": "standard project paths, nested scopes; excludes personal config and custom paths",
        "limitations": [
            "No client loading, trust, inheritance, YAML, or connection validation",
            "JSONC and custom skill discovery require separate inspection",
            "Folder-name collisions include intentional aliases; resolve using client precedence",
            "Scoped rule contents and symlinked ordinary subdirectories are not traversed",
        ],
        "artifacts": sorted(artifacts, key=lambda row: row["path"]),
        "potential_skill_collisions": sorted(collisions),
        "findings": sorted(findings, key=lambda row: (row["path"], row["code"])),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    try:
        report = inventory(args.project)
    except (OSError, RuntimeError):
        print("Project directory is unavailable.", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
