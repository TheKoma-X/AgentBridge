"""
FastAPI server for AgentBridge - Provides REST and WebSocket endpoints
"""

# FastAPI will be imported at runtime when needed
from typing import Dict, Any
import asyncio
import json
from .bridge import AgentBridge
from .protocol import Message, MessageType
from .security import SecurityMiddleware, AuthenticationError, AuthorizationError


def create_app(agent_bridge: AgentBridge):
    """Create and configure the FastAPI application."""
    # Import FastAPI here to defer loading of dependencies
    try:
        from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks, Request
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError:
        raise ImportError("FastAPI is required to run the server. Please install it with 'pip install fastapi uvicorn'")
    
    app = FastAPI(
        title="AgentBridge API",
        description="Universal AI Agent Interoperability Protocol",
        version="0.1.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if "*" in agent_bridge.config.security.allowed_origins 
                     else agent_bridge.config.security.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store the bridge instance
    app.state.bridge = agent_bridge
    app.state.security_middleware = SecurityMiddleware(agent_bridge.security_manager)
    
    async def authenticate_request(request: Request):
        """Authenticate incoming request."""
        if agent_bridge.config.security.require_auth:
            try:
                headers = dict(request.headers)
                token = await app.state.security_middleware.authenticate_request(headers)
                return token
            except AuthenticationError as e:
                raise HTTPException(status_code=401, detail=str(e))
        return None
    
    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        """Apply security checks to all requests."""
        # Validate origin
        origin = request.headers.get('origin', request.client.host if request.client else 'unknown')
        if not agent_bridge.security_manager.validate_origin(origin):
            return HTTPException(status_code=403, detail="Origin not allowed")
        
        # Apply rate limiting if enabled
        if agent_bridge.config.security.rate_limit_enabled:
            # In a real implementation, we would track requests per IP/time window
            # For now, we just note that rate limiting is enabled
            pass
        
        response = await call_next(request)
        return response
    
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to AgentBridge - Universal AI Agent Interoperability Protocol",
            "version": "0.1.0",
            "endpoints": [
                "/status",
                "/connect",
                "/send_message",
                "/broadcast",
                "/ws"  # WebSocket endpoint
            ]
        }
    
    @app.get("/status")
    async def get_status():
        """Get the current status of the bridge."""
        token = await authenticate_request(Request(scope={'type': 'http'}))
        if token:
            await app.state.security_middleware.authorize_request(token, 'read')
        return agent_bridge.get_status()
    
    @app.post("/connect")
    async def connect_framework(framework: str, endpoint: str, request: Request, **kwargs):
        """Connect to a specific agent framework."""
        token = await authenticate_request(request)
        if token:
            await app.state.security_middleware.authorize_request(token, 'write')
        
        try:
            # Security check: verify if framework is trusted
            if not agent_bridge.security_manager.is_trusted_framework(framework):
                raise HTTPException(status_code=403, detail=f"Framework {framework} is not trusted")
            
            adapter = agent_bridge.connect_framework(framework, endpoint, **kwargs)
            return {
                "success": True,
                "message": f"Connected to {framework} at {endpoint}",
                "framework": framework,
                "endpoint": endpoint
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/send_message")
    async def send_message(source: str, target: str, message_data: Dict[Any, Any], request: Request):
        """Send a message from one framework to another."""
        token = await authenticate_request(request)
        if token:
            await app.state.security_middleware.authorize_request(token, 'write')
        
        try:
            # Security check: verify if frameworks are trusted
            if not agent_bridge.security_manager.is_trusted_framework(source):
                raise HTTPException(status_code=403, detail=f"Source framework {source} is not trusted")
            if not agent_bridge.security_manager.is_trusted_framework(target):
                raise HTTPException(status_code=403, detail=f"Target framework {target} is not trusted")
            
            # Create a message object from the received data
            from datetime import datetime
            message = Message(
                type=MessageType[message_data.get('type', 'TASK_REQUEST').upper()],
                source=source,
                target=target,
                content=message_data.get('content', {}),
                timestamp=datetime.now().timestamp(),
                correlation_id=message_data.get('correlation_id'),
                reply_to=message_data.get('reply_to'),
                metadata=message_data.get('metadata')
            )
            
            result = await agent_bridge.send_message(source, target, message)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/broadcast")
    async def broadcast_message(source: str, message_data: Dict[Any, Any], 
                              target_frameworks: list = None, request: Request):
        """Broadcast a message to multiple frameworks."""
        token = await authenticate_request(request)
        if token:
            await app.state.security_middleware.authorize_request(token, 'write')
        
        try:
            # Security check: verify if source framework is trusted
            if not agent_bridge.security_manager.is_trusted_framework(source):
                raise HTTPException(status_code=403, detail=f"Source framework {source} is not trusted")
            
            # Create a message object from the received data
            from datetime import datetime
            message = Message(
                type=MessageType[message_data.get('type', 'TASK_REQUEST').upper()],
                source=source,
                target="all",  # Broadcast target
                content=message_data.get('content', {}),
                timestamp=datetime.now().timestamp(),
                correlation_id=message_data.get('correlation_id'),
                reply_to=message_data.get('reply_to'),
                metadata=message_data.get('metadata')
            )
            
            result = await agent_bridge.broadcast_message(
                source, message, target_frameworks
            )
            return {
                "success": True,
                "results": result
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time communication."""
        await websocket.accept()
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_dict = json.loads(data)
                
                # Authenticate WebSocket requests if required
                if agent_bridge.config.security.require_auth:
                    token = message_dict.get('token')
                    if token:
                        try:
                            agent_bridge.security_manager.authenticate(token)
                            # Authorize based on action
                            action = message_dict.get('action', 'read')
                            perm = 'write' if action in ['send_message', 'connect'] else 'read'
                            agent_bridge.security_manager.authorize(token, perm)
                        except (AuthenticationError, AuthorizationError) as e:
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "message": str(e)
                            }))
                            continue
                
                # Process the message based on type
                if message_dict.get('action') == 'send_message':
                    source = message_dict.get('source')
                    target = message_dict.get('target')
                    
                    # Security check: verify if frameworks are trusted
                    if not agent_bridge.security_manager.is_trusted_framework(source):
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": f"Source framework {source} is not trusted"
                        }))
                        continue
                        
                    if not agent_bridge.security_manager.is_trusted_framework(target):
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": f"Target framework {target} is not trusted"
                        }))
                        continue
                    
                    content = message_dict.get('content', {})
                    
                    # Create a message object
                    from datetime import datetime
                    message = Message(
                        type=MessageType[message_dict.get('type', 'TASK_REQUEST').upper()],
                        source=source,
                        target=target,
                        content=content,
                        timestamp=datetime.now().timestamp(),
                        correlation_id=message_dict.get('correlation_id'),
                        reply_to=message_dict.get('reply_to'),
                        metadata=message_dict.get('metadata')
                    )
                    
                    # Send message through bridge
                    result = await agent_bridge.send_message(source, target, message)
                    
                    # Send response back to client
                    await websocket.send_text(json.dumps({
                        "type": "response",
                        "correlation_id": message.correlation_id,
                        "result": result
                    }))
                
                elif message_dict.get('action') == 'subscribe_status':
                    # Security check: verify read permission
                    if agent_bridge.config.security.require_auth:
                        token = message_dict.get('token')
                        if token:
                            try:
                                agent_bridge.security_manager.authenticate(token)
                                agent_bridge.security_manager.authorize(token, 'read')
                            except (AuthenticationError, AuthorizationError) as e:
                                await websocket.send_text(json.dumps({
                                    "type": "error",
                                    "message": str(e)
                                }))
                                continue
                    
                    # Send current status
                    status = agent_bridge.get_status()
                    await websocket.send_text(json.dumps({
                        "type": "status_update",
                        "status": status
                    }))
                    
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            await websocket.close()
    
    @app.get("/frameworks")
    async def list_connected_frameworks(request: Request):
        """List all connected frameworks."""
        token = await authenticate_request(request)
        if token:
            await app.state.security_middleware.authorize_request(token, 'read')
        
        return {
            "connected_frameworks": list(agent_bridge.connected_frameworks.keys()),
            "count": len(agent_bridge.connected_frameworks)
        }
    
    @app.get("/protocols")
    async def list_supported_protocols(request: Request):
        """List supported protocols."""
        token = await authenticate_request(request)
        if token:
            await app.state.security_middleware.authorize_request(token, 'read')
        
        return {
            "supported_types": [msg_type.value for msg_type in MessageType],
            "protocol_version": "1.0"
        }
    
    return app