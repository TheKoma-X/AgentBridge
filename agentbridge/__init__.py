"""
AgentBridge - Universal AI Agent Interoperability Protocol
"""

__version__ = "0.1.0"
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
    "TaskStatus"
]

# Provide lazy loading functions
def get_workflow_components():
    """Get workflow components without causing circular imports."""
    from .workflow import WorkflowEngine, WorkflowBuilder, WorkflowDefinition, TaskDefinition, WorkflowStatus, TaskStatus
    return WorkflowEngine, WorkflowBuilder, WorkflowDefinition, TaskDefinition, WorkflowStatus, TaskStatus
