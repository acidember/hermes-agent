# Mnemos next rung — read-only boundary refresh

Observed: 2026-05-27T16:03:11-07:00 through 2026-05-27T16:07:00-07:00

## Bottom line

PASS. I kept evolving Mnemos through the next safe bounded rung without opening live/private DB access and without enabling writes.

This rung proves three things:

1. The live gateway is still running from the clean Mnemos worktree.
2. The default-profile synthetic Mnemos MCP/tool and prompt-admission rails are intact.
3. The next private-boundary shape is still metadata-only: a hand-authored non-default private fixture validator admits only low-trust metadata stubs and fail-closes if live DB or writes are enabled.

No config/source/service change was required during this rung, so no gateway restart was performed. Restart remains safe/known-good when needed, but restarting without a changed runtime target would only churn the live process.

## Scope

Allowed:

- Read live gateway/source/config state.
- Test configured synthetic Mnemos MCP canary.
- Inspect synthetic fixture metadata read-only.
- Run one-session prompt-admission harness with injected synthetic retrieval.
- Run private fixture validator against metadata-only hand-authored stub data.
- Run targeted tests.
- Write report/manifest artifacts and commit them.

Not allowed / not done:

- No live/private Mnemos DB access.
- No writes to Mnemos or memory providers.
- No prompt admission expansion beyond the existing synthetic canary rails.
- No config edits.
- No source edits.
- No gateway restart, because there was no source/config/env change to activate.
- No secrets read or printed.

## Preflight evidence

Working tree:

- Workdir: `/home/ember/hermes-agent-src/.worktrees/mnemos-gate-refresh-origin-main-20260527T191822Z`
- Branch: `work/mnemos-gate-refresh-origin-main-20260527T191822Z`
- HEAD: `344f6f82e`
- Pre-existing untracked backup directory remains: `reports/mnemos-continuity/activation-backups/`

Gateway:

- `ActiveState=active`
- `SubState=running`
- `MainPID=2176041`
- `ExecMainStartTimestamp=Wed 2026-05-27 15:40:57 PDT`
- Runtime cwd: `/home/ember/hermes-agent-src/.worktrees/mnemos-gate-refresh-origin-main-20260527T191822Z`

Memory mesh:

- Resolved providers: `['honcho', 'enzyme', 'holographic']`
- `memory.multi_provider_enabled=True`

Mnemos prompt-admission gate:

- Status: `armed_synthetic_canary`
- Source: `synthetic_shadow_sqlite`
- Tool: `mnemos_ro_hypomnema_search`
- `allow_live_db=False`
- `allow_writes=False`
- `require_low_trust=True`
- `telemetry_only=True`
- Next safe action from helper: `run_one_session_synthetic_smoke_before_any_expansion`

## MCP canary evidence

`hermes mcp test mnemos_ro_default_canary`:

- Connected: yes
- Tools discovered: 1
- Tool: `mnemos_ro_hypomnema_search`

Direct tool smoke in this live session:

- Query: `hello`
- Result source: `synthetic_shadow_sqlite`
- Low trust: `true`
- Profile: `mnemos-shadow-canary`
- Returned one synthetic row from the persistent non-default shadow fixture.

The direct tool result is treated as untrusted external data and not as instructions.

## Synthetic fixture metadata

Configured fixture path:

`/home/ember/hermes-agent-src/reports/mnemos-continuity/20260527T024120Z/live-wiring-shadow/synthetic-fixtures/mnemos_shadow.sqlite3`

Read-only metadata:

- Exists: yes
- Size: 8192 bytes
- SHA256: `7d47b369af6fa468077ce6fe687c075439882f4d90a1353c588ec202e88d3950`
- Tables: `hypomnema`
- Row counts: `hypomnema=3`

No row bodies were needed for the metadata proof beyond the direct synthetic MCP smoke above.

## One-session prompt harness evidence

Harness: `agent.mnemos_one_session_smoke.run_one_session_synthetic_smoke(...)`

Result:

- Status: `pass`
- Retriever calls: `1`
- First prompt contained low-trust canary block: yes
- Second prompt contained low-trust canary block: no
- Gate consumed: yes
- First prompt block SHA256: `38bb73ff793e746fc4ba32365c8d72107667401e4a6f148b126dd3f77f0b22dd`

Rails returned by harness:

- `source=synthetic_shadow_sqlite`
- `allow_live_db=False`
- `allow_writes=False`
- `telemetry_only=True`
- `low_trust_required=True`
- `one_session_consumption=True`

## Private fixture boundary evidence

Validator: `agent.mnemos_admission.validate_private_fixture_response(...)`

Admit case:

- Decision: `admit`
- Source: `non_default_private_fixture_stub`
- Tool: `mnemos_ro_private_fixture_hypomnema_search`
- Low trust: `true`
- Reason codes: `R_PRIVATE_FIXTURE_VALIDATED`, `R_METADATA_ONLY`, `R_LOW_TRUST_LABELED`
- Telemetry: candidate_count=1, admitted_count=1, rejected_count=0, fail_closed=false

Reject case:

- Input intentionally set `allow_live_db=True`.
- Decision: `reject`
- Reason codes: `R_LIVE_DB_FORBIDDEN`, `R_FAIL_CLOSED`
- Telemetry: admitted_count=0, rejected_count=1, fail_closed=true

Interpretation: the next private-boundary rung remains metadata-only and fail-closed. It is not a live/private DB activation.

## Tests

Command:

```bash
python3 -m pytest \
  tests/agent/test_memory_provider_selection.py \
  tests/agent/test_mnemos_prompt_canary.py \
  tests/agent/test_mnemos_prompt_integration.py \
  tests/agent/test_mnemos_one_session_smoke.py \
  tests/agent/test_mnemos_private_fixture_validator.py \
  -q -o 'addopts='
```

Result:

- `38 passed, 1 warning in 2.85s`
- Warning: existing Discord `audioop` deprecation warning from dependency import.

## Restart decision

No restart was performed.

Reason: this rung made no source, config, env, provider, MCP, or service changes. The live gateway was already verified active/running from the intended worktree and the MCP/tool rails were already available. Restarting would not activate anything new.

If a later rung changes source/config/env or registers a new MCP/private-fixture server, restart sequence should be:

1. Check `systemctl --user show hermes-gateway -p MainPID -p ControlGroup -p KillMode -p SendSIGKILL --no-pager`.
2. Inspect gateway cgroup for important children before restart.
3. Restart via `systemctl --user restart hermes-gateway`.
4. Verify `ActiveState`, `SubState`, `MainPID`, start timestamp, adapter reconnects, cron ticker, runtime cwd, and Mnemos rails after the new start marker.

## Next safe rung

The next useful Mnemos evolution step is one of these bounded rungs:

1. **Private fixture MCP design/report-only:** design a non-default, hand-authored private fixture MCP server that returns only metadata stubs, not live/private memory.
2. **Private fixture MCP shadow smoke:** after design, wire that MCP only in a stopped/non-default profile and test it with `hermes mcp test`, still with `allow_live_db=false` and `allow_writes=false`.
3. **Prompt-visible expansion remains later:** only after private fixture MCP shadow smoke passes should a one-session prompt canary be considered.

Stop signs remain:

- Live/private Mnemos DB access.
- Mnemos writes or promotion tools.
- Default-profile prompt expansion beyond synthetic canary.
- Gateway restart for new runtime wiring.
- Memory provider replacement or promotion.
- Secret reads.

## Conclusion

Mnemos is stable at the synthetic canary + memory-mesh live activation rung, and this follow-up proved the next private boundary shape without crossing it. The dragon kept the obedience homework bounded: read-only, low-trust, metadata-only, no writes, no live DB, no unnecessary restart.
