# Mnemos parent-rerunnable one-session smoke harness

## Verdict
Implemented and verified a side-effect-free parent-rerunnable harness for the synthetic one-session Mnemos prompt canary.

## What changed
- Added `agent/mnemos_one_session_smoke.py` with `run_one_session_synthetic_smoke(...)`.
- Added `tests/agent/test_mnemos_one_session_smoke.py`.

## What the harness proves
- First synthetic prompt-admission build contains the low-trust canary.
- The gate is consumed after successful admission.
- The second build omits the canary.
- The retriever is called exactly once.
- Failed/rejected packets fail closed and do not consume the gate.
- Returned evidence contains metadata and hashes only, not raw retrieved rows or raw prompt text.

## Rails
- No Hermes config read.
- No tool discovery.
- No live/private Mnemos DB.
- No memory writes.
- No provider promotion.
- No gateway restart.

## Verification
- `verification.txt`: py_compile plus targeted pytest (`41 passed, 1 warning`).
- `harness-sample.txt`: sample metadata-only harness result.
- `secret-sweep.json`: changed/report scope secret scan (`0 secrets found`).
- Live synthetic MCP canary was checked from the chat tool and returned low-trust synthetic source.

## Next safe rung
Either commit/push this helper, then write a design-only card for a non-default private fixture. Stop before creating/seeding/copying any private/live memory.
