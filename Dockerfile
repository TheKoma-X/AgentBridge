FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and install dependencies
COPY pyproject.toml ./
COPY README.md ./

# Create a requirements.txt from pyproject.toml for easier installation
RUN pip install --upgrade pip && \
    pip install build && \
    python -m build && \
    pip install dist/*.whl

# Copy the rest of the application
COPY agentbridge/ ./agentbridge/
COPY example*.py ./
COPY tests/ ./tests/

# Create logs directory
RUN mkdir -p logs

# Expose the default port
EXPOSE 8080

# Set up entrypoint
CMD ["python3", "-c", "from agentbridge import AgentBridge; import asyncio; bridge = AgentBridge(); asyncio.run(bridge.start_server())"]