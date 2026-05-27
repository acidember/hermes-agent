# Mnemos live wiring plan — plan-only boundary rung

Generated: 2026-05-27T21:02:18Z
Branch: `work/mnemos-gate-refresh-origin-main-20260527T191822Z`
Status: **PLAN ONLY — no live wiring applied**

## Stop sign / consent boundary

This plan crosses the boundary from synthetic, inert, tests-only Mnemos rungs toward a real read-only live-memory canary. It must not be applied until Ember explicitly approves a separate activation handle.

This plan does **not**:

- edit `~/.hermes/config.yaml`
- edit default profile config
- point the running gateway at a live/private Mnemos DB
- restart the gateway
- enable Mnemos as the active Hermes memory provider
- replace Honcho
- migrate, seed, index, or write any DB
- copy Honcho, Holographic, Enzyme, built-in memory, or chat/session data into Mnemos
- make raw private Mnemos rows prompt-visible

## Current observed state, read-only

From read-only inspection before writing this artifact:

- `memory.provider = honcho`
- built-in memory files are enabled (`memory_enabled=True`, `user_profile_enabled=True`)
- `context.engine = compressor`
- `mnemos_prompt_admission.enabled = True`
- current Mnemos prompt-admission source is `synthetic_shadow_sqlite`
- current Mnemos rails: `allow_live_db=False`, `allow_writes=False`, `telemetry_only=True`
- `hermes memory status` reports Honcho installed and active; Holographic and Enzyme installed but not active
- source code currently initializes exactly one external memory provider via `memory.provider`, then `MemoryManager` rejects additional external providers

## Architecture decision

First live boundary should **not** make Mnemos a Hermes memory provider yet.

Instead, use a narrow live-canary sidecar path:

1. Mnemos remains a read-only retrieval candidate.
2. Honcho remains the single active external memory provider.
3. Mnemos live canary is gated by its own prompt-admission policy.
4. Prompt admission is either off or metadata-only until the canary proves fail-closed behavior.
5. Any Mnemos output admitted into the prompt is fenced, low-trust, bounded, and explicitly subordinate to user input + current task context.

This preserves the current single-provider invariant while allowing a real, reversible live read probe.

## Proposed rungs

### L0 — this artifact: plan only

Evidence:

- Write this plan artifact.
- Verify git status and that no config/runtime files changed except this report.

Activation: none.

### L1 — live-read discovery, no prompt admission

Goal: prove the process can locate a live Mnemos DB path without reading private rows into the prompt.

Proposed mechanism:

- Add a config stanza under a new explicit key, not `memory.provider`:

```yaml
mnemos_live_canary:
  enabled: false
  source: live_mnemos_sqlite_readonly_canary
  db_path_env: MNEMOS_LIVE_DB_PATH
  allow_live_db: true
  allow_writes: false
  telemetry_only: true
  prompt_admission: false
  max_items: 0
  low_trust: true
  redact_content: true
```

Safety:

- `enabled: false` by default.
- DB path comes from env var, not committed config.
- No row content is read or stored in artifacts.
- Query/response evidence is counts, schema shape, and redacted labels only.

Verification commands:

```bash
python -m pytest tests/agent/test_mnemos_private_fixture_validator.py tests/agent/test_mnemos_prompt_canary.py -q -o 'addopts='
git diff --check
python -m py_compile agent/mnemos_admission.py agent/mnemos_prompt_canary.py
```

Abort if:

- any write capability appears
- any private row content appears in stdout/report/test fixtures
- `memory.provider` changes
- gateway restart is required at L1

### L2 — non-default profile live canary, still no default gateway

Goal: test live Mnemos read-only behavior in a non-default stopped/isolated profile.

Proposed profile:

- use existing stopped `mnemos-shadow-ro` profile or create a separately approved profile only after approval
- keep default profile and gateway unchanged
- set canary source to `live_mnemos_sqlite_readonly_canary`
- `allow_writes=false`
- `telemetry_only=true`
- `prompt_admission=false` or `max_items=0`

Verification:

- run CLI/profile-local smoke with no gateway restart
- produce redacted artifact with only status, counts, source labels, and fail-closed evidence

Abort if:

- profile starts ambiently in gateway
- tool surface leaks unapproved Mnemos tools into default chat
- raw private row text reaches prompt/log/report

### L3 — default-profile prompt admission canary, bounded

Goal: allow a tiny amount of live Mnemos-derived context into the default profile, but only after L1/L2 pass and Ember approves.

Proposed config shape:

```yaml
mnemos_prompt_admission:
  enabled: true
  source: live_mnemos_sqlite_readonly_canary
  allow_live_db: true
  allow_writes: false
  telemetry_only: false
  low_trust_label: true
  max_items: 1
  max_chars: 600
  require_boundary_marker: true
  fail_closed: true
  tool: mnemos_ro_live_canary_hypomnema_search
```

Prompt block requirements:

- fenced as low-trust retrieved memory
- not new user input
- not instructions
- maximum one item initially
- content redacted or summarized if the source row contains sensitive/private raw payloads
- rejected packets do not consume gate budget

Gateway restart:

- required only for this rung if default profile config changes
- must be preflighted, announced, and followed by health verification

Abort if:

- Honcho disappears as active provider unexpectedly
- external provider changes from `honcho`
- Mnemos becomes writable
- more than one live item is injected
- raw private content appears outside the fenced memory block
- gateway fails health checks or reconnects poorly

### L4 — router/broker phase, not part of first live activation

Goal: eventual proper mesh across Honcho, Mnemos, Holographic, Enzyme.

Principle: introduce a `MemoryDriverRouter` or equivalent broker before attempting multiple ambient backends. The router owns policy, source selection, audit, and prompt admission; backends stay separate organs.

This is explicitly later work.

## Honcho impact

### What happens in L1/L2

Nothing should change for Honcho.

- `memory.provider` remains `honcho`.
- Honcho remains the only active external Hermes memory provider.
- Honcho tools remain available through the memory tool surface when the platform enables memory tools.
- Honcho continues its configured writes/sync/prefetch behavior after completed turns.
- Honcho data is not copied into Mnemos.
- Mnemos data is not written into Honcho.

### What happens in L3

Honcho still remains active, but Mnemos may add a separate low-trust prompt-admission packet.

Expected user-visible effect:

- The model may see both Honcho context and a tiny Mnemos live canary block.
- If they conflict, current user input and explicit instructions win; Honcho remains the established external memory provider; Mnemos canary is labeled low-trust until promoted.
- There may be extra context pressure, so L3 starts with `max_items=1` and `max_chars=600`.

Risk:

- Double-memory ambiguity: Honcho representation and Mnemos retrieved packet might disagree.

Mitigation:

- Mnemos canary block must carry source, timestamp/evidence metadata, and low-trust label.
- Do not let Mnemos silently overwrite or mirror Honcho conclusions.
- Keep rollback as a single config toggle: set Mnemos prompt admission back to synthetic/telemetry or disabled.

## Holographic impact

Current observed state: Holographic is installed but not the active provider. Repository code enforces one external memory provider via `memory.provider`, so activating Holographic directly would displace Honcho.

This plan does not activate Holographic.

- No Holographic config changes.
- No Holographic DB/vector writes.
- No HRR/vector prompt injection.
- No switch from `memory.provider: honcho` to `memory.provider: holographic`.

Future role:

- Holographic can become a router backend later for symbolic/vector similarity, but only behind broker policy.
- It should not be made ambient alongside Honcho by bypassing the one-provider guard.

## Enzyme impact

Current observed state: Enzyme is installed according to `hermes memory status`, but not active because `memory.provider=honcho`. Enzyme files/DBs are not touched by this plan.

This plan does not activate or index Enzyme.

- No Enzyme CLI `catalyze` run.
- No Enzyme DB migration or ingestion.
- No Enzyme provider switch.
- No Enzyme prompt injection.
- No Enzyme writes from Mnemos or Honcho.

Future role:

- Enzyme can be an explicit retrieval backend for semantic/project recall after a router exists.
- It should remain tool/router-mediated rather than becoming another ambient prompt injector.

## Built-in memory / USER.md impact

Built-in MEMORY.md and USER.md remain active and unchanged.

This plan does not write durable user facts or procedural memories. The only write is this plan artifact in the repository report directory.

## Rollback plan

For any live canary rung after approval:

1. Set Mnemos live canary `enabled: false` or return `mnemos_prompt_admission.source` to `synthetic_shadow_sqlite`.
2. Ensure `allow_live_db: false`, `allow_writes: false`, `telemetry_only: true`.
3. If default gateway was restarted for activation, restart once more after rollback with the same preflight discipline.
4. Verify:

```bash
hermes memory status
hermes profile list
python - <<'PY'
from hermes_cli.config import load_config
cfg = load_config() or {}
print(cfg.get('memory', {}).get('provider'))
print(cfg.get('mnemos_prompt_admission', {}))
PY
```

Expected rollback proof:

- `memory.provider` is still `honcho`
- default gateway running
- no live Mnemos prompt packet admitted
- synthetic/fail-closed tests pass

## Evidence bundle requirements for activation rung

Each future activation rung must produce a timestamped bundle containing:

- `plan.md` or `decision.json`
- `config-before.redacted.yaml`
- `config-after.redacted.yaml` if config changed
- `verification.txt`
- `negative-space.md`
- `rollback-proof.md` for any rung that touches default profile/gateway
- `secret-sweep.json` or equivalent no-secret evidence

Never store secrets, credential material, DB DSNs, or raw private memory rows. Use `[REDACTED]`.

## Exact next approval handle

If Ember wants the next step after this plan, use:

`YES L1 LIVE READ DISCOVERY — NO PROMPT ADMISSION`

That approval would authorize only L1: code/tests/config-draft for read-only live DB discovery with telemetry-only evidence. It would still not authorize default prompt admission, provider replacement, gateway restart, Mnemos writes, or Honcho replacement.
