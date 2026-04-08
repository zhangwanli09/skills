# skills

A Claude Code plugin providing reusable skills for AI-assisted development workflows.

## Overview

This repository is a [Claude Code](https://claude.ai/code) plugin. It packages skills, commands, and agents that extend Claude Code's capabilities across projects.

## Plugin Contents

### Skills

| Skill | Description |
|-------|-------------|
| [example-skill](./skills/example-skill/SKILL.md) | Template demonstrating the standard skill structure |
| [init-nextjs](./skills/init-nextjs/SKILL.md) | Initialize a new Next.js app with Prettier and pre-commit git hooks |

### Commands

*Add `.md` files to `commands/` to create slash commands.*

### Agents

*Add `.md` files to `agents/` to create specialized agents.*

## Development

See [CLAUDE.md](./CLAUDE.md) for the full contributor guide, including how to create new skills, commands, and agents.

### Quick Start: Add a New Skill

```bash
cp -r skills/example-skill skills/my-new-skill
# Edit skills/my-new-skill/SKILL.md with your skill's name, description, and instructions
```

## Repository

- GitHub: https://github.com/zhangwanli09/skills
- Author: zhangwanli
- License: MIT
