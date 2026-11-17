---
name: agent-config-sync
description: Audit and synchronize project-level coding agent instructions, skills, and MCP configuration across Codex, Claude Code, Cursor, Gemini CLI, GitHub Copilot, and OpenCode. Use when a project needs cross-agent compatibility, shared AGENTS.md or SKILL.md discovery, migration from agent-specific directories, MCP format conversion, or detection and repair of configuration drift. Also trigger for requests to check or sync AI coding tool setup across editors and CLIs.
---

# Synchronize project agent configuration

Make the requested agents discover the same project guidance, reusable skills,
and intended MCP services while preserving client-specific behavior. Work in the
target repository, not in this skill's installation directory.

Use [the compatibility reference](references/compatibility.md) to select adapters
and primary documentation. Its verification date is a research snapshot, not a
promise about the user's installed clients. Read
[the synchronization recipes](references/sync-recipes.md) before editing.

## 1. Establish scope and inspect

- Resolve the target project, repository root, working directory, applicable
  instructions, and existing uncommitted changes. Honor the user's requested
  agents and mode: **check** is read-only; **sync/fix** authorizes the necessary
  reversible project edits. If mode is unclear, inspect and propose a concrete
  patch before asking. Do not add a new approval step to an authorized sync.
- If no Git root exists, record each client's project-root assumptions; static
  subdirectory inspection does not establish runtime ancestor discovery.
- If targets are unspecified, infer them from tracked configuration and project
  docs; ask a short optional question while continuing the inspection. Do not
  create adapters for every supported agent merely because they are supported.
- Record versions and surfaces where available: CLI, editor extension, VS Code
  harness (Copilot, Claude, Codex, legacy Local), local versus remote/cloud host,
  operating systems, trust settings, disabled skills, and custom discovery paths.
  Missing clients mean runtime behavior is unverified, not broken.
- Inspect project files first. Include nested scopes and ancestor instructions
  that affect the launch directory. Do not copy personal/global credentials or
  settings into the project. Inspect global discovery overrides only when needed
  to explain behavior; do not modify them unless requested.

Optionally run the bundled inventory with Python 3.9+ (standard library only;
use 3.11+ to parse TOML, otherwise it is marked for manual inspection):

```bash
python3 <skill-dir>/scripts/audit_config.py /path/to/project
```

Replace `<skill-dir>` with this skill's actual installed directory. The script
prints JSON containing paths, MCP field names, and structural findings; it never
prints command arguments, endpoint URLs, environment values, or file contents.
It does not launch clients or servers or write files. Exit 1 means structural
findings require attention; exit 2 means usage or project access failed.

Treat this as an inventory, not a client validator. JSONC is marked for manual
parsing, custom discovery directories need separate inspection, and equal skill
folder names are only potential collisions. The report records external or
broken links without reading their targets. Use client documentation to determine
which listed artifacts actually load, and read contents selectively without
exposing secrets.

## 2. Verify current behavior

Consult official docs for the selected clients before choosing paths or schemas.
Prefer docs matching the installed version; examine changelogs or source when a
current page differs from that version. Record URL, verification date, version or
surface, and uncertainty for each material compatibility decision.

Community installers and package managers are useful evidence for layout and
drift management, but their destination tables do not establish client behavior.
When offline, use the dated reference as provisional evidence, prepare safe edits
where justified, and label unresolved runtime or schema assumptions explicitly.

Check three independent layers:

| Layer | Questions |
| --- | --- |
| Instructions | Is the entry file loaded? How do imports, ancestor files, nested scope, overrides, globs, and size limits work? |
| Skills | Which directories load? Are entire skill packages reachable? Do duplicate names shadow each other? Are frontmatter, substitutions, tools, and invocation controls equivalent? |
| MCP | Which project file and root key apply? Are transport, arguments, working directory, environment expansion, auth, tool filters, timeouts, and enablement equivalent? |

Do not equate a Markdown link with a native instruction import. Do not infer
support for hooks, slash commands, subagents, permissions, or plugin manifests
from support for SKILL.md. Report those separately if encountered.

## 3. Choose a source and compatibility plan

Prefer a single authoritative source per artifact:

- **Instructions:** keep established project guidance; for a new shared setup,
  prefer `AGENTS.md` and the smallest verified native imports or configuration
  adapters. Preserve nested rules in their original scope.
- **Skills:** preserve an existing authoritative directory if it already serves
  the targets. For a new multi-agent setup, prefer `.agents/skills/<name>/`.
  A repository's distribution directory such as `skills/` is not automatically a
  runtime discovery location. Add only adapters needed by actual clients.
- **MCP:** reuse an existing maintained definition source and render client
  configuration semantically. There is no universally discovered MCP config
  filename or interchangeable client schema. If an internal manifest is useful,
  document its generator and adapters; do not imply clients read it directly.

List each proposed path, source, operation, and reason. Surface conflicting
authorship or behavior before overwriting anything. Resolve routine choices from
the user's intent; ask only for a material decision that evidence cannot settle.

Prefer native shared discovery over aliases. Use relative, repository-contained
per-skill symlinks only when the client and team platforms support them. For
Windows or environments that do not preserve symlinks, use documented full-folder
copies with a deterministic sync/check command and recorded content hashes.

## 4. Apply the authorized sync

Follow the recipes, merge narrowly, and preserve unrelated fields, comments,
formatting, and user edits. Inspect a link's target before writing; never replace
an existing directory with a link or edit outside the project through a link.

For generated copies, record the source, destination, owning generator, and last
generated hash in the project's existing metadata convention (or a small
documented manifest). Compare current destination hash to that baseline before
regenerating; preserve and report local divergence. Track removed source files
as explicit stale outputs rather than silently deleting user content. A second
sync with unchanged input must produce no diff.

Keep secrets as client-supported environment references, secret inputs, or local
authentication. Never paste resolved tokens into files, reports, diffs, or logs.
Preserve disabled services and existing restrictions. Unsupported fields require
an explicit unresolved item or a separately documented equivalent, not silent
dropping or broader auto-approval. Do not start servers, authenticate, install
packages, or make service calls merely to inspect configuration.

## 5. Verify and report

- Parse changed JSON/JSONC/TOML using a suitable parser; do not strip JSONC comments
  with regular expressions. Catch duplicate keys. Keep comments when editing.
- Re-run inventory, resolve relative links from their containing directory, check
  whole skill packages and references, and compare the intended MCP semantics
  across all generated adapters. Verify from the project's normal launch paths,
  including any relevant monorepo subdirectory.
- Inspect the diff for lost content, secrets, accidental global edits, weakened
  restrictions, and unrelated changes. Repeat synchronization to check idempotence.
- Where available, inspect each client's loaded instruction/skill UI or documented
  discovery diagnostics without invoking an action skill. Distinguish file
  parsing, discovery, connection, authentication, and an actual tool call. Run
  connection checks only when the request includes them; they can start processes
  or contact services. Do not claim runtime success for absent clients.

Respond in the user's language with: targets and versions; findings by layer;
chosen sources and changed paths; validation completed; remaining conflicts or
unverified behavior; and the repeatable sync/check command for generated copies.
Include primary-source links next to version-sensitive conclusions. In check
mode provide concrete fixes without changing the project.
