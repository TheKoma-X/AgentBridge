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


@click.group()
def main():
    """AgentBridge CLI - Universal AI Agent Interoperability Protocol"""
    pass


@main.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
def init(config):
    """Initialize a new AgentBridge configuration."""
    config_path = config or "agentbridge.yaml"
    
    default_config = {
        'version': '1.0',
        'server': {
            'host': 'localhost',
            'port': 8080
        },
        'frameworks': {},
        'security': {
            'require_auth': False,
            'allowed_origins': ['*']
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
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
    asyncio.run(bridge.start_server(host=host, port=port))


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
@click.option('--message-type', default='task_request', help='Type of message')
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
        message = Message(
            type=MessageType[message_type.upper()],
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
    except Exception as e:
        click.echo(f"Failed to send message: {str(e)}")


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


if __name__ == '__main__':
    main()