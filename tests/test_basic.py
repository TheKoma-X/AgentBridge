"""
Basic tests for AgentBridge
"""

import asyncio
import sys
sys.path.insert(0, '.')

from agentbridge import AgentBridge
from agentbridge.protocol import Message, MessageType
from agentbridge.adapter import AdapterRegistry


def test_bridge_initialization():
    """Test that the bridge initializes correctly."""
    bridge = AgentBridge()
    assert bridge is not None
    assert hasattr(bridge, 'adapters')
    assert hasattr(bridge, 'protocol')
    assert hasattr(bridge, 'adapter_registry')
    assert isinstance(bridge.adapters, dict)
    assert len(bridge.adapters) == 0
    print("✓ test_bridge_initialization passed")


def test_protocol_creation():
    """Test that the bridge has a valid protocol."""
    bridge = AgentBridge()
    assert bridge.protocol is not None
    assert hasattr(bridge.protocol, 'register_protocol')
    assert hasattr(bridge.protocol, 'translate_message')
    print("✓ test_protocol_creation passed")


def test_adapter_registry():
    """Test that the bridge has a valid adapter registry."""
    bridge = AgentBridge()
    assert bridge.adapter_registry is not None
    assert isinstance(bridge.adapter_registry, AdapterRegistry)
    
    # Check that default adapters are registered
    adapters = bridge.adapter_registry.list_adapters()
    expected_adapters = ['crewai', 'langgraph', 'autogen', 'claude-flow', 'claude_flow']
    for adapter in expected_adapters:
        assert adapter in adapters
    print("✓ test_adapter_registry passed")


def test_create_message():
    """Test creating a message through the protocol."""
    import time
    timestamp = time.time()
    
    message = Message(
        type=MessageType.TASK_REQUEST,
        source="test_source",
        target="test_target",
        content={"task": "test_task"},
        timestamp=timestamp
    )
    
    assert message.type == MessageType.TASK_REQUEST
    assert message.source == "test_source"
    assert message.target == "test_target"
    assert message.content == {"task": "test_task"}
    assert message.timestamp == timestamp
    print("✓ test_create_message passed")


def test_protocol_translate_message():
    """Test message translation."""
    import time
    bridge = AgentBridge()
    timestamp = time.time()
    
    original_message = Message(
        type=MessageType.TASK_REQUEST,
        source="test_source",
        target="test_target",
        content={"task": "test_task"},
        timestamp=timestamp
    )
    
    # Translate message (source and target protocols are the same for this test)
    translated_message = bridge.protocol.translate_message(
        original_message, "test_v1", "test_v1"
    )
    
    assert translated_message.type == original_message.type
    assert translated_message.source == original_message.source
    assert translated_message.target == original_message.target
    assert translated_message.content == original_message.content
    print("✓ test_protocol_translate_message passed")


def test_bridge_status():
    """Test getting bridge status."""
    bridge = AgentBridge()
    status = bridge.get_status()
    
    assert isinstance(status, dict)
    assert "connected_frameworks" in status
    assert "adapter_count" in status
    assert "registry_status" in status
    assert "config_loaded" in status
    assert "metrics" in status  # New addition
    
    assert status["adapter_count"] == 0
    assert len(status["connected_frameworks"]) == 0
    # Config is now loaded by default with default values
    assert status["config_loaded"] is True  # Changed from False
    print("✓ test_bridge_status passed")


def test_bridge_connect_framework_not_registered():
    """Test connecting to an unregistered framework."""
    bridge = AgentBridge()
    
    try:
        bridge.connect_framework("nonexistent_framework", "http://example.com")
        assert False, "Expected ValueError was not raised"
    except ValueError:
        pass  # Expected
    print("✓ test_bridge_connect_framework_not_registered passed")


async def test_adapter_registry_operations():
    """Test adapter registry operations."""
    registry = AdapterRegistry()
    
    # Test listing adapters
    adapters = registry.list_adapters()
    assert len(adapters) > 0  # Should have default adapters
    
    # Test getting an existing adapter
    adapter_class = registry.get_adapter("crewai")
    assert adapter_class is not None
    
    # Test getting a non-existing adapter
    adapter_class = registry.get_adapter("nonexistent")
    assert adapter_class is None
    
    # Test registering a new adapter
    class TestAdapter:
        pass
    
    registry.register("test_framework", TestAdapter)
    assert registry.get_adapter("test_framework") is TestAdapter
    print("✓ test_adapter_registry_operations passed")


if __name__ == "__main__":
    print("Running AgentBridge tests...")
    
    # Run synchronous tests
    test_bridge_initialization()
    test_protocol_creation()
    test_adapter_registry()
    test_create_message()
    test_protocol_translate_message()
    test_bridge_status()
    test_bridge_connect_framework_not_registered()
    
    # Run asynchronous tests
    asyncio.run(test_adapter_registry_operations())
    
    print("\\n✓ All tests passed successfully!")
