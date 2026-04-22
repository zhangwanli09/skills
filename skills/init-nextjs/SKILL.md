---
name: init-nextjs
description: Initialize a new Next.js app with Prettier and a pre-commit hook. Use whenever the user wants to create, scaffold, or start a new Next.js project.
---

# Initialize a New Next.js App

Ask for the project name if not given, then run the phases in order. All `@latest` tags resolve to current stable at install time — no doc lookups.

## 1. Create
```bash
npx create-next-app@latest <name> --yes
cd <name>
```

## 2. Prettier
```bash
npm i -D prettier eslint-config-prettier
```
- Write `.prettierrc` → `{}`
- In `eslint.config.mjs`, append `"prettier"` to the end of the extends array.

## 3. Husky + lint-staged
```bash
npm i -D husky lint-staged
npx husky init
```
- Overwrite `.husky/pre-commit` with: `npx lint-staged`
- Add to `package.json`: `"lint-staged": { "*": "prettier --ignore-unknown --write" }`

## 4. Verify
Run `npx prettier --write .` and `npm run lint`. Fix any errors before declaring success. Tell the user the project path and that commits now auto-format.
