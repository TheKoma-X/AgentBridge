"""
Workflow engine demonstration for AgentBridge
"""

import asyncio
import sys
sys.path.insert(0, '.')

from agentbridge import AgentBridge, get_workflow_components
from agentbridge.logging import AgentBridgeLogger, LogLevel
from agentbridge.protocol import MessageType


# Get workflow components
WorkflowEngine, WorkflowBuilder, WorkflowDefinition, TaskDefinition, WorkflowStatus, TaskStatus = get_workflow_components()


async def workflow_demo():
    """Demonstrate AgentBridge workflow engine capabilities."""
    
    print("=" * 70)
    print("AGENTBRIDGE WORKFLOW ENGINE DEMONSTRATION")
    print("=" * 70)
    
    # 1. SET UP BRIDGE AND LOGGER
    print("\n1. 🌉 SETTING UP BRIDGE WITH WORKFLOW ENGINE")
    print("-" * 40)
    
    bridge = AgentBridge()
    
    print("   ✓ AgentBridge initialized")
    print("   ✓ Workflow engine available")
    
    # 2. CREATE A SAMPLE WORKFLOW
    print("\n2. 🏗️  CREATING SAMPLE WORKFLOW")
    print("-" * 40)
    
    # Create a workflow for data analysis: 
    # 1. Data preprocessing (crewai)
    # 2. Analysis (langgraph) - depends on preprocessing
    # 3. Report generation (autogen) - depends on analysis
    builder = WorkflowBuilder()
    
    workflow_def = (
        builder
        .add_task(
            framework="crewai_preprocessor",
            operation="preprocess_data",
            inputs={"raw_data": "${input_data}", "format": "csv"},
            outputs=["cleaned_data", "metadata"],
            timeout=600
        )
        .add_task(
            framework="langgraph_analyzer",
            operation="analyze_data", 
            inputs={"data": "${task_0.cleaned_data}", "analysis_type": "statistical"},
            outputs=["analysis_results", "insights"],
            dependencies=["task_0"],  # Depends on task_0
            timeout=1200
        )
        .add_task(
            framework="autogen_reporter",
            operation="generate_report",
            inputs={
                "analysis": "${task_1.analysis_results}", 
                "insights": "${task_1.insights}",
                "format": "executive_summary"
            },
            outputs=["report"],
            dependencies=["task_1"],  # Depends on task_1
            timeout=900
        )
        .build(
            workflow_id="data_analysis_wf",
            name="Data Analysis Workflow",
            description="Complete pipeline: preprocess -> analyze -> report"
        )
    )
    
    print(f"   ✓ Workflow created: {workflow_def.name}")
    print(f"   ✓ Workflow ID: {workflow_def.id}")
    print(f"   ✓ Number of tasks: {len(workflow_def.tasks)}")
    print(f"   ✓ Start tasks: {workflow_def.start_tasks}")
    print(f"   ✓ End tasks: {workflow_def.end_tasks}")
    
    # 3. REGISTER THE WORKFLOW
    print("\n3. 📝 REGISTERING WORKFLOW")
    print("-" * 40)
    
    engine = bridge.get_workflow_engine()
    engine.register_workflow(workflow_def)
    
    print("   ✓ Workflow registered with engine")
    print(f"   ✓ Total registered workflows: {len(engine.workflow_definitions)}")
    
    # 4. EXAMINE TASK DEFINITIONS
    print("\n4. 🔍 EXAMINING TASK DEFINITIONS")
    print("-" * 40)
    
    for i, task in enumerate(workflow_def.tasks):
        print(f"   Task {i} ({task.id}):")
        print(f"     • Framework: {task.framework}")
        print(f"     • Operation: {task.operation}")
        print(f"     • Inputs: {list(task.inputs.keys())}")
        print(f"     • Outputs: {task.outputs}")
        print(f"     • Dependencies: {task.dependencies}")
        print(f"     • Timeout: {task.timeout}s")
    
    # 5. ATTEMPT WORKFLOW EXECUTION (SIMULATED)
    print("\n5. ▶️  ATTEMPTING WORKFLOW EXECUTION")
    print("-" * 40)
    
    print("   NOTE: Actual execution requires real agent frameworks to be connected.")
    print("   For demo purposes, we'll show how execution would be initiated:")
    print("")
    print("   # Execute workflow with input data")
    print('   execution_id = await engine.execute_workflow(')
    print('       "data_analysis_wf", ')
    print('       input_variables={"input_data": "path/to/data.csv"}')
    print('   )')
    print("")
    print("   # Check execution status")
    print("   status = engine.get_workflow_status(execution_id)")
    print("")
    print("   # Get results when complete")
    print("   results = engine.get_workflow_result(execution_id)")
    
    # 6. DYNAMIC WORKFLOW CREATION
    print("\n6. ⚡ DYNAMIC WORKFLOW CREATION")
    print("-" * 40)
    
    # Create a simpler ad-hoc workflow
    quick_workflow = (
        WorkflowBuilder()
        .add_task(
            framework="quick_framework",
            operation="simple_operation",
            inputs={"param": "value"},
            outputs=["result"]
        )
        .build("quick_wf", "Quick Workflow", "A dynamically created workflow")
    )
    
    engine.register_workflow(quick_workflow)
    print("   ✓ Dynamic workflow created and registered")
    print(f"   ✓ Total workflows now: {len(engine.workflow_definitions)}")
    
    # 7. WORKFLOW ENGINE CAPABILITIES
    print("\n7. 🌟 WORKFLOW ENGINE CAPABILITIES")
    print("-" * 40)
    
    capabilities = [
        "Sequential task execution",
        "Parallel task execution for independent tasks",
        "Dependency management between tasks",
        "Input/output variable resolution",
        "Error handling and retry mechanisms",
        "Timeout management",
        "Status tracking and monitoring",
        "Cancellation support",
        "Cross-framework orchestration"
    ]
    
    for i, capability in enumerate(capabilities, 1):
        print(f"   {i}. {capability}")
    
    # 8. VARIABLE RESOLUTION SYSTEM
    print("\n8. 🔁 VARIABLE RESOLUTION SYSTEM")
    print("-" * 40)
    
    print("   The workflow engine supports dynamic variable resolution:")
    print('   • ${variable_name} - References workflow variables')
    print('   • ${task_id.output_name} - References outputs from completed tasks')
    print('   • Enables data flow between tasks across different frameworks')
    print('   • Supports complex data transformation pipelines')
    
    # 9. INTEGRATION WITH EXISTING FEATURES
    print("\n9. 🔗 INTEGRATION WITH EXISTING FEATURES")
    print("-" * 40)
    
    integrations = [
        "Uses bridge's messaging system for cross-framework communication",
        "Integrates with security system for protected workflow execution",
        "Leverages logging system for detailed workflow tracing",
        "Utilizes metrics system for performance monitoring",
        "Works with configuration system for workflow settings",
        "Compatible with CLI for workflow management"
    ]
    
    for i, integration in enumerate(integrations, 1):
        print(f"   {i}. {integration}")
    
    # 10. CLI WORKFLOW COMMANDS
    print("\n10. 💻 CLI WORKFLOW COMMANDS")
    print("-" * 40)
    
    print("   Planned CLI commands for workflow management:")
    print("   • agentbridge workflow list - List all registered workflows")
    print("   • agentbridge workflow execute --id <wf_id> --inputs <json> - Execute workflow")
    print("   • agentbridge workflow status --execution-id <exec_id> - Check execution status")
    print("   • agentbridge workflow cancel --execution-id <exec_id> - Cancel execution")
    print("   • agentbridge workflow create --definition <file> - Register new workflow")
    
    print("\n" + "=" * 70)
    print("🎉 WORKFLOW ENGINE DEMONSTRATION COMPLETE!")
    print("🔄 AgentBridge now includes powerful workflow orchestration capabilities")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(workflow_demo())