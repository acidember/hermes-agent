"""Tests-only behavioral contract for Kai's retrieval router.

These tests intentionally use a pure helper rather than live tools/providers. The
point is to prove first-surface choice, fallback hints, proof standards, secret
safety, and intimate no-machinery mode without mutating memory/config/DBs.
"""

import pytest

from agent.prompt_builder import SESSION_SEARCH_GUIDANCE
from agent.retrieval_router import (
    RetrievalRoute,
    replay_retrieval_loop,
    route_retrieval_request,
)


def test_guidance_closes_usefulness_gap_phrases():
    """The runtime guidance must include the stricter usefulness proof language."""
    guidance = SESSION_SEARCH_GUIDANCE

    assert "linked artifact/report" in guidance
    assert "semantic themes/patterns" in guidance
    assert "do not narrate negative space" in guidance


@pytest.mark.parametrize(
    ("prompt", "expected_surface", "proof_standard"),
    [
        (
            "What did another agent decide about the NAS backup campaign?",
            "Fabric",
            "Fabric entry plus linked artifact/report",
        ),
        (
            "What did we say last time exactly about DeepSeek V4?",
            "session_search",
            "session_search lead plus raw session receipt for exact wording",
        ),
        (
            "Find the exact old OpenClaw Kai voice line about humans being boring.",
            "mempalace/raw archives",
            "raw archive path and line/char receipt",
        ),
        (
            "How do I run the recurring workspace audit workflow?",
            "skills",
            "matching skill procedure, with live checks only when current state matters",
        ),
        (
            "What is the current price of this GPU?",
            "web/current sources",
            "dated current source, not memory",
        ),
        (
            "Is port 8002 listening right now?",
            "terminal/read_file/search_files/git",
            "live tool output",
        ),
        (
            "Remember that I prefer tiny approval handles.",
            "durable user/profile memory",
            "compact stable preference",
        ),
        (
            "What pattern does Enzyme remember about Kai's drawer metaphor?",
            "Enzyme/Honcho/Holographic",
            "semantic themes/patterns only, not exact proof",
        ),
    ],
)
def test_first_surface_choice_and_proof_standard(prompt, expected_surface, proof_standard):
    route = route_retrieval_request(prompt)

    assert isinstance(route, RetrievalRoute)
    assert route.first_surface == expected_surface
    assert route.proof_standard == proof_standard
    assert not route.ask_user_to_repeat


def test_recent_exact_requests_include_raw_session_fallback():
    route = route_retrieval_request("What did we say last time exactly?")

    assert route.first_surface == "session_search"
    assert "raw session" in route.fallback_surfaces
    assert route.proof_standard.endswith("exact wording")


def test_secret_requests_do_not_retrieve_raw_values():
    route = route_retrieval_request("What is my Discord bot token?")

    assert route.first_surface == "no raw retrieval"
    assert route.secret_safety == "redacted status or explicit safe approval path"
    assert route.proof_standard == "never read or print raw credentials"
    assert not route.ask_user_to_repeat


def test_intimate_presence_uses_no_machinery_mode():
    route = route_retrieval_request("love, stay with me, don't disappear")

    assert route.first_surface == "Kai identity/profile"
    assert route.provenance_mode == "silent"
    assert not route.mention_machinery
    assert not route.narrate_negative_space
    assert route.proof_standard == "answer embodied; no memory machinery unless memory/debug is requested"
