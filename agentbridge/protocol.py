"""
Agent Protocol - Standardized message format and translation layer
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Union
from enum import Enum
import json


class MessageType(Enum):
    """Types of messages that can be exchanged between agents."""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    METADATA_REQUEST = "metadata_request"
    METADATA_RESPONSE = "metadata_response"


@dataclass
class Message:
    """Standardized message structure for agent communication."""
    type: MessageType
    source: str
    target: str
    content: Any
    timestamp: float
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "source": self.source,
            "target": self.target,
            "content": self.content,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(
            type=MessageType(data['type']),
            source=data['source'],
            target=data['target'],
            content=data['content'],
            timestamp=data['timestamp'],
            correlation_id=data.get('correlation_id'),
            reply_to=data.get('reply_to'),
            metadata=data.get('metadata')
        )


class AgentProtocol:
    """Handles message translation between different agent frameworks."""
    
    def __init__(self):
        self.framework_protocols = {}
        self.translation_rules = {}
        
    def register_protocol(self, framework_name: str, version: str, 
                         message_format: Dict[str, Any]):
        """Register a new framework protocol."""
        if framework_name not in self.framework_protocols:
            self.framework_protocols[framework_name] = {}
        self.framework_protocols[framework_name][version] = message_format
        
    def translate_message(self, message: Message, source_protocol: str, 
                        target_protocol: str) -> Message:
        """Translate a message from source protocol to target protocol."""
        # Default translation - in real implementation this would be more complex
        translated_content = self._translate_content(
            message.content, source_protocol, target_protocol
        )
        
        return Message(
            type=message.type,
            source=message.source,
            target=message.target,
            content=translated_content,
            timestamp=message.timestamp,
            correlation_id=message.correlation_id,
            reply_to=message.reply_to,
            metadata=message.metadata
        )
    
    def _translate_content(self, content: Any, source_protocol: str, 
                          target_protocol: str) -> Any:
        """Translate content between protocols."""
        # This is a simplified translation
        # In practice, this would involve complex mapping between different
        # agent framework structures
        if isinstance(content, dict):
            # Apply translation rules based on source and target protocols
            return self._apply_translation_rules(content, source_protocol, target_protocol)
        return content
    
    def _apply_translation_rules(self, content: Dict[str, Any], 
                                source_protocol: str, 
                                target_protocol: str) -> Dict[str, Any]:
        """Apply translation rules between protocols."""
        # In a real implementation, this would have detailed mapping rules
        # between different agent framework schemas
        return content  # Placeholder
    
    def validate_message(self, message: Message, protocol_version: str) -> bool:
        """Validate a message against a protocol."""
        # Implementation would validate message structure against protocol
        return True  # Placeholder
    
    def create_task_request(self, source: str, target: str, task_description: str,
                           params: Optional[Dict[str, Any]] = None) -> Message:
        """Create a standardized task request message."""
        import time
        return Message(
            type=MessageType.TASK_REQUEST,
            source=source,
            target=target,
            content={
                "task": task_description,
                "parameters": params or {},
                "request_time": time.time()
            },
            timestamp=time.time()
        )
    
    def create_tool_call(self, source: str, target: str, tool_name: str,
                        arguments: Dict[str, Any]) -> Message:
        """Create a standardized tool call message."""
        import time
        return Message(
            type=MessageType.TOOL_CALL,
            source=source,
            target=target,
            content={
                "tool": tool_name,
                "arguments": arguments
            },
            timestamp=time.time()
        )
    
    def create_error_response(self, source: str, target: str, error_message: str,
                            original_correlation_id: Optional[str] = None) -> Message:
        """Create a standardized error response message."""
        import time
        return Message(
            type=MessageType.ERROR,
            source=source,
            target=target,
            content={
                "error": error_message,
                "original_request_id": original_correlation_id
            },
            timestamp=time.time(),
            correlation_id=original_correlation_id
        )