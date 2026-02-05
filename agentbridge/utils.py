"""
Utility functions for AgentBridge
"""

import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import asyncio
import hashlib
import uuid
from datetime import datetime


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML or JSON file."""
    path = Path(config_path)
    
    if path.suffix.lower() in ['.yaml', '.yml']:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    elif path.suffix.lower() == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported config file format: {path.suffix}")


def save_config(config: Dict[str, Any], config_path: str, format: str = 'yaml'):
    """Save configuration to file."""
    path = Path(config_path)
    
    if format.lower() == 'yaml' or path.suffix.lower() in ['.yaml', '.yml']:
        with open(path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    elif format.lower() == 'json' or path.suffix.lower() == '.json':
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for tracking messages."""
    return str(uuid.uuid4())


def calculate_checksum(data: Any) -> str:
    """Calculate checksum of data for integrity verification."""
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(data_str.encode()).hexdigest()


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Basic JSON schema validation."""
    try:
        # This is a simplified validation - in practice you'd use a proper schema validator
        required_fields = schema.get('required', [])
        properties = schema.get('properties', {})
        
        for field in required_fields:
            if field not in data:
                return False
                
        for field, field_spec in properties.items():
            if field in data:
                expected_type = field_spec.get('type')
                if expected_type == 'string' and not isinstance(data[field], str):
                    return False
                elif expected_type == 'integer' and not isinstance(data[field], int):
                    return False
                elif expected_type == 'number' and not isinstance(data[field], (int, float)):
                    return False
                elif expected_type == 'boolean' and not isinstance(data[field], bool):
                    return False
                elif expected_type == 'array' and not isinstance(data[field], list):
                    return False
                elif expected_type == 'object' and not isinstance(data[field], dict):
                    return False
        
        return True
    except:
        return False


def format_timestamp(timestamp: float) -> str:
    """Format timestamp to readable string."""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


async def retry_with_backoff(func, retries: int = 3, backoff_factor: float = 1.0):
    """Retry a function with exponential backoff."""
    for attempt in range(retries):
        try:
            return await func()
        except Exception as e:
            if attempt == retries - 1:
                raise e
            
            delay = backoff_factor * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)


def sanitize_input(user_input: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    # Remove potentially dangerous characters/sequences
    sanitized = user_input.replace('\0', '')  # Null bytes
    sanitized = sanitized.replace('..', '')   # Path traversal
    # Add more sanitization as needed
    
    return sanitized


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two configuration dictionaries."""
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def get_nested_value(data: Dict[str, Any], path: str, separator: str = '.') -> Any:
    """Get a value from nested dictionary using dot notation path."""
    keys = path.split(separator)
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    
    return current


def set_nested_value(data: Dict[str, Any], path: str, value: Any, separator: str = '.') -> None:
    """Set a value in nested dictionary using dot notation path."""
    keys = path.split(separator)
    current = data
    
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value