# AgentBridge Security Features

## Overview

AgentBridge includes comprehensive security features designed to protect multi-agent communications in enterprise environments. The security system provides authentication, authorization, encryption, and trust validation capabilities.

## Security Architecture

The security system consists of several interconnected components:

- **Security Manager**: Centralized security control and policy enforcement
- **Security Middleware**: Request interception and validation
- **Authentication System**: Token-based identity verification
- **Authorization System**: Permission-based access control
- **Encryption System**: Data protection in transit
- **Trust Validation**: Framework reputation and verification

## Authentication

### Token-Based Authentication
- JWT-style tokens generated with cryptographically secure random strings
- Configurable token expiration periods
- Multiple permission levels per token
- Automatic cleanup of expired tokens

### Example Usage
```python
from agentbridge import AgentBridge

bridge = AgentBridge()
# Generate a read-only token
read_token = bridge.security_manager.generate_token(["read"], expires_in_hours=24)

# Generate an admin token
admin_token = bridge.security_manager.generate_token(
    ["read", "write", "admin"], 
    expires_in_hours=1
)

# Authenticate requests
try:
    bridge.security_manager.authenticate(admin_token)
    print("Authentication successful")
except AuthenticationError:
    print("Authentication failed")
```

## Authorization

### Role-Based Permissions
- Granular permission system (read, write, admin, etc.)
- Permission validation per operation
- Automatic permission checking
- Configurable permission sets

### Example Usage
```python
# Check if a token has specific permissions
try:
    bridge.security_manager.authorize(admin_token, 'write')
    print("Write permission granted")
except AuthorizationError:
    print("Write permission denied")
```

## Encryption

### Data Protection
- AES-256 encryption for sensitive data
- Automatic encryption/decryption of payloads
- Secure key generation and management
- Optional encryption per configuration

### Example Usage
```python
# Encrypt sensitive data
encrypted_data = bridge.security_manager.encrypt_data("sensitive information")

# Decrypt data
decrypted_data = bridge.security_manager.decrypt_data(encrypted_data)
```

## Framework Trust Validation

### Trusted Framework System
- Configurable list of trusted agent frameworks
- Enforcement of trusted framework connections
- Prevention of unauthorized framework access
- Dynamic trust management

### Example Usage
```python
# Check if framework is trusted
if bridge.security_manager.is_trusted_framework("crewai_main"):
    # Proceed with connection
    pass
else:
    # Reject connection
    raise ValueError("Framework not trusted")
```

## Origin Validation

### Request Source Verification
- Configurable list of allowed origins
- Prevention of cross-origin attacks
- Whitelist-based validation
- Flexible origin matching

## Rate Limiting

### Request Throttling
- Configurable request limits per time period
- Prevention of API abuse
- Fair usage enforcement
- Automatic reset of counters

## API Security

### Protected Endpoints
All API endpoints are protected by security middleware:

- **Authentication Required**: All endpoints check for valid tokens when configured
- **Authorization Checked**: Specific permissions required for different operations
- **Origin Validated**: Requests validated against allowed origins
- **Rate Limited**: Requests limited according to configuration

### WebSocket Security
- Token-based authentication for WebSocket connections
- Permission-based authorization for operations
- Secure message transmission
- Connection validation

## CLI Security Commands

### Token Management
```bash
# Generate new tokens
agentbridge generate-token --permissions read write --expires-in 24
agentbridge generate-token --permissions admin --expires-in 8

# Check security status
agentbridge security-status
```

## Configuration Options

### Security Settings
```yaml
security:
  require_auth: true              # Require authentication
  allowed_origins:               # Allow requests from these origins
    - "https://trusted.com"
    - "localhost"
  auth_tokens: []                # Pre-defined valid tokens
  rate_limit_enabled: true       # Enable rate limiting
  max_requests_per_minute: 100   # Max requests per minute
  encryption_enabled: true       # Enable data encryption
  trusted_frameworks_only: true  # Only allow trusted frameworks
  allowed_frameworks:           # List of trusted frameworks
    - "crewai_main"
    - "langgraph_prod"
```

## Security Best Practices

### For Production Deployments
1. **Always enable authentication** in production environments
2. **Use HTTPS** for all communications
3. **Implement proper token lifecycle** management
4. **Regularly rotate tokens** and credentials
5. **Monitor security logs** for suspicious activity
6. **Limit framework access** to only necessary frameworks
7. **Configure appropriate rate limits** to prevent abuse
8. **Enable encryption** for sensitive data

### Recommended Configuration
```yaml
security:
  require_auth: true
  encryption_enabled: true
  trusted_frameworks_only: true
  rate_limit_enabled: true
  max_requests_per_minute: 50
  allowed_origins:
    - "https://yourdomain.com"
  allowed_frameworks:
    - "production_crewai"
    - "production_langgraph"
```

## Security Monitoring

### Security Events
- Authentication failures
- Authorization violations
- Trust validation failures
- Rate limit exceedances
- Suspicious origin requests

### Logging
All security events are logged with appropriate severity levels and correlation IDs for tracking.

## Integration Points

### With Other Systems
- Configuration system for security policies
- Logging system for security events
- Metrics system for security statistics
- Framework adapters for trust validation
- Server middleware for request filtering

The security system is designed to be enterprise-ready, providing defense-in-depth protection while maintaining ease of use for legitimate operations.