"""Inert Mnemos prompt-admission canary config parsing.

This module is intentionally side-effect free: it does not read Hermes config from
disk, inspect environment variables, call MCP/tools, touch Mnemos, mutate memory,
or wire anything into runtime prompts. Callers must pass an already-materialized
config object, and malformed/unsafe input fails closed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from agent.mnemos_admission import ALLOWED_SYNTHETIC_SOURCE, MNEMOS_TOOL_NAME, build_mnemos_prompt_packet, score_mnemos_candidate

_SECTION = "mnemos_prompt_admission"
_DEFAULT_MAX_ITEMS = 2
_DEFAULT_MAX_CHARS = 800
_MAX_ITEMS_LIMIT = 3
_MAX_CHARS_LIMIT = 1000


@dataclass(frozen=True)
class MnemosPromptAdmissionConfig:
    """Parsed Mnemos prompt-admission canary gate.

    ``enabled`` and ``activation_possible`` are true only for an explicitly
    enabled, synthetic-only, telemetry-only test object. Every malformed or
    unsafe value is normalized back to the locked/default-disabled shape.
    """

    enabled: bool = False
    activation_possible: bool = False
    canary: bool = True
    source: str = ALLOWED_SYNTHETIC_SOURCE
    mcp_tool: str = MNEMOS_TOOL_NAME
    max_items: int = _DEFAULT_MAX_ITEMS
    max_chars: int = _DEFAULT_MAX_CHARS
    fail_closed: bool = True
    require_low_trust: bool = True
    allow_live_db: bool = False
    allow_writes: bool = False
    telemetry_only: bool = True
    reason_codes: list[str] = field(default_factory=lambda: ["disabled_by_default"])


def parse_mnemos_prompt_admission_config(config: Mapping[str, Any] | None) -> MnemosPromptAdmissionConfig:
    """Parse the inert ``mnemos_prompt_admission`` section fail-closed.

    The helper deliberately accepts a caller-supplied config object instead of
    loading real config from disk. It never enables live DB access, writes, or
    persistent prompt activation; the only enabled result is a bounded synthetic
    canary config with exact safety flags.
    """

    if not isinstance(config, Mapping):
        return _disabled("fail_closed", "malformed_config")

    if _SECTION not in config:
        return MnemosPromptAdmissionConfig()

    raw_section = config.get(_SECTION)
    if raw_section is None:
        return _disabled("fail_closed", "malformed_section")
    if not isinstance(raw_section, Mapping):
        return _disabled("fail_closed", "malformed_section")

    enabled = raw_section.get("enabled", False)
    if enabled is False or enabled is None:
        return MnemosPromptAdmissionConfig()
    if enabled is not True:
        return _disabled("fail_closed", "enabled_must_be_boolean_true")

    if raw_section.get("canary") is not True:
        return _disabled("fail_closed", "canary_required")
    if raw_section.get("source") != ALLOWED_SYNTHETIC_SOURCE:
        return _disabled("fail_closed", "synthetic_source_required")
    if raw_section.get("mcp_tool") != MNEMOS_TOOL_NAME:
        return _disabled("fail_closed", "expected_mcp_tool_required")
    if raw_section.get("fail_closed") is not True:
        return _disabled("fail_closed", "fail_closed_required")
    if raw_section.get("require_low_trust") is not True:
        return _disabled("fail_closed", "low_trust_required")
    if raw_section.get("allow_live_db") is not False:
        return _disabled("fail_closed", "live_db_disallowed")
    if raw_section.get("allow_writes") is not False:
        return _disabled("fail_closed", "writes_disallowed")
    if raw_section.get("telemetry_only") is not True:
        return _disabled("fail_closed", "telemetry_only_required")

    max_items = raw_section.get("max_items")
    max_chars = raw_section.get("max_chars")
    if not isinstance(max_items, int) or isinstance(max_items, bool) or not (1 <= max_items <= _MAX_ITEMS_LIMIT):
        return _disabled("fail_closed", "max_items_out_of_bounds")
    if not isinstance(max_chars, int) or isinstance(max_chars, bool) or not (1 <= max_chars <= _MAX_CHARS_LIMIT):
        return _disabled("fail_closed", "max_chars_out_of_bounds")

    return MnemosPromptAdmissionConfig(
        enabled=True,
        activation_possible=True,
        canary=True,
        source=ALLOWED_SYNTHETIC_SOURCE,
        mcp_tool=MNEMOS_TOOL_NAME,
        max_items=max_items,
        max_chars=max_chars,
        fail_closed=True,
        require_low_trust=True,
        allow_live_db=False,
        allow_writes=False,
        telemetry_only=True,
        reason_codes=["explicit_test_config_enabled"],
    )


def build_mnemos_prompt_gate_refresh(
    config: Mapping[str, Any] | None,
    *,
    retriever_available: bool | None = None,
) -> dict[str, Any]:
    """Return a metadata-only status snapshot for the prompt-admission gate.

    This is the safe "gate refresh" rung: it parses caller-supplied config and
    reports whether the synthetic canary is merely configured, actually able to
    inject after runtime retriever wiring, or fail-closed. It performs no I/O,
    opens no DB, calls no tools, and returns no retrieved prompt text.
    """

    parsed = parse_mnemos_prompt_admission_config(config)
    rails = {
        "canary": parsed.canary,
        "source": parsed.source,
        "mcp_tool": parsed.mcp_tool,
        "max_items": parsed.max_items,
        "max_chars": parsed.max_chars,
        "fail_closed": parsed.fail_closed,
        "require_low_trust": parsed.require_low_trust,
        "allow_live_db": parsed.allow_live_db,
        "allow_writes": parsed.allow_writes,
        "telemetry_only": parsed.telemetry_only,
    }
    reason_codes = list(parsed.reason_codes)

    if not parsed.activation_possible:
        status = "disabled"
        prompt_injection_possible = False
        next_safe_action = "keep_disabled_or_prepare_synthetic_canary_config"
    elif retriever_available is False:
        status = "armed_but_retriever_missing"
        prompt_injection_possible = False
        reason_codes.append("retriever_unavailable")
        next_safe_action = "fix_runtime_retriever_or_keep_disabled_before_expanding"
    else:
        status = "armed_synthetic_canary"
        prompt_injection_possible = retriever_available is not False
        next_safe_action = "run_one_session_synthetic_smoke_before_any_expansion"

    return {
        "status": status,
        "rung": "default-profile synthetic prompt-admission canary",
        "activation_possible": parsed.activation_possible,
        "prompt_injection_possible": prompt_injection_possible,
        "retriever_available": retriever_available,
        "low_trust": True,
        "source": parsed.source,
        "tool": parsed.mcp_tool,
        "rails": rails,
        "reason_codes": reason_codes,
        "next_safe_action": next_safe_action,
    }


def retrieve_mnemos_prompt_packet(
    config: MnemosPromptAdmissionConfig,
    *,
    query: str,
    retrieve: Callable[[dict[str, Any]], Any] | None,
) -> dict[str, Any]:
    """Run an injected synthetic retrieval seam and return a scored prompt packet.

    The adapter is deliberately dependency-injected for tests/canaries. It never
    looks up tools, opens a DB, or calls live MCP by itself; callers must provide
    a fake/tool callable. Any missing dependency, exception, malformed response,
    unsafe provenance, secret, or prompt-injection-shaped row fails closed with an
    empty prompt and telemetry only.
    """

    if not isinstance(config, MnemosPromptAdmissionConfig) or not config.activation_possible:
        return _adapter_reject(["disabled_or_inactive"], retrieval_attempted=False)
    if retrieve is None:
        return _adapter_reject(["missing_retrieval_tool"], retrieval_attempted=False)

    request = {
        "tool": config.mcp_tool,
        "source": config.source,
        "query": query,
        "max_items": config.max_items,
        "low_trust_required": config.require_low_trust,
        "allow_live_db": False,
        "allow_writes": False,
    }

    try:
        raw_response = retrieve(request)
    except Exception as exc:  # fail closed; never expose exception text
        return _adapter_reject(["retrieval_error"], retrieval_attempted=True, error_class=exc.__class__.__name__)

    response = _coerce_response(raw_response)
    if response is None:
        return _adapter_reject(["malformed_response"], retrieval_attempted=True, error_class="malformed_json")

    if response.get("tool") != MNEMOS_TOOL_NAME:
        return _adapter_reject(["tool_mismatch"], retrieval_attempted=True, error_class="malformed_response")
    if response.get("source") != ALLOWED_SYNTHETIC_SOURCE:
        return _adapter_reject(["source_mismatch"], retrieval_attempted=True, error_class="malformed_response")

    rows = response.get("rows")
    if not isinstance(rows, list):
        return _adapter_reject(["malformed_rows"], retrieval_attempted=True, error_class="malformed_response")

    scored = []
    unsafe_reasons: list[str] = []
    for row in rows[: config.max_items]:
        if not isinstance(row, Mapping):
            unsafe_reasons.append("malformed_row")
            continue
        candidate = dict(row)
        candidate.setdefault("source", response["source"])
        candidate.setdefault("query", query)
        if response.get("low_trust") is True:
            candidate.setdefault("low_trust", True)
        result = score_mnemos_candidate(candidate)
        scored.append(result)
        reason_codes = result.get("reason_codes", [])
        if result.get("redaction", {}).get("applied") or "R_SECRET_DETECTED" in reason_codes:
            unsafe_reasons.append("secret_row_rejected")
        if "R_PROMPT_INJECTION" in reason_codes or "R_TOOL_OR_RUNTIME_COMMAND" in reason_codes:
            unsafe_reasons.append("injection_row_rejected")

    if unsafe_reasons:
        return _adapter_reject(unsafe_reasons, retrieval_attempted=True)

    packet = build_mnemos_prompt_packet(scored, max_chars=config.max_chars, max_items=config.max_items)
    _attach_adapter_telemetry(
        packet,
        retrieval_attempted=True,
        fail_closed=packet.get("decision") == "reject",
        reason_codes=packet.get("reason_codes", []),
    )
    return packet


def _disabled(*reason_codes: str) -> MnemosPromptAdmissionConfig:
    return MnemosPromptAdmissionConfig(reason_codes=list(reason_codes) or ["disabled_by_default"])


def _coerce_response(raw_response: Any) -> dict[str, Any] | None:
    if isinstance(raw_response, str):
        try:
            raw_response = json.loads(raw_response)
        except json.JSONDecodeError:
            return None
    if not isinstance(raw_response, dict):
        return None
    return raw_response


def _adapter_reject(
    reason_codes: list[str],
    *,
    retrieval_attempted: bool,
    error_class: str | None = None,
) -> dict[str, Any]:
    packet = {
        "decision": "reject",
        "reason_codes": ["fail_closed", *reason_codes],
        "low_trust": True,
        "source": ALLOWED_SYNTHETIC_SOURCE,
        "prompt_text": "",
        "telemetry": {
            "candidate_count": 0,
            "admitted_count": 0,
            "summarized_count": 0,
            "rejected_count": 0,
        },
    }
    _attach_adapter_telemetry(
        packet,
        retrieval_attempted=retrieval_attempted,
        fail_closed=True,
        reason_codes=packet["reason_codes"],
        error_class=error_class,
    )
    return packet


def _attach_adapter_telemetry(
    packet: dict[str, Any],
    *,
    retrieval_attempted: bool,
    fail_closed: bool,
    reason_codes: list[str],
    error_class: str | None = None,
) -> None:
    packet.setdefault("telemetry", {})["adapter"] = {
        "retrieval_attempted": retrieval_attempted,
        "fail_closed": fail_closed,
        "tool": MNEMOS_TOOL_NAME,
        "source": ALLOWED_SYNTHETIC_SOURCE,
        "reason_codes": list(reason_codes),
        "error_class": error_class,
    }
