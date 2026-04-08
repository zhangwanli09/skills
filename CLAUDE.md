# Claude Code Plugin Project Guide

This repository is a **Claude Code plugin** — a structured collection of skills, commands, agents, and hooks that extend Claude Code's capabilities.

## Project Structure

```
skills/                          # repo root
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (name, version, author, repo)
├── commands/                    # Slash commands (*.md files)
├── agents/                      # Specialized AI agents (*.md files)
├── skills/                      # Reusable agent skills
│   └── <skill-name>/
│       └── SKILL.md             # Required — one per skill
├── hooks/
│   └── hooks.json               # Hook configuration
├── CLAUDE.md                    # This file
└── README.md                    # Project documentation
```

## Creating a New Skill

1. Create a new directory: `skills/<your-skill-name>/`
2. Create `skills/<your-skill-name>/SKILL.md` with this format:

```markdown
---
name: Your Skill Name
description: When Claude Code should invoke this skill (be specific and use "when to use" phrasing)
version: 1.0.0
---

# Your Skill Name

## When to Use
...

## Instructions
...
```

3. Use `skills/example-skill/SKILL.md` as a reference template.
4. Bump the plugin `version` in `.claude-plugin/plugin.json` after adding skills.

### Optional Skill Subdirectories

| Directory | Purpose |
|-----------|---------|
| `references/` | Supporting reference documentation |
| `examples/` | Executable code examples |
| `scripts/` | Helper scripts and utilities |
| `assets/` | Data files, templates, configuration |

## Creating a New Command

Add a `*.md` file to `commands/`. The filename becomes the slash command name (e.g., `commands/deploy.md` → `/deploy`).

```markdown
---
description: Brief description of what the command does
argument-hint: [arg1] [arg2]
allowed-tools: Read, Bash(git:*), Edit
---

Command prompt text. Use $ARGUMENTS for user-provided arguments.
```

## Creating a New Agent

Add a `*.md` file to `agents/`. Each file defines the agent's persona, instructions, and scope.

## Versioning Convention

Follows [Semantic Versioning](https://semver.org/):
- **Patch** (`1.0.x`): Fix typos, clarify instructions in existing skills
- **Minor** (`1.x.0`): Add a new skill, command, or agent
- **Major** (`x.0.0`): Breaking restructuring or removal of existing skills

Update `.claude-plugin/plugin.json` version on every meaningful change.

## Key Conventions

- Every skill **must** have a `SKILL.md` at the root of its directory.
- The frontmatter `description` field is the routing trigger — write it as a precise "when to use" statement.
- Keep each skill focused on a single responsibility.
- Document any external dependencies in the skill's `SKILL.md` under a `## Dependencies` section.
