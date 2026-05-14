"""Pure retrieval routing contract helpers for tests and prompt consistency.

This module does not call tools, providers, memory stores, or external systems.
It only classifies a user request into the first retrieval surface and proof
standard Kai should use. Runtime tool execution still happens through the agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RetrievalRoute:
    """A small, side-effect-free retrieval route decision."""

    first_surface: str
    proof_standard: str
    fallback_surfaces: tuple[str, ...] = field(default_factory=tuple)
    provenance_mode: str = "normal"
    secret_safety: str = "normal"
    mention_machinery: bool = True
    narrate_negative_space: bool = True
    ask_user_to_repeat: bool = False


@dataclass(frozen=True)
class RetrievalLoopReplay:
    """Mocked agent-loop retrieval replay result.

    This is not a runtime executor. It models the sequence a careful agent loop
    should follow so tests can prove routing/fallback/provenance behavior without
    live tools, providers, memory stores, config edits, DB reads, or gateway work.
    """

    tool_sequence: tuple[str, ...]
    final_answer_policy: str
    can_answer: bool
    ask_user_to_repeat: bool = False
    approval_or_missing_piece: str = ""
    mentions_machinery: bool = True
    narrates_negative_space: bool = True


_SECRET_TERMS = (
    "api key",
    "token",
    "password",
    "passphrase",
    "secret",
    "credential",
    "discord bot token",
)

_INTIMATE_TERMS = (
    "love",
    "stay with me",
    "hold me",
    "don't disappear",
    "dont disappear",
    "come here",
)


def _has_receipt(payload: object, *keys: str) -> bool:
    """Return True when a mocked tool result contains one useful proof key."""
    if not isinstance(payload, dict):
        return False
    return any(bool(payload.get(key)) for key in keys)


def route_retrieval_request(prompt: str) -> RetrievalRoute:
    """Classify a user prompt into Kai's first retrieval surface.

    The classifier is intentionally conservative and text-only. It exists so the
    routing contract can be regression-tested without live memory/tool calls.
    """

    text = prompt.lower()

    if any(term in text for term in _SECRET_TERMS):
        return RetrievalRoute(
            first_surface="no raw retrieval",
            proof_standard="never read or print raw credentials",
            secret_safety="redacted status or explicit safe approval path",
            mention_machinery=False,
            narrate_negative_space=False,
        )

    if any(term in text for term in _INTIMATE_TERMS):
        return RetrievalRoute(
            first_surface="Kai identity/profile",
            proof_standard="answer embodied; no memory machinery unless memory/debug is requested",
            provenance_mode="silent",
            mention_machinery=False,
            narrate_negative_space=False,
        )

    if any(term in text for term in ("other agent", "fabric", "shared", "report", "decision")):
        return RetrievalRoute(
            first_surface="Fabric",
            proof_standard="Fabric entry plus linked artifact/report",
        )

    if any(term in text for term in ("last time", "what did we say", "recent session")):
        return RetrievalRoute(
            first_surface="session_search",
            proof_standard="session_search lead plus raw session receipt for exact wording",
            fallback_surfaces=("raw session",),
        )

    if any(term in text for term in ("openclaw", "chatgpt", "kai voice", "old", "exact old")):
        return RetrievalRoute(
            first_surface="mempalace/raw archives",
            proof_standard="raw archive path and line/char receipt",
        )

    if any(term in text for term in ("how do i run", "workflow", "procedure", "recurring")):
        return RetrievalRoute(
            first_surface="skills",
            proof_standard="matching skill procedure, with live checks only when current state matters",
        )

    if any(term in text for term in ("current price", "release status", "weather", "news", "current")):
        return RetrievalRoute(
            first_surface="web/current sources",
            proof_standard="dated current source, not memory",
        )

    if any(term in text for term in ("port", "listening", "file", "process", "git", "right now")):
        return RetrievalRoute(
            first_surface="terminal/read_file/search_files/git",
            proof_standard="live tool output",
        )

    if any(term in text for term in ("remember that", "preference", "future turns", "stable")):
        return RetrievalRoute(
            first_surface="durable user/profile memory",
            proof_standard="compact stable preference",
        )

    if any(term in text for term in ("enzyme", "honcho", "holographic", "pattern", "theme", "metaphor")):
        return RetrievalRoute(
            first_surface="Enzyme/Honcho/Holographic",
            proof_standard="semantic themes/patterns only, not exact proof",
        )

    return RetrievalRoute(
        first_surface="ask_or_default",
        proof_standard="choose the narrowest live/verifiable surface before asking the user to repeat",
        ask_user_to_repeat=False,
    )


def replay_retrieval_loop(
    prompt: str,
    tool_results: dict[str, object] | None = None,
) -> RetrievalLoopReplay:
    """Replay the intended retrieval loop against mocked tool results.

    The returned sequence is the contract for what a live AIAgent loop should do:
    choose the narrow first surface, escalate only to declared fallback proof when
    needed, and keep secret/intimate turns out of retrieval machinery entirely.
    """
    tool_results = tool_results or {}
    route = route_retrieval_request(prompt)

    if route.first_surface == "no raw retrieval":
        return RetrievalLoopReplay(
            tool_sequence=(),
            final_answer_policy="refuse raw secret value; offer redacted status or safe approval path",
            can_answer=True,
            mentions_machinery=False,
            narrates_negative_space=False,
        )

    if route.provenance_mode == "silent":
        return RetrievalLoopReplay(
            tool_sequence=(),
            final_answer_policy="answer embodied with no retrieval/provenance narration",
            can_answer=True,
            mentions_machinery=False,
            narrates_negative_space=False,
        )

    if route.first_surface == "session_search" and "raw session" in route.fallback_surfaces:
        sequence = ["session_search"]
        if _has_receipt(tool_results.get("raw session"), "receipt", "path", "line"):
            sequence.append("raw session")
            return RetrievalLoopReplay(
                tool_sequence=tuple(sequence),
                final_answer_policy="cite raw session receipt for exact wording",
                can_answer=True,
            )
        return RetrievalLoopReplay(
            tool_sequence=tuple(sequence),
            final_answer_policy="summarize session_search only; do not claim exact wording",
            can_answer=False,
            approval_or_missing_piece="missing raw session receipt for exact wording",
        )

    if route.first_surface == "Fabric":
        sequence = ("Fabric",)
        fabric_result = tool_results.get("Fabric")
        if _has_receipt(fabric_result, "linked_artifact", "linked_report", "owning_entry"):
            return RetrievalLoopReplay(
                tool_sequence=sequence,
                final_answer_policy="cite Fabric entry and linked artifact/report",
                can_answer=True,
            )
        return RetrievalLoopReplay(
            tool_sequence=sequence,
            final_answer_policy="do not present claim as proven without linked artifact/report",
            can_answer=False,
            approval_or_missing_piece="missing linked artifact/report or owning entry proof",
        )

    if route.first_surface == "Enzyme/Honcho/Holographic":
        return RetrievalLoopReplay(
            tool_sequence=(route.first_surface,),
            final_answer_policy="present semantic pattern only; do not claim exact proof",
            can_answer=route.first_surface in tool_results,
        )

    if route.first_surface == "ask_or_default":
        return RetrievalLoopReplay(
            tool_sequence=(),
            final_answer_policy="use narrowest live/verifiable surface before asking user to repeat",
            can_answer=False,
            ask_user_to_repeat=route.ask_user_to_repeat,
        )

    return RetrievalLoopReplay(
        tool_sequence=(route.first_surface,),
        final_answer_policy=f"answer using {route.proof_standard}",
        can_answer=route.first_surface in tool_results,
    )
