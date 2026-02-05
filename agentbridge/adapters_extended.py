"""
Extended Framework Adapters for AgentBridge
Additional adapters for popular AI frameworks
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import aiohttp
import requests

from .protocol import Message, Protocol
from .utils import sanitize_input


class BaseExtendedAdapter(ABC):
    """Base class for extended adapters"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_connected = False
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the framework"""
        pass
    
    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task in the framework"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the framework"""
        pass


class LangChainAdapter(BaseExtendedAdapter):
    """Adapter for LangChain framework"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("langchain", config)
        self.api_base = config.get("api_base", "http://localhost:8000")
        self.session = None
        
    async def connect(self) -> bool:
        """Connect to LangChain server"""
        try:
            # Import here to defer dependency loading
            try:
                import langchain
            except ImportError:
                raise ImportError(
                    "LangChain is not installed. Please install it with: "
                    "pip install langchain"
                )
            
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Test connection
            async with self.session.get(f"{self.api_base}/health") as resp:
                if resp.status == 200:
                    self.is_connected = True
                    return True
        except Exception as e:
            print(f"Failed to connect to LangChain: {e}")
            return False
        return False
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using LangChain"""
        if not self.is_connected:
            raise RuntimeError("Not connected to LangChain")
        
        try:
            # Sanitize input
            sanitized_task = sanitize_input(task_data)
            
            # Prepare payload
            payload = {
                "task": sanitized_task.get("operation", "default"),
                "input": sanitized_task.get("input", {}),
                "chain_type": sanitized_task.get("chain_type", "llm_chain"),
                "model_params": sanitized_task.get("model_params", {})
            }
            
            # Execute via API
            async with self.session.post(f"{self.api_base}/execute", 
                                      json=payload) as resp:
                result = await resp.json()
                
            return {
                "status": "success",
                "result": result,
                "adapter": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "adapter": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def disconnect(self):
        """Disconnect from LangChain"""
        if self.session:
            await self.session.close()
        self.is_connected = False


class LlamaIndexAdapter(BaseExtendedAdapter):
    """Adapter for LlamaIndex framework"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("llamaindex", config)
        self.api_base = config.get("api_base", "http://localhost:8001")
        self.session = None
        
    async def connect(self) -> bool:
        """Connect to LlamaIndex server"""
        try:
            # Import here to defer dependency loading
            try:
                import llama_index
            except ImportError:
                raise ImportError(
                    "LlamaIndex is not installed. Please install it with: "
                    "pip install llama-index"
                )
            
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Test connection
            async with self.session.get(f"{self.api_base}/health") as resp:
                if resp.status == 200:
                    self.is_connected = True
                    return True
        except Exception as e:
            print(f"Failed to connect to LlamaIndex: {e}")
            return False
        return False
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using LlamaIndex"""
        if not self.is_connected:
            raise RuntimeError("Not connected to LlamaIndex")
        
        try:
            # Sanitize input
            sanitized_task = sanitize_input(task_data)
            
            # Prepare payload based on task type
            task_type = sanitized_task.get("operation", "query")
            payload = {
                "task_type": task_type,
                "query": sanitized_task.get("query", ""),
                "index_id": sanitized_task.get("index_id", "default"),
                "retriever_params": sanitized_task.get("retriever_params", {}),
                "response_mode": sanitized_task.get("response_mode", "tree_summarize")
            }
            
            # Execute via API
            async with self.session.post(f"{self.api_base}/query", 
                                      json=payload) as resp:
                result = await resp.json()
                
            return {
                "status": "success",
                "result": result,
                "adapter": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "adapter": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def disconnect(self):
        """Disconnect from LlamaIndex"""
        if self.session:
            await self.session.close()
        self.is_connected = False


class HaystackAdapter(BaseExtendedAdapter):
    """Adapter for Haystack framework"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("haystack", config)
        self.api_base = config.get("api_base", "http://localhost:8002")
        self.session = None
        
    async def connect(self) -> bool:
        """Connect to Haystack server"""
        try:
            # Import here to defer dependency loading
            try:
                import haystack
            except ImportError:
                raise ImportError(
                    "Haystack is not installed. Please install it with: "
                    "pip install farm-haystack"
                )
            
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Test connection
            async with self.session.get(f"{self.api_base}/health") as resp:
                if resp.status == 200:
                    self.is_connected = True
                    return True
        except Exception as e:
            print(f"Failed to connect to Haystack: {e}")
            return False
        return False
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using Haystack"""
        if not self.is_connected:
            raise RuntimeError("Not connected to Haystack")
        
        try:
            # Sanitize input
            sanitized_task = sanitize_input(task_data)
            
            # Prepare payload based on task type
            task_type = sanitized_task.get("operation", "query")
            payload = {
                "query": sanitized_task.get("query", ""),
                "params": sanitized_task.get("params", {}),
                "debug": sanitized_task.get("debug", False)
            }
            
            # Execute via API
            endpoint = "/query" if task_type == "query" else "/index"
            async with self.session.post(f"{self.api_base}{endpoint}", 
                                      json=payload) as resp:
                result = await resp.json()
                
            return {
                "status": "success",
                "result": result,
                "adapter": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "adapter": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def disconnect(self):
        """Disconnect from Haystack"""
        if self.session:
            await self.session.close()
        self.is_connected = False


class DatabaseAdapter(BaseExtendedAdapter):
    """Generic database adapter for various databases"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("database", config)
        self.db_type = config.get("db_type", "mysql")
        self.connection_string = config.get("connection_string", "")
        self.connection = None
        
    async def connect(self) -> bool:
        """Connect to database"""
        try:
            # Import based on database type
            if self.db_type == "postgresql":
                try:
                    import asyncpg
                except ImportError:
                    raise ImportError(
                        "asyncpg is not installed. Please install it with: "
                        "pip install asyncpg"
                    )
                # Implementation would connect to PostgreSQL
                pass
            elif self.db_type == "mysql":
                try:
                    import aiomysql
                except ImportError:
                    raise ImportError(
                        "aiomysql is not installed. Please install it with: "
                        "pip install aiomysql"
                    )
                # Implementation would connect to MySQL
                pass
            elif self.db_type == "mongodb":
                try:
                    import motor.motor_asyncio
                except ImportError:
                    raise ImportError(
                        "motor is not installed. Please install it with: "
                        "pip install motor"
                    )
                # Implementation would connect to MongoDB
                pass
            elif self.db_type == "redis":
                try:
                    import redis.asyncio as redis_async
                except ImportError:
                    raise ImportError(
                        "redis is not installed. Please install it with: "
                        "pip install redis"
                    )
                # Implementation would connect to Redis
                pass
            
            # For now, we'll simulate connection
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to {self.db_type} database: {e}")
            return False
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database operation"""
        if not self.is_connected:
            raise RuntimeError("Not connected to database")
        
        try:
            operation = task_data.get("operation", "query")
            query = task_data.get("query", "")
            params = task_data.get("params", {})
            
            # Simulate database operation
            result = {
                "operation": operation,
                "query_executed": query,
                "rows_affected": 1,  # Simulated
                "result_data": [{"id": 1, "data": "sample"}]  # Simulated
            }
            
            return {
                "status": "success",
                "result": result,
                "adapter": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "adapter": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def disconnect(self):
        """Disconnect from database"""
        # Close database connection
        self.is_connected = False


class APIAdapter(BaseExtendedAdapter):
    """Generic API adapter for REST APIs"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("api", config)
        self.base_url = config.get("base_url", "")
        self.headers = config.get("headers", {})
        self.session = None
        
    async def connect(self) -> bool:
        """Validate API connectivity"""
        try:
            self.session = aiohttp.ClientSession(headers=self.headers)
            
            # Test connection with a simple health check
            try:
                async with self.session.get(f"{self.base_url}/health") as resp:
                    if resp.status in [200, 404]:  # 404 is OK, means server is reachable
                        self.is_connected = True
                        return True
            except:
                # If health check fails, try basic connectivity
                async with self.session.get(self.base_url) as resp:
                    if resp.status < 500:
                        self.is_connected = True
                        return True
        except Exception as e:
            print(f"Failed to connect to API: {e}")
            return False
        return False
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call"""
        if not self.is_connected:
            raise RuntimeError("Not connected to API")
        
        try:
            method = task_data.get("method", "GET").upper()
            endpoint = task_data.get("endpoint", "/")
            url = f"{self.base_url}{endpoint}"
            body = task_data.get("body", {})
            headers = task_data.get("headers", {})
            
            # Merge headers
            all_headers = {**self.headers, **headers}
            
            # Make API call
            if method == "GET":
                async with self.session.get(url, headers=all_headers) as resp:
                    result = await resp.json() if resp.content_type == 'application/json' else await resp.text()
            elif method == "POST":
                async with self.session.post(url, json=body, headers=all_headers) as resp:
                    result = await resp.json() if resp.content_type == 'application/json' else await resp.text()
            elif method == "PUT":
                async with self.session.put(url, json=body, headers=all_headers) as resp:
                    result = await resp.json() if resp.content_type == 'application/json' else await resp.text()
            elif method == "DELETE":
                async with self.session.delete(url, headers=all_headers) as resp:
                    result = await resp.json() if resp.content_type == 'application/json' else await resp.text()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return {
                "status": "success",
                "result": result,
                "adapter": self.name,
                "timestamp": asyncio.get_event_loop().time(),
                "http_status": resp.status
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "adapter": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def disconnect(self):
        """Close API session"""
        if self.session:
            await self.session.close()
        self.is_connected = False


class HumanAdapter(BaseExtendedAdapter):
    """
    Adapter for Human-in-the-Loop interactions.
    Stores messages in a queue for human review/response via API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("human", config)
        self.pending_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self) -> bool:
        """Simulate connection"""
        self.is_connected = True
        return True
        
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a task for human review.
        This is non-blocking in this implementation (returns 'pending').
        The caller should poll for status or use a callback mechanism.
        """
        if not self.is_connected:
            raise RuntimeError("Not connected")
            
        task_id = task_data.get("id") or f"human_task_{len(self.pending_tasks)}"
        
        # Store the task
        self.pending_tasks[task_id] = {
            "task_data": task_data,
            "status": "pending_approval",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # In a real async workflow, we might wait here using an Event
        # For this simple adapter, we return PENDING status
        
        return {
            "status": "pending",
            "task_id": task_id,
            "message": "Task submitted for human approval",
            "adapter": self.name
        }
        
    def submit_human_response(self, task_id: str, response: Dict[str, Any]) -> bool:
        """
        Called by the API when a human responds.
        """
        if task_id in self.pending_tasks:
            task = self.pending_tasks.pop(task_id)
            task["status"] = "completed"
            task["response"] = response
            task["completed_at"] = asyncio.get_event_loop().time()
            self.completed_tasks[task_id] = task
            return True
        return False
        
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks waiting for human input."""
        return [
            {"id": k, **v} for k, v in self.pending_tasks.items()
        ]

    async def disconnect(self):
        """Disconnect"""
        self.is_connected = False



class ExtendedAdapterManager:
    """Manager for extended adapters"""
    
    def __init__(self):
        self.adapters = {}
        self.adapter_types = {
            'langchain': LangChainAdapter,
            'llamaindex': LlamaIndexAdapter,
            'haystack': HaystackAdapter,
            'database': DatabaseAdapter,
            'api': APIAdapter,
            'human': HumanAdapter
        }
    
    def register_adapter(self, name: str, adapter_class):
        """Register a new adapter type"""
        self.adapter_types[name] = adapter_class
    
    async def create_adapter(self, adapter_type: str, config: Dict[str, Any]) -> Optional[BaseExtendedAdapter]:
        """Create an adapter instance"""
        if adapter_type not in self.adapter_types:
            return None
        
        adapter_class = self.adapter_types[adapter_type]
        adapter = adapter_class(config)
        return adapter
    
    def list_supported_adapters(self) -> List[str]:
        """List all supported adapter types"""
        return list(self.adapter_types.keys())