---
name: example-skill
description: A template skill demonstrating the standard SKILL.md format. Use this as a starting point when creating new skills in this plugin project.
version: 1.0.0
---

# Example Skill

This skill is a reference template. Copy this directory and customize `SKILL.md` to create a new skill.

## When to Use

Invoke this skill when you need a starting point for building a new skill in this plugin project.

## Instructions

1. Copy the `skills/example-skill/` directory to `skills/your-skill-name/`.
2. Open `skills/your-skill-name/SKILL.md`.
3. Update the frontmatter: `name`, `description`, and `version`.
4. Replace the body of this file with the actual instructions for your skill.

## Notes

- Keep the frontmatter YAML valid at all times.
- The `description` field is what Claude Code uses to decide when to invoke this skill — write it as a clear "when to use" statement.
- Each skill lives in its own subdirectory under `skills/` with exactly one `SKILL.md`.
- Optional subdirectories: `references/` (docs), `examples/` (code samples), `scripts/` (helper scripts), `assets/` (data files).
