"""
Adapters for different AI agent frameworks
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
import asyncio
import importlib
import os
import sys
from pathlib import Path
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


class PluginLoader:
    """Dynamically loads adapter plugins from external modules."""
    
    def __init__(self, plugin_dirs=None):
        self.plugin_dirs = plugin_dirs or []
        if 'AGENTBRIDGE_PLUGIN_DIR' in os.environ:
            self.plugin_dirs.append(os.environ['AGENTBRIDGE_PLUGIN_DIR'])
    
    def load_plugin_from_path(self, module_path: str, class_name: str) -> Optional[type]:
        """Load an adapter plugin from a file path."""
        try:
            # Add the directory to sys.path temporarily
            module_dir = os.path.dirname(module_path)
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)
            
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the adapter class
            adapter_class = getattr(module, class_name)
            
            # Verify it's a subclass of BaseAdapter
            if not issubclass(adapter_class, BaseAdapter):
                raise TypeError(f"{class_name} is not a subclass of BaseAdapter")
            
            return adapter_class
            
        except Exception as e:
            print(f"Error loading plugin from {module_path}: {e}")
            return None
    
    def load_plugin_from_module(self, module_name: str, class_name: str) -> Optional[type]:
        """Load an adapter plugin from an installed module."""
        try:
            module = importlib.import_module(module_name)
            adapter_class = getattr(module, class_name)
            
            # Verify it's a subclass of BaseAdapter
            if not issubclass(adapter_class, BaseAdapter):
                raise TypeError(f"{class_name} is not a subclass of BaseAdapter")
            
            return adapter_class
            
        except Exception as e:
            print(f"Error loading plugin from {module_name}: {e}")
            return None


from .plugin import PluginManager

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
        self.plugin_loader = PluginLoader()
        self.plugin_manager = PluginManager()
        
    def load_plugins(self):
        """Discover and register adapter plugins."""
        plugins = self.plugin_manager.discover_plugins(BaseAdapter)
        for plugin_class in plugins:
            # Assume plugin name is lowercased class name without 'Adapter' suffix
            name = plugin_class.__name__.lower().replace('adapter', '')
            self.register(name, plugin_class)
            print(f"Loaded adapter plugin: {name}")
            
    def register(self, framework_name: str, adapter_class: type):
        """Register a new adapter class."""
        self.adapters[framework_name.lower()] = adapter_class
        
    def register_dynamic(self, framework_name: str, module_path: str, class_name: str) -> bool:
        """Dynamically register an adapter from a plugin file."""
        adapter_class = self.plugin_loader.load_plugin_from_path(module_path, class_name)
        if adapter_class:
            self.adapters[framework_name.lower()] = adapter_class
            return True
        return False
    
    def register_from_installed_module(self, framework_name: str, module_name: str, class_name: str) -> bool:
        """Register an adapter from an installed module."""
        adapter_class = self.plugin_loader.load_plugin_from_module(module_name, class_name)
        if adapter_class:
            self.adapters[framework_name.lower()] = adapter_class
            return True
        return False
        
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
            "adapter_count": len(self.adapters),
            "plugin_loader_available": True
        }


# Factory function to create adapters
def create_adapter(framework_name: str, endpoint: str, **kwargs) -> BaseAdapter:
    """Factory function to create an adapter instance."""
    registry = AdapterRegistry()
    adapter_class = registry.get_adapter(framework_name)
    
    if not adapter_class:
        raise ValueError(f"No adapter found for framework: {framework_name}")
        
    return adapter_class(endpoint, **kwargs)