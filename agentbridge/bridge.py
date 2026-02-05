"""
Core AgentBridge class - The central hub for connecting different agent frameworks
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from .protocol import AgentProtocol, Message
from .adapter import AdapterRegistry


class AgentBridge:
    """
    The core bridge that connects different AI agent frameworks and enables
    interoperability between them.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.adapters: Dict[str, Any] = {}
        self.protocol = AgentProtocol()
        self.adapter_registry = AdapterRegistry()
        self.connected_frameworks: Dict[str, Any] = {}
        self.message_queue = asyncio.Queue()
        self.config = self._load_config(config_path) if config_path else {}
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from file."""
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def register_adapter(self, framework_name: str, adapter_class: Any):
        """Register a new adapter for a specific agent framework."""
        self.adapter_registry.register(framework_name, adapter_class)
        
    def connect_framework(self, framework_name: str, endpoint: str, **kwargs):
        """Connect to a specific agent framework."""
        if framework_name not in self.adapter_registry.adapters:
            raise ValueError(f"Adapter for {framework_name} not registered")
            
        adapter_class = self.adapter_registry.adapters[framework_name]
        adapter_instance = adapter_class(endpoint, **kwargs)
        self.adapters[framework_name] = adapter_instance
        self.connected_frameworks[framework_name] = endpoint
        
        print(f"Connected to {framework_name} at {endpoint}")
        return adapter_instance
    
    async def send_message(self, source_framework: str, target_framework: str, 
                          message: Message) -> Any:
        """Send a message from one framework to another."""
        if target_framework not in self.adapters:
            raise ValueError(f"Target framework {target_framework} not connected")
            
        # Translate message to target framework's protocol
        translated_msg = self.protocol.translate_message(
            message, 
            self.adapters[source_framework].protocol_version,
            self.adapters[target_framework].protocol_version
        )
        
        # Send the message
        result = await self.adapters[target_framework].send_message(translated_msg)
        return result
    
    async def broadcast_message(self, source_framework: str, message: Message, 
                               target_frameworks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Broadcast a message to multiple frameworks."""
        if target_frameworks is None:
            target_frameworks = list(self.adapters.keys())
            
        results = {}
        for framework in target_frameworks:
            if framework != source_framework:
                try:
                    results[framework] = await self.send_message(
                        source_framework, framework, message
                    )
                except Exception as e:
                    results[framework] = {"error": str(e)}
                    
        return results
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the bridge server to accept external connections."""
        import uvicorn
        from .server import create_app
        
        app = create_app(self)
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        
        print(f"AgentBridge server starting on {host}:{port}")
        await server.serve()
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the bridge."""
        return {
            "connected_frameworks": list(self.connected_frameworks.keys()),
            "adapter_count": len(self.adapters),
            "registry_status": self.adapter_registry.get_status(),
            "config_loaded": bool(self.config)
        }
    
    async def run_bridge_loop(self):
        """Main bridge loop for handling messages."""
        while True:
            try:
                message = await self.message_queue.get()
                await self._process_message(message)
                self.message_queue.task_done()
            except Exception as e:
                print(f"Error processing message: {e}")
                
    async def _process_message(self, message: Dict[str, Any]):
        """Process an incoming message."""
        # Implementation for message processing
        pass