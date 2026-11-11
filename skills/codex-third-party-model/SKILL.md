---
name: codex-third-party-model
description: Configure third-party or self-hosted model providers for Codex CLI using isolated named profiles. Use whenever a user asks to add, switch, or troubleshoot a non-default model provider in Codex, including DeepSeek, gateways, compatible APIs, and multiple providers, especially when the default Codex setup must remain unchanged.
---

# Configure a third-party model in Codex

Set up the requested provider as a named Codex profile while preserving the user's existing default configuration. Treat Codex's current official configuration documentation as authoritative for Codex fields and behavior; consult the provider's current official API documentation for endpoint, model IDs, protocol compatibility, authentication, context length, and output limits. If sources conflict, follow Codex documentation for client configuration and state any provider-side uncertainty.

## Workflow

1. **Inspect before editing.** Read the user's existing `~/.codex/config.toml` and any profile files relevant to the requested provider. Never print, copy, or expose API key values. Check Codex CLI version and `codex --help` to confirm profile and config support.
2. **Research current docs.** Use current official Codex docs for profile layering, custom provider fields, and model metadata. Use current official provider docs for model IDs and API details. Do not rely on old integration scripts or copied snippets when they conflict with Codex docs.
3. **Choose the profile approach.** Unless the user asks to change the default, create `~/.codex/<profile>.config.toml`; do not modify `~/.codex/config.toml`. A profile overlays the base config, so include only settings needed for that provider. Select it with `codex --profile <profile>`.
4. **Configure the provider.** Use a unique provider ID and current Codex-supported keys such as `model`, `model_provider`, and `[model_providers.<id>]` with `name`, `base_url`, `env_key`, and `wire_api` as appropriate. Use only a protocol the provider currently supports. Never embed secrets in TOML, shell history, skill files, or command output; refer to a named environment variable for API keys.
5. **Handle model metadata separately from server limits.** Distinguish the provider's API context/output maximum from the context window Codex uses to manage the session. Check Codex's current supported metadata settings, such as `model_context_window` or a custom model catalog, and the provider's current published capabilities. Set context metadata only when verified and useful. Do not claim that a server-side limit automatically informs Codex.
6. **Validate safely.** Run `codex --profile <profile> --strict-config --help` (or the equivalent supported by the installed version) to catch configuration errors. This validates parsing, not API access. Do not make a billable API request unless the user asks to verify connectivity. Avoid editing shell startup files; tell the user which environment variable must be present in the terminal that launches Codex.
7. **Report clearly.** State the profile file path, selected model/provider, protocol and context metadata if configured, launch command, required environment variable, validation performed, and any limitations. Clarify that plain `codex` still uses the default setup.

## Configuration principles

- Keep provider-specific settings in the named profile so default Codex behavior remains unchanged.
- Use profile files named `<profile>.config.toml` in `$CODEX_HOME` (normally `~/.codex`) and invoke with `--profile <profile>`.
- Preserve existing files and user changes. If a requested file already exists, inspect and merge carefully rather than overwrite it.
- Prefer the Codex documentation's currently supported schema over vendor setup scripts. Vendor docs remain useful for API capabilities and model limits.
- Do not add settings just because they appear in an old provider tutorial. Explain optional settings and only add them when the user requests or when required for correct Codex operation.
