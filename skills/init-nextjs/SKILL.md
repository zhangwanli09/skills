---
name: init-nextjs
description: Initialize a new Next.js app with Prettier and a pre-commit hook. Use whenever the user wants to create, scaffold, or start a new Next.js project.
---

# Initialize a New Next.js App

Ask for the project name if not given, then run the phases in order. All `@latest` tags resolve to current stable at install time — no doc lookups.

## 1. Create
```bash
npx create-next-app@latest <name> --yes
```

## 2. Prettier
```bash
cd <name> && npm i -D prettier eslint-config-prettier
```
- Write `<name>/.prettierrc` → `{}`
- Read `<name>/eslint.config.mjs`. Add `import eslintConfigPrettier from "eslint-config-prettier/flat";` near the other imports, then append `eslintConfigPrettier` as the last element of the `eslintConfig` array (after the `...compat.extends(...)` spread).

## 3. Husky + lint-staged
```bash
cd <name> && npm i -D husky lint-staged && npx husky init
```
- Overwrite `<name>/.husky/pre-commit` with: `npx lint-staged`
- Add to `<name>/package.json`: `"lint-staged": { "*": "prettier --ignore-unknown --write" }`

## 4. Verify
```bash
cd <name> && npx prettier --write . && npm run lint
```
Fix any errors before declaring success. Tell the user the project path and that commits now auto-format.
