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

## Architecture

AgentBridge operates as a middleware layer that translates between different agent frameworks:

```
[Framework A] <---> [AgentBridge] <---> [Framework B]
     |                   |                   |
   Protocol A        Translation       Protocol B
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.