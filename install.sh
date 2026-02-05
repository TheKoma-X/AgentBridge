#!/bin/bash

# AgentBridge Installation Script
echo "🚀 Installing AgentBridge - Universal AI Agent Interoperability Protocol"

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo "❌ Python version $PYTHON_VERSION is not supported. Please upgrade to Python 3.8 or higher."
    exit 1
fi

echo "✅ Python version $PYTHON_VERSION detected"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "⚠️  pip3 not found, attempting to install..."
    python3 -m ensurepip --upgrade
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip3 is required but could not be installed."
        exit 1
    fi
fi

echo "✅ pip3 is available"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv agentbridge-env
source agentbridge-env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install AgentBridge
echo "📦 Installing AgentBridge..."
pip install .

# Install optional dependencies for full functionality
echo "🔌 Installing optional dependencies..."
pip install "fastapi[all]" uvicorn aiohttp

# Create default configuration
echo "⚙️  Creating default configuration..."
mkdir -p config
cat > config/default_config.yaml << EOF
version: "1.1"
server:
  host: "0.0.0.0"
  port: 8080
  ssl_enabled: false
security:
  require_auth: false
  encryption_enabled: false
  auth_tokens: []
  trusted_frameworks_only: false
  max_request_size: 10485760  # 10MB
frameworks:
  - name: "demo_framework"
    endpoint: "http://localhost:8000"
    adapter: "demo"
    enabled: true
logging:
  level: "INFO"
  file_output: "./logs/agentbridge.log"
  max_file_size: 10485760  # 10MB
  backup_count: 5
metrics:
  enabled: true
  collection_interval: 60
EOF

# Create logs directory
mkdir -p logs

echo "✅ AgentBridge installed successfully!"

echo ""
echo "🎉 Quick Start Commands:"
echo ""
echo "# Activate virtual environment"
echo "source agentbridge-env/bin/activate"
echo ""
echo "# Start the server"
echo "agentbridge serve --config config/default_config.yaml"
echo ""
echo "# Or run directly"
echo "python3 -c \"from agentbridge import AgentBridge; import asyncio; bridge = AgentBridge('config/default_config.yaml'); asyncio.run(bridge.start_server())\""
echo ""
echo "# Run a simple test"
echo "python3 -c \"from agentbridge import AgentBridge; bridge = AgentBridge(); print('AgentBridge initialized successfully!')\""
echo ""

echo "📖 For more information, visit: https://github.com/your-repo/AgentBridge"
echo "💬 Join our community for support and updates"