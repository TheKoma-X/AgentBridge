# Community Integrations

AgentBridge is designed to integrate seamlessly with the broader AI ecosystem. Here are examples of how to integrate with popular tools and platforms.

## 1. LangChain Integration

```python
from langchain.agents import AgentType, initialize_agent
from agentbridge import AgentBridge

class AgentBridgeTool:
    """LangChain tool to interact with AgentBridge"""
    
    def __init__(self, bridge: AgentBridge):
        self.bridge = bridge
    
    async def run(self, command: str, target_framework: str, **kwargs):
        from agentbridge.protocol import Message, MessageType
        
        message = Message(
            type=MessageType.TASK_REQUEST,
            source="langchain",
            target=target_framework,
            content={"command": command, **kwargs},
        )
        
        response = await self.bridge.send_message("langchain", target_framework, message)
        return str(response)

# Usage example
bridge = AgentBridge()
tool = AgentBridgeTool(bridge)

# Initialize LangChain agent with AgentBridge tool
agent = initialize_agent(
    [tool],
    llm,  # Your LLM instance
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Now the LangChain agent can orchestrate tasks across different AI frameworks
agent.run("Analyze the sales data using the analytics framework and generate a report with the reporting framework")
```

## 2. LlamaIndex Integration

```python
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.core.tools import FunctionTool
from agentbridge import AgentBridge

def create_agentbridge_tool(bridge: AgentBridge):
    """Create a LlamaIndex tool for AgentBridge integration"""
    
    async def route_query(query: str, target_framework: str = "default"):
        from agentbridge.protocol import Message, MessageType
        
        message = Message(
            type=MessageType.QUERY_REQUEST,
            source="llamaindex",
            target=target_framework,
            content={"query": query},
        )
        
        response = await bridge.send_message("llamaindex", target_framework, message)
        return str(response)
    
    tool = FunctionTool.from_defaults(
        fn=route_query,
        name="agentbridge_router",
        description="Route queries to specialized AI agent frameworks via AgentBridge"
    )
    
    return tool

# Usage example
bridge = AgentBridge()
agentbridge_tool = create_agentbridge_tool(bridge)

# Create an index with the AgentBridge tool
index = VectorStoreIndex.from_documents(documents=[])
query_engine = index.as_query_engine(tools=[agentbridge_tool])

# Query will be routed to appropriate AI framework
response = query_engine.query("Analyze this document using the specialized analysis framework")
```

## 3. AutoGen Integration

```python
import autogen
from agentbridge import AgentBridge

class AgentBridgeGroupChatManager(autogen.GroupChatManager):
    """Custom GroupChatManager that can communicate with external AgentBridge frameworks"""
    
    def __init__(self, oai Assistant, groupchat, agentbridge: AgentBridge, **kwargs):
        super().__init__(assistant, groupchat, **kwargs)
        self.agentbridge = agentbridge
    
    async def forward_to_external_framework(self, message: str, framework: str):
        """Forward messages to external frameworks via AgentBridge"""
        from agentbridge.protocol import Message as ABMessage, MessageType
        
        ab_message = ABMessage(
            type=MessageType.TASK_REQUEST,
            source="autogen",
            target=framework,
            content={"message": message},
        )
        
        response = await self.agentbridge.send_message("autogen", framework, ab_message)
        return response

# Usage example
bridge = AgentBridge()

# Create AutoGen agents
llm_config = {"config_list": [{"model": "gpt-4", "api_key": "YOUR_API_KEY"}]}

user_proxy = autogen.UserProxyAgent(
    name="User",
    code_execution_config={"use_docker": False},
)

assistant = autogen.AssistantAgent(
    name="Assistant",
    llm_config=llm_config,
)

# Create group chat with AgentBridge integration
groupchat = autogen.GroupChat(
    agents=[user_proxy, assistant],
    messages=[],
    max_round=12
)

manager = AgentBridgeGroupChatManager(
    assistant=assistant,
    groupchat=groupchat,
    agentbridge=bridge,
    llm_config=llm_config
)

# Now the AutoGen group chat can coordinate with external AI frameworks
user_proxy.initiate_chat(
    manager,
    message="Please coordinate with the external analytics framework to analyze our sales data, then use the reporting framework to generate a summary."
)
```

## 4. Streamlit Integration

```python
import streamlit as st
from agentbridge import AgentBridge
import asyncio

# Initialize AgentBridge
@st.cache_resource
def get_bridge():
    return AgentBridge()

bridge = get_bridge()

st.title("AgentBridge Dashboard")
st.write("Coordinate AI agents across multiple frameworks")

# Select target framework
frameworks = st.multiselect(
    "Select target frameworks:",
    ["crewai", "langgraph", "autogen", "claude_flow"]
)

# Enter task
task = st.text_area("Enter your task:")

if st.button("Execute Task"):
    if frameworks and task:
        with st.spinner("Executing task across frameworks..."):
            from agentbridge.protocol import Message, MessageType
            
            # Execute on selected frameworks
            responses = []
            for fw in frameworks:
                message = Message(
                    type=MessageType.TASK_REQUEST,
                    source="streamlit_ui",
                    target=fw,
                    content={"task": task},
                )
                
                # Since we're in a sync context, we need to run the async call
                response = asyncio.run(bridge.send_message("streamlit_ui", fw, message))
                responses.append((fw, str(response)))
            
            # Display results
            for fw, response in responses:
                st.subheader(f"Response from {fw}:")
                st.write(response)
    else:
        st.warning("Please select at least one framework and enter a task.")
```

## 5. API Gateway Integration

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agentbridge import AgentBridge

app = FastAPI(title="AgentBridge API Gateway")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AgentBridge
bridge = AgentBridge()

class TaskRequest(BaseModel):
    target_framework: str
    task: str
    parameters: dict = {}

@app.post("/execute-task")
async def execute_task(request: TaskRequest):
    """Execute a task on a specific AI framework via AgentBridge"""
    try:
        from agentbridge.protocol import Message, MessageType
        
        message = Message(
            type=MessageType.TASK_REQUEST,
            source="api_gateway",
            target=request.target_framework,
            content={"task": request.task, "parameters": request.parameters},
        )
        
        response = await bridge.send_message(
            "api_gateway", 
            request.target_framework, 
            message
        )
        
        return {"status": "success", "response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/frameworks/status")
async def get_frameworks_status():
    """Get status of all connected frameworks"""
    return bridge.get_status()

# Run with: uvicorn api_gateway:app --reload
```

## 6. Monitoring Integration (Prometheus/Grafana)

AgentBridge includes built-in metrics collection compatible with Prometheus:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'agentbridge'
    static_configs:
      - targets: ['localhost:8080']  # AgentBridge server
    metrics_path: '/metrics'  # If exposing metrics endpoint
    scrape_interval: 15s
```

```python
# Add metrics endpoint to your FastAPI app
from fastapi.responses import PlainTextResponse
from agentbridge.logging import get_metrics_collector

@app.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """Prometheus metrics endpoint"""
    collector = get_metrics_collector()
    return collector.export_prometheus()  # Assuming you implement this method
```

## 7. GitHub Actions Integration

```yaml
# .github/workflows/agentbridge-test.yml
name: Test AgentBridge Integration

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        pip install .
        pip install pytest
        
    - name: Run tests
      run: |
        python -m pytest tests/
        
    - name: Run integration tests
      run: |
        python example_comprehensive.py
        python example_workflow_demo.py
```

## 8. Container Orchestration (Kubernetes)

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentbridge
spec:
  replicas: 1
  selector:
    matchLabels:
      app: agentbridge
  template:
    metadata:
      labels:
        app: agentbridge
    spec:
      containers:
      - name: agentbridge
        image: your-registry/agentbridge:latest
        ports:
        - containerPort: 8080
        env:
        - name: AGENTBRIDGE_CONFIG_PATH
          value: "/etc/agentbridge/config.yaml"
        volumeMounts:
        - name: config-volume
          mountPath: /etc/agentbridge
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: config-volume
        configMap:
          name: agentbridge-config
      - name: logs-volume
        persistentVolumeClaim:
          claimName: agentbridge-logs
---
apiVersion: v1
kind: Service
metadata:
  name: agentbridge-service
spec:
  selector:
    app: agentbridge
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

These integration examples demonstrate how AgentBridge can be incorporated into various AI and development ecosystems, making it accessible to users of different tools and platforms. The unified protocol allows diverse AI agent frameworks to interoperate seamlessly while maintaining their individual strengths.