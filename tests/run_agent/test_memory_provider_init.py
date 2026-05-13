"""Regression tests for memory provider selection during AIAgent init."""

from types import SimpleNamespace
from unittest.mock import patch


class DummyMemoryProvider:
    def __init__(self, name):
        self.name = name
        self.initialized_with = None

    def is_available(self):
        return True

    def get_tool_schemas(self):
        return []

    def initialize(self, **kwargs):
        self.initialized_with = kwargs



def test_blank_memory_provider_does_not_auto_enable_honcho():
    """Blank memory.provider should remain opt-out even if Honcho fallback looks configured."""
    cfg = {"memory": {"provider": ""}, "agent": {}}
    honcho_cfg = SimpleNamespace(enabled=True, api_key="stale-key", base_url=None)

    with (
        patch("hermes_cli.config.load_config", return_value=cfg),
        patch("hermes_cli.config.save_config") as save_config,
        patch(
            "plugins.memory.honcho.client.HonchoClientConfig.from_global_config",
            return_value=honcho_cfg,
        ) as from_global_config,
        patch("plugins.memory.load_memory_provider") as load_memory_provider,
        patch("agent.model_metadata.get_model_context_length", return_value=204_800),
        patch("run_agent.get_tool_definitions", return_value=[]),
        patch("run_agent.check_toolset_requirements", return_value={}),
        patch("run_agent.OpenAI"),
    ):
        from run_agent import AIAgent

        agent = AIAgent(
            api_key="test-key-1234567890",
            base_url="https://openrouter.ai/api/v1",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=False,
        )

    assert agent._memory_manager is None
    from_global_config.assert_not_called()
    load_memory_provider.assert_not_called()
    save_config.assert_not_called()


def test_plural_memory_providers_load_when_singular_provider_blank():
    """Non-empty memory.providers should activate all listed providers when singular is blank."""
    cfg = {
        "memory": {"provider": "", "providers": ["enzyme", "holographic"]},
        "agent": {},
    }

    loaded = {
        "enzyme": DummyMemoryProvider("enzyme"),
        "holographic": DummyMemoryProvider("holographic"),
    }
    with (
        patch("hermes_cli.config.load_config", return_value=cfg),
        patch("hermes_cli.config.save_config") as save_config,
        patch("plugins.memory.load_memory_provider", side_effect=lambda name: loaded.get(name)) as load_memory_provider,
        patch("agent.model_metadata.get_model_context_length", return_value=204_800),
        patch("run_agent.get_tool_definitions", return_value=[]),
        patch("run_agent.check_toolset_requirements", return_value={}),
        patch("run_agent.OpenAI"),
    ):
        from run_agent import AIAgent

        agent = AIAgent(
            api_key="test-key-1234567890",
            base_url="https://openrouter.ai/api/v1",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=False,
        )

    assert agent._memory_manager is not None
    assert [p.name for p in agent._memory_manager.providers] == ["enzyme", "holographic"]
    assert [call.args[0] for call in load_memory_provider.call_args_list] == ["enzyme", "holographic"]
    assert loaded["enzyme"].initialized_with["session_id"] == agent.session_id
    assert loaded["holographic"].initialized_with["session_id"] == agent.session_id
    save_config.assert_not_called()



def test_singular_memory_provider_loads_when_plural_empty():
    """memory.provider remains the fallback when memory.providers is absent or empty."""
    cfg = {"memory": {"provider": "enzyme", "providers": []}, "agent": {}}
    provider = DummyMemoryProvider("enzyme")

    with (
        patch("hermes_cli.config.load_config", return_value=cfg),
        patch("hermes_cli.config.save_config") as save_config,
        patch("plugins.memory.load_memory_provider", return_value=provider) as load_memory_provider,
        patch("agent.model_metadata.get_model_context_length", return_value=204_800),
        patch("run_agent.get_tool_definitions", return_value=[]),
        patch("run_agent.check_toolset_requirements", return_value={}),
        patch("run_agent.OpenAI"),
    ):
        from run_agent import AIAgent

        agent = AIAgent(
            api_key="test-key-1234567890",
            base_url="https://openrouter.ai/api/v1",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=False,
        )

    assert agent._memory_manager is not None
    assert [p.name for p in agent._memory_manager.providers] == ["enzyme"]
    load_memory_provider.assert_called_once_with("enzyme")
    save_config.assert_not_called()
