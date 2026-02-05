"""
Adapters for different AI agent frameworks
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
# Defer importing of external dependencies to runtime


class BaseAdapter(ABC):
    """Base class for all framework adapters."""
    
    def __init__(self, endpoint: str, **kwargs):
        self.endpoint = endpoint
        self.session = None  # Will be initialized at runtime
        self.config = kwargs
        
    async def initialize(self):
        """Initialize the adapter connection."""
        # Import here to defer dependency loading
        try:
            import aiohttp
            self.session = aiohttp.ClientSession()
        except ImportError:
            raise ImportError("aiohttp is required for network operations. Please install it with 'pip install aiohttp'")
        
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            
    @abstractmethod
    async def send_message(self, message: Any) -> Any:
        """Send a message to the framework."""
        pass
        
    @abstractmethod
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get the framework's capabilities."""
        pass
        
    @abstractmethod
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """List tools available in the framework."""
        pass


class CrewAIAdapter(BaseAdapter):
    """Adapter for CrewAI framework."""
    
    async def send_message(self, message: Any) -> Any:
        if not self.session:
            await self.initialize()
            
        # Import here to defer dependency loading
        import aiohttp
        
        # Implementation for CrewAI communication
        # This would connect to CrewAI's API endpoints
        async with self.session.post(f"{self.endpoint}/execute", json=message.to_dict()) as resp:
            return await resp.json()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        async with self.session.get(f"{self.endpoint}/capabilities") as resp:
            return await resp.json()
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        async with self.session.get(f"{self.endpoint}/tools") as resp:
            return await resp.json()


class LangGraphAdapter(BaseAdapter):
    """Adapter for LangGraph framework."""
    
    async def send_message(self, message: Any) -> Any:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        # Implementation for LangGraph communication
        async with self.session.post(f"{self.endpoint}/invoke", json=message.to_dict()) as resp:
            return await resp.json()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        async with self.session.get(f"{self.endpoint}/state") as resp:
            return await resp.json()
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        async with self.session.get(f"{self.endpoint}/nodes") as resp:
            return await resp.json()


class AutoGenAdapter(BaseAdapter):
    """Adapter for Microsoft AutoGen framework."""
    
    async def send_message(self, message: Any) -> Any:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        # Implementation for AutoGen communication
        async with self.session.post(f"{self.endpoint}/chat", json=message.to_dict()) as resp:
            return await resp.json()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        async with self.session.get(f"{self.endpoint}/agents") as resp:
            return await resp.json()
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        async with self.session.get(f"{self.endpoint}/functions") as resp:
            return await resp.json()


class ClaudeFlowAdapter(BaseAdapter):
    """Adapter for Claude-Flow framework."""
    
    async def send_message(self, message: Any) -> Any:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        # Implementation for Claude-Flow communication
        headers = {'Content-Type': 'application/json'}
        async with self.session.post(f"{self.endpoint}/mcp", json=message.to_dict(), headers=headers) as resp:
            return await resp.json()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        async with self.session.get(f"{self.endpoint}/mcp/capabilities") as resp:
            return await resp.json()
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        if not self.session:
            await self.initialize()
            
        import aiohttp
        
        async with self.session.get(f"{self.endpoint}/mcp/tools") as resp:
            return await resp.json()


class AdapterRegistry:
    """Registry for managing different framework adapters."""
    
    def __init__(self):
        self.adapters: Dict[str, type] = {
            'crewai': CrewAIAdapter,
            'langgraph': LangGraphAdapter,
            'autogen': AutoGenAdapter,
            'claude-flow': ClaudeFlowAdapter,
            'claude_flow': ClaudeFlowAdapter,  # Alternative naming
        }
        
    def register(self, framework_name: str, adapter_class: type):
        """Register a new adapter class."""
        self.adapters[framework_name.lower()] = adapter_class
        
    def get_adapter(self, framework_name: str) -> Optional[type]:
        """Get an adapter class by framework name."""
        return self.adapters.get(framework_name.lower())
        
    def list_adapters(self) -> List[str]:
        """List all registered adapters."""
        return list(self.adapters.keys())
        
    def get_status(self) -> Dict[str, Any]:
        """Get status of registered adapters."""
        return {
            "registered_adapters": list(self.adapters.keys()),
            "adapter_count": len(self.adapters)
        }


# Factory function to create adapters
def create_adapter(framework_name: str, endpoint: str, **kwargs) -> BaseAdapter:
    """Factory function to create an adapter instance."""
    registry = AdapterRegistry()
    adapter_class = registry.get_adapter(framework_name)
    
    if not adapter_class:
        raise ValueError(f"No adapter found for framework: {framework_name}")
        
    return adapter_class(endpoint, **kwargs)