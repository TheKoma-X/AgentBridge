"""
Command Line Interface for AgentBridge
"""

import asyncio
import click
import json
import yaml
from pathlib import Path
from .bridge import AgentBridge
from .protocol import Message, MessageType
from .config import BridgeConfig, ConfigManager
from .security import SecurityManager, get_security_manager


@click.group()
def main():
    """AgentBridge CLI - Universal AI Agent Interoperability Protocol"""
    pass


@main.command()
@click.option('--config', '-c', default='agentbridge.yaml', help='Configuration file path')
def init(config):
    """Initialize a new AgentBridge configuration."""
    config_path = config
    
    # Create a default configuration using BridgeConfig
    default_config = BridgeConfig()
    
    # Convert to dict and save as YAML
    config_dict = default_config.to_dict()
    
    with open(config_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False)
    
    click.echo(f"Created default configuration at {config_path}")


@main.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8080, help='Port to bind to')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
def serve(host, port, config):
    """Start the AgentBridge server."""
    bridge = AgentBridge(config_path=config)
    
    click.echo(f"Starting AgentBridge server on {host}:{port}")
    
    # Run the async server
    try:
        asyncio.run(bridge.start_server(host=host, port=port))
    except KeyboardInterrupt:
        click.echo("\nServer stopped by user")
    except Exception as e:
        click.echo(f"Server error: {e}")
        raise


@main.command()
@click.argument('framework_name')
@click.argument('endpoint')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
def connect(framework_name, endpoint, config):
    """Connect to an agent framework."""
    bridge = AgentBridge(config_path=config)
    
    try:
        adapter = bridge.connect_framework(framework_name, endpoint)
        click.echo(f"Successfully connected to {framework_name} at {endpoint}")
    except Exception as e:
        click.echo(f"Failed to connect: {str(e)}")


@main.command()
@click.option('--source', required=True, help='Source framework name')
@click.option('--target', required=True, help='Target framework name')
@click.option('--message-type', default='TASK_REQUEST', help='Type of message')
@click.option('--content', required=True, help='Message content (JSON)')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
def send_message(source, target, message_type, content, config):
    """Send a message between agent frameworks."""
    bridge = AgentBridge(config_path=config)
    
    try:
        # Parse content as JSON
        content_json = json.loads(content)
        
        # Create message
        import time
        message_type_enum = MessageType[message_type.upper()]
        message = Message(
            type=message_type_enum,
            source=source,
            target=target,
            content=content_json,
            timestamp=time.time()
        )
        
        # Since this is sync command, we need to run the async function
        async def send():
            result = await bridge.send_message(source, target, message)
            return result
            
        result = asyncio.run(send())
        click.echo(f"Message sent successfully. Result: {result}")
    except KeyError:
        click.echo(f"Invalid message type: {message_type}. Valid types: {[t.name for t in MessageType]}")
    except Exception as e:
        click.echo(f"Failed to send message: {str(e)}")


@main.command()
@click.option('--source', required=True, help='Source framework name')
@click.option('--content', required=True, help='Message content (JSON)')
@click.option('--target-frameworks', '-t', multiple=True, help='Target framework names (can specify multiple)')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
def broadcast(source, content, target_frameworks, config):
    """Broadcast a message to multiple agent frameworks."""
    bridge = AgentBridge(config_path=config)
    
    try:
        # Parse content as JSON
        content_json = json.loads(content)
        
        # Create message
        import time
        message = Message(
            type=MessageType.TASK_REQUEST,  # Default type for broadcast
            source=source,
            target="all",
            content=content_json,
            timestamp=time.time()
        )
        
        # Convert tuple to list for target_frameworks
        target_list = list(target_frameworks) if target_frameworks else None
        
        # Since this is sync command, we need to run the async function
        async def broadcast():
            result = await bridge.broadcast_message(source, message, target_list)
            return result
            
        result = asyncio.run(broadcast())
        click.echo(f"Message broadcasted successfully. Results: {json.dumps(result, indent=2)}")
    except Exception as e:
        click.echo(f"Failed to broadcast message: {str(e)}")


@main.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
def status(config):
    """Get the status of the bridge."""
    bridge = AgentBridge(config_path=config)
    status_info = bridge.get_status()
    
    click.echo("AgentBridge Status:")
    click.echo(json.dumps(status_info, indent=2))


@main.command()
def list_frameworks():
    """List supported agent frameworks."""
    from .adapter import AdapterRegistry
    
    registry = AdapterRegistry()
    frameworks = registry.list_adapters()
    
    click.echo("Supported agent frameworks:")
    for framework in frameworks:
        click.echo(f"- {framework}")


@main.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
def validate_config(config):
    """Validate the configuration file."""
    if not config:
        click.echo("No configuration file provided")
        return
    
    try:
        config_manager = ConfigManager(config_path=config)
        errors = config_manager.validate_config()
        
        if errors:
            click.echo("Configuration validation errors:")
            for error in errors:
                click.echo(f"  - {error}")
        else:
            click.echo("Configuration is valid!")
    except Exception as e:
        click.echo(f"Error validating configuration: {str(e)}")


@main.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--permissions', '-p', multiple=True, default=['read', 'write'], help='Permissions for the token')
@click.option('--expires-in', '-e', default=24, help='Token expiration in hours (0 for no expiration)')
def generate_token(config, permissions, expires_in):
    """Generate a new authentication token."""
    bridge = AgentBridge(config_path=config)
    
    try:
        token = bridge.security_manager.generate_token(
            permissions=list(permissions), 
            expires_in_hours=int(expires_in) if int(expires_in) > 0 else None
        )
        click.echo(f"Generated token: {token}")
        click.echo(f"Permissions: {list(permissions)}")
        if expires_in != "0":
            click.echo(f"Expires in: {expires_in} hours")
        else:
            click.echo("Expires: Never")
    except Exception as e:
        click.echo(f"Failed to generate token: {str(e)}")


@main.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
def security_status(config):
    """Show security configuration and status."""
    bridge = AgentBridge(config_path=config)
    
    sec_config = bridge.config.security
    click.echo("Security Configuration:")
    click.echo(f"  Authentication required: {sec_config.require_auth}")
    click.echo(f"  Encryption enabled: {sec_config.encryption_enabled}")
    click.echo(f"  Trusted frameworks only: {sec_config.trusted_frameworks_only}")
    click.echo(f"  Allowed frameworks: {sec_config.allowed_frameworks}")
    click.echo(f"  Rate limiting: {sec_config.rate_limit_enabled}")
    if sec_config.rate_limit_enabled:
        click.echo(f"  Max requests per minute: {sec_config.max_requests_per_minute}")
    
    click.echo(f"\nActive security tokens: {len(bridge.security_manager.tokens)}")


if __name__ == '__main__':
    main()