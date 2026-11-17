# Synchronization recipes

Apply these to the user's selected project and supported client versions. Keep
existing canonical locations when they work; migration is not a prerequisite.

## Shared instructions

1. Identify common guidance and client-specific instructions. Resolve conflicts
   without changing their scope. Keep nested `AGENTS.md`, scoped Cursor rules,
   and Copilot `applyTo` rules local to the code they govern.
2. For a new shared setup, write common guidance in `AGENTS.md`. Codex and Cursor
   can discover it natively. Verify Copilot's chosen surface and OpenCode version.
3. For Claude, first check native conditional loading. Where an adapter is needed,
   add `@AGENTS.md` to a root `CLAUDE.md`, retaining Claude-specific text. If a
   wrapper lives in `.claude/CLAUDE.md`, its import must instead be `@../AGENTS.md`.
4. For Gemini, merge `AGENTS.md` into the existing `context.fileName` string/list
   in `.gemini/settings.json`, or add `@./AGENTS.md` to root `GEMINI.md`. Choose
   one mechanism; preserve existing context and avoid loading shared text twice.
5. When native imports are unavailable, render shared text into a clearly marked
   generated section of the client's real instruction file. A link saying
   “read AGENTS.md” alone does not prove automatic inclusion.

Use an import before a symlink for instruction wrappers on mixed Windows teams.
Never make `AGENTS.md` import its own wrapper. Recheck ancestor files and native
deduplication before concluding that both entries produce duplicate context.

## Shared skills

For a new setup, place whole skill directories at `.agents/skills/<name>/`.
Codex, Cursor, Gemini CLI, Copilot CLI, and OpenCode V2 document native discovery
there. For VS Code, confirm the selected harness rather than inferring discovery
from the editor or CLI name.

Claude Code needs `.claude/skills/<name>/`. If relative symlinks are appropriate,
the link target from that directory entry is `../../.agents/skills/<name>`:

```text
.agents/skills/review/SKILL.md       # authoritative package
.agents/skills/review/references/...
.claude/skills/review -> ../../.agents/skills/review
```

If the existing source is `.claude/skills`, a Codex adapter in
`.agents/skills/<name>` can instead point to `../../.claude/skills/<name>`.
Resolve paths from the link's parent. Do not create reciprocal links or replace
directories containing existing edits. Check per-skill symlinks with the actual
clients; do not infer whole-parent-directory symlink support.

For Windows or copy-based delivery:

- Use the project's package manager/sync tooling if it already owns skills.
- Otherwise add a small project sync/check script and manifest. Hash sorted
  relative filenames plus file bytes (including binary assets); document any
  exclusions and never exclude runtime resources accidentally. Do not follow
  external symlinks. Preserve executable-bit intent where supported and document
  platform normalization; content equality alone cannot prove a script remains
  executable. Hashing just `SKILL.md` misses drift in scripts and assets.
- Record source, destination, last generated hash, and generator ownership.
  No existing baseline means an existing differing destination needs review.
- On sync, update only owned destinations whose current hash equals the baseline.
  A conflicting edit stays intact and is reported. In check mode return a nonzero
  status for stale generated content; in sync mode a second run changes nothing.
- Handle added/removed resources deliberately. Remove a stale owned resource
  only when its previous generated hash still matches and deletion is authorized.

Portability review extends beyond location: client-specific frontmatter such as
`context: fork`, invocation restrictions, hooks, shell expansion, placeholders,
or tool names may not carry across. Preserve the common workflow and document
unsupported behavior or separate adapters. Never silently turn a manual-only
workflow into an automatically invoked one.

## MCP conversion procedure

Do not build a universal JSON symlink. Read the selected reference and each
client's schema. For every intended server, keep a temporary semantic inventory:

```text
identity / source / target clients
transport (stdio | streamable-http | legacy-sse)
executable + ordered arguments / endpoint
working-directory base + path requirements
environment variable names / secret references / authentication method
enabled state / tool allow-deny policy / timeouts with units
client-only fields and unresolved mappings
```

1. Establish the maintained source from current files and user intent; do not
   choose the first file discovered as authoritative. Treat conflicting same-name
   definitions as a decision to resolve, not as a last-file-wins merge.
2. Render only supported fields. Split an OpenCode command array into executable
   plus ordered arguments for string-command clients, and join as an array in the
   opposite direction; never use a shell-joined string or execute it. Preserve
   quoting as argument boundaries. Verify relative `cwd` semantics on each host.
3. Map transport explicitly. For example, a Claude `type: http`/`url` becomes a
   Gemini `httpUrl`, not Gemini `url`. A legacy SSE endpoint cannot be converted
   into HTTP by renaming the field. Mark unsupported transports unresolved.
4. Translate credential references, not resolved values. For a Codex bearer token,
   use `bearer_token_env_var = "SERVICE_TOKEN"`; don't serialize
   `"${SERVICE_TOKEN}"` as the token. Use current documented expansion for other
   clients. Keep OAuth login state local and independent.
5. Preserve disabled state, tool filters, approvals, sandboxing, and timeout units.
   If the destination has no equivalent, leave that server unconfigured there
   and report the exact limitation rather than weakening its behavior. Explicit
   user intent may authorize a different equivalent design; document it.
6. Merge server entries into native containers (`mcp_servers`, `mcpServers`,
   `servers`, or V2 `mcp.servers`). Preserve unrelated settings and comments.
   VS Code input prompts, env files, and sandbox settings do not become portable
   Copilot fields just by changing the root object name.
7. Parse and compare semantics again, then repeat rendering for idempotence.
   Parsing success alone does not prove client discovery, login, or connectivity.

## Repeatable handoff

For a project that needs repeated synchronization, leave the actual source and
generator documented in its established contributor docs. Include commands for
check, sync, conflict recovery, and the expected launch directory. Respect an
existing installer lockfile and CI workflow rather than competing with them.

Report each layer separately as verified, changed, conflict, unsupported, or
unverified. Include the paths, source links/date, and runtime checks still needed.
An audit with no known artifacts means “nothing detected in standard locations,”
not “all six clients are compatible.”
