#!/usr/bin/env python3
"""
Example demonstrating AgentBridge's intelligent features and extended adapters
"""

import asyncio
import json
from datetime import datetime

from agentbridge import AgentBridge, get_intelligence_components, get_extended_adapter_components
from agentbridge.protocol import Message, MessageType
from agentbridge.intelligence import OptimizationStrategy


async def demonstrate_intelligent_routing():
    """Demonstrate intelligent task routing based on performance predictions"""
    print("🚀 Demonstrating Intelligent Routing")
    print("=" * 50)
    
    # Get intelligence components
    IntelligenceManager, OptimizationStrategy = get_intelligence_components()
    
    # Create bridge instance
    bridge = AgentBridge()
    
    # Simulate having some frameworks connected
    # In a real scenario, we would connect actual frameworks
    print("📋 Available frameworks: ['crewai', 'langgraph', 'autogen']")
    
    # Simulate recording some performance data for learning
    await bridge.intelligence_manager.record_task_outcome(
        "crewai", "data_analysis", 2.5, True, 0.02
    )
    await bridge.intelligence_manager.record_task_outcome(
        "langgraph", "data_analysis", 3.2, True, 0.015
    )
    await bridge.intelligence_manager.record_task_outcome(
        "autogen", "data_analysis", 1.8, True, 0.03
    )
    
    # Now test intelligent routing
    task_description = "complex data analysis with visualization"
    available_frameworks = ["crewai", "langgraph", "autogen"]
    
    print(f"\n🧠 Optimizing task: '{task_description}'")
    
    # Test different optimization strategies
    strategies = [
        OptimizationStrategy.PERFORMANCE_BASED,
        OptimizationStrategy.COST_OPTIMIZED,
        OptimizationStrategy.LOAD_BALANCED
    ]
    
    for strategy in strategies:
        optimal_framework = await bridge.intelligence_manager.optimize_task_execution(
            task_description, available_frameworks
        )
        print(f"   {strategy.value}: {optimal_framework}")
    
    print("\n✅ Intelligent routing demonstration complete")


async def demonstrate_extended_adapters():
    """Demonstrate extended adapters for various services"""
    print("\n🔌 Demonstrating Extended Adapters")
    print("=" * 50)
    
    # Get extended adapter components
    ExtendedAdapterManager, BaseExtendedAdapter = get_extended_adapter_components()
    
    # Create bridge instance
    bridge = AgentBridge()
    
    # Show available extended adapters
    extended_manager = bridge.get_extended_adapter_manager()
    supported_adapters = extended_manager.list_supported_adapters()
    
    print(f"📋 Supported extended adapters: {supported_adapters}")
    
    # Demonstrate creating different types of adapters
    adapter_configs = {
        'langchain': {
            'api_base': 'http://localhost:8000',
            'timeout': 30
        },
        'llamaindex': {
            'api_base': 'http://localhost:8001',
            'timeout': 30
        },
        'database': {
            'db_type': 'postgresql',
            'connection_string': 'postgresql://user:pass@localhost/db'
        },
        'api': {
            'base_url': 'https://api.example.com',
            'headers': {'Authorization': 'Bearer token'}
        }
    }
    
    print("\n🔧 Creating extended adapters:")
    for adapter_type, config in adapter_configs.items():
        try:
            adapter = await extended_manager.create_adapter(adapter_type, config)
            if adapter:
                print(f"   ✓ {adapter_type} adapter created")
            else:
                print(f"   ⚠ {adapter_type} adapter creation failed")
        except Exception as e:
            print(f"   ❌ {adapter_type} adapter error: {e}")
    
    print("\n✅ Extended adapters demonstration complete")


async def demonstrate_intelligent_workflow():
    """Demonstrate intelligent workflow execution"""
    print("\n⚙️  Demonstrating Intelligent Workflow")
    print("=" * 50)
    
    # Create bridge instance
    bridge = AgentBridge()
    
    # Simulate connecting some frameworks
    print("🔌 Simulating framework connections...")
    
    # Record some performance data to enable learning
    await bridge.intelligence_manager.record_task_outcome(
        "crewai", "report_generation", 5.0, True, 0.05
    )
    await bridge.intelligence_manager.record_task_outcome(
        "langgraph", "report_generation", 4.2, True, 0.04
    )
    await bridge.intelligence_manager.record_task_outcome(
        "autogen", "report_generation", 6.1, True, 0.06
    )
    
    # Execute intelligent workflow
    task_description = "Generate quarterly business report with financial analysis"
    capabilities_needed = ["data_analysis", "report_generation", "visualization"]
    
    print(f"\n🧠 Executing intelligent workflow:")
    print(f"   Task: {task_description}")
    print(f"   Capabilities: {capabilities_needed}")
    
    result = await bridge.execute_intelligent_workflow(
        task_description=task_description,
        required_capabilities=capabilities_needed,
        optimization_strategy=OptimizationStrategy.PERFORMANCE_BASED
    )
    
    print(f"\n📋 Execution result:")
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        print(f"   Selected Framework: {result['selected_framework']}")
        print(f"   Strategy: {result['optimization_strategy']}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    print("\n✅ Intelligent workflow demonstration complete")


async def main():
    """Main demonstration function"""
    print("🌟 AgentBridge Intelligent Features Demonstration")
    print("=" * 60)
    print("This demo showcases the advanced intelligence and ecosystem")
    print("features added to AgentBridge.")
    print()
    
    # Run demonstrations
    await demonstrate_intelligent_routing()
    await demonstrate_extended_adapters()
    await demonstrate_intelligent_workflow()
    
    print("\n🎯 All demonstrations completed!")
    print("\n💡 Key Intelligent Features:")
    print("   • AI-driven optimization strategies")
    print("   • Performance prediction and learning")
    print("   • Adaptive resource allocation")
    print("   • Extended ecosystem adapters")
    print("   • Intelligent workflow execution")
    print("   • Predictive analytics for task routing")


if __name__ == "__main__":
    asyncio.run(main())