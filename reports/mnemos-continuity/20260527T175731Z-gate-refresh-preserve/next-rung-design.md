# Mnemos next rung design — locked-door one-session synthetic smoke

Generated: 2026-05-27T17:57:31Z

## Current rung

`default-profile synthetic prompt-admission canary` is configured and rail-locked, with a new metadata-only gate-refresh helper:

- `agent.mnemos_prompt_canary.build_mnemos_prompt_gate_refresh(...)`
- no I/O
- no tool calls
- no Mnemos/Kai DB access
- no prompt text returned
- distinguishes `enabled config` from `runtime retriever actually available`

## Next rung: one-session synthetic prompt smoke, still locked-door

Purpose: prove the canary prompt path can admit **only** synthetic low-trust context for one fresh session, while producing metadata evidence that it does not persist raw retrieved text into session messages and does not touch live/private memory.

### Preconditions / clean gate refresh

1. Run targeted tests:
   - `python -m pytest tests/agent/test_mnemos_prompt_canary.py tests/agent/test_mnemos_prompt_integration.py tests/agent/test_mnemos_admission.py -q -o 'addopts='`
2. Run pure gate refresh on loaded config:
   - status must be `armed_synthetic_canary` or explicit `armed_but_retriever_missing` with a documented fix-before-expansion decision.
3. Verify live synthetic MCP canary only:
   - tool result must report `source=synthetic_shadow_sqlite`, `low_trust=true`, `profile=mnemos-shadow-canary`.
4. Verify no live/private route:
   - `allow_live_db=false`
   - `allow_writes=false`
   - `telemetry_only=true`

### Implementation shape

Add a small test-only harness, not a broad runtime rewrite:

- create `tests/agent/test_mnemos_one_session_smoke.py` or extend `test_mnemos_prompt_integration.py`;
- instantiate an agent with synthetic config + fake retriever;
- build system prompt once and assert the low-trust packet appears;
- simulate a second build/continuation boundary with no new retriever call unless explicitly configured;
- assert raw retrieved rows are not appended to persisted user/assistant messages;
- assert prompt block is bounded by `max_chars` and `max_items`;
- assert unsafe rows fail closed and produce empty prompt text.

### Evidence artifacts

Write a fresh report root:

`reports/mnemos-continuity/<timestamp>-one-session-smoke/`

Required files:

- `report.md` — PASS / ISSUES / NEXT
- `manifest.json` — exact source files, tests, hashes, rails
- `gate-refresh.json` — metadata-only gate status
- `pytest-output.txt` — targeted tests
- `negative-space.md` — explicit no-live/no-write/no-persist proof

### Stop signs

Stop and report before any of these:

- live/private Mnemos DB
- default memory provider integration
- broad prompt-visible retrieval beyond synthetic fixture
- config/env edits beyond the existing canary section
- gateway restart
- cron/provider/model changes
- deletion/cleanup
- secret reads

### Rollback

If the rung modifies source/tests only:

```bash
git checkout -- agent/mnemos_prompt_canary.py tests/agent/test_mnemos_prompt_canary.py tests/agent/test_mnemos_prompt_integration.py tests/agent/test_mnemos_one_session_smoke.py
```

If the existing canary config must be disabled:

```bash
cp /home/ember/hermes-agent-src/reports/mnemos-continuity/activation-backups/config.yaml.before-prompt-admission-20260527T165204Z /home/ember/.hermes/config.yaml
```

### Next handle after this design

Because Ember has given standing approval for safe clean-gated ladder movement, the next allowed action is:

`AUTO-SAFE: implement one-session synthetic smoke tests only`

Still stop for all stop signs above.
