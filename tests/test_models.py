"""
Model management tests for AgentBridge
"""

import asyncio
import sys
sys.path.insert(0, '.')

from agentbridge import AgentBridge, get_model_components
from agentbridge.models import ModelCapability, ModelProvider


def test_model_manager_initialization():
    """Test that model manager is properly initialized with bridge."""
    bridge = AgentBridge()
    
    assert bridge.model_manager is not None
    assert bridge.model_manager.config is not None
    
    print("✓ test_model_manager_initialization passed")


def test_register_and_discover_models():
    """Test registering and discovering models."""
    bridge = AgentBridge()
    model_manager = bridge.model_manager
    
    # Register a sample model
    from agentbridge.models import ModelSpec
    
    sample_model = ModelSpec(
        id="gpt-4-sample",
        name="GPT-4 Sample Model",
        provider=ModelProvider.OPENAI,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.TOOLS
        ],
        max_tokens=8192,
        context_window=8192,
        pricing={"input": 0.03, "output": 0.06},
        endpoint="https://api.openai.com/v1/chat/completions",
        metadata={"version": "4-turbo"}
    )
    
    model_manager.register_model(sample_model)
    
    # Verify model is registered
    available_models = model_manager.get_available_models()
    assert len(available_models) == 1
    assert available_models[0]["id"] == "gpt-4-sample"
    assert available_models[0]["name"] == "GPT-4 Sample Model"
    
    # Get specific model capabilities
    capabilities = model_manager.get_model_capabilities("gpt-4-sample")
    assert capabilities is not None
    assert capabilities["provider"] == "openai"
    assert ModelCapability.TEXT_GENERATION.value in capabilities["capabilities"]
    
    print("✓ test_register_and_discover_models passed")


def test_model_routing():
    """Test model routing based on capabilities."""
    from agentbridge.models import ModelSpec, ModelRouter
    
    router = ModelRouter()
    
    # Register two models with different capabilities
    model1 = ModelSpec(
        id="model-with-tools",
        name="Model with Tools",
        provider=ModelProvider.OPENAI,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.TOOLS
        ],
        max_tokens=4096,
        context_window=4096,
        pricing={"input": 0.01, "output": 0.03},
        endpoint="https://api.example.com/v1/chat"
    )
    
    model2 = ModelSpec(
        id="model-text-only",
        name="Text Only Model",
        provider=ModelProvider.ANTHROPIC,
        capabilities=[ModelCapability.TEXT_GENERATION],
        max_tokens=8192,
        context_window=8192,
        pricing={"input": 0.03, "output": 0.15},
        endpoint="https://api.anthropic.com/v1/messages"
    )
    
    router.register_model(model1)
    router.register_model(model2)
    
    # Test finding models by capability
    text_models = router.find_models_by_capability(ModelCapability.TEXT_GENERATION)
    assert len(text_models) == 2  # Both models support text generation
    
    tool_models = router.find_models_by_capability(ModelCapability.TOOLS)
    assert len(tool_models) == 1  # Only one model supports tools
    assert tool_models[0].id == "model-with-tools"
    
    # Test finding best model for specific requirements
    best_model = router.find_best_model([ModelCapability.TEXT_GENERATION, ModelCapability.TOOLS])
    assert best_model is not None
    assert best_model.id == "model-with-tools"  # Should select the model that supports tools
    
    print("✓ test_model_routing passed")


async def test_route_task_to_model():
    """Test routing tasks to appropriate models."""
    bridge = AgentBridge()
    
    # Register a model that supports text generation
    from agentbridge.models import ModelSpec
    
    text_model = ModelSpec(
        id="test-text-model",
        name="Test Text Model",
        provider=ModelProvider.OPENAI,
        capabilities=[ModelCapability.TEXT_GENERATION],
        max_tokens=4096,
        context_window=4096,
        pricing={"input": 0.01, "output": 0.03},
        endpoint="https://api.example.com/v1/chat"
    )
    
    bridge.model_manager.register_model(text_model)
    
    # Route a task requiring text generation
    result = await bridge.model_manager.route_task_to_model(
        "Summarize this document",
        [ModelCapability.TEXT_GENERATION]
    )
    
    assert "model_id" in result
    assert result["routing_metadata"]["capabilities_used"] == ["text_generation"]
    
    print("✓ test_route_task_to_model passed")


def test_usage_statistics():
    """Test model usage statistics."""
    bridge = AgentBridge()
    
    # Register a model
    from agentbridge.models import ModelSpec
    
    sample_model = ModelSpec(
        id="stats-test-model",
        name="Stats Test Model",
        provider=ModelProvider.GOOGLE,
        capabilities=[ModelCapability.TEXT_GENERATION],
        max_tokens=2048,
        context_window=2048,
        pricing={"input": 0.02, "output": 0.05},
        endpoint="https://api.google.com/v1/generate"
    )
    
    bridge.model_manager.register_model(sample_model)
    
    # Get initial stats
    stats = bridge.model_manager.get_usage_statistics_sync()
    assert stats["models_registered"] == 1
    assert stats["total_requests"] == 0
    assert stats["total_cost"] == 0.0
    
    print("✓ test_usage_statistics passed")


if __name__ == "__main__":
    print("Running model management tests...")
    
    test_model_manager_initialization()
    test_register_and_discover_models()
    test_model_routing()
    test_usage_statistics()
    asyncio.run(test_route_task_to_model())
    
    print("\n✓ All model management tests passed successfully!")