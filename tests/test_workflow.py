"""
Workflow tests for AgentBridge
"""

import asyncio
import sys
sys.path.insert(0, '.')

from agentbridge import (
    AgentBridge,
    get_workflow_components
)

# Get workflow components without circular import issues
WorkflowEngine, WorkflowBuilder, WorkflowDefinition, TaskDefinition, WorkflowStatus, TaskStatus = get_workflow_components()


def test_workflow_builder():
    """Test the workflow builder functionality."""
    builder = WorkflowBuilder()
    
    # Build a simple workflow
    workflow_def = (
        builder
        .add_task("crewai", "analyze_data", 
                 inputs={"dataset": "sales_data", "method": "statistical"})
        .add_task("langgraph", "generate_report", 
                 inputs={"analysis": "${task_0.result}", "format": "pdf"},
                 dependencies=["task_0"])
        .build("wf1", "Data Analysis Workflow", "Complete data analysis and reporting")
    )
    
    assert workflow_def.id == "wf1"
    assert workflow_def.name == "Data Analysis Workflow"
    assert len(workflow_def.tasks) == 2
    assert workflow_def.tasks[0].framework == "crewai"
    assert workflow_def.tasks[1].dependencies == ["task_0"]
    
    print("✓ test_workflow_builder passed")


def test_workflow_engine_initialization():
    """Test that workflow engine is properly initialized with bridge."""
    bridge = AgentBridge()
    
    # Use the getter method to access the workflow engine
    engine = bridge.get_workflow_engine()
    
    assert engine is not None
    assert engine.bridge == bridge
    
    print("✓ test_workflow_engine_initialization passed")


async def test_simple_workflow_registration():
    """Test registering a simple workflow."""
    bridge = AgentBridge()
    
    builder = WorkflowBuilder()
    workflow_def = (
        builder
        .add_task("test_framework", "simple_task", 
                 inputs={"param": "value"})
        .build("simple_wf", "Simple Workflow", "A simple test workflow")
    )
    
    engine = bridge.get_workflow_engine()
    engine.register_workflow(workflow_def)
    
    assert "simple_wf" in engine.workflow_definitions
    assert engine.workflow_definitions["simple_wf"].name == "Simple Workflow"
    
    print("✓ test_simple_workflow_registration passed")


if __name__ == "__main__":
    print("Running workflow tests...")
    
    test_workflow_builder()
    test_workflow_engine_initialization()
    asyncio.run(test_simple_workflow_registration())
    
    print("\n✓ All workflow tests passed successfully!")