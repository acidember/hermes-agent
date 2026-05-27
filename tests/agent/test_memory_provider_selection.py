from agent.memory_provider_selection import resolve_memory_provider_names


def test_legacy_single_provider_wins_when_mesh_disabled_even_if_providers_list_exists():
    config = {
        "provider": "honcho",
        "providers": ["enzyme", "holographic"],
    }

    assert resolve_memory_provider_names(config) == ["honcho"]


def test_mesh_must_be_explicitly_enabled_before_providers_list_is_used():
    config = {
        "provider": "honcho",
        "providers": ["enzyme", "holographic"],
        "multi_provider_enabled": True,
    }

    assert resolve_memory_provider_names(config) == ["honcho", "enzyme", "holographic"]


def test_mesh_selection_deduplicates_and_drops_empty_names():
    config = {
        "provider": " honcho ",
        "providers": ["enzyme", "", "honcho", " holographic "],
        "multi_provider_enabled": True,
    }

    assert resolve_memory_provider_names(config) == ["honcho", "enzyme", "holographic"]


def test_mesh_without_legacy_provider_uses_ordered_providers_list_when_enabled():
    config = {
        "providers": ["enzyme", "holographic"],
        "multi_provider_enabled": True,
    }

    assert resolve_memory_provider_names(config) == ["enzyme", "holographic"]


def test_empty_config_returns_no_external_providers():
    assert resolve_memory_provider_names({}) == []
