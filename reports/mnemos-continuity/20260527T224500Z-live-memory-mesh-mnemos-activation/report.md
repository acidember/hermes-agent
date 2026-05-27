# Live memory mesh + Mnemos synthetic canary activation

## Bottom line

PASS with one operational caveat.

The default profile is now configured so the external memory provider resolver selects all three memory organs:

```text
['honcho', 'enzyme', 'holographic']
```

The gateway was restarted and is now running from the intended clean worktree:

```text
/home/ember/hermes-agent-src/.worktrees/mnemos-gate-refresh-origin-main-20260527T191822Z
```

Mnemos prompt admission remains bounded to the synthetic, low-trust, read-only canary rail:

```text
status=armed_synthetic_canary
source=synthetic_shadow_sqlite
allow_live_db=False
allow_writes=False
telemetry_only=True
```

The restart interrupted the active Discord turn as expected, but post-restart verification completed successfully.

## What changed

Edited default profile config only:

```yaml
memory:
  provider: honcho
  providers:
    - enzyme
    - holographic
  multi_provider_enabled: true
```

This keeps Honcho as the legacy/singular provider while explicitly allowing the mesh resolver to initialize Honcho + Enzyme + Holographic together.

No source code changes were made in this rung.

## Backup / rollback

A local pre-change config backup was written at:

```text
reports/mnemos-continuity/activation-backups/config.yaml.before-memory-mesh-20260527T223826Z
```

Rollback command:

```bash
cp /home/ember/hermes-agent-src/.worktrees/mnemos-gate-refresh-origin-main-20260527T191822Z/reports/mnemos-continuity/activation-backups/config.yaml.before-memory-mesh-20260527T223826Z /home/ember/.hermes/config.yaml
systemctl --user restart hermes-gateway
```

The backup is intentionally local/untracked and should not be pushed because it is a full config snapshot.

## Verification

### Config resolver

```text
resolved_memory_providers = ['honcho', 'enzyme', 'holographic']
memory.multi_provider_enabled = True
```

All three provider plugins loaded and reported available in pre-restart smoke:

```text
honcho available True
enzyme available True
holographic available True
```

A direct `AIAgent` initialization after config change produced:

```text
agent_memory_providers ['honcho', 'enzyme', 'holographic']
```

### Mnemos synthetic prompt canary

MCP server test passed before restart:

```text
✓ Connected
✓ Tools discovered: 1
mnemos_ro_hypomnema_search
```

Direct runtime smoke after MCP discovery showed:

```text
mcp_registry_entry True
mnemos_low_trust_header_in_volatile True
mnemos_metadata.decision = admit
mnemos_metadata.low_trust = True
mnemos_metadata.source = synthetic_shadow_sqlite
```

Rails stayed locked:

```text
allow_live_db=False
allow_writes=False
telemetry_only=True
require_low_trust=True
```

### Tests

Targeted tests passed twice; final rerun:

```text
22 passed, 1 warning in 2.56s
```

Command:

```bash
python -m pytest \
  tests/agent/test_memory_provider_selection.py \
  tests/agent/test_mnemos_prompt_canary.py \
  tests/agent/test_mnemos_prompt_integration.py \
  -q -o 'addopts='
```

Also passed py_compile for:

```text
agent/agent_init.py
agent/memory_provider_selection.py
agent/mnemos_prompt_canary.py
agent/mnemos_admission.py
```

### Gateway post-restart proof

Gateway restart was intentionally disruptive to the active Discord reply. The old process drained for 60s, interrupted the active tool command, then systemd started the new process.

Post-restart live state:

```text
ActiveState=active
SubState=running
MainPID=2176041
ExecMainStartTimestamp=Wed 2026-05-27 15:40:57 PDT
cwd=/home/ember/hermes-agent-src/.worktrees/mnemos-gate-refresh-origin-main-20260527T191822Z
cmdline=/home/ember/hermes-agent-src/venv/bin/python -m hermes_cli.main gateway run --replace
```

Adapter/log markers after restart:

```text
[Telegram] Connected to Telegram (polling mode)
[Discord] Connected as Kai- Hermes#0838
Gateway running with 3 platform(s)
Cron ticker started (interval=60s)
```

Current gateway cgroup includes the expected synthetic Mnemos MCP server and Enzyme daemon:

```text
mnemos_shadow_mcp_server.py ... synthetic-fixtures/mnemos_shadow.sqlite3 ... mnemos-shadow-canary
/home/ember/.local/bin/enzyme __daemon -v
```

## Observed caveats

1. During shutdown, systemd logged that it killed an old Enzyme daemon from the old gateway cgroup. This appears to be restart cleanup, not a post-restart fault. A fresh Enzyme daemon is present under the current gateway cgroup.
2. Mnemos is still synthetic canary prompt context, not live/private Mnemos DB admission.
3. Honcho remains tools/summoned-style plus memory-provider lifecycle; broad raw ambient dumping was not enabled by this rung.
4. The current Discord session received Enzyme context after restart, which is evidence that the memory mesh is now actually participating in live prompt context.

## Negative-space proof

No destructive cleanup, no secret reads/printing, no Mnemos live DB access, no Mnemos writes, no Holographic/fact-store write call, no cron/provider/model changes, and no source code changes were performed in this rung.

## Current state

- Default profile memory mesh: live after restart.
- Gateway: running from intended worktree after restart.
- Mnemos: prompt-visible only through low-trust synthetic canary rail.
- Next expansion, if wanted later: live/private Mnemos read-only discovery without prompt admission, still no writes.
