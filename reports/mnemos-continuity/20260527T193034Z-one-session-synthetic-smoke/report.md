# Mnemos one-session synthetic smoke rung

## Verdict
Implemented a locked-door one-session synthetic prompt-admission smoke seam in source/tests.

## What changed
- `agent/system_prompt.py` now consumes `_mnemos_prompt_admission_consumed` after exactly one successful low-trust synthetic prompt injection.
- Rejected/failed packets do **not** consume the gate.
- `tests/agent/test_mnemos_prompt_integration.py` proves single-use behavior with a mocked synthetic MCP result.

## Rails preserved
- synthetic shadow SQLite only
- no live/private Mnemos DB
- no writes
- telemetry-only metadata
- low-trust label required
- no provider promotion
- no gateway restart performed for this code rung

## TDD evidence
- RED: `red-pytest.txt` shows the one-session consumption test failed because the retriever was called twice.
- GREEN: `green-new-tests.txt` shows the new one-session tests passing.

## Next ladder rung
Build a parent-rerunnable smoke harness/report that exercises the same seam and records redacted metadata, then stop before non-default private fixture design.
