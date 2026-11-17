# Project compatibility reference

Last verified: **2026-11-17**. Recheck selected clients on each use. These are local
project defaults; cloud agents, enterprise policy, remote hosts, feature flags,
and older versions can differ. A path listed for one surface does not establish
support for another.

## Discovery matrix

| Client / surface | Project instructions | Project skill directories | Project MCP |
| --- | --- | --- | --- |
| Codex CLI / IDE | `AGENTS.md`; check `AGENTS.override.md` and configured fallback names | `.agents/skills`, from launch directory up to repo root | `.codex/config.toml`, `mcp_servers` tables; trusted projects |
| Claude Code local | `CLAUDE.md`; conditional native `AGENTS.md` in v2.1.277+ | `.claude/skills` | `.mcp.json`, `mcpServers` |
| Cursor | `AGENTS.md`; scoped `.cursor/rules/*.mdc` | `.agents/skills`, `.cursor/skills`; compatibility `.claude/skills`, `.codex/skills` | `.cursor/mcp.json`, `mcpServers` |
| Gemini CLI | `GEMINI.md`, configurable `context.fileName` | `.agents/skills`, `.gemini/skills` | `.gemini/settings.json`, `mcpServers` |
| Copilot CLI | `AGENTS.md`, `.github/copilot-instructions.md`, scoped `.github/instructions` | `.agents/skills`, `.github/skills`, `.claude/skills` | `.mcp.json` or `.github/mcp.json`, `mcpServers` or bare server map; folder trust required |
| VS Code Copilot harness | Verify instruction support for selected harness | Current UI docs illustrate `.github/skills`; CLI docs verify `.agents/skills`; confirm actual harness discovery before adding aliases | Root `.mcp.json`, `mcpServers`; editor forwarding is a separate mechanism |
| VS Code legacy Local harness | Editor instruction settings and scoped instruction files | `.github/skills`, `.agents/skills`, `.claude/skills` | `.vscode/mcp.json`, `servers`; editor-only fields |
| OpenCode V2 | `AGENTS.md`; no `CLAUDE.md` fallback | `.agents/skills`, `.opencode/skills`, `.claude/skills` | `opencode.json` / `opencode.jsonc`, `mcp.servers` |

The two Copilot surfaces and legacy Local row are distinctions within the GitHub
Copilot target, not additional agents to configure automatically.

## Instructions and skill caveats

- **Codex:** ancestor scope, per-directory override selection, configured limits,
  and fallback names matter. Symlinked skill folders are supported; duplicate
  skill names are not merged. [Instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
  [skills](https://learn.chatgpt.com/docs/build-skills).
- **Claude Code:** default native `AGENTS.md` loading requires v2.1.277+ and no
  applicable `CLAUDE.md` / `CLAUDE.local.md`; settings or disabled built-in plugins
  can change this. A `CLAUDE.md` with `@AGENTS.md` is a documented compatibility
  import, including for older clients. `.agents/skills` is not a documented skill
  discovery location here. Per-skill symlink folders are supported; inspect name
  precedence and client-specific frontmatter. [Memory and AGENTS.md](https://code.claude.com/docs/en/memory),
  [skills](https://code.claude.com/docs/en/skills).
- **Cursor:** shared paths already work; do not add every historical alias. Keep
  scoped rule globs rather than flattening them into global guidance.
  [Skills](https://cursor.com/docs/skills), [rules](https://cursor.com/docs/rules).
- **Gemini:** `.agents/skills` wins over `.gemini/skills` within the same tier.
  Set `context.fileName` to include `AGENTS.md`, or use a native `GEMINI.md` import.
  Preserve existing context names to avoid dropping guidance.
  [Skills](https://geminicli.com/docs/cli/skills/),
  [context names and imports](https://geminicli.com/docs/cli/gemini-md/).
- **Copilot:** distinguish CLI, selected VS Code harness, and GitHub cloud agent.
  Do not apply one surface's table or editor settings to all of them.
  CLI combines instruction sources without a general precedence order and supports
  repository-local `@path` imports in documented instruction file types.
  [CLI skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills),
  [CLI instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions),
  [VS Code skills by harness](https://code.visualstudio.com/docs/agent-customization/agent-skills).
- **OpenCode:** V2 natively searches compatibility skill paths; custom directories
  use a `skills` array. V1 behavior and schema differ. Do not upgrade a V1 project
  just to share a skill. [Skills](https://opencode.ai/docs/skills/),
  [instructions](https://opencode.ai/docs/instructions/). For installed V1 clients,
  start with the [versioned V1 docs](https://opencode.ai/v1/docs/mcp-servers/) and
  confirm the minor version before adapting configuration.

## MCP adapters

These field mappings are starting points, not full schema converters. Recheck
unlisted fields and supported environment expansion locations before rendering.

| Target | Stdio | Streamable HTTP | Environment / credentials |
| --- | --- | --- | --- |
| Codex | `command` string, `args` array, optional `cwd` | `url`; `http_headers`, `env_http_headers` | `env_vars` forwards stdio variables; `bearer_token_env_var` names a token variable. Do not copy `${NAME}` into TOML expecting generic expansion. |
| Claude Code | `type: stdio`, `command`, `args` | `type: http`, `url`, `headers` | `${NAME}` / `${NAME:-default}` in documented fields |
| Cursor | `command`, `args` | `url`, `headers`; preserve documented transport selection | `${env:NAME}` and other Cursor variables only where supported |
| Gemini CLI | `command`, `args`, optional `cwd` | **`httpUrl`**; `url` means legacy SSE | `env` supports `$NAME` / `${NAME}`; check field-specific expansion |
| Copilot runtime | `type: stdio`, `command`, `args` | `type: http`, `url`, `headers` | `${NAME}`; preserve `tools` selection and supported OAuth fields |
| VS Code Local | `type: stdio`, `command`, `args` | `type: http`, `url`, `headers` | `${env:NAME}` / `${input:id}`; root `inputs`, `envFile` are editor features |
| OpenCode V2 | `type: local`, `command` **array**, `environment` | `type: remote`, `url`, `headers` | `{env:NAME}`; `disabled: true` prevents connection |

Primary MCP references:

- [Codex](https://learn.chatgpt.com/docs/extend/mcp?surface=cli): project trust and
  environment-backed fields; client configuration is TOML.
- [Claude Code](https://code.claude.com/docs/en/mcp): project `.mcp.json` differs
  from local/user storage in `~/.claude.json`; preserve scope and trust behavior.
- [Cursor](https://cursor.com/docs/mcp): configuration and variable interpolation.
- [Gemini CLI](https://geminicli.com/docs/tools/mcp-server/): `httpUrl` versus `url`,
  tool filtering, and millisecond timeouts. Do not turn on `trust` while converting.
- [VS Code MCP reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration):
  native Copilot root `.mcp.json` differs from editor `servers` format. Current
  docs deprecate Local, with removal planned for February 2027. Native Copilot
  doesn't support editor `inputs`, `envFile`, `dev`, or per-server sandbox fields.
  Forwarding eligible editor definitions is not file migration. A shared
  `.mcp.json` between Claude and Copilot still needs field-by-field verification.
- [Copilot CLI MCP](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers):
  walks from working directory to repo root; `.mcp.json` beats `.github/mcp.json`
  at the same level, nearer definitions beat ancestors. It does not read editor
  `.vscode/mcp.json`. Examples also use `type: local` for stdio; verify accepted
  transport spellings for the installed CLI when sharing a file with VS Code.
- [OpenCode V2](https://opencode.ai/docs/mcp-servers/): servers live under
  `mcp.servers`; use `disabled`, not V1's `enabled`. Check installed major version
  before editing. Do not assume OAuth state transfers between clients.

## Ecosystem practice and design inference

[Agent Skills](https://agentskills.io/specification) standardizes skill packages
and core metadata; it does not standardize every client's discovery, invocation,
or MCP configuration. Preserve complete packages and relative resource paths.

[Vercel skills](https://github.com/vercel-labs/skills) and its
[agent destinations](https://github.com/vercel-labs/skills/blob/main/docs/agents.md),
plus [Microsoft APM's targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/),
show convergence on `.agents/skills` with adapters for client-specific locations.
Use an existing installer/lockfile when appropriate; do not independently rewrite
its managed files or introduce a second competing generator.

Our engineering recommendation from these sources: share content once, prefer
native discovery, add only necessary adapters, and track drift for generated
copies. This is a design choice, not a cross-vendor guarantee. Full-folder
symlinks need platform/client validation; MCP files with different schemas should
be rendered separately rather than linked to one raw file.
