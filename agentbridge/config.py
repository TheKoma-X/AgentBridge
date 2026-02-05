"""
Configuration management for AgentBridge
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from .utils import load_config, save_config, merge_configs


@dataclass
class SecurityConfig:
    """Security configuration for AgentBridge."""
    require_auth: bool = False
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    auth_tokens: List[str] = field(default_factory=list)
    rate_limit_enabled: bool = False
    max_requests_per_minute: int = 60
    encryption_enabled: bool = False
    trusted_frameworks_only: bool = False
    allowed_frameworks: List[str] = field(default_factory=list)


@dataclass
class ServerConfig:
    """Server configuration for AgentBridge."""
    host: str = "0.0.0.0"
    port: int = 8080
    cors_enabled: bool = True
    ssl_enabled: bool = False
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None
    max_connections: int = 100
    timeout: int = 30


@dataclass
class FrameworkConfig:
    """Configuration for individual agent frameworks."""
    name: str
    endpoint: str
    auth_token: Optional[str] = None
    enabled: bool = True
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BridgeConfig:
    """Main configuration for AgentBridge."""
    version: str = "1.0"
    server: ServerConfig = field(default_factory=ServerConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    frameworks: List[FrameworkConfig] = field(default_factory=list)
    default_timeout: int = 30
    log_level: str = "INFO"
    enable_metrics: bool = False
    
    def add_framework(self, name: str, endpoint: str, **kwargs) -> None:
        """Add a framework to the configuration."""
        framework_config = FrameworkConfig(name=name, endpoint=endpoint, **kwargs)
        self.frameworks.append(framework_config)
    
    def get_framework(self, name: str) -> Optional[FrameworkConfig]:
        """Get a framework by name."""
        for framework in self.frameworks:
            if framework.name == name:
                return framework
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {
            "version": self.version,
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "cors_enabled": self.server.cors_enabled,
                "ssl_enabled": self.server.ssl_enabled,
                "ssl_cert_file": self.server.ssl_cert_file,
                "ssl_key_file": self.server.ssl_key_file,
                "max_connections": self.server.max_connections,
                "timeout": self.server.timeout,
            },
            "security": {
                "require_auth": self.security.require_auth,
                "allowed_origins": self.security.allowed_origins,
                "auth_tokens": self.security.auth_tokens,
                "rate_limit_enabled": self.security.rate_limit_enabled,
                "max_requests_per_minute": self.security.max_requests_per_minute,
                "encryption_enabled": self.security.encryption_enabled,
                "trusted_frameworks_only": self.security.trusted_frameworks_only,
                "allowed_frameworks": self.security.allowed_frameworks,
            },
            "frameworks": [
                {
                    "name": fw.name,
                    "endpoint": fw.endpoint,
                    "auth_token": fw.auth_token,
                    "enabled": fw.enabled,
                    "timeout": fw.timeout,
                    "retry_attempts": fw.retry_attempts,
                    "retry_delay": fw.retry_delay,
                    "metadata": fw.metadata
                } for fw in self.frameworks
            ],
            "default_timeout": self.default_timeout,
            "log_level": self.log_level,
            "enable_metrics": self.enable_metrics,
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BridgeConfig':
        """Create configuration from dictionary."""
        config = cls(
            version=data.get("version", "1.0"),
            server=ServerConfig(**data.get("server", {})),
            security=SecurityConfig(**data.get("security", {})),
            default_timeout=data.get("default_timeout", 30),
            log_level=data.get("log_level", "INFO"),
            enable_metrics=data.get("enable_metrics", False),
        )
        
        # Add frameworks
        for fw_data in data.get("frameworks", []):
            config.add_framework(**fw_data)
        
        return config


class ConfigManager:
    """Manages loading, saving, and validating configurations."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "agentbridge.yaml"
        self.config: BridgeConfig = BridgeConfig()
        
        if os.path.exists(self.config_path):
            self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        raw_config = load_config(self.config_path)
        self.config = BridgeConfig.from_dict(raw_config)
    
    def save_config(self) -> None:
        """Save configuration to file."""
        config_dict = self.config.to_dict()
        save_config(config_dict, self.config_path)
    
    def update_framework(self, name: str, **updates) -> bool:
        """Update a framework configuration."""
        framework = self.config.get_framework(name)
        if framework:
            for key, value in updates.items():
                if hasattr(framework, key):
                    setattr(framework, key, value)
            return True
        return False
    
    def validate_config(self) -> List[str]:
        """Validate the configuration and return a list of errors."""
        errors = []
        
        # Validate server config
        if self.config.server.port < 1 or self.config.server.port > 65535:
            errors.append("Server port must be between 1 and 65535")
        
        # Validate security config
        if self.config.security.rate_limit_enabled and self.config.security.max_requests_per_minute <= 0:
            errors.append("Max requests per minute must be positive when rate limiting is enabled")
        
        # Validate frameworks
        framework_names = set()
        for framework in self.config.frameworks:
            if framework.name in framework_names:
                errors.append(f"Duplicate framework name: {framework.name}")
            else:
                framework_names.add(framework.name)
            
            # Validate endpoint format
            if not framework.endpoint.startswith(("http://", "https://")):
                errors.append(f"Framework endpoint must be a valid URL: {framework.endpoint}")
        
        return errors
    
    def get_active_frameworks(self) -> List[FrameworkConfig]:
        """Get list of enabled frameworks."""
        return [fw for fw in self.config.frameworks if fw.enabled]


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def set_config_manager(manager: ConfigManager) -> None:
    """Set the global configuration manager instance."""
    global _config_manager
    _config_manager = manager
