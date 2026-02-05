"""
Advanced example usage of AgentBridge with new features
"""

import asyncio
import sys
sys.path.insert(0, '.')

from agentbridge import (
    AgentBridge, 
    BridgeConfig, 
    get_logger, 
    get_metrics_collector,
    set_logger,
    set_metrics_collector
)
from agentbridge.logging import AgentBridgeLogger, FileLogHandler, MetricsCollector, LogLevel
from agentbridge.protocol import Message, MessageType


async def advanced_example():
    """Advanced example showing new features of AgentBridge."""
    
    print("=== Advanced AgentBridge Example ===\\n")
    
    # 1. Create a custom logger with file output
    print("1. Setting up custom logger with file output...")
    logger = AgentBridgeLogger(name="AdvancedExample", level=LogLevel.INFO)
    
    # Add file handler to save logs
    file_handler = FileLogHandler("./logs/agentbridge_demo.log")
    logger.handlers.append(file_handler)
    
    # Set as global logger
    set_logger(logger)
    
    print("   ✓ Logger configured with file output")
    
    # 2. Set up metrics collector
    print("\\n2. Setting up metrics collector...")
    metrics = MetricsCollector()
    set_metrics_collector(metrics)
    
    print("   ✓ Metrics collector configured")
    
    # 3. Initialize the bridge with custom configuration
    print("\\n3. Initializing bridge with configuration...")
    bridge = AgentBridge()
    
    # Add some frameworks to config
    bridge.config.add_framework("crewai_demo", "http://localhost:8000", enabled=True)
    bridge.config.add_framework("langgraph_demo", "http://localhost:8001", enabled=True)
    
    print(f"   ✓ Bridge initialized with config version: {bridge.config.version}")
    print(f"   ✓ Server configured for {bridge.config.server.host}:{bridge.config.server.port}")
    print(f"   ✓ Security: Auth required={bridge.config.security.require_auth}")
    
    # 4. Demonstrate enhanced error handling
    print("\\n4. Demonstrating enhanced error handling...")
    try:
        # This will fail gracefully with logging
        bridge.connect_framework("nonexistent_framework", "http://invalid")
    except ValueError as e:
        print(f"   ✓ Error handled gracefully: {str(e)[:60]}...")
    
    # 5. Show metrics collection
    print("\\n5. Showing metrics collection...")
    metrics_collector = get_metrics_collector()
    
    # Simulate some operations to collect metrics
    metrics_collector.increment_counter('messages_sent', 5)
    metrics_collector.increment_counter('errors', 1)
    
    for i in range(3):
        metrics_collector.record_timer('avg_response_time', 0.1 + (i * 0.05))
    
    # Show current metrics
    current_metrics = metrics_collector.get_metrics()
    print(f"   ✓ Current metrics: {current_metrics['counters']['messages_sent']} messages sent, "
          f"{current_metrics['counters']['errors']} errors")
    
    # 6. Show configuration management
    print("\\n6. Showing configuration management...")
    print(f"   ✓ Active frameworks: {[fw.name for fw in bridge.config_manager.get_active_frameworks()]}")
    
    # Validate configuration
    validation_errors = bridge.config_manager.validate_config()
    print(f"   ✓ Config validation: {len(validation_errors)} errors found")
    
    # 7. Show enhanced status
    print("\\n7. Showing enhanced status...")
    status = bridge.get_status()
    print(f"   ✓ Connected frameworks: {len(status['connected_frameworks'])}")
    print(f"   ✓ Adapter count: {status['adapter_count']}")
    print(f"   ✓ Metrics available: {'metrics' in status}")
    
    # 8. Demonstrate correlation tracking
    print("\\n8. Demonstrating correlation tracking...")
    logger.push_correlation_id("demo-correlation-123")
    logger.info("Demo", "Processing demo request", {"step": 1})
    correlation_id = logger.get_current_correlation_id()
    print(f"   ✓ Correlation ID in context: {correlation_id}")
    logger.pop_correlation_id()
    
    print("\\n=== Advanced Example Completed ===")
    print("\\nKey improvements demonstrated:")
    print("- Enhanced logging with file output")
    print("- Metrics collection and reporting")
    print("- Improved error handling with detailed logging")
    print("- Configuration management and validation")
    print("- Correlation tracking for request tracing")
    print("- Detailed status reporting with metrics")


if __name__ == "__main__":
    asyncio.run(advanced_example())
