"""
Security tests for AgentBridge
"""

import asyncio
import sys
sys.path.insert(0, '.')

from agentbridge import (
    AgentBridge, 
    BridgeConfig, 
    get_security_manager,
    AuthenticationError,
    AuthorizationError
)
from agentbridge.security import SecurityManager


def test_security_manager_initialization():
    """Test security manager initialization."""
    config = BridgeConfig()
    config.security.require_auth = False
    config.security.encryption_enabled = False
    
    security_manager = SecurityManager(config)  # Create directly to avoid global state
    
    assert security_manager is not None
    assert len(security_manager.tokens) == 0  # No tokens initially
    
    print("✓ test_security_manager_initialization passed")


def test_token_generation():
    """Test token generation functionality."""
    config = BridgeConfig()
    security_manager = SecurityManager(config)
    
    # Generate a token
    token = security_manager.generate_token(['read', 'write'], expires_in_hours=1)
    
    assert token is not None
    assert len(token) > 10  # Tokens should be reasonably long
    assert token in security_manager.tokens
    
    token_info = security_manager.tokens[token]
    assert 'read' in token_info['permissions']
    assert 'write' in token_info['permissions']
    
    print("✓ test_token_generation passed")


def test_authentication():
    """Test authentication functionality."""
    config = BridgeConfig()
    config.security.require_auth = True  # Require auth for this test
    security_manager = SecurityManager(config)  # Create directly to bypass global state
    
    # Generate a token
    token = security_manager.generate_token(['read', 'write'])
    
    # Authenticate with valid token
    result = security_manager.authenticate(token)
    assert result is True
    
    # Authenticate with invalid token
    try:
        security_manager.authenticate("invalid_token")
        assert False, "Should have raised AuthenticationError"
    except AuthenticationError:
        pass  # Expected
    
    print("✓ test_authentication passed")


def test_authorization():
    """Test authorization functionality."""
    config = BridgeConfig()
    security_manager = SecurityManager(config)
    
    # Generate a token with specific permissions
    token = security_manager.generate_token(['read', 'admin'])
    
    # Authorize with valid permission
    result = security_manager.authorize(token, 'read')
    assert result is True
    
    # Authorize with invalid permission
    try:
        security_manager.authorize(token, 'write')  # Not in token's permissions
        assert False, "Should have raised AuthorizationError"
    except AuthorizationError:
        pass  # Expected
    
    print("✓ test_authorization passed")


def test_encryption():
    """Test encryption functionality."""
    config = BridgeConfig()
    config.security.encryption_enabled = True
    security_manager = SecurityManager(config)
    
    test_data = "This is sensitive data"
    
    # Encrypt data
    encrypted = security_manager.encrypt_data(test_data)
    assert encrypted is not None
    assert encrypted != test_data  # Should be different when encrypted
    
    # Decrypt data
    decrypted = security_manager.decrypt_data(encrypted)
    assert decrypted == test_data
    
    print("✓ test_encryption passed")


def test_trusted_frameworks():
    """Test trusted framework functionality."""
    config = BridgeConfig()
    config.security.trusted_frameworks_only = True
    config.security.allowed_frameworks = ["trusted_framework_1", "trusted_framework_2"]
    
    security_manager = SecurityManager(config)
    
    # Test trusted framework
    assert security_manager.is_trusted_framework("trusted_framework_1") is True
    assert security_manager.is_trusted_framework("trusted_framework_2") is True
    
    # Test untrusted framework
    assert security_manager.is_trusted_framework("untrusted_framework") is False
    
    # Test when trusted frameworks enforcement is disabled
    config.security.trusted_frameworks_only = False
    assert security_manager.is_trusted_framework("any_framework") is True
    
    print("✓ test_trusted_frameworks passed")


def test_bridge_security_integration():
    """Test that bridge integrates security properly."""
    config = BridgeConfig()
    config.security.trusted_frameworks_only = True
    config.security.allowed_frameworks = ["test_framework"]
    
    bridge = AgentBridge()
    bridge.config = config
    bridge.security_manager = SecurityManager(config)
    
    # Should be able to connect trusted framework
    assert bridge.security_manager.is_trusted_framework("test_framework") is True
    
    # Should not be able to connect untrusted framework
    assert bridge.security_manager.is_trusted_framework("untrusted") is False
    
    print("✓ test_bridge_security_integration passed")


if __name__ == "__main__":
    print("Running security tests...")
    
    test_security_manager_initialization()
    test_token_generation()
    test_authentication()
    test_authorization()
    test_encryption()
    test_trusted_frameworks()
    test_bridge_security_integration()
    
    print("\n✓ All security tests passed successfully!")