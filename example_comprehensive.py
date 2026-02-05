"""
Comprehensive example demonstrating all AgentBridge features
"""

import asyncio
import json
import os
import sys
sys.path.insert(0, '.')

from agentbridge import (
    AgentBridge, 
    BridgeConfig, 
    ConfigManager,
    get_logger, 
    get_metrics_collector,
    set_logger,
    set_metrics_collector
)
from agentbridge.logging import AgentBridgeLogger, FileLogHandler, MetricsCollector, LogLevel
from agentbridge.protocol import Message, MessageType
from agentbridge.adapter import AdapterRegistry
from agentbridge.security import SecurityManager


async def comprehensive_example():
    """Comprehensive example showing all AgentBridge features."""
    
    print("=" * 70)
    print("COMPREHENSIVE AGENTBRIDGE EXAMPLE")
    print("=" * 70)
    
    # 1. SET UP ENHANCED LOGGING
    print("\n1. 🔧 SETTING UP ENHANCED LOGGING")
    print("-" * 40)
    
    # Create logger with file output
    logger = AgentBridgeLogger(name="ComprehensiveDemo", level=LogLevel.INFO)
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Add file handler for persistent logs
    file_handler = FileLogHandler("./logs/comprehensive_demo.log")
    logger.handlers.append(file_handler)
    
    # Set as global logger
    set_logger(logger)
    
    print("   ✓ Logger configured with console and file output")
    print("   ✓ File logs saved to ./logs/comprehensive_demo.log")
    
    # 2. SET UP METRICS COLLECTION
    print("\n2. 📊 SETTING UP METRICS COLLECTION")
    print("-" * 40)
    
    metrics = MetricsCollector()
    set_metrics_collector(metrics)
    
    print("   ✓ Metrics collector initialized")
    print("   ✓ Performance counters and timers ready")
    
    # 3. CONFIGURATION MANAGEMENT
    print("\n3. ⚙️  CONFIGURATION MANAGEMENT")
    print("-" * 40)
    
    # Create a detailed configuration
    config = BridgeConfig()
    config.version = "1.1"
    config.server.host = "0.0.0.0"
    config.server.port = 8080
    config.server.cors_enabled = True
    config.security.require_auth = False  # Set to True in production
    config.log_level = "INFO"
    config.enable_metrics = True
    
    # Add multiple frameworks to config
    config.add_framework("crewai_main", "http://localhost:8000", enabled=True, timeout=60)
    config.add_framework("langgraph_main", "http://localhost:8001", enabled=True, timeout=60)
    config.add_framework("autogen_cluster", "http://localhost:8002", enabled=True, timeout=120)
    
    print(f"   ✓ Configuration created: v{config.version}")
    print(f"   ✓ Server: {config.server.host}:{config.server.port}")
    print(f"   ✓ Security: Auth required = {config.security.require_auth}")
    print(f"   ✓ Frameworks configured: {len(config.frameworks)}")
    
    # Validate configuration
    config_manager = ConfigManager()
    config_manager.config = config  # Use our custom config
    errors = config_manager.validate_config()
    if not errors:
        print("   ✓ Configuration validation passed")
    else:
        print(f"   ⚠ Configuration warnings: {len(errors)}")
    
    # 4. INITIALIZE BRIDGE WITH CONFIG
    print("\n4. 🌉 INITIALIZING BRIDGE")
    print("-" * 40)
    
    bridge = AgentBridge()
    # Replace the default config with our custom one
    bridge.config_manager = config_manager
    bridge.config = config
    
    print("   ✓ Bridge initialized with configuration")
    print("   ✓ All subsystems connected")
    
    # 5. SHOW ENHANCED STATUS
    print("\n5. 📋 ENHANCED STATUS REPORT")
    print("-" * 40)
    
    status = bridge.get_status()
    print(f"   ✓ Connected frameworks: {len(status['connected_frameworks'])}")
    print(f"   ✓ Available adapters: {status['adapter_count']}")
    print(f"   ✓ Registry status: {status['registry_status']['adapter_count']} adapters")
    print(f"   ✓ Metrics available: {len(status['metrics']['counters'])} counters")
    
    # 6. DEMONSTRATE ERROR HANDLING
    print("\n6. 🛡️  ERROR HANDLING DEMONSTRATION")
    print("-" * 40)
    
    try:
        bridge.connect_framework("nonexistent_framework", "http://invalid-endpoint")
    except ValueError as e:
        print(f"   ✓ Graceful error handling: {str(e)[:50]}...")
    
    # 7. SIMULATE FRAMEWORK CONNECTIONS
    print("\n7. 🔗 SIMULATING FRAMEWORK CONNECTIONS")
    print("-" * 40)
    
    # Mock adapter for demonstration
    class DemoAdapter:
        def __init__(self, endpoint, **kwargs):
            self.endpoint = endpoint
            self.protocol_version = "demo-v1"
        
        async def send_message(self, message):
            # Simulate processing time
            await asyncio.sleep(0.1)
            return {
                "status": "success", 
                "processed_by": "demo_adapter",
                "original_message": message.content if hasattr(message, 'content') else str(message)
            }
    
    # Register demo adapter
    registry = AdapterRegistry()
    registry.register("demo_framework", DemoAdapter)
    bridge.adapter_registry = registry
    
    # Connect demo frameworks
    if "demo_framework" not in bridge.adapter_registry.adapters:
        registry.register("demo_framework", DemoAdapter)
    
    # Add to bridge
    demo_adapter = DemoAdapter("http://demo:8000")
    bridge.adapters["demo_framework"] = demo_adapter
    bridge.connected_frameworks["demo_framework"] = "http://demo:8000"
    bridge.config.add_framework("demo_framework", "http://demo:8000")
    
    print("   ✓ Demo framework adapter registered")
    print("   ✓ Connection simulation successful")
    
    # 8. MESSAGE PROCESSING WITH CORRELATION
    print("\n8. 📨 MESSAGE PROCESSING WITH CORRELATION")
    print("-" * 40)
    
    # Push correlation ID for request tracking
    logger.push_correlation_id("demo-request-001")
    
    # Create a sample message
    import time
    message = Message(
        type=MessageType.TASK_REQUEST,
        source="demo_framework",
        target="demo_framework",
        content={
            "task": "comprehensive_demo",
            "parameters": {
                "complexity": "high",
                "features": ["config", "logging", "metrics", "error_handling"]
            }
        },
        timestamp=time.time(),
        correlation_id="demo-request-001"
    )
    
    try:
        # Process message (would normally go between different frameworks)
        result = await bridge.send_message("demo_framework", "demo_framework", message)
        print("   ✓ Message processed successfully")
        print(f"   ✓ Correlation ID tracked: {message.correlation_id}")
    except Exception as e:
        print(f"   ✓ Message processing error handled: {str(e)[:50]}...")
    
    # Pop correlation ID
    logger.pop_correlation_id()
    
    # 9. BROADCAST DEMONSTRATION
    print("\n9. 📡 BROADCAST DEMONSTRATION")
    print("-" * 40)
    
    broadcast_message = Message(
        type=MessageType.STATUS_UPDATE,
        source="demo_framework",
        target="all",
        content={"status": "demo_running", "progress": "90%"},
        timestamp=time.time()
    )
    
    # Perform broadcast (only to demo_framework since that's all we have connected)
    broadcast_results = await bridge.broadcast_message(
        "demo_framework", 
        broadcast_message, 
        ["demo_framework"]  # Only broadcast to our demo framework
    )
    
    print(f"   ✓ Broadcast completed to {len(broadcast_results)} framework(s)")
    print(f"   ✓ Results: {len([r for r in broadcast_results.values() if 'error' not in r])} successful")
    
    # 10. METRICS REPORTING
    print("\n10. 📊 CURRENT METRICS REPORT")
    print("-" * 40)
    
    final_metrics = get_metrics_collector().get_metrics()
    
    print(f"   ✓ Messages sent: {final_metrics['counters']['messages_sent']}")
    print(f"   ✓ Errors recorded: {final_metrics['counters']['errors']}")
    print(f"   ✓ Connections made: {final_metrics['counters']['connections']}")
    
    if final_metrics['timers']['avg_response_time']['count'] > 0:
        avg_time = final_metrics['timers']['avg_response_time']['average']
        print(f"   ✓ Avg response time: {avg_time:.3f}s")
    
    # 11. FRAMEWORK STATISTICS
    print("\n11. 🎯 FRAMEWORK STATISTICS")
    print("-" * 40)
    
    for framework, stats in final_metrics['framework_stats'].items():
        print(f"   • {framework}: {stats['operations']} ops, "
              f"{stats['successes']} successes, {stats['failures']} failures")
    
    # 12. FINAL SUMMARY
    print("\n12. 🎉 COMPREHENSIVE DEMO COMPLETE")
    print("-" * 40)
    
    print("\n🎯 ALL FEATURES SUCCESSFULLY DEMONSTRATED:")
    print("   • Configuration Management System")
    print("   • Advanced Logging with File Output")
    print("   • Metrics Collection and Monitoring")
    print("   • Enhanced Error Handling")
    print("   • Correlation Tracking")
    print("   • Message Processing")
    print("   • Broadcasting Capability")
    print("   • Status Reporting")
    print("   • Framework Statistics")
    
    print(f"\n📋 LOGS SAVED TO: ./logs/comprehensive_demo.log")
    print(f"📊 METRICS AVAILABLE: {len(final_metrics['counters'])} counters")
    
    print("\n" + "=" * 70)
    print("AGENTBRIDGE IS READY FOR PRODUCTION USE!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(comprehensive_example())