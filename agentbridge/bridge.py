"""
Core AgentBridge class - The central hub for connecting different agent frameworks
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from .protocol import AgentProtocol, Message
from .adapter import AdapterRegistry
from .config import BridgeConfig, ConfigManager
from .logging import get_logger, get_metrics_collector
from .security import get_security_manager, AuthenticationError, AuthorizationError
from .workflow import WorkflowEngine


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
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        self.security_manager = get_security_manager(self.config)
        self._workflow_engine = None  # Initialize later to avoid circular import

    def connect_framework(self, framework_name: str, endpoint: str, **kwargs):
        """Connect to a specific agent framework."""
        logger = get_logger()
        metrics = get_metrics_collector()
        
        try:
            # Security check: verify if framework is trusted
            if not self.security_manager.is_trusted_framework(framework_name):
                error_msg = f"Framework {framework_name} is not in trusted frameworks list"
                logger.error("Bridge", error_msg)
                raise ValueError(error_msg)
            
            if framework_name not in self.adapter_registry.adapters:
                error_msg = f"Adapter for {framework_name} not registered"
                logger.error("Bridge", error_msg)
                raise ValueError(error_msg)
                
            adapter_class = self.adapter_registry.adapters[framework_name]
            adapter_instance = adapter_class(endpoint, **kwargs)
            self.adapters[framework_name] = adapter_instance
            self.connected_frameworks[framework_name] = endpoint
            
            # Add framework to config if not already present
            if not self.config_manager.config.get_framework(framework_name):
                self.config_manager.config.add_framework(framework_name, endpoint, **kwargs)
            
            success_msg = f"Connected to {framework_name} at {endpoint}"
            logger.info("Bridge", success_msg)
            metrics.increment_counter('connections')
            metrics.update_framework_stats(framework_name, 'connect', success=True)
            
            print(success_msg)
            return adapter_instance
        except Exception as e:
            logger.exception("Bridge", f"Failed to connect to {framework_name}", exc_info=e)
            metrics.increment_counter('errors')
            if framework_name:
                metrics.update_framework_stats(framework_name, 'connect', success=False)
            raise

    async def send_message(self, source_framework: str, target_framework: str, 
                          message: Message) -> Any:
        """Send a message from one framework to another."""
        import time
        start_time = time.time()
        
        logger = get_logger()
        metrics = get_metrics_collector()
        
        try:
            # Security check: verify both frameworks are trusted
            if not self.security_manager.is_trusted_framework(source_framework):
                error_msg = f"Source framework {source_framework} is not trusted"
                logger.error("Bridge", error_msg)
                metrics.increment_counter('errors')
                raise ValueError(error_msg)
                
            if not self.security_manager.is_trusted_framework(target_framework):
                error_msg = f"Target framework {target_framework} is not trusted"
                logger.error("Bridge", error_msg)
                metrics.increment_counter('errors')
                raise ValueError(error_msg)
            
            if target_framework not in self.adapters:
                error_msg = f"Target framework {target_framework} not connected"
                logger.error("Bridge", error_msg)
                metrics.increment_counter('errors')
                raise ValueError(error_msg)
            
            if source_framework not in self.adapters:
                error_msg = f"Source framework {source_framework} not connected"
                logger.error("Bridge", error_msg)
                metrics.increment_counter('errors')
                raise ValueError(error_msg)
                
            # Encrypt message content if security requires it
            if self.config.security.encryption_enabled and message.content:
                encrypted_content = self.security_manager.encrypt_data(str(message.content))
                # Create a copy of the message with encrypted content
                import copy
                message = copy.copy(message)
                message.content = {"encrypted_data": encrypted_content}
            
            # Translate message to target framework's protocol
            translated_msg = self.protocol.translate_message(
                message, 
                "current",  # Would use actual protocol versions in real implementation
                "current"   # Would use actual protocol versions in real implementation
            )
            
            # Send the message
            result = await self.adapters[target_framework].send_message(translated_msg)
            
            # Record metrics
            elapsed_time = time.time() - start_time
            metrics.increment_counter('messages_sent')
            metrics.record_timer('avg_response_time', elapsed_time)
            metrics.update_framework_stats(target_framework, 'send_message', success=True)
            
            logger.info("Bridge", f"Message sent from {source_framework} to {target_framework}", {
                "message_type": message.type.value if hasattr(message, 'type') and message.type else 'unknown',
                "elapsed_time": elapsed_time
            })
            
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.exception("Bridge", f"Failed to send message from {source_framework} to {target_framework}", exc_info=e)
            metrics.increment_counter('errors')
            metrics.record_timer('avg_response_time', elapsed_time)
            if target_framework:
                metrics.update_framework_stats(target_framework, 'send_message', success=False)
            raise

    async def broadcast_message(self, source_framework: str, message: Message, 
                               target_frameworks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Broadcast a message to multiple frameworks."""
        logger = get_logger()
        metrics = get_metrics_collector()
        
        if target_frameworks is None:
            target_frameworks = list(self.adapters.keys())
        
        logger.info("Bridge", f"Broadcasting message from {source_framework} to {len(target_frameworks)} frameworks", {
            "target_frameworks": target_frameworks,
            "message_type": message.type.value if hasattr(message, 'type') and message.type else 'unknown'
        })
            
        results = {}
        success_count = 0
        failure_count = 0
        
        for framework in target_frameworks:
            if framework != source_framework:
                try:
                    result = await self.send_message(
                        source_framework, framework, message
                    )
                    results[framework] = result
                    success_count += 1
                except Exception as e:
                    error_result = {"error": str(e)}
                    results[framework] = error_result
                    failure_count += 1
                    logger.warning("Bridge", f"Broadcast to {framework} failed", error_result)
                    
        logger.info("Bridge", f"Broadcast completed: {success_count} successes, {failure_count} failures", {
            "total_targets": len([f for f in target_frameworks if f != source_framework]),
            "successes": success_count,
            "failures": failure_count
        })
        
        # Update metrics
        metrics.increment_counter('messages_sent', success_count)
        if failure_count > 0:
            metrics.increment_counter('errors', failure_count)
                    
        return results

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the bridge."""
        from .logging import get_metrics_collector
        
        metrics = get_metrics_collector()
        
        status = {
            "connected_frameworks": list(self.connected_frameworks.keys()),
            "adapter_count": len(self.adapters),
            "registry_status": self.adapter_registry.get_status(),
            "config_loaded": bool(self.config),
            "metrics": metrics.get_metrics()
        }
        
        # Add workflow info if available
        if hasattr(self, '_workflow_engine') and self._workflow_engine:
            status["workflow_engine"] = {
                "registered_workflows": len(self._workflow_engine.workflow_definitions),
                "active_executions": len(self._workflow_engine.active_executions)
            }
        
        return status

    def get_workflow_engine(self):
        """Get the workflow engine, initializing it if needed."""
        if self._workflow_engine is None:
            from .workflow import WorkflowEngine
            self._workflow_engine = WorkflowEngine(self)
        return self._workflow_engine

    async def start_server(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the FastAPI server."""
        from .server import create_app
        import uvicorn
        
        app = create_app(self)
        
        # Configure uvicorn to use the specified host and port
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        
        # Add workflow engine to app state if needed
        app.state.workflow_engine = self.get_workflow_engine()
        
        server = uvicorn.Server(config)
        
        try:
            await server.serve()
        except KeyboardInterrupt:
            print("Server stopped by user")
        except Exception as e:
            print(f"Server error: {e}")
            raise
