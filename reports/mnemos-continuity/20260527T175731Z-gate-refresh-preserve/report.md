# Mnemos gate-refresh preservation bundle

Generated: 2026-05-27T17:59:05.991514+00:00

## PASS

- Preserved current Mnemos working-tree state, config gate snapshot, HEAD context, and source patch.
- Implemented metadata-only gate refresh helper: `build_mnemos_prompt_gate_refresh(...)`.
- This helper performs no I/O, opens no DB, calls no MCP/tool, writes no memory, and returns no retrieved prompt text.
- Current rung remains: **synthetic default-profile canary**, not live/private Mnemos memory.

## Rails held

- no live Mnemos/Kai DB access
- no memory provider promotion
- no config/env change in this rung
- no gateway restart in this rung
- synthetic low-trust retrieval only for live smoke evidence

## Artifacts

- `manifest.json`
- `git-status.txt`
- `git-name-status.txt`
- `git-stat.txt`
- `git-head.txt`
- `config-gate-refresh.txt`
- `gate-refresh-source.patch` is empty because current Mnemos files are untracked.
- `source-snapshot/` contains authoritative preserved copies of the Mnemos helper/tests with SHA256s in `manifest.json`.

## Rollback

Source helper/test rollback:

```bash
git checkout -- agent/mnemos_prompt_canary.py tests/agent/test_mnemos_prompt_canary.py
```

Config rollback if the canary itself needs disabling:

```bash
cp /home/ember/hermes-agent-src/reports/mnemos-continuity/activation-backups/config.yaml.before-prompt-admission-20260527T165204Z /home/ember/.hermes/config.yaml
```

## ISSUE / watchpoint

Plain process registry inspection may report the dynamic MCP tool as absent outside a fully loaded gateway/session tool context; live tool invocation was verified separately. The new helper makes that distinction explicit as `armed_but_retriever_missing` rather than pretending enabled config equals prompt injection.

## NEXT

Design next rung as a locked-door one-session synthetic smoke with metadata-only evidence and a stop before live/private Mnemos.

## Final verification

- `verification.md` records targeted pytest + py_compile PASS.
- Latest targeted result: `70 passed, 1 warning`.
- Added second safe rung: sanitized packet metadata retained without raw `prompt_text`/row body.
