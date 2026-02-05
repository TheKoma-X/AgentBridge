"""
AgentBridge - Universal AI Agent Interoperability Protocol
"""

__version__ = "1.1.0"
__author__ = "TheKoma-X"
__license__ = "MIT"

from .bridge import AgentBridge
from .protocol import AgentProtocol
from .adapter import AdapterRegistry
from .config import BridgeConfig, ConfigManager, get_config_manager
from .logging import (
    AgentBridgeLogger, 
    get_logger, 
    set_logger, 
    get_metrics_collector, 
    set_metrics_collector
)
from .security import (
    SecurityManager,
    SecurityMiddleware,
    get_security_manager,
    set_security_manager,
    AuthenticationError,
    AuthorizationError
)

# Import workflow components separately to avoid circular imports
def _import_workflows():
    """Lazy import for workflow components to avoid circular imports."""
    from .workflow import WorkflowEngine, WorkflowBuilder, WorkflowDefinition, TaskDefinition, WorkflowStatus, TaskStatus
    return WorkflowEngine, WorkflowBuilder, WorkflowDefinition, TaskDefinition, WorkflowStatus, TaskStatus

# Import model components separately to avoid circular imports
def _import_models():
    """Lazy import for model components to avoid circular imports."""
    from .models import ModelManager, ModelRouter, ModelSpec, ModelCapability, ModelProvider
    return ModelManager, ModelRouter, ModelSpec, ModelCapability, ModelProvider

# Import intelligence components separately to avoid circular imports
def _import_intelligence():
    """Lazy import for intelligence components to avoid circular imports."""
    from .intelligence import IntelligenceManager, OptimizationStrategy
    return IntelligenceManager, OptimizationStrategy

# Import extended adapter components separately to avoid circular imports
def _import_extended_adapters():
    """Lazy import for extended adapter components to avoid circular imports."""
    from .adapters_extended import ExtendedAdapterManager, BaseExtendedAdapter
    return ExtendedAdapterManager, BaseExtendedAdapter

# Define all exports
__all__ = [
    "AgentBridge", 
    "AgentProtocol", 
    "AdapterRegistry",
    "BridgeConfig",
    "ConfigManager",
    "get_config_manager",
    "AgentBridgeLogger",
    "get_logger",
    "set_logger",
    "get_metrics_collector",
    "set_metrics_collector",
    "SecurityManager",
    "SecurityMiddleware",
    "get_security_manager",
    "set_security_manager",
    "AuthenticationError",
    "AuthorizationError",
    "WorkflowEngine",
    "WorkflowBuilder", 
    "WorkflowDefinition",
    "TaskDefinition",
    "WorkflowStatus",
    "TaskStatus",
    "ModelManager",
    "ModelRouter",
    "ModelSpec",
    "ModelCapability",
    "ModelProvider",
    "IntelligenceManager",
    "OptimizationStrategy",
    "ExtendedAdapterManager",
    "BaseExtendedAdapter"
]

# Provide lazy loading functions
def get_workflow_components():
    """Get workflow components without causing circular imports."""
    from .workflow import WorkflowEngine, WorkflowBuilder, WorkflowDefinition, TaskDefinition, WorkflowStatus, TaskStatus
    return WorkflowEngine, WorkflowBuilder, WorkflowDefinition, TaskDefinition, WorkflowStatus, TaskStatus

def get_model_components():
    """Get model components without causing circular imports."""
    from .models import ModelManager, ModelRouter, ModelSpec, ModelCapability, ModelProvider
    return ModelManager, ModelRouter, ModelSpec, ModelCapability, ModelProvider

def get_intelligence_components():
    """Get intelligence components without causing circular imports."""
    from .intelligence import IntelligenceManager, OptimizationStrategy
    return IntelligenceManager, OptimizationStrategy

def get_extended_adapter_components():
    """Get extended adapter components without causing circular imports."""
    from .adapters_extended import ExtendedAdapterManager, BaseExtendedAdapter
    return ExtendedAdapterManager, BaseExtendedAdapter
