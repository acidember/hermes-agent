"""Memory provider selection helpers.

This module is intentionally policy-only: it decides which provider names should
be loaded from the memory config, but it does not import or initialize providers.
That keeps the Honcho/Enzyme/Holographic mesh behind an explicit feature flag
instead of accidentally activating the existing ``memory.providers`` list.
"""

from __future__ import annotations

from typing import Any


def _clean_provider_name(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def resolve_memory_provider_names(memory_config: dict[str, Any] | None) -> list[str]:
    """Return external memory provider names to initialize, in order.

    Backward compatibility and safety rule:
    - By default Hermes honors only ``memory.provider``.
    - ``memory.providers`` is ignored unless ``multi_provider_enabled`` is true.

    This prevents a stale or experimental provider list from silently becoming
    live on the default gateway after a restart.
    """
    if not isinstance(memory_config, dict):
        return []

    legacy_provider = _clean_provider_name(memory_config.get("provider"))
    multi_enabled = bool(memory_config.get("multi_provider_enabled", False))

    raw_names: list[Any]
    if multi_enabled:
        raw_names = []
        if legacy_provider:
            raw_names.append(legacy_provider)
        providers = memory_config.get("providers", [])
        if isinstance(providers, (list, tuple)):
            raw_names.extend(providers)
    else:
        raw_names = [legacy_provider] if legacy_provider else []

    names: list[str] = []
    seen: set[str] = set()
    for raw in raw_names:
        name = _clean_provider_name(raw)
        if not name or name in seen:
            continue
        names.append(name)
        seen.add(name)
    return names
