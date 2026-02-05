"""
Security features demonstration for AgentBridge
"""

import asyncio
import json
import sys
sys.path.insert(0, '.')

from agentbridge import (
    AgentBridge, 
    BridgeConfig, 
    get_logger,
    set_logger
)
from agentbridge.logging import AgentBridgeLogger, LogLevel
from agentbridge.security import SecurityManager, AuthenticationError, AuthorizationError


async def security_demo():
    """Demonstrate AgentBridge security features."""
    
    print("=" * 70)
    print("AGENTBRIDGE SECURITY FEATURES DEMONSTRATION")
    print("=" * 70)
    
    # 1. SET UP LOGGING
    print("\n1. 🔐 SETTING UP SECURITY-AWARE LOGGING")
    print("-" * 40)
    
    logger = AgentBridgeLogger(name="SecurityDemo", level=LogLevel.INFO)
    set_logger(logger)
    
    print("   ✓ Security-aware logger initialized")
    
    # 2. CREATE SECURE CONFIGURATION
    print("\n2. ⚙️  CREATING SECURE CONFIGURATION")
    print("-" * 40)
    
    config = BridgeConfig()
    config.version = "1.1"
    config.security.require_auth = True
    config.security.encryption_enabled = True
    config.security.trusted_frameworks_only = True
    config.security.allowed_frameworks = ["secure_crewai", "secure_langgraph", "trusted_autogen"]
    config.security.allowed_origins = ["https://trusted-domain.com", "localhost", "127.0.0.1"]
    config.security.rate_limit_enabled = True
    config.security.max_requests_per_minute = 100
    
    print(f"   ✓ Authentication required: {config.security.require_auth}")
    print(f"   ✓ Encryption enabled: {config.security.encryption_enabled}")
    print(f"   ✓ Trusted frameworks only: {config.security.trusted_frameworks_only}")
    print(f"   ✓ Allowed frameworks: {config.security.allowed_frameworks}")
    print(f"   ✓ Rate limiting: {config.security.rate_limit_enabled}")
    
    # 3. INITIALIZE BRIDGE WITH SECURITY
    print("\n3. 🛡️  INITIALIZING BRIDGE WITH SECURITY")
    print("-" * 40)
    
    bridge = AgentBridge()
    bridge.config = config
    # The bridge.__init__ automatically sets up security_manager with the config
    
    print("   ✓ Bridge initialized with security configuration")
    print("   ✓ Security manager active")
    
    # 4. TOKEN MANAGEMENT DEMONSTRATION
    print("\n4. 🔑 TOKEN MANAGEMENT DEMONSTRATION")
    print("-" * 40)
    
    # Generate different types of tokens
    read_token = bridge.security_manager.generate_token(["read"], expires_in_hours=24)
    write_token = bridge.security_manager.generate_token(["read", "write"], expires_in_hours=24)
    admin_token = bridge.security_manager.generate_token(["read", "write", "admin"], expires_in_hours=1)
    
    print(f"   ✓ Read-only token generated: {read_token[:16]}...")
    print(f"   ✓ Read-write token generated: {write_token[:16]}...")
    print(f"   ✓ Admin token generated: {admin_token[:16]}...")
    print("   ✓ Tokens have different permission levels")
    print("   ✓ Tokens have configurable expiration")
    
    # 5. AUTHENTICATION DEMONSTRATION
    print("\n5. ✅ AUTHENTICATION DEMONSTRATION")
    print("-" * 40)
    
    try:
        # Valid authentication
        result = bridge.security_manager.authenticate(read_token)
        print("   ✓ Valid token authentication successful")
    except AuthenticationError as e:
        print(f"   ✗ Authentication failed: {e}")
    
    try:
        # Invalid authentication
        bridge.security_manager.authenticate("invalid_token_12345")
        print("   ✗ Invalid token should have failed")
    except AuthenticationError:
        print("   ✓ Invalid token authentication correctly rejected")
    
    # 6. AUTHORIZATION DEMONSTRATION
    print("\n6. 🚧 AUTHORIZATION DEMONSTRATION")
    print("-" * 40)
    
    try:
        # Read permission with read-token (should succeed)
        result = bridge.security_manager.authorize(read_token, "read")
        print("   ✓ Read permission granted to read-token")
    except AuthorizationError:
        print("   ✗ Read permission should have been granted")
    
    try:
        # Write permission with read-token (should fail)
        bridge.security_manager.authorize(read_token, "write")
        print("   ✗ Write permission should have been denied to read-token")
    except AuthorizationError:
        print("   ✓ Write permission correctly denied to read-token")
    
    try:
        # Write permission with write-token (should succeed)
        result = bridge.security_manager.authorize(write_token, "write")
        print("   ✓ Write permission granted to write-token")
    except AuthorizationError:
        print("   ✗ Write permission should have been granted to write-token")
    
    # 7. FRAMEWORK TRUST VERIFICATION
    print("\n7. 🛡️  FRAMEWORK TRUST VERIFICATION")
    print("-" * 40)
    
    trusted_framework = "secure_crewai"
    untrusted_framework = "malicious_framework"
    
    is_trusted_1 = bridge.security_manager.is_trusted_framework(trusted_framework)
    is_trusted_2 = bridge.security_manager.is_trusted_framework(untrusted_framework)
    
    print(f"   ✓ '{trusted_framework}' is trusted: {is_trusted_1}")
    print(f"   ✓ '{untrusted_framework}' is trusted: {is_trusted_2}")
    print("   ✓ Framework trust verification active")
    
    # 8. DATA ENCRYPTION DEMONSTRATION
    print("\n8. 🔐 DATA ENCRYPTION DEMONSTRATION")
    print("-" * 40)
    
    sensitive_data = "This is highly confidential agent communication"
    
    # Encrypt the data
    encrypted_data = bridge.security_manager.encrypt_data(sensitive_data)
    print(f"   ✓ Original data: {sensitive_data[:30]}...")
    print(f"   ✓ Encrypted: {encrypted_data[:30]}..." if encrypted_data != sensitive_data else "   ✓ Encryption not applied (disabled in config)")
    
    if config.security.encryption_enabled and encrypted_data != sensitive_data:
        # Decrypt the data
        decrypted_data = bridge.security_manager.decrypt_data(encrypted_data)
        print(f"   ✓ Decrypted: {decrypted_data[:30]}...")
        print(f"   ✓ Data integrity verified: {sensitive_data == decrypted_data}")
    
    # 9. ORIGIN VALIDATION
    print("\n9. 🌐 ORIGIN VALIDATION DEMONSTRATION")
    print("-" * 40)
    
    valid_origin = "https://trusted-domain.com"
    invalid_origin = "https://malicious-site.com"
    
    origin_check_1 = bridge.security_manager.validate_origin(valid_origin)
    origin_check_2 = bridge.security_manager.validate_origin(invalid_origin)
    
    print(f"   ✓ Valid origin '{valid_origin}' allowed: {origin_check_1}")
    print(f"   ✓ Invalid origin '{invalid_origin}' allowed: {origin_check_2}")
    
    # 10. ATTEMPTING SECURE OPERATIONS
    print("\n10. 🛠️  ATTEMPTING SECURE OPERATIONS")
    print("-" * 40)
    
    # This would connect frameworks, but we'll simulate the security checks
    try:
        # Try to connect a trusted framework
        if bridge.security_manager.is_trusted_framework("secure_crewai"):
            print("   ✓ Security check passed for trusted framework")
        else:
            print("   ✗ Security check failed for trusted framework")
    except Exception as e:
        print(f"   ? Security check error: {e}")
    
    try:
        # Try to connect an untrusted framework (simulated)
        if bridge.security_manager.is_trusted_framework("untrusted_framework"):
            print("   ? Security check unexpectedly passed for untrusted framework")
        else:
            print("   ✓ Security check correctly blocked untrusted framework")
    except Exception as e:
        print(f"   ? Security check error: {e}")
    
    # 11. SECURITY STATUS REPORT
    print("\n11. 📊 SECURITY STATUS REPORT")
    print("-" * 40)
    
    sec_config = bridge.config.security
    print(f"   • Authentication: {'Required' if sec_config.require_auth else 'Not required'}")
    print(f"   • Encryption: {'Enabled' if sec_config.encryption_enabled else 'Disabled'}")
    print(f"   • Trust enforcement: {'Active' if sec_config.trusted_frameworks_only else 'Inactive'}")
    print(f"   • Rate limiting: {'Active' if sec_config.rate_limit_enabled else 'Inactive'}")
    print(f"   • Active tokens: {len(bridge.security_manager.tokens)}")
    print(f"   • Trusted frameworks: {len(sec_config.allowed_frameworks)}")
    
    # 12. CLI SECURITY COMMANDS SIMULATION
    print("\n12. 💻 CLI SECURITY COMMANDS")
    print("-" * 40)
    
    print("   Example CLI commands for security management:")
    print("   • agentbridge generate-token --permissions read write")
    print("   • agentbridge generate-token --permissions admin --expires-in 8")
    print("   • agentbridge security-status")
    print("   • agentbridge connect --framework secure_crewai (if trusted)")
    
    print("\n" + "=" * 70)
    print("🎉 SECURITY FEATURES DEMONSTRATION COMPLETE!")
    print("🔒 AgentBridge is now configured with enterprise-grade security")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(security_demo())