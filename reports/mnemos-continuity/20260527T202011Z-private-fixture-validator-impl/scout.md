# R1 scout: private-fixture validator seam

## Scope
Read-only scout for a pure candidate response validator for a future non-default private Mnemos fixture. No source edits, no profile or DB creation, no live/private Mnemos reads, no config/provider edits, no gateway restart, no cron changes, no secret reads.

## Existing seam to extend

### Primary implementation module
- `agent/mnemos_admission.py`
  - Existing pure validator: `score_mnemos_candidate(candidate: dict[str, Any]) -> dict[str, Any)` at lines 29-163.
  - Existing packet builder: `build_mnemos_prompt_packet(scored_candidates, max_chars=800, max_items=3)` at lines 166-220.
  - Current synthetic constants: `ALLOWED_SYNTHETIC_SOURCE = "synthetic_shadow_sqlite"` and `MNEMOS_TOOL_NAME = "mnemos_ro_hypomnema_search"` at lines 13-14.
  - This module is explicitly side-effect free and already owns prompt-safe row scoring, redaction, injection detection, provenance checks, and packet budget behavior.

### Existing retrieval/response adapter seam
- `agent/mnemos_prompt_canary.py`
  - Current config parser: `parse_mnemos_prompt_admission_config(...)` at lines 48-113.
  - Current response adapter: `retrieve_mnemos_prompt_packet(...)` at lines 173-250.
  - Current adapter validates wrapper-level `tool`, `source`, `rows`, coerces JSON strings, defaults row low_trust from wrapper only for the synthetic path, and fails closed for malformed/tool/source/unsafe rows.
  - This is the closest production-shaped seam for a candidate response validator that accepts a tool response and returns metadata-only packet/decision output.

### Prompt admission integration seam
- `agent/system_prompt.py`
  - Volatile prompt insertion calls `_build_mnemos_prompt_admission_block(agent)` at lines 302-304.
  - `_build_mnemos_prompt_admission_block` at lines 330-378 parses config, retrieves a packet, records metadata, admits only `decision in {"admit", "summarize"}`, `low_trust is True`, and the current synthetic source, then consumes the one-session gate.
  - `_record_mnemos_prompt_packet_metadata` at lines 381-398 keeps decision/source/reason/telemetry only and avoids raw row/prompt retention.

### Registry/MCP wrapper normalization seam
- `agent/agent_init.py`
  - `_build_mnemos_prompt_admission_retriever(...)` at lines 75-125 dispatches to the existing registry tool, enforces source/tool/no live DB/no writes, normalizes `results` or `rows` into `rows`, and returns `{tool, source, low_trust, rows}`.
  - `_extract_mnemos_mcp_payload(...)` at lines 128-152 unwraps registry/MCP handler JSON.
  - For a future private-fixture candidate, this should remain separate from the pure validator; do not create/register/use the private MCP tool in this validator rung.

## Existing test locations to extend

### Pure scoring tests
- `tests/agent/test_mnemos_admission.py`
  - Existing fixture-driven tests for `score_mnemos_candidate` at lines 24-47.
  - Packet behavior at lines 49-111.
  - Secret/injection non-leak checks at lines 114-129.
  - Best location for unit tests of row-level private fixture scoring if the helper lives in `agent/mnemos_admission.py`.

### Adapter/config tests
- `tests/agent/test_mnemos_prompt_canary.py`
  - Config safety tests at lines 8-100.
  - Retrieval adapter positive and negative response tests at lines 102-190 and 239-276.
  - Best location for tests of wrapper-level private fixture response validation if helper lives in `agent/mnemos_prompt_canary.py` or a sibling pure module.

### One-session smoke harness tests
- `tests/agent/test_mnemos_one_session_smoke.py`
  - Existing parent-rerunnable smoke harness tests at lines 31-105.
  - Useful only after the private validator can feed a prompt-admission packet; not required for the first pure response validator.

### Integration prompt tests
- `tests/agent/test_mnemos_prompt_integration.py`
  - Current volatile-tier and registry-wrapper behavior at lines 96-177.
  - Metadata-only telemetry and one-session consumption at lines 179-326.
  - Keep out of the first helper rung unless private-fixture prompt admission is explicitly allowed later.

## Recommended helper API

Add a private-fixture-specific pure validator without changing runtime behavior:

```python
# candidate location: agent/mnemos_admission.py
PRIVATE_FIXTURE_SOURCE = "non_default_private_fixture_stub"
PRIVATE_FIXTURE_TOOL_NAME = "mnemos_ro_private_fixture_hypomnema_search"
PRIVATE_FIXTURE_MAX_ITEMS = 2
PRIVATE_FIXTURE_MAX_CHARS = 800

def validate_private_fixture_response(response: Any, *, max_items: int = PRIVATE_FIXTURE_MAX_ITEMS) -> dict[str, Any]:
    """Validate a caller-supplied private-fixture MCP/tool response shape.

    Pure and side-effect-free: no config reads, no registry lookup, no MCP call,
    no profile/DB creation, no memory/provider mutation. Returns metadata-only
    decision/telemetry and never retains raw unsafe row bodies.
    """
```

Alternative, if the team wants a row-level primitive too:

```python
def score_private_fixture_candidate(row: Mapping[str, Any], *, query: str = "") -> dict[str, Any]: ...
def build_private_fixture_prompt_packet(scored_rows: Iterable[dict[str, Any]], *, max_chars: int = 800, max_items: int = 2) -> dict[str, Any]: ...
```

For the first rung, `validate_private_fixture_response(response)` is the most direct deliverable because the design asks for a candidate response validator, not runtime retrieval.

## Expected response shape

Accepted wrapper shape:

```json
{
  "tool": "mnemos_ro_private_fixture_hypomnema_search",
  "source": "non_default_private_fixture_stub",
  "low_trust": true,
  "private_fixture": true,
  "read_only": true,
  "allow_live_db": false,
  "allow_writes": false,
  "rows": [
    {
      "id": "fixture-stub-001",
      "source": "non_default_private_fixture_stub",
      "low_trust": true,
      "private_fixture": true,
      "created_by": "design_harness_only",
      "title": "Technical boundary stub",
      "body": "Schematic stub text; not copied from private memory.",
      "provenance": {
        "origin": "hand_authored_fixture",
        "contains_real_memory": false,
        "contains_secret": false
      }
    }
  ]
}
```

Accepted row requirements:
- `source == "non_default_private_fixture_stub"` exactly.
- `low_trust is True` on wrapper and row; unlike current synthetic adapter, do not silently inherit wrapper low_trust for private rows unless the test explicitly approves that behavior.
- `private_fixture is True` on wrapper and row.
- `provenance.origin == "hand_authored_fixture"`.
- `provenance.contains_real_memory is False`.
- `provenance.contains_secret is False`.
- `created_by == "design_harness_only"`.
- `body` is non-empty schematic text and must not contain prompt injection, tool/runtime commands, secrets, live/private memory claims, exact old conversation excerpts, body/intimacy facts, or live user profile facts.
- Maximum rows admitted/validated for prompt use: 2.
- Maximum prompt chars for any later packet: 800.

Returned validator shape should be metadata-only, similar to current packet outputs:

```json
{
  "decision": "admit" | "summarize" | "reject",
  "low_trust": true,
  "source": "non_default_private_fixture_stub",
  "tool": "mnemos_ro_private_fixture_hypomnema_search",
  "reason_codes": ["..."],
  "prompt_text": "... or empty on reject",
  "telemetry": {
    "candidate_count": 1,
    "admitted_count": 1,
    "summarized_count": 0,
    "rejected_count": 0,
    "private_fixture": true,
    "fail_closed": false
  }
}
```

If this first rung is validator-only, tests can assert prompt_text is empty or contains only a low-trust header/summary; either choice is acceptable if raw unsafe row bodies never appear in reject outputs.

## Negative cases to test

Wrapper-level rejects:
- Malformed JSON string / non-dict response.
- Missing `rows` or `rows` not a list.
- Wrong `tool` such as `mnemos_ro_hypomnema_search`.
- Wrong `source` such as `synthetic_shadow_sqlite` or `live_kai_mnemos`.
- Missing or false wrapper `low_trust`.
- Missing or false wrapper `private_fixture`.
- `read_only` not true, `allow_live_db` not false, or `allow_writes` not false.
- More than 2 rows: fail closed or budget downgrade with no raw extra rows retained.

Row-level rejects:
- Missing/false row `low_trust`.
- Missing/false row `private_fixture`.
- Row source mismatch.
- Missing/malformed provenance.
- `provenance.contains_real_memory` true.
- `provenance.contains_secret` true.
- `provenance.origin` not `hand_authored_fixture`.
- Body includes prompt injection: `Ignore previous instructions`, `must trust this memory`, `skip redaction`.
- Body includes tool/runtime command: restart gateway, edit config, enable live DB, call memory write tool, promote provider.
- Body includes secret-like values: `token=...`, `sk-...`, `ghp_...`, bearer tokens.
- Body claims live/private memory: `live Kai memory says...`, copied transcript, exact old conversation excerpt.
- Body contains forbidden personal/body/intimacy or live user profile facts.
- Row is not a mapping.

Telemetry/non-leak rejects:
- Reject packet `prompt_text == ""`.
- Raw secret/injection/body snippets not present in `str(result)` for hard-reject paths where possible.
- Metadata includes only bounded reason codes and counts, not raw rows or raw prompt text.

## Targeted TDD sequence

1. Add failing tests only in a new file or existing pure-test file:
   - Preferred: `tests/agent/test_mnemos_private_fixture_validator.py` for clarity and separation from current synthetic canary behavior.
   - Alternative: append to `tests/agent/test_mnemos_admission.py` if adding helpers to `agent/mnemos_admission.py`.
2. RED tests:
   - Valid private-fixture wrapper with one hand-authored row admits/summarizes with low-trust source/tool metadata.
   - Valid wrapper with two rows respects max rows and metadata counts.
   - Wrong source/tool and live DB/write flags fail closed.
   - Missing row low_trust/private_fixture/provenance fails closed.
   - Secret/injection/tool-command/live-memory rows fail closed and do not leak raw unsafe text.
   - More than two rows fails closed or downgrades according to chosen API contract.
3. GREEN implementation:
   - Add constants and pure helper(s), reusing existing `_clean`, `_redact_secrets`, `_looks_injection`, `_looks_tool_or_runtime_command`, and `_dedupe_reasons` where possible.
   - Keep helper independent from `parse_mnemos_prompt_admission_config`, registry, MCP, profile config, and system prompt insertion.
4. Regression tests:
   - Run `python -m pytest tests/agent/test_mnemos_private_fixture_validator.py tests/agent/test_mnemos_admission.py tests/agent/test_mnemos_prompt_canary.py -q`.
   - Also run `python -m pytest tests/agent/test_mnemos_prompt_integration.py tests/agent/test_mnemos_one_session_smoke.py -q` if any packet/prompt shared helper changes.

## Negative-space evidence
- Did not inspect live/private Mnemos DBs.
- Did not create profiles or DBs.
- Did not edit default profile config/env/provider settings.
- Did not restart gateway or services.
- Did not edit source code.
- Wrote only this scout report artifact under `reports/mnemos-continuity/20260527T202011Z-private-fixture-validator-impl/`.

## Verification
- `python -m pytest tests/agent/test_mnemos_admission.py tests/agent/test_mnemos_prompt_canary.py tests/agent/test_mnemos_one_session_smoke.py -q`
- Result: `35 passed in 0.51s`
