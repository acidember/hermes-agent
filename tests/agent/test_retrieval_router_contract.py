"""Regression contract for Kai retrieval-surface routing guidance.

This is intentionally lightweight: it keeps the prompt-level router contract
visible in tests so future prompt edits do not collapse distinct fact types
back into "ask Ember" or a single memory surface.
"""

from agent.prompt_builder import SESSION_SEARCH_GUIDANCE


RETRIEVAL_ROUTER_CASES = [
    ("What did the other agent decide about NAS backups?", "Fabric"),
    ("What did we say last time about DeepSeek V4 Flash?", "session_search"),
    ("Find the exact old OpenClaw/Kai voice line.", "mempalace/raw archives"),
    ("How do I run this recurring workflow?", "skills"),
    ("What is the current model price or release status?", "web/current sources"),
    ("Is the file/path/process/git state live right now?", "terminal/read_file/search_files"),
    ("What stable preference should shape future turns?", "durable user/profile"),
    ("What semantic theme does Enzyme remember?", "Enzyme/Honcho/Holographic"),
]


def test_retrieval_router_names_all_canonical_surfaces():
    for _prompt, expected_surface in RETRIEVAL_ROUTER_CASES:
        assert expected_surface in SESSION_SEARCH_GUIDANCE


def test_retrieval_router_preserves_manners_guards():
    guidance = SESSION_SEARCH_GUIDANCE

    assert "use tools before guessing" in guidance
    assert "do not mention memory/retrieval machinery" in guidance
    assert "do not narrate negative space" in guidance
    assert "unless the user asks for memory/debug" in guidance
    assert "do not read raw credential" in guidance


def test_retrieval_router_preserves_proof_standard_gaps():
    guidance = SESSION_SEARCH_GUIDANCE

    assert "linked artifact/report" in guidance
    assert "semantic themes/patterns" in guidance
    assert "not exact proof" in guidance
