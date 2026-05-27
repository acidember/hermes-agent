# Memory mesh shadow smoke — Honcho + Enzyme + Holographic

Generated: 2026-05-27T21:52:52Z
Updated: 2026-05-27T22:00Z actual-profile config smoke
Branch: `work/mnemos-gate-refresh-origin-main-20260527T191822Z`
Status: **actual stopped profile smoke passed**

## Scope

Ember approved trying the memory mesh in a non-default/shadow shape. This smoke did not use the default gateway and did not edit the default profile.

Because `mnemos-shadow-ro` is intentionally stopped and has `disabled-placeholder` model config, this smoke used an ephemeral shadow `HERMES_HOME` under this report directory instead of launching chat/model inference. The smoke exercised the real provider loader, the new multi-provider resolver, `MemoryManager(allow_multiple_external=True)`, provider initialization, system prompt blocks, and tool schema aggregation.

## Result

Actual stopped-profile smoke passed after applying profile-local config to `/home/ember/.hermes/profiles/mnemos-shadow-ro`:

- profile remains `enabled: false`, `state: stopped`, `default_profile: false`
- gateway remains disabled for the profile
- cron remains disabled for the profile
- resolver returned `['honcho', 'enzyme', 'holographic']`
- all three providers loaded
- all three providers reported available
- all three registered in one `MemoryManager`
- aggregate tool surface contained:
  - `honcho_profile`
  - `honcho_search`
  - `honcho_reasoning`
  - `honcho_context`
  - `honcho_conclude`
  - `enzyme_search`
  - `fact_store`
  - `fact_feedback`

## First attempt finding

The first attempt only registered Holographic. It revealed two practical mesh requirements:

1. **Honcho availability needs credentials in the smoke subprocess.** The shell did not inherit `HONCHO_API_KEY` until the default `.env` was sourced.
2. **User-installed Enzyme must be visible under the active `HERMES_HOME/plugins`.** With an ephemeral profile home, `plugins.memory` did not discover `/home/ember/.hermes/plugins/enzyme` until the plugin was copied into the ephemeral shadow home.

These were smoke harness issues, not provider absence. The second attempt fixed them without default config/gateway changes.

## Shadow config used

The ephemeral shadow config used:

```yaml
memory:
  memory_enabled: false
  user_profile_enabled: false
  provider: honcho
  providers:
    - enzyme
    - holographic
  multi_provider_enabled: true
plugins:
  enzyme:
    injection_mode: tools
    refresh_on_sync: false
  hermes-memory-store:
    auto_extract: false
```

Honcho was configured as tools-only with `initOnSessionStart: false` and `saveMessages: false` for the shadow host, so initialization did not call Honcho tools or intentionally write a conversation turn.

## Evidence

Primary actual-profile evidence:

- `actual-profile-smoke-output.json`
- `post-verify.json`
- `profile-artifact-inventory.json`
- `profile-before/config.yaml`
- `profile-after/config.yaml`
- `profile-after/honcho.json`

Earlier ephemeral-harness evidence retained:

- `smoke-output-2.json`
- `smoke-output.json`

Ephemeral config fixtures retained:

- `shadow-hermes-home/config.yaml`
- `shadow-hermes-home/honcho.json`
- `enzyme-vault/README.md`

Generated DBs and copied plugin source were removed from the report bundle before commit to avoid committing binary/index artifacts or copied user plugin code.

## Verification / negative space

Confirmed by smoke output and follow-up verification:

- `sync_turn_called: false`
- `memory_tool_calls_invoked: false`
- `gateway_restarted: false`
- `default_profile_config_touched: false`
- `honcho_tool_call_or_session_write: false`

Still true for default config:

- default `memory.provider = honcho`
- default `memory.multi_provider_enabled = None`
- default resolver result remains `['honcho']`
- Mnemos remains synthetic: `source=synthetic_shadow_sqlite`, `allow_live_db=False`, `allow_writes=False`

## Interpretation

The all-three memory mesh is now technically plausible behind the explicit gate. The blockers are no longer “provider missing” or “one-provider manager refuses everything”; they are operational policy questions:

- whether Enzyme should be installed/copied/resolved per profile or discovered from a shared plugin source
- whether Enzyme should stay `tools` mode initially to avoid auto-index/auto-injection
- whether Holographic should start empty/tool-only and avoid built-in memory mirroring until approved
- whether Honcho should stay tools-only or hybrid in the mesh profile

## Next safe handle

`YES MEMORY MESH SHADOW CHAT SMOKE — NO DEFAULT GATEWAY`

That would authorize launching one bounded one-shot/CLI chat under the stopped `mnemos-shadow-ro` profile with the disabled placeholder model replaced only if needed for that shadow process, exercising tool visibility from the model side. It still would not authorize default gateway restart, default profile changes, or ambient prompt injection in this chat.
