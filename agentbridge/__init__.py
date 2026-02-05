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
    "set_metrics_collector"
]
