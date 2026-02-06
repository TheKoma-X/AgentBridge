"""
Security module for AgentBridge - Authentication, authorization, and encryption
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from .config import BridgeConfig


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthorizationError(Exception):
    """Raised when authorization fails."""
    pass


class ResourcePermission:
    """Defines specific permissions for resources."""
    
    def __init__(self, resource: str, actions: List[str]):
        self.resource = resource  # e.g., "frameworks", "models", "workflows"
        self.actions = actions    # e.g., ["read", "write", "delete", "execute"]


class SecurityManager:
    """
    Security manager for AgentBridge - handles authentication, authorization, and encryption
    """
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.roles: Dict[str, List[ResourcePermission]] = {}  # Role-based permissions
        self.user_roles: Dict[str, List[str]] = {}  # Token to roles mapping
        self._initialize_security()
    
    def _initialize_security(self):
        """Initialize security components based on configuration."""
        # Initialize tokens from config if provided
        if self.config.security.auth_tokens:
            for token in self.config.security.auth_tokens:
                # Add token with default permissions
                self.tokens[token] = {
                    'permissions': ['read', 'write'],
                    'expires_at': None,
                    'created_at': datetime.now(),
                    'roles': []  # No roles initially
                }
        
        # Generate encryption key if needed
        if self.config.security.encryption_enabled:
            self.encryption_key = self._generate_encryption_key()
            self.cipher_suite = Fernet(self.encryption_key)
        else:
            self.encryption_key = None
            self.cipher_suite = None
    
    def create_role(self, role_name: str, permissions: List[ResourcePermission]):
        """Create a new role with specific permissions."""
        self.roles[role_name] = permissions
    
    def assign_role_to_token(self, token: str, role_name: str):
        """Assign a role to a token."""
        if token in self.tokens and role_name in self.roles:
            if role_name not in self.tokens[token]['roles']:
                self.tokens[token]['roles'].append(role_name)
    
    def revoke_role_from_token(self, token: str, role_name: str):
        """Remove a role from a token."""
        if token in self.tokens and role_name in self.tokens[token]['roles']:
            self.tokens[token]['roles'].remove(role_name)
    
    def has_resource_permission(self, token: str, resource: str, action: str) -> bool:
        """Check if a token has permission to perform an action on a resource."""
        if token not in self.tokens:
            return False
        
        # Check direct permissions
        if action in self.tokens[token].get('permissions', []):
            return True
        
        # Check role-based permissions
        for role_name in self.tokens[token].get('roles', []):
            if role_name in self.roles:
                for permission in self.roles[role_name]:
                    if permission.resource == resource and action in permission.actions:
                        return True
        
        return False
    
    def _generate_encryption_key(self) -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()
    
    def generate_token(self, permissions: List[str] = None, expires_in_hours: int = 24) -> str:
        """Generate a new authentication token."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expires_in_hours) if expires_in_hours else None
        
        self.tokens[token] = {
            'permissions': permissions or ['read', 'write'],
            'expires_at': expires_at,
            'created_at': datetime.now(),
            'roles': []  # Initialize roles for new tokens
        }
        
        return token
    
    def authenticate(self, token: str) -> bool:
        """Authenticate a token."""
        if not self.config.security.require_auth:
            return True  # Authentication not required
        
        if token not in self.tokens:
            raise AuthenticationError("Invalid token")
        
        token_info = self.tokens[token]
        
        # Check if token has expired
        if token_info['expires_at'] and datetime.now() > token_info['expires_at']:
            del self.tokens[token]  # Remove expired token
            raise AuthenticationError("Token has expired")
        
        return True
    
    def authorize(self, token: str, permission: str, resource: str = None) -> bool:
        """Authorize a token for a specific permission."""
        if token not in self.tokens:
            raise AuthenticationError("Invalid token")
        
        token_info = self.tokens[token]
        
        # Check if token has expired
        if token_info['expires_at'] and datetime.now() > token_info['expires_at']:
            del self.tokens[token]  # Remove expired token
            raise AuthenticationError("Token has expired")
        
        # If resource is specified, use resource-based permission check
        if resource:
            if self.has_resource_permission(token, resource, permission):
                return True
        else:
            # Check direct permissions
            if permission in token_info['permissions']:
                return True
        
        raise AuthorizationError(f"Permission '{permission}' not granted for resource '{resource or 'default'}'")
    
    def encrypt_data(self, data: str) -> Optional[str]:
        """Encrypt data if encryption is enabled."""
        if not self.cipher_suite:
            return data  # Return as-is if encryption not enabled
        
        try:
            encrypted_bytes = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """Decrypt data if encryption is enabled."""
        if not self.cipher_suite:
            return encrypted_data  # Return as-is if encryption not enabled
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def hash_data(self, data: str) -> str:
        """Hash data for integrity verification."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_hash(self, data: str, expected_hash: str) -> bool:
        """Verify data integrity against hash."""
        return self.hash_data(data) == expected_hash
    
    def is_trusted_framework(self, framework_name: str) -> bool:
        """Check if a framework is in the trusted list."""
        if not self.config.security.trusted_frameworks_only:
            return True  # All frameworks trusted if not enforcing trusted list
        
        return framework_name in self.config.security.allowed_frameworks
    
    def validate_origin(self, origin: str) -> bool:
        """Validate request origin against allowed origins."""
        allowed_origins = self.config.security.allowed_origins
        
        if "*" in allowed_origins:
            return True  # Allow all origins
        
        return origin in allowed_origins


class SecurityMiddleware:
    """
    Middleware class to integrate security into request handling
    """
    
    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager
    
    async def authenticate_request(self, headers: Dict[str, str]) -> Optional[str]:
        """Extract and validate token from request headers."""
        auth_header = headers.get('Authorization', '')
        
        if not auth_header:
            if self.security_manager.config.security.require_auth:
                raise AuthenticationError("Authorization header required")
            return None
        
        # Handle different auth schemes
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        elif auth_header.startswith('Token '):
            token = auth_header[6:]
        else:
            token = auth_header
        
        # Authenticate the token
        self.security_manager.authenticate(token)
        
        return token
    
    async def authorize_request(self, token: str, permission: str, resource: str = None) -> bool:
        """Authorize a request for a specific permission."""
        return self.security_manager.authorize(token, permission, resource)
    
    def encrypt_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive parts of response if needed."""
        # Only encrypt if specifically marked or if security requires it
        if self.security_manager.config.security.encryption_enabled:
            # This is a simplified approach - in practice you'd want to be more selective
            # about what data to encrypt
            return response_data
        return response_data


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager(config: BridgeConfig) -> SecurityManager:
    """Get the global security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(config)
    return _security_manager


def set_security_manager(manager: SecurityManager) -> None:
    """Set the global security manager instance."""
    global _security_manager
    _security_manager = manager