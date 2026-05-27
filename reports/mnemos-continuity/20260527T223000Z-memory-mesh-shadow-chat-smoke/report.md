# Memory mesh shadow chat smoke

Generated: 2026-05-27T22:30:00Z
Branch: `work/mnemos-gate-refresh-origin-main-20260527T191822Z`
Status: **PASS**

## Scope

Ember approved `YES MEMORY MESH SHADOW CHAT SMOKE — NO DEFAULT GATEWAY`.

This rung launched bounded non-interactive Hermes chat under the stopped `mnemos-shadow-ro` profile to verify that the **model-side tool menu** could see Honcho + Enzyme + Holographic together.

Important rails:

- used current worktree source via `python -m hermes_cli.main`, not the globally installed source checkout
- used `--profile mnemos-shadow-ro`
- used provider/model override on the command line only: `--provider openai-codex -m gpt-5.5`
- did not edit default profile config
- did not edit shadow profile config during the chat smoke
- did not restart default gateway
- did not launch an interactive `/goal`; direct one-shot chat was sufficient
- instructed model not to call tools, retrieve memory, or store memory

## Commands exercised

Both smoke calls used:

```bash
python -m hermes_cli.main --profile mnemos-shadow-ro chat \
  --provider openai-codex \
  -m gpt-5.5 \
  --toolsets memory \
  --max-turns 1 \
  -Q \
  -q "..."
```

## Result

Two one-shot chat smokes passed:

1. **Guided smoke** — asked model to list exact expected memory tools from its tool menu.
2. **Blind smoke** — did not list the expected names in the prompt; asked for memory-related tool names visible from the tool menu.

The blind smoke returned all eight expected memory tools:

- `functions.honcho_profile`
- `functions.honcho_search`
- `functions.honcho_reasoning`
- `functions.honcho_context`
- `functions.honcho_conclude`
- `functions.enzyme_search`
- `functions.fact_store`
- `functions.fact_feedback`

Verification normalized those names and confirmed all expected bare tool names were present:

- `honcho_profile`
- `honcho_search`
- `honcho_reasoning`
- `honcho_context`
- `honcho_conclude`
- `enzyme_search`
- `fact_store`
- `fact_feedback`

## Evidence files

- `preflight.txt`
- `pre-hashes.json`
- `prompt.txt`
- `chat-smoke-output.txt`
- `chat-smoke-stderr.txt`
- `chat-smoke-exit-code.txt`
- `blind-prompt.txt`
- `blind-chat-smoke-output.txt`
- `blind-chat-smoke-stderr.txt`
- `blind-chat-smoke-exit-code.txt`
- `session-id.txt`
- `post-hashes.json`
- `gateway-post.txt`
- `gateway-post-2.txt`
- `verify-summary.json`
- `targeted-tests.txt`

## Verification summary

`verify-summary.json` reports:

```json
{
  "guided_exit_code": "0",
  "blind_exit_code": "0",
  "guided_seen_required_count": 8,
  "blind_seen_required_count": 8,
  "blind_all_required_seen": true,
  "default_config_hash_unchanged": true,
  "shadow_config_hash_unchanged_during_chat": true,
  "default_memory_multi_provider_enabled": null,
  "shadow_profile_state": "stopped",
  "shadow_gateway_enabled": false,
  "shadow_cron_enabled": false,
  "memory_tool_call_markers_in_outputs": false,
  "pass": true
}
```

Gateway service timestamp remained:

`ExecMainStartTimestamp=Wed 2026-05-27 12:42:42 PDT`

So no gateway restart occurred during the smoke.

Targeted tests still passed:

`7 passed`

## Interpretation

This proves the mesh is no longer only a provider-manager/internal smoke. A real Hermes chat run under the shadow profile sends the model a memory tool surface containing all three organs:

- Honcho: identity/context/conclusion memory tools
- Enzyme: project/vault semantic search tool
- Holographic: fact store/feedback tools

The model can see all three together when the explicit profile-local `multi_provider_enabled: true` gate is active.

## Negative space

Not done:

- no default config edit
- no default gateway restart
- no default profile mesh activation
- no Mnemos live prompt admission
- no memory tool calls
- no memory store/retrieve action
- no `sync_turn`
- no cron change
- no provider/model config persistence; model override was CLI-only

## Next safe handle

`YES MEMORY MESH SHADOW READONLY TOOL CALLS — NO WRITES`

That would authorize one more shadow-profile smoke where the model may call **read-only** tools only, likely `enzyme_search` and a low-cost Honcho read such as `honcho_profile` or `honcho_context`, but still may not call `fact_store`, `honcho_conclude`, or any write-like tool. It still would not authorize default gateway restart or default profile activation.
