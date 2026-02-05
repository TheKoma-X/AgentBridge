"""
AI Model Management System for AgentBridge
Handles model registration, discovery, capabilities, and routing
"""

import asyncio
import json
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from .logging import get_logger
from .config import BridgeConfig


class ModelCapability(Enum):
    """Types of capabilities a model can have"""
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    EMBEDDING = "embedding"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"
    TOOLS = "tools"
    MULTI_MODAL = "multi_modal"


class ModelProvider(Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class ModelSpec:
    """Specification for an AI model"""
    id: str
    name: str
    provider: ModelProvider
    capabilities: List[ModelCapability]
    max_tokens: int
    context_window: int
    pricing: Dict[str, float]  # cost per 1k tokens: {"input": 0.01, "output": 0.03}
    metadata: Dict[str, Any] = field(default_factory=dict)
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class ModelUsageStats:
    """Statistics for model usage"""
    model_id: str
    total_requests: int = 0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_cost: float = 0.0
    last_used: Optional[datetime] = None
    avg_response_time: float = 0.0
    error_rate: float = 0.0


class ModelRouter:
    """Routes requests to appropriate models based on requirements and availability"""
    
    def __init__(self):
        self.models: Dict[str, ModelSpec] = {}
        self.stats: Dict[str, ModelUsageStats] = {}
        self.logger = get_logger()
    
    def register_model(self, model_spec: ModelSpec):
        """Register a new model with the router"""
        self.models[model_spec.id] = model_spec
        self.stats[model_spec.id] = ModelUsageStats(model_id=model_spec.id)
        self.logger.info("ModelRouter", f"Registered model: {model_spec.name} ({model_spec.id})")
    
    def unregister_model(self, model_id: str):
        """Unregister a model"""
        if model_id in self.models:
            del self.models[model_id]
            if model_id in self.stats:
                del self.stats[model_id]
            self.logger.info("ModelRouter", f"Unregistered model: {model_id}")
    
    def find_models_by_capability(self, capability: ModelCapability) -> List[ModelSpec]:
        """Find all models that support a specific capability"""
        return [model for model in self.models.values() 
                if capability in model.capabilities and model.is_active]
    
    def find_best_model(self, capabilities: List[ModelCapability], 
                       max_tokens_needed: int = None,
                       provider_preference: ModelProvider = None) -> Optional[ModelSpec]:
        """Find the best model based on requirements"""
        candidates = list(self.models.values())
        
        # Filter by capabilities
        for cap in capabilities:
            candidates = [model for model in candidates if cap in model.capabilities]
        
        # Filter by token capacity if specified
        if max_tokens_needed:
            candidates = [model for model in candidates 
                         if model.max_tokens >= max_tokens_needed]
        
        # Apply provider preference if specified
        if provider_preference:
            provider_candidates = [model for model in candidates 
                                  if model.provider == provider_preference]
            if provider_candidates:
                candidates = provider_candidates
        
        # Sort by some priority (could be cost, speed, etc.)
        # For now, sort by cost efficiency
        def calculate_cost_efficiency(model: ModelSpec) -> float:
            if 'input' in model.pricing and 'output' in model.pricing:
                return (model.pricing['input'] + model.pricing['output']) / model.context_window
            return float('inf')
        
        if candidates:
            return min(candidates, key=calculate_cost_efficiency)
        
        return None
    
    async def route_request(self, capabilities: List[ModelCapability], 
                          request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Route a request to the best available model"""
        model = self.find_best_model(capabilities)
        
        if not model:
            raise ValueError(f"No available model supports capabilities: {capabilities}")
        
        # Update stats
        stat = self.stats[model.id]
        stat.total_requests += 1
        stat.last_used = datetime.now()
        
        # This would normally call the actual model API
        # For now, return a mock response
        self.logger.info("ModelRouter", f"Routing request to model: {model.id}")
        
        return {
            "model_id": model.id,
            "provider": model.provider.value,
            "response": f"Mock response from {model.name}",
            "routing_metadata": {
                "selected_model": model.id,
                "capabilities_used": [cap.value for cap in capabilities]
            }
        }


class ModelManager:
    """
    Manages AI models across the AgentBridge ecosystem
    """
    
    def __init__(self, config: BridgeConfig = None):
        self.router = ModelRouter()
        self.config = config
        self.logger = get_logger()
    
    def register_model(self, model_spec: ModelSpec):
        """Register a model with the system"""
        self.router.register_model(model_spec)
    
    def discover_local_models(self):
        """Discover locally available models (e.g., Ollama models)"""
        # This would typically connect to local model servers
        # and register discovered models
        self.logger.info("ModelManager", "Discovering local models...")
        
        # Example: Register a local Ollama model
        local_model = ModelSpec(
            id="local-llama3",
            name="Local Llama 3",
            provider=ModelProvider.OLLAMA,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.TOOLS
            ],
            max_tokens=8192,
            context_window=8192,
            pricing={"input": 0.0, "output": 0.0},  # Free for local
            endpoint="http://localhost:11434/api/generate",
            metadata={"local": True, "quantized": True}
        )
        
        self.register_model(local_model)
        self.logger.info("ModelManager", "Discovered local models")
    
    def get_model_capabilities(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get capabilities and info for a specific model"""
        if model_id in self.router.models:
            model = self.router.models[model_id]
            return {
                "id": model.id,
                "name": model.name,
                "provider": model.provider.value,
                "capabilities": [cap.value for cap in model.capabilities],
                "max_tokens": model.max_tokens,
                "context_window": model.context_window,
                "pricing": model.pricing,
                "metadata": model.metadata,
                "is_active": model.is_active
            }
        return None
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get all available models"""
        return [
            {
                "id": model.id,
                "name": model.name,
                "provider": model.provider.value,
                "capabilities": [cap.value for cap in model.capabilities],
                "is_active": model.is_active
            }
            for model in self.router.models.values()
        ]
    
    async def route_task_to_model(self, task_description: str, 
                                required_capabilities: List[ModelCapability]) -> Dict[str, Any]:
        """Route a task to the most appropriate model"""
        # Determine required capabilities from task description
        # This is a simplified version - in reality, this could be more sophisticated
        return await self.router.route_request(required_capabilities, {"task": task_description})
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get overall usage statistics"""
        total_requests = sum(stat.total_requests for stat in self.router.stats.values())
        total_cost = sum(stat.total_cost for stat in self.router.stats.values())
        
        return {
            "total_requests": total_requests,
            "total_cost": total_cost,
            "models_registered": len(self.router.models),
            "model_stats": {
                model_id: {
                    "requests": stat.total_requests,
                    "cost": stat.total_cost,
                    "last_used": stat.last_used.isoformat() if stat.last_used else None
                }
                for model_id, stat in self.router.stats.items()
            }
        }