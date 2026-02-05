# AgentBridge

Universal AI Agent Interoperability Protocol - Connecting the fragmented AI agent ecosystem

## Vision

AgentBridge is the universal protocol that enables seamless communication and collaboration between different AI agent frameworks. Whether you're using CrewAI, LangGraph, AutoGen, Claude-Flow, or any other agent framework, AgentBridge provides the standardized bridge for them to work together.

## Key Innovations

- **Universal Protocol**: Standardized message format for cross-framework communication
- **Framework Adapters**: Connect any AI agent framework through pluggable adapters
- **Workflow Engine**: Cross-framework orchestration and task management
- **AI Model Management**: Intelligent model routing and capability-based selection
- **Pre-built Templates**: Ready-to-use templates for common AI workflows
- **Enterprise Security**: Multi-layer authentication, authorization, and encryption
- **Advanced Monitoring**: Comprehensive logging, metrics, and observability
- **Container-Native**: Docker and Kubernetes ready for cloud deployments
- **Community Ecosystem**: Integrations with LangChain, LlamaIndex, AutoGen and more
- **Enhanced Configuration**: Comprehensive configuration management system
- **Advanced Logging**: Detailed logging with file output and correlation tracking
- **Metrics Collection**: Built-in metrics and monitoring capabilities
- **Security Features**: Authentication, authorization, encryption, and framework trust validation
- **Improved Error Handling**: Detailed error reporting and graceful degradation
- **Production Ready**: Enterprise-grade reliability and operational excellence

## Key Features

- **Universal Compatibility**: Bridge any AI agent framework with standardized protocols
- **MCP Enhancement**: Extended Model Context Protocol for cross-framework communication  
- **Framework Adapters**: Pre-built adapters for major agent frameworks
- **Tool Standardization**: Unified tool interfaces across different frameworks
- **Workflow Composition**: Combine agents from different frameworks into single workflows
- **AI Model Orchestration**: Intelligent routing based on model capabilities and pricing
- **Security First**: Sandboxed execution and permission management

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

### Broadcasting Messages
Send messages to multiple frameworks simultaneously:

```python
from agentbridge import AgentBridge

bridge = AgentBridge()
await bridge.broadcast_message(
    source="crewai",
    message=my_message,
    target_frameworks=["langgraph", "autogen", "claude-flow"]
)
```

### Security Features
AgentBridge includes comprehensive security features:

```python
from agentbridge import AgentBridge, BridgeConfig

# Create secure configuration
config = BridgeConfig()
config.security.require_auth = True
config.security.encryption_enabled = True
config.security.trusted_frameworks_only = True
config.security.allowed_frameworks = ["trusted_framework_1", "trusted_framework_2"]

# Initialize bridge with security
bridge = AgentBridge(config_path="secure_config.yaml")

# Generate secure tokens
read_token = bridge.security_manager.generate_token(["read"], expires_in_hours=24)
admin_token = bridge.security_manager.generate_token(["read", "write", "admin"], expires_in_hours=1)
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

### Pre-Built Workflow Templates
AgentBridge ships with pre-built templates for common use cases:

```python
from workflow_templates.data_analysis_workflow import get_template

# Get a pre-built data analysis workflow
workflow = get_template("data_analysis")

# Or content creation workflow
content_workflow = get_template("content_creation")

# Or decision support workflow
decision_workflow = get_template("decision_support")
```

Available templates include:
- **Data Analysis Pipeline**: End-to-end data processing and analysis
- **Content Creation Pipeline**: Multi-stage content generation and refinement  
- **Decision Support Pipeline**: Structured decision-making with multi-perspective evaluation

### Quick Installation
Install AgentBridge with our simple installation script:

```bash
# Download and run the installation script
curl -o install.sh https://raw.githubusercontent.com/your-repo/AgentBridge/main/install.sh
chmod +x install.sh
./install.sh
```

Or use Docker:
```bash
# Build and run with Docker
docker build -t agentbridge .
docker run -p 8080:8080 agentbridge

# Or with docker-compose for multi-service setup
docker-compose up -d
```

### CLI Enhancements
New CLI commands for enhanced functionality:

```bash
# Validate configuration
agentbridge validate-config --config my_config.yaml

# Generate authentication tokens
agentbridge generate-token --permissions read write --expires-in 24
agentbridge generate-token --permissions admin --expires-in 8

# Check security status
agentbridge security-status

# Broadcast messages to multiple frameworks
agentbridge broadcast --source crewai --target-frameworks langgraph autogen \
  --content '{"task": "analyze"}'

# Check detailed status with metrics
agentbridge status
```

## Architecture

AgentBridge operates as a middleware layer that translates between different agent frameworks:

```
[Framework A] <---> [AgentBridge] <---> [Framework B]
     |                   |                   |
   Protocol A        Translation       Protocol B
                     + Model Mgmt
                     + Workflow Eng
                     + Security
                     + Monitoring
```

The system includes:
- **Core Bridge**: Central hub for message routing
- **Protocol Layer**: Standardized message format and translation
- **Adapters**: Framework-specific connectors
- **Model Management**: Intelligent routing based on capabilities and cost
- **Workflow Engine**: Cross-framework orchestration and task management
- **Configuration System**: Comprehensive config management
- **Logging System**: Advanced logging with correlation tracking
- **Metrics System**: Performance monitoring and collection
- **Security Layer**: Authentication, authorization, and access control

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

# Broadcast to multiple frameworks
agentbridge broadcast --source crewai --target-frameworks langgraph autogen --content '{"task": "analyze"}'

# Validate configuration
agentbridge validate-config --config my_config.yaml
```

## Production Deployment

AgentBridge is designed for production use with enterprise-grade features:

- **Configuration Management**: Comprehensive YAML/JSON configuration with validation
- **Operational Excellence**: Health checks, monitoring, and logging
- **Security**: Authentication, authorization, and secure defaults
- **Scalability**: Asynchronous architecture with efficient resource usage
- **Reliability**: Error recovery, circuit breakers, and graceful degradation

### Configuration Example
```yaml
version: "1.1"
server:
  host: "0.0.0.0"
  port: 8080
  cors_enabled: true
  max_connections: 100
security:
  require_auth: false
  allowed_origins: ["*"]
  rate_limit_enabled: true
  max_requests_per_minute: 100
frameworks:
  - name: "crewai_main"
    endpoint: "http://localhost:8000"
    enabled: true
    timeout: 60
  - name: "langgraph_main"
    endpoint: "http://localhost:8001"
    enabled: true
    timeout: 60
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.
