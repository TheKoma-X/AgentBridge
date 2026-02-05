"""
FastAPI server for AgentBridge - Provides REST and WebSocket endpoints
"""

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import asyncio
import json
from .bridge import AgentBridge
from .protocol import Message, MessageType


def create_app(agent_bridge: AgentBridge):
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="AgentBridge API",
        description="Universal AI Agent Interoperability Protocol",
        version="0.1.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store the bridge instance
    app.state.bridge = agent_bridge
    
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
        return agent_bridge.get_status()
    
    @app.post("/connect")
    async def connect_framework(framework: str, endpoint: str, **kwargs):
        """Connect to a specific agent framework."""
        try:
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
    async def send_message(source: str, target: str, message_data: Dict[Any, Any]):
        """Send a message from one framework to another."""
        try:
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
                              target_frameworks: list = None):
        """Broadcast a message to multiple frameworks."""
        try:
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
                
                # Process the message based on type
                if message_dict.get('action') == 'send_message':
                    source = message_dict.get('source')
                    target = message_dict.get('target')
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
    async def list_connected_frameworks():
        """List all connected frameworks."""
        return {
            "connected_frameworks": list(agent_bridge.connected_frameworks.keys()),
            "count": len(agent_bridge.connected_frameworks)
        }
    
    @app.get("/protocols")
    async def list_supported_protocols():
        """List supported protocols."""
        return {
            "supported_types": [msg_type.value for msg_type in MessageType],
            "protocol_version": "1.0"
        }
    
    return app