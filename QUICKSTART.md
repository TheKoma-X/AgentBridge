# AgentBridge Quick Start Guide

Welcome to AgentBridge - the universal AI agent interoperability protocol! This guide will help you get up and running quickly.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation Methods

### Method 1: Using the Installation Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-repo/AgentBridge.git
cd AgentBridge

# Run the installation script
./install.sh
```

### Method 2: Manual Installation

```bash
# Create virtual environment
python3 -m venv agentbridge-env
source agentbridge-env/bin/activate

# Install AgentBridge
pip install .

# Install additional dependencies for full functionality
pip install "fastapi[all]" uvicorn aiohttp
```

## Quick Setup

### 1. Start the AgentBridge Server

```bash
# Activate your environment
source agentbridge-env/bin/activate

# Start the server with default configuration
agentbridge serve
```

Or programmatically:

```python
from agentbridge import AgentBridge
import asyncio

# Create and start bridge
bridge = AgentBridge()
asyncio.run(bridge.start_server(host="0.0.0.0", port=8080))
```

### 2. Connect Your First Framework

```python
from agentbridge import AgentBridge

bridge = AgentBridge()

# Register a sample adapter
class SampleFrameworkAdapter:
    def __init__(self):
        self.framework_name = "sample_framework"
    
    async def handle_message(self, message):
        # Process the message and return a response
        return {"status": "success", "data": f"Processed: {message.content}"}

# Register the adapter
bridge.adapter_registry.register_adapter("sample_framework", SampleFrameworkAdapter())

# Connect to the framework
bridge.connect_framework("sample_framework")
```

### 3. Send Your First Message

```python
from agentbridge import AgentBridge
from agentbridge.protocol import Message, MessageType

bridge = AgentBridge()

# Create a message
message = Message(
    type=MessageType.TASK_REQUEST,
    source="my_app",
    target="sample_framework",
    content={"task": "process_data", "data": "some important data"},
    timestamp=1234567890
)

# Send the message
response = await bridge.send_message("my_app", "sample_framework", message)
print(response)
```

## Common Use Cases

### 1. Cross-Framework Data Processing

```python
from agentbridge import get_workflow_components

WorkflowBuilder = get_workflow_components()[1]  # Get WorkflowBuilder

# Create a workflow that processes data across multiple frameworks
builder = WorkflowBuilder()

workflow_def = (
    builder
    .add_task(
        framework="data_preprocessor",
        operation="clean",
        inputs={"raw_data": "${input_data}"},
        outputs=["cleaned_data"]
    )
    .add_task(
        framework="analyzer", 
        operation="analyze",
        inputs={"data": "${task_0.cleaned_data}"},
        outputs=["results"],
        dependencies=["task_0"]
    )
    .build("data_processing_wf", "Data Processing Workflow", "Clean and analyze data")
)

# Register and execute
bridge = AgentBridge()
engine = bridge.get_workflow_engine()
engine.register_workflow(workflow_def)

# Execute workflow
execution_id = await engine.execute_workflow(
    "data_processing_wf",
    input_variables={"input_data": "path/to/data.csv"}
)
```

### 2. Secure Multi-Agent Communication

```python
from agentbridge import AgentBridge

# Initialize bridge with security
bridge = AgentBridge()
security_manager = bridge.security_manager

# Generate secure token
token = security_manager.generate_token(
    permissions=["read", "write"],
    expires_in_hours=24
)

# Use token for authenticated communication
headers = {"Authorization": f"Bearer {token}"}
```

### 3. Monitoring and Metrics

```python
from agentbridge import AgentBridge

bridge = AgentBridge()

# Get status and metrics
status = bridge.get_status()
print(f"Connected frameworks: {status['connected_frameworks']}")
print(f"Metrics: {status['metrics']}")

# Access specific metrics
from agentbridge.logging import get_metrics_collector
metrics = get_metrics_collector()
print(f"Messages sent: {metrics.get_counter('messages_sent')}")
```

## Command Line Interface

AgentBridge comes with a powerful CLI:

```bash
# Start the server
agentbridge serve --config config/my_config.yaml

# Validate configuration
agentbridge validate-config --config config/my_config.yaml

# Generate authentication tokens
agentbridge generate-token --permissions read write --expires-in 24

# Check security status
agentbridge security-status

# Broadcast messages
agentbridge broadcast --source my_framework --target-frameworks framework1 framework2 \
  --content '{"task": "sync_data"}'

# View status
agentbridge status
```

## Docker Deployment

For containerized deployment:

```bash
# Build and run with Docker
docker build -t agentbridge .
docker run -p 8080:8080 agentbridge

# Or use docker-compose for multi-service setup
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you've activated your virtual environment
2. **Port already in use**: Change the port in your configuration file
3. **Permission denied**: Check file permissions for config and log directories

### Getting Help

- Check the [full documentation](README.md)
- Look at the [examples](example_comprehensive.py)
- Run the [tests](tests/) to verify functionality

## Next Steps

1. Explore the [full feature documentation](FEATURES.md)
2. Review the [security features](SECURITY_FEATURES.md)
3. Learn about [workflow capabilities](WORKFLOW_FEATURES.md)
4. Check out the [contributing guidelines](CONTRIBUTING.md)

Happy bridging! 🌉