# Memory mesh safe seam + Mnemos L1 discovery prerequisite

Generated: 2026-05-27T21:41:42Z

## What changed

Added an inert, backwards-compatible memory-provider selection seam so Honcho can remain active while future Enzyme/Holographic mesh work is explicitly gated.

New code/tests:

- `agent/memory_provider_selection.py`
- `tests/agent/test_memory_provider_selection.py`
- `tests/agent/test_memory_manager_multi_provider.py`
- patched `agent/memory_manager.py` with explicit `allow_multiple_external=False` default
- patched `agent/agent_init.py` to use provider-name resolution and only allow multiple external providers when `memory.multi_provider_enabled: true`

## Important finding

Current config contains both:

```text
memory.provider = honcho
memory.providers = ['enzyme', 'holographic']
memory.multi_provider_enabled = None
```

Before this seam, the list was effectively stale/ignored by the current initialization path. With this seam, it is still ignored by default for safety. Resolution remains:

```text
resolved_provider_names = ['honcho']
```

So the default gateway will not silently wake Enzyme/Holographic on restart.

## Provider reality check

Read-only loader check found:

- `honcho`: loads, available, tools: `honcho_profile`, `honcho_search`, `honcho_reasoning`, `honcho_context`, `honcho_conclude`
- `holographic`: loads, available, tools: `fact_store`, `fact_feedback`
- `enzyme`: loads from `/home/ember/.hermes/plugins/enzyme`, available, tools: `enzyme_search`

So the problem is not that the organs are absent. The problem is activation policy and lifecycle safety:

- Hermes was built around one external memory provider.
- Enzyme has sync/write/refresh behavior and can write temp/mirror files.
- Holographic can store explicit facts and mirror built-in memory writes.
- Honcho already owns active user modeling.

Therefore all-three-live needs an explicit mesh gate, not accidental config-list activation.

## Mnemos L1 discovery prerequisite

A read-only search for candidate Mnemos live DB paths found no obvious live/private Mnemos DB path or env var. Only synthetic shadow fixture SQLite files were found, all 8192 bytes:

- `/home/ember/.hermes/workspace/reports/mnemos-integration-ladder/2026-05-26T234837-0700/phase-2-fail-closed/cases/empty-fixture/home/synthetic-scope/mnemos_shadow.sqlite3`
- `/home/ember/.hermes/workspace/reports/mnemos-integration-ladder/2026-05-26T234837-0700/phase-2-fail-closed/cases/disabled-server/home/synthetic-scope/mnemos_shadow.sqlite3`
- `/home/ember/.hermes/workspace/reports/mnemos-integration-ladder/2026-05-26T234837-0700/phase-1-builder/temp-hermes-home/synthetic-scope/mnemos_shadow.sqlite3`
- `/home/ember/hermes-agent-src/reports/mnemos-continuity/20260527T024120Z/live-wiring-shadow/synthetic-fixtures/mnemos_shadow.sqlite3`

No private row content was read into this report.

## Verification

Targeted verification passed:

```text
32 passed
py_compile passed
Verify current config resolution:
memory.provider= honcho
memory.providers= ['enzyme', 'holographic']
multi_provider_enabled= None
resolved_provider_names= ['honcho']
git diff --check passed
```

## Negative space

This rung did not:

- edit `~/.hermes/config.yaml`
- set `memory.multi_provider_enabled`
- activate Enzyme
- activate Holographic
- change `memory.provider`
- restart the gateway
- admit live Mnemos prompt packets
- open or read private Mnemos row content
- migrate/index/seed any memory DB

## Next safe handle

To actually test Honcho + Enzyme + Holographic in a non-default isolated profile, use:

`YES MEMORY MESH SHADOW PROFILE — HONCHO ENZYME HOLOGRAPHIC NO DEFAULT GATEWAY`

That should authorize only a shadow/profile-local activation smoke. It should still not authorize default gateway restart or default-profile ambient prompt injection.
