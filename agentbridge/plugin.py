"""
Plugin system for AgentBridge.
Allows extending functionality through external modules.
"""

import importlib
import importlib.util
import os
import sys
import logging
import inspect
from typing import Dict, List, Any, Optional, Type, TypeVar
from abc import ABC

logger = logging.getLogger(__name__)

T = TypeVar('T')

class PluginInterface(ABC):
    """Base interface for all plugins."""
    pass

class PluginManager:
    """Manages loading and lifecycle of plugins."""
    
    def __init__(self, plugin_dirs: List[str] = None):
        self.plugin_dirs = plugin_dirs or ["plugins"]
        self.loaded_plugins: Dict[str, Any] = {}
        self.registry: Dict[str, Type] = {}
        
        # Ensure plugin directories exist
        for d in self.plugin_dirs:
            if not os.path.exists(d):
                try:
                    os.makedirs(d)
                except OSError:
                    pass
                    
    def discover_plugins(self, base_class: Type[T] = None) -> List[Type[T]]:
        """Discover available plugins in plugin directories."""
        discovered = []
        
        for directory in self.plugin_dirs:
            if not os.path.exists(directory):
                continue
                
            # Add directory to sys.path
            if directory not in sys.path:
                sys.path.insert(0, directory)
                
            for filename in os.listdir(directory):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = filename[:-3]
                    try:
                        # Import module
                        module_path = os.path.join(directory, filename)
                        spec = importlib.util.spec_from_file_location(module_name, module_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            # Inspect module for plugin classes
                            for name, obj in inspect.getmembers(module):
                                if inspect.isclass(obj) and obj.__module__ == module.__name__:
                                    # Check if it inherits from base_class if provided
                                    if base_class:
                                        if issubclass(obj, base_class) and obj is not base_class:
                                            discovered.append(obj)
                                            self.registry[name] = obj
                                    else:
                                        discovered.append(obj)
                                        self.registry[name] = obj
                                        
                    except Exception as e:
                        logger.error(f"Failed to load plugin from {filename}: {e}")
                        
        return discovered
        
    def load_plugin(self, plugin_name: str, **kwargs) -> Optional[Any]:
        """Instantiate a loaded plugin."""
        if plugin_name in self.registry:
            try:
                plugin_class = self.registry[plugin_name]
                instance = plugin_class(**kwargs)
                self.loaded_plugins[plugin_name] = instance
                return instance
            except Exception as e:
                logger.error(f"Failed to instantiate plugin {plugin_name}: {e}")
                return None
        return None

    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """Get an instantiated plugin."""
        return self.loaded_plugins.get(plugin_name)
