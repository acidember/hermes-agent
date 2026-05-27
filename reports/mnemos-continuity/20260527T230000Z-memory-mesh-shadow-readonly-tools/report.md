# Memory mesh shadow read-only tool-call smoke

Generated: 2026-05-27T23:00:00Z
Branch: `work/mnemos-gate-refresh-origin-main-20260527T191822Z`
Status: **PASS with one important Honcho-read caveat**

## Scope

Ember approved: `YES MEMORY MESH SHADOW READONLY TOOL CALLS — NO WRITES`.

This rung ran a bounded one-shot Hermes chat under `mnemos-shadow-ro` and allowed the model to call only these read-like tools:

- `enzyme_search`
- `honcho_profile` with a synthetic peer name and no card/update payload

Explicitly forbidden:

- `fact_store`
- `fact_feedback`
- `honcho_conclude`
- write/update/store/delete tools
- default gateway restart
- default profile activation
- Mnemos live prompt admission

## Command shape

```bash
python -m hermes_cli.main --profile mnemos-shadow-ro chat \
  --provider openai-codex \
  -m gpt-5.5 \
  --toolsets memory \
  --max-turns 5 \
  --source mnemos-shadow-memory-mesh-readonly-tools \
  -Q \
  -q "$(cat prompt.txt)"
```

Provider/model override was CLI-only and not persisted.

## Model result

The model returned:

```json
{
  "called_readonly_tools": ["enzyme_search", "honcho_profile"],
  "forbidden_tools_called": [],
  "enzyme_result_shape": "0 results",
  "honcho_result_shape": "no profile facts available; hint present",
  "notes": "Read-only smoke completed without writes or forbidden tool calls."
}
```

## Independent verification from shadow profile state DB

`tool-call-verification.json` confirms the actual assistant tool call message contained exactly:

```json
[
  {
    "name": "enzyme_search",
    "arguments": "{\"query\":\"shadow Enzyme smoke vault\",\"max_results\":3}"
  },
  {
    "name": "honcho_profile",
    "arguments": "{\"peer\":\"shadow-smoke-readonly-probe-20260527\"}"
  }
]
```

And tool result names were exactly:

```json
["enzyme_search", "honcho_profile"]
```

Forbidden calls:

```json
[]
```

Unexpected calls:

```json
[]
```

## Honcho caveat

The Honcho read path is not side-effect-free in the strictest possible sense. The agent log shows that calling `honcho_profile` lazily initialized the Honcho client and created/opened a Honcho session for the shadow host:

- `Initializing Honcho client (host: hermes.mnemos-shadow-ro, workspace: hermes-shadow-smoke)`
- `Honcho session 'mnemos-gate-refresh-origin-main-20260527T191822Z' created (new)`

No write-like Honcho tool was called (`honcho_conclude` was not called), and the requested peer profile returned only the no-facts/hint shape. But future reports should label Honcho profile reads as **read-like but session-touching**, not perfectly inert.

## Evidence files

- `preflight.txt`
- `pre-hashes.json`
- `prompt.txt`
- `chat-output.txt`
- `chat-stderr.txt`
- `chat-exit-code.txt`
- `session-id.txt`
- `session-file-search.txt`
- `profile-db-files.txt`
- `agent-log-session-extract.txt`
- `state-db-inspect.txt`
- `tool-call-verification.json`
- `post-hashes.json`
- `gateway-post.txt`
- `targeted-tests.txt`

## Verification

Passed:

- chat exit code `0`
- state DB shows exactly 2 tool calls
- allowed calls exactly: `enzyme_search`, `honcho_profile`
- forbidden calls: none
- unexpected calls: none
- default config hash unchanged
- shadow config hash unchanged
- shadow `honcho.json` hash unchanged
- shadow Enzyme fixture README hash unchanged
- gateway timestamp unchanged: `ExecMainStartTimestamp=Wed 2026-05-27 12:42:42 PDT`
- targeted tests: `7 passed`
- `git diff --check` passed

## Negative space

Not done:

- no default config edit
- no default profile memory mesh activation
- no default gateway restart
- no shadow config edit during chat
- no `fact_store`
- no `fact_feedback`
- no `honcho_conclude`
- no Mnemos live prompt admission
- no persistent model/provider config change
- no cron change

## Interpretation

The shadow memory mesh has now passed three increasingly real rungs:

1. Provider-manager registration smoke.
2. Model-side tool menu visibility smoke.
3. Model-initiated read-only tool-call smoke.

The read-only tool-call rung proves a model running under `mnemos-shadow-ro` can actually use multiple memory organs in one turn. Enzyme search executed and returned an empty result shape; Honcho profile executed and returned a no-facts/hint shape for the synthetic probe peer.

## Next safe handle

`YES MEMORY MESH SHADOW INDEXED ENZYME FIXTURE — PROFILE LOCAL ONLY`

That would authorize creating or refreshing only the shadow profile's local Enzyme index so `enzyme_search` returns the known non-private fixture. Still no default gateway restart, no default profile activation, no Honcho writes, no Holographic writes, and no Mnemos live prompt admission.
