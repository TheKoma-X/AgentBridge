# AgentBridge

Universal AI Agent Interoperability Protocol - Connecting the fragmented AI agent ecosystem

## Vision

AgentBridge is the universal protocol that enables seamless communication and collaboration between different AI agent frameworks. Whether you're using CrewAI, LangGraph, AutoGen, Claude-Flow, or any other agent framework, AgentBridge provides the standardized bridge for them to work together.

## Key Innovations

- **Universal Protocol**: Standardized message format for cross-framework communication
- **Framework Adapters**: Connect any AI agent framework through pluggable adapters
- **Workflow Engine**: Cross-framework orchestration and task management
- **AI Model Management**: Intelligent model routing and capability-based selection
- **Intelligent Decision Making**: AI-driven optimization and routing strategies
- **Extended Ecosystem**: Support for LangChain, LlamaIndex, databases, APIs and more
- **Enterprise Security**: Multi-layer authentication, authorization, and encryption
- **Advanced Monitoring**: Comprehensive logging, metrics, and observability

## Key Features

- **Universal Compatibility**: Bridge any AI agent framework with standardized protocols
- **MCP Enhancement**: Extended Model Context Protocol for cross-framework communication  
- **Framework Adapters**: Pre-built adapters for major agent frameworks
- **Tool Standardization**: Unified tool interfaces across different frameworks
- **Workflow Composition**: Combine agents from different frameworks into single workflows
- **AI Model Orchestration**: Intelligent routing based on model capabilities and pricing
- **Intelligent Routing**: AI-driven optimization strategies (Performance, Cost, Load-balancing)
- **Extended Ecosystem**: Connect to LangChain, LlamaIndex, databases, APIs and more
- **Security First**: Sandboxed execution and permission management

## Supported Frameworks

- Claude-Flow
- CrewAI
- LangGraph
- AutoGen
- ActivePieces
- LangChain
- LlamaIndex
- Haystack
- Databases (PostgreSQL, MySQL, MongoDB, Redis)
- REST APIs
- Custom Agent Frameworks

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

### Intelligent Task Routing
Use AI-driven optimization to route tasks intelligently:

```python
from agentbridge import AgentBridge, OptimizationStrategy

bridge = AgentBridge()

# Execute intelligent workflow with automatic framework selection
result = await bridge.execute_intelligent_workflow(
    task_description="Complex data analysis with visualization",
    required_capabilities=["data_analysis", "visualization"],
    optimization_strategy=OptimizationStrategy.PERFORMANCE_BASED
)
```

### Extended Ecosystem Integration
Connect to various services beyond traditional AI frameworks:

```python
from agentbridge import AgentBridge

bridge = AgentBridge()

# Create database adapter
db_adapter = bridge.get_extended_adapter("database", {
    "db_type": "postgresql",
    "connection_string": "postgresql://user:pass@localhost/db"
})

# Create API adapter
api_adapter = bridge.get_extended_adapter("api", {
    "base_url": "https://api.example.com",
    "headers": {"Authorization": "Bearer token"}
})
```

### Workflow Engine
AgentBridge includes a powerful workflow engine for orchestrating complex multi-framework processes:

```python
from agentbridge import AgentBridge, get_workflow_components

WorkflowBuilder, WorkflowStatus = get_workflow_components()

# Create a bridge instance
bridge = AgentBridge()

# Create a workflow across multiple frameworks
builder = WorkflowBuilder()

workflow_def = (
    builder
    .add_task(
        framework="crewai",
        operation="data_preprocessing",
        inputs={"data": "${input_data}"},
        outputs=["processed_data"]
    )
    .add_task(
        framework="langgraph", 
        operation="analyze_data",
        inputs={"data": "${task_0.processed_data}"},
        outputs=["analysis_results"],
        dependencies=["task_0"]  # Depends on first task
    )
    .add_task(
        framework="autogen",
        operation="generate_report",
        inputs={"analysis": "${task_1.analysis_results}"},
        dependencies=["task_1"]  # Depends on second task
    )
    .build("cross_framework_wf", "Cross-Framework Analysis", "Complete analysis workflow")
)

# Register and execute the workflow
engine = bridge.get_workflow_engine()
engine.register_workflow(workflow_def)

# Execute with input data
execution_id = await engine.execute_workflow(
    "cross_framework_wf",
    input_variables={"input_data": "path/to/data.csv"}
)
```

### AI Model Management
AgentBridge includes intelligent model management for optimal AI resource utilization:

```python
from agentbridge import AgentBridge, get_model_components

ModelManager, ModelSpec, ModelCapability, ModelProvider = get_model_components()

# Create a bridge instance
bridge = AgentBridge()
model_manager = bridge.model_manager

# Register a model
gpt_model = ModelSpec(
    id="gpt-4-turbo",
    name="GPT-4 Turbo",
    provider=ModelProvider.OPENAI,
    capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.TOOLS],
    max_tokens=128000,
    context_window=128000,
    pricing={"input": 0.01, "output": 0.03},  # per 1k tokens
    endpoint="https://api.openai.com/v1/chat/completions"
)

model_manager.register_model(gpt_model)

# Find models by capability
text_models = model_manager.router.find_models_by_capability(ModelCapability.TEXT_GENERATION)

# Route tasks to best-suited models
best_model = model_manager.router.find_best_model([
    ModelCapability.TEXT_GENERATION, 
    ModelCapability.TOOLS
])

# Automatically route tasks based on requirements
result = await model_manager.route_task_to_model(
    "Analyze this document and summarize key points",
    [ModelCapability.TEXT_GENERATION, ModelCapability.SUMMARIZATION]
)
```

## Architecture

AgentBridge operates as a middleware layer that translates between different agent frameworks:

```
[Framework A] <---> [AgentBridge] <---> [Framework B]
     |                   |                   |
   Protocol A        Translation       Protocol B
                     + Model Mgmt
                     + Workflow Eng
                     + Intelligence
                     + Security
                     + Monitoring
```

## API Endpoints

When running the server, the following endpoints are available:

- `GET /` - Root endpoint with API information
- `GET /status` - Bridge status and metrics
- `POST /connect` - Connect to a framework
- `POST /send_message` - Send message between frameworks
- `POST /broadcast` - Broadcast message to multiple frameworks
- `POST /execute_intelligent_workflow` - Execute task with intelligent routing
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

# Broadcast to multiple frameworks
agentbridge broadcast --source crewai --target-frameworks langgraph autogen --content '{"task": "analyze"}'

# Validate configuration
agentbridge validate-config --config my_config.yaml
```

## Project Status

AgentBridge is a complete, production-ready solution for AI agent interoperability. The project includes:

- ✅ Universal protocol for cross-framework communication
- ✅ Comprehensive workflow engine with templates
- ✅ Advanced AI model management system
- ✅ AI-driven intelligent routing and optimization
- ✅ Extended ecosystem adapters (LangChain, LlamaIndex, DBs, APIs)
- ✅ Enterprise-grade security features
- ✅ Complete configuration and logging systems
- ✅ Docker containerization and deployment tools
- ✅ Full test coverage and documentation
- ✅ Clean, organized codebase ready for contribution

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.