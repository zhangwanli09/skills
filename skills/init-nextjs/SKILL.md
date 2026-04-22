---
name: init-nextjs
description: Initialize a new Next.js application with Prettier and git hooks (pre-commit). Use this skill whenever the user wants to create a new Next.js project, scaffold a Next.js app, set up a new Next.js codebase, or initialize a new web app with Next.js — even if they just say "new nextjs project", "scaffold a nextjs app", "start a nextjs project", or "help me init nextjs".
---

# Initialize a New Next.js App

This skill sets up a new Next.js project with official defaults, then adds Prettier formatting and a pre-commit git hook. The command sequence is fixed — execute the phases in order without looking anything up.

All `@latest` tags resolve to the current stable release at install time, so no doc lookups are needed.

---

## Phase 1: Create the Next.js App

Ask the user for the project name if not already provided. Then run:

```bash
npx create-next-app@latest <name> --yes
cd <name>
```

`--yes` accepts all create-next-app defaults non-interactively. Do not prompt the user for framework options.

---

## Phase 2: Add Prettier

1. Install dependencies:
   ```bash
   npm install --save-dev --save-exact prettier
   npm install --save-dev eslint-config-prettier
   ```
2. Create `.prettierrc` with contents `{}` (use all Prettier defaults — do not ask the user for preferences).
3. Create `.prettierignore` with at least:
   ```
   .next/
   node_modules/
   package-lock.json
   ```
4. Wire `eslint-config-prettier` into the generated ESLint config:
   - If the project has `eslint.config.mjs` (Next.js 15+ flat config), append `"prettier"` to the end of the extends array.
   - If the project has the legacy `.eslintrc.json`, append `"prettier"` to the end of its `extends` array.

   The `prettier` entry must come last so it can disable conflicting rules from earlier configs.

---

## Phase 3: Set Up Git Hooks (Husky + lint-staged)

1. Install dependencies:
   ```bash
   npm install --save-dev husky lint-staged
   ```
2. Initialize Husky:
   ```bash
   npx husky init
   ```
   This creates `.husky/pre-commit` and adds a `"prepare": "husky"` script to `package.json`.
3. Replace the contents of `.husky/pre-commit` with a single line:
   ```
   npx lint-staged
   ```
4. Add the lint-staged config to `package.json`:
   ```json
   "lint-staged": { "*": "prettier --ignore-unknown --write" }
   ```

---

## Phase 4: Verify

1. Format existing files:
   ```bash
   npx prettier --write .
   ```
2. Run the linter to confirm no ESLint/Prettier conflicts:
   ```bash
   npm run lint
   ```
3. Report and fix any issues before declaring success.

---

## Wrap Up

Tell the user:
- Where the project lives
- That every `git commit` will now auto-format staged files
