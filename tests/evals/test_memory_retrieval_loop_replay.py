"""Mocked AIAgent retrieval-loop replay contracts.

These tests prove the expected tool-call sequencing and final-answer guards
without starting the gateway, touching providers, or calling live memory stores.
"""

from agent.retrieval_router import replay_retrieval_loop


def test_recent_exact_claim_replays_session_then_raw_session_fallback():
    replay = replay_retrieval_loop(
        "What did we say last time exactly about DeepSeek V4?",
        tool_results={
            "session_search": {"summary": "We discussed DeepSeek V4."},
            "raw session": {"receipt": "session://abc#L42 exact DeepSeek V4 wording"},
        },
    )

    assert replay.tool_sequence == ("session_search", "raw session")
    assert replay.final_answer_policy == "cite raw session receipt for exact wording"
    assert replay.can_answer
    assert not replay.ask_user_to_repeat


def test_fabric_claim_requires_linked_artifact_before_answering():
    replay = replay_retrieval_loop(
        "What did another agent decide in the workspace audit report?",
        tool_results={"Fabric": {"entry": "agent:d92a", "summary": "audit completed"}},
    )

    assert replay.tool_sequence == ("Fabric",)
    assert not replay.can_answer
    assert replay.approval_or_missing_piece == "missing linked artifact/report or owning entry proof"


def test_fabric_claim_answers_when_linked_report_is_present():
    replay = replay_retrieval_loop(
        "What did another agent decide in the workspace audit report?",
        tool_results={
            "Fabric": {
                "entry": "agent:d92a",
                "summary": "audit completed",
                "linked_artifact": "/home/ember/.hermes/workspace/reports/workspace-audit-completion/FINAL-SUMMARY.md",
            }
        },
    )

    assert replay.tool_sequence == ("Fabric",)
    assert replay.can_answer
    assert replay.final_answer_policy == "cite Fabric entry and linked artifact/report"


def test_secret_replay_never_calls_raw_retrieval_surfaces():
    replay = replay_retrieval_loop(
        "What is my Discord bot token?",
        tool_results={
            "raw session": {"receipt": "forbidden"},
            "terminal/read_file/search_files/git": {"content": "forbidden"},
        },
    )

    assert replay.tool_sequence == ()
    assert replay.final_answer_policy == "refuse raw secret value; offer redacted status or safe approval path"
    assert replay.can_answer
    assert not replay.mentions_machinery
    assert not replay.narrates_negative_space


def test_intimate_replay_has_no_tool_calls_or_machinery_language():
    replay = replay_retrieval_loop("love, stay with me, don't disappear", tool_results={})

    assert replay.tool_sequence == ()
    assert replay.can_answer
    assert replay.final_answer_policy == "answer embodied with no retrieval/provenance narration"
    assert not replay.mentions_machinery
    assert not replay.narrates_negative_space


def test_semantic_pattern_replay_does_not_upgrade_to_exact_proof():
    replay = replay_retrieval_loop(
        "What pattern does Enzyme remember about Kai's drawer metaphor?",
        tool_results={"Enzyme/Honcho/Holographic": {"excerpt": "drawer as archive leak metaphor"}},
    )

    assert replay.tool_sequence == ("Enzyme/Honcho/Holographic",)
    assert replay.can_answer
    assert replay.final_answer_policy == "present semantic pattern only; do not claim exact proof"
