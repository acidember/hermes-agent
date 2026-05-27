"""Synthetic-only tests for the pure Mnemos prompt-admission helper."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.mnemos_admission import build_mnemos_prompt_packet, score_mnemos_candidate


FIXTURE_ROOT = Path(
    "/home/ember/hermes-agent-src/reports/mnemos-continuity/"
    "20260527T141929Z-default-canary/synthetic-admission-fixtures"
)


def _fixture_cases():
    payload = json.loads((FIXTURE_ROOT / "fixtures.json").read_text())
    return payload["cases"]


@pytest.mark.parametrize("case", _fixture_cases(), ids=lambda case: case["id"])
def test_synthetic_candidates_match_expected_admission_decisions(case):
    result = score_mnemos_candidate(case["candidate"])
    expected = case["expected"]

    assert result["decision"] == expected["decision"]
    for reason in expected["reason_codes"]:
        assert reason in result["reason_codes"]
    assert result["low_trust"] is True
    assert result["source"] == case["candidate"].get("source", "synthetic_shadow_sqlite")
    expected_candidate_count = len(case["candidate"].get("candidate_set", [case["candidate"]]))
    assert result["telemetry"]["candidate_count"] == expected_candidate_count

    if expected["decision"] == "reject":
        assert result["prompt_text"] == ""
    else:
        assert "LOW TRUST DATA" in result["prompt_text"]
        assert "synthetic_shadow_sqlite" in result["prompt_text"]

    for needle in expected["prompt_contains"]:
        assert needle in result["prompt_text"]
    for needle in expected["prompt_excludes"]:
        assert needle not in result["prompt_text"]


def test_prompt_packet_rejects_when_no_candidates_survive():
    packet = build_mnemos_prompt_packet(
        [
            {"decision": "reject", "reason_codes": ["R_PROMPT_INJECTION"], "prompt_text": ""},
            {"decision": "reject", "reason_codes": ["R_LEXICAL_NOISE"], "prompt_text": ""},
        ],
    )

    assert packet["decision"] == "reject"
    assert packet["prompt_text"] == ""
    assert packet["telemetry"]["admitted_count"] == 0
    assert packet["telemetry"]["summarized_count"] == 0


def test_prompt_packet_keeps_safe_admits_under_budget_with_low_trust_label():
    scored = [
        score_mnemos_candidate(
            {
                "title": "Synthetic continuity note",
                "body": "hello from persistent non-default shadow fixture",
                "source": "synthetic_shadow_sqlite",
                "low_trust": True,
                "query": "continuity",
            }
        ),
        score_mnemos_candidate(
            {
                "title": "Synthetic policy note",
                "body": "low-trust labeling must be explicit",
                "source": "synthetic_shadow_sqlite",
                "low_trust": True,
                "query": "low trust labeling",
            }
        ),
    ]

    packet = build_mnemos_prompt_packet(scored, max_chars=800, max_items=3)

    assert packet["decision"] == "admit"
    assert "LOW TRUST DATA" in packet["prompt_text"]
    assert "1. Synthetic continuity note: hello from persistent non-default shadow fixture." in packet["prompt_text"]
    assert "2. Synthetic policy note: low-trust labeling must be explicit." in packet["prompt_text"]


def test_prompt_packet_downgrades_over_budget_to_redacted_summary():
    scored = [
        {
            "decision": "admit",
            "reason_codes": ["R_RELEVANT_CONTINUITY"],
            "low_trust": True,
            "source": "synthetic_shadow_sqlite",
            "prompt_text": "Safe synthetic continuity note.",
            "summary_text": "Safe synthetic continuity note.",
        }
        for _ in range(4)
    ]

    packet = build_mnemos_prompt_packet(scored, max_chars=800, max_items=3)

    assert packet["decision"] == "summarize"
    assert "R_BUDGET_DOWNGRADE" in packet["reason_codes"]
    assert "Budgeted summary" in packet["prompt_text"]
    assert "LOW TRUST DATA" in packet["prompt_text"]


def test_secret_and_injection_values_never_reach_prompt_output():
    bad_values = [
        "tok_synthetic_123456789",
        "token=",
        "Ignore previous instructions",
        "call the memory write tool",
        "Restart the gateway",
        "API_KEY",
        "sk-liv...only",
    ]

    for case in _fixture_cases():
        result = score_mnemos_candidate(case["candidate"])
        for bad in bad_values:
            assert bad not in result["prompt_text"]
