---
name: init-nextjs
description: Initialize a new Next.js application with Prettier and git hooks (pre-commit). Use this skill whenever the user wants to create a new Next.js project, scaffold a Next.js app, set up a new Next.js codebase, or initialize a new web app with Next.js — even if they just say "new nextjs project", "scaffold a nextjs app", "start a nextjs project", or "help me init nextjs".
---

# Initialize a New Next.js App

This skill sets up a new Next.js project with the latest official recommended defaults, then adds Prettier formatting and a pre-commit git hook.

**Important**: Before executing any step, always fetch the latest documentation using the context7 MCP tool (or web search as fallback). The commands, flags, and config formats for these tools evolve over time — never rely on memorized defaults.

---

## Phase 0: Research Latest Docs (always do this first)

Before writing a single command, look up the current recommended setup for each tool. Run these lookups in parallel:

1. **create-next-app** — fetch `/vercel/next.js` from context7, query "create-next-app CLI flags skip prompts installation". Find the current recommended command to create a project non-interactively with official defaults.

2. **Prettier** — fetch `/websites/prettier_io` from context7, query "prettier installation configuration setup". Find the current install command and recommended `.prettierrc` setup.

3. **Husky** — fetch `/typicode/husky` from context7, query "husky installation setup pre-commit hook". Find the current init command, how to create a pre-commit hook, and confirm the current recommended way to write the pre-commit hook file content.

4. **lint-staged** — fetch `/lint-staged/lint-staged` from context7, query "lint-staged recommended setup with prettier". Find the current install, recommended configuration format, and how to wire it with Husky.

5. **eslint-config-prettier** — check whether it's still the recommended way to prevent ESLint/Prettier conflicts in a Next.js project.

---

## Phase 1: Create the Next.js App

Ask the user for the project name if not already provided.

Using the command found in Phase 0, create the app non-interactively with official recommended defaults (skip all prompts). Then `cd` into the project directory.

---

## Phase 2: Add Prettier

Using the setup steps found in Phase 0:

1. Install Prettier (and eslint-config-prettier if still recommended) as dev dependencies.
2. Create an empty `.prettierrc` (`{}`) to use all Prettier defaults — do not ask the user for preferences.
3. Update the ESLint config to disable rules that conflict with Prettier (inspect the existing ESLint config format in the generated project first, then extend it correctly).

---

## Phase 3: Set Up Git Hooks (Husky + lint-staged)

Using the setup steps found in Phase 0:

1. Install Husky and lint-staged as dev dependencies.
2. Initialize Husky.
3. Create the pre-commit hook file using the current recommended format confirmed in Phase 0 — it should run lint-staged.
4. Configure lint-staged using the wildcard pattern with `--ignore-unknown` flag:
   ```json
   { "*": "prettier --ignore-unknown --write" }
   ```

---

## Phase 4: Verify

1. Run Prettier over all existing files to format them from the start.
2. Run the project's linter to confirm no ESLint/Prettier conflicts.
3. Report and fix any issues before declaring success.

---

## Wrap Up

Tell the user:
- Where the project lives
- That every `git commit` will now auto-format staged files
