# AgentBridge

Universal AI Agent Interoperability Protocol - Connecting the fragmented AI agent ecosystem

## Vision

AgentBridge is the universal protocol that enables seamless communication and collaboration between different AI agent frameworks. Whether you're using CrewAI, LangGraph, AutoGen, Claude-Flow, or any other agent framework, AgentBridge provides the standardized bridge for them to work together.

## Key Features

- **Universal Compatibility**: Bridge any AI agent framework with standardized protocols
- **MCP Enhancement**: Extended Model Context Protocol for cross-framework communication  
- **Framework Adapters**: Pre-built adapters for major agent frameworks
- **Tool Standardization**: Unified tool interfaces across different frameworks
- **Workflow Composition**: Combine agents from different frameworks into single workflows
- **Security First**: Sandboxed execution and permission management
- **Performance Optimized**: Efficient message routing and execution coordination
- **Enhanced Configuration**: Comprehensive configuration management system
- **Advanced Logging**: Detailed logging with file output and correlation tracking
- **Metrics Collection**: Built-in metrics and monitoring capabilities
- **Improved Error Handling**: Detailed error reporting and graceful degradation

## Supported Frameworks

- Claude-Flow
- CrewAI
- LangGraph
- AutoGen
- ActivePieces
- Custom Agent Frameworks
- More coming soon...

## Quick Start

```bash
# Install AgentBridge
pip install agentbridge

# Initialize bridge configuration
agentbridge init

# Connect different agent frameworks
agentbridge connect --framework crewai --endpoint http://localhost:8000
agentbridge connect --framework langgraph --endpoint http://localhost:8001

# Start the bridge server
agentbridge serve --port 8080
```

## Advanced Features

### Configuration Management
AgentBridge includes a comprehensive configuration system with validation and management capabilities:

```python
from agentbridge import BridgeConfig, ConfigManager

# Create a configuration
config = BridgeConfig()
config.add_framework("my_framework", "http://localhost:8000", enabled=True)

# Validate configuration
config_manager = ConfigManager()
errors = config_manager.validate_config()
if not errors:
    print("Configuration is valid!")
```

### Enhanced Logging and Monitoring
Detailed logging with correlation tracking and file output:

```python
from agentbridge import get_logger
from agentbridge.logging import LogLevel, FileLogHandler

logger = get_logger()
# Add file handler for persistent logs
file_handler = FileLogHandler("./logs/agentbridge.log")
logger.handlers.append(file_handler)

# Track requests with correlation IDs
logger.push_correlation_id("request-123")
logger.info("MyComponent", "Processing request", {"step": 1})
```

### Metrics Collection
Built-in metrics collection for monitoring performance:

```python
from agentbridge import get_metrics_collector

metrics = get_metrics_collector()
metrics.increment_counter('messages_processed')
metrics.record_timer('response_time', 0.25)

# Get all collected metrics
all_metrics = metrics.get_metrics()
print(f"Processed {all_metrics['counters']['messages_processed']} messages")
```

## Architecture

AgentBridge operates as a middleware layer that translates between different agent frameworks:

```
[Framework A] <---> [AgentBridge] <---> [Framework B]
     |                   |                   |
   Protocol A        Translation       Protocol B
```

The system includes:
- **Core Bridge**: Central hub for message routing
- **Protocol Layer**: Standardized message format and translation
- **Adapters**: Framework-specific connectors
- **Configuration System**: Comprehensive config management
- **Logging System**: Advanced logging with correlation tracking
- **Metrics System**: Performance monitoring and collection

## API Endpoints

When running the server, the following endpoints are available:

- `GET /` - Root endpoint with API information
- `GET /status` - Bridge status and metrics
- `POST /connect` - Connect to a framework
- `POST /send_message` - Send message between frameworks
- `POST /broadcast` - Broadcast message to multiple frameworks
- `GET /frameworks` - List connected frameworks
- `GET /protocols` - List supported protocols
- `WS /ws` - WebSocket endpoint for real-time communication

## CLI Commands

AgentBridge provides a comprehensive CLI for management:

```bash
# Initialize configuration
agentbridge init

# Start the server
agentbridge serve --port 8080

# Connect to frameworks
agentbridge connect --framework crewai --endpoint http://localhost:8000

# Check status
agentbridge status

# List supported frameworks
agentbridge list-frameworks

# Send a message
agentbridge send-message --source crewai --target langgraph --content '{"task": "analyze"}'
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.
