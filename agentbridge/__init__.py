"""
AgentBridge - Universal AI Agent Interoperability Protocol
"""

__version__ = "0.1.0"
__author__ = "TheKoma-X"
__license__ = "MIT"

from .bridge import AgentBridge
from .protocol import AgentProtocol
from .adapter import AdapterRegistry

__all__ = ["AgentBridge", "AgentProtocol", "AdapterRegistry"]