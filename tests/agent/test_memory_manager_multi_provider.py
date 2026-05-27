from agent.memory_manager import MemoryManager
from agent.memory_provider import MemoryProvider


class DummyProvider(MemoryProvider):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return True

    def initialize(self, session_id: str, **kwargs) -> None:
        pass

    def get_tool_schemas(self):
        return []


def test_memory_manager_keeps_single_external_provider_default():
    manager = MemoryManager()

    manager.add_provider(DummyProvider("honcho"))
    manager.add_provider(DummyProvider("enzyme"))

    assert [provider.name for provider in manager.providers] == ["honcho"]


def test_memory_manager_can_be_explicitly_constructed_for_multiple_external_providers():
    manager = MemoryManager(allow_multiple_external=True)

    manager.add_provider(DummyProvider("honcho"))
    manager.add_provider(DummyProvider("enzyme"))
    manager.add_provider(DummyProvider("holographic"))

    assert [provider.name for provider in manager.providers] == [
        "honcho",
        "enzyme",
        "holographic",
    ]
