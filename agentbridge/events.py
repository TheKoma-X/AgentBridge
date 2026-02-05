"""
Event Bus system for AgentBridge.
Enables decoupled communication via publish-subscribe pattern.
"""

import asyncio
import logging
from typing import Dict, List, Any, Callable, Awaitable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    """Standard event types."""
    MESSAGE_SENT = "message.sent"
    MESSAGE_RECEIVED = "message.received"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    TASK_COMPLETED = "task.completed"
    ERROR_OCCURRED = "error.occurred"
    SYSTEM_STATUS = "system.status"

@dataclass
class Event:
    """An event in the system."""
    type: str
    payload: Dict[str, Any]
    source: str
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    id: str = field(default_factory=lambda: f"evt_{datetime.now().timestamp()}")

# Type alias for event handlers
EventHandler = Callable[[Event], Awaitable[None]]

class EventBus:
    """
    Simple in-memory event bus.
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[EventHandler]] = {}
        self.logger = logging.getLogger("AgentBridge.EventBus")
        
    def subscribe(self, event_type: str, handler: EventHandler):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        self.logger.debug(f"Subscribed handler to {event_type}")
        
    def unsubscribe(self, event_type: str, handler: EventHandler):
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            if handler in self.subscribers[event_type]:
                self.subscribers[event_type].remove(handler)
                
    async def publish(self, event: Event):
        """Publish an event to all subscribers."""
        if event.type in self.subscribers:
            handlers = self.subscribers[event.type]
            if not handlers:
                return
                
            # Execute handlers concurrently
            tasks = []
            for handler in handlers:
                try:
                    task = asyncio.create_task(handler(event))
                    tasks.append(task)
                except Exception as e:
                    self.logger.error(f"Error creating task for handler {handler}: {e}")
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        # Also publish to wildcard subscribers if implemented
        # For now, simplistic implementation

    async def emit(self, type_str: str, payload: Dict[str, Any], source: str = "system"):
        """Helper to create and publish an event."""
        event = Event(type=type_str, payload=payload, source=source)
        await self.publish(event)
