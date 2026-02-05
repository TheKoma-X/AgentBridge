"""
Example showing how to use pre-built workflow templates
"""

import asyncio
import sys
sys.path.insert(0, '.')

from agentbridge import AgentBridge
from workflow_templates.data_analysis_workflow import get_template, WORKFLOW_TEMPLATES


async def demonstrate_template_usage():
    """Demonstrate using pre-built workflow templates."""
    
    print("=" * 80)
    print("AGENTBRIDGE TEMPLATE USAGE DEMONSTRATION")
    print("=" * 80)
    
    # 1. SET UP BRIDGE
    print("\n1. 🌉 SETTING UP BRIDGE")
    print("-" * 40)
    
    bridge = AgentBridge()
    engine = bridge.get_workflow_engine()
    
    print("   ✓ AgentBridge initialized")
    print("   ✓ Workflow engine ready")
    
    # 2. SHOW AVAILABLE TEMPLATES
    print("\n2. 📋 AVAILABLE WORKFLOW TEMPLATES")
    print("-" * 40)
    
    for i, (name, func) in enumerate(WORKFLOW_TEMPLATES.items(), 1):
        print(f"   {i}. {name.replace('_', ' ').title()}")
    
    print(f"\n   Total templates: {len(WORKFLOW_TEMPLATES)}")
    
    # 3. LOAD AND EXAMINE A TEMPLATE
    print("\n3. 🔍 EXAMINING DATA ANALYSIS TEMPLATE")
    print("-" * 40)
    
    data_analysis_wf = get_template("data_analysis")
    print(f"   ✓ Template loaded: {data_analysis_wf.name}")
    print(f"   ✓ Workflow ID: {data_analysis_wf.id}")
    print(f"   ✓ Description: {data_analysis_wf.description}")
    print(f"   ✓ Number of tasks: {len(data_analysis_wf.tasks)}")
    print(f"   ✓ Start tasks: {data_analysis_wf.start_tasks}")
    print(f"   ✓ End tasks: {data_analysis_wf.end_tasks}")
    
    print("\n   Task breakdown:")
    for j, task in enumerate(data_analysis_wf.tasks):
        print(f"     {j+1}. {task.operation} on {task.framework}")
        print(f"         Dependencies: {task.dependencies}")
        print(f"         Outputs: {task.outputs}")
        print(f"         Timeout: {task.timeout}s")
    
    # 4. REGISTER THE TEMPLATE
    print("\n4. 📝 REGISTERING TEMPLATE")
    print("-" * 40)
    
    engine.register_workflow(data_analysis_wf)
    print("   ✓ Data analysis workflow registered")
    print(f"   ✓ Total registered workflows: {len(engine.workflow_definitions)}")
    
    # 5. LOAD OTHER TEMPLATES
    print("\n5. 📦 LOADING OTHER TEMPLATES")
    print("-" * 40)
    
    content_wf = get_template("content_creation")
    decision_wf = get_template("decision_support")
    
    engine.register_workflow(content_wf)
    engine.register_workflow(decision_wf)
    
    print(f"   ✓ {content_wf.name} registered")
    print(f"   ✓ {decision_wf.name} registered")
    print(f"   ✓ Total workflows now: {len(engine.workflow_definitions)}")
    
    # 6. TEMPLATE CUSTOMIZATION
    print("\n6. 🔧 TEMPLATE CUSTOMIZATION")
    print("-" * 40)
    
    print("   Templates can be customized by:")
    print("   • Modifying task inputs before execution")
    print("   • Adjusting timeouts and retry policies")
    print("   • Adding or removing tasks as needed")
    print("   • Changing framework assignments")
    print("")
    print("   Example customization:")
    print("   # Override specific inputs for execution")
    print("   custom_inputs = {")
    print("       'dataset_desc': 'Sales data Q1 2024',")
    print("       'goals': ['trend_analysis', 'anomaly_detection'],")
    print("       'requirements': {'format': 'pdf', 'sections': ['exec_summary', 'detailed_analysis']}")
    print("   }")
    print("   execution_id = await engine.execute_workflow('data_analysis_pipeline', custom_inputs)")
    
    # 7. USE CASE SCENARIOS
    print("\n7. 🎯 COMMON USE CASE SCENARIOS")
    print("-" * 40)
    
    scenarios = [
        ("Data Analysis", "Process and analyze datasets using multiple AI frameworks"),
        ("Content Creation", "Generate high-quality content with collaborative AI agents"),
        ("Decision Support", "Make informed decisions with multi-perspective AI analysis")
    ]
    
    for scenario, description in scenarios:
        print(f"   • {scenario}: {description}")
    
    # 8. ADVANTAGES OF TEMPLATES
    print("\n8. 🌟 ADVANTAGES OF USING TEMPLATES")
    print("-" * 40)
    
    advantages = [
        "Rapid deployment of complex workflows",
        "Best practices built-in",
        "Reduced development time",
        "Consistent workflow patterns",
        "Easy customization for specific needs",
        "Proven architectures for common tasks",
        "Reduced configuration errors"
    ]
    
    for i, advantage in enumerate(advantages, 1):
        print(f"   {i}. {advantage}")
    
    # 9. INTEGRATION WITH EXISTING SYSTEMS
    print("\n9. 🔗 INTEGRATION CAPABILITIES")
    print("-" * 40)
    
    print("   Templates integrate with:")
    print("   • Existing data pipelines")
    print("   • Business logic systems")
    print("   • Monitoring and alerting tools")
    print("   • Security and compliance frameworks")
    print("   • Custom AI models and services")
    
    # 10. EXTENSION POINTS
    print("\n10. 🔌 EXTENSION POINTS")
    print("-" * 40)
    
    print("   To extend templates:")
    print("   • Create new template functions following the same pattern")
    print("   • Add domain-specific templates for your use case")
    print("   • Integrate with your proprietary AI systems")
    print("   • Add custom error handling and recovery procedures")
    
    print("\n" + "=" * 80)
    print("🎉 TEMPLATE USAGE DEMONSTRATION COMPLETE!")
    print("🔄 AgentBridge now includes ready-to-use workflow templates")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demonstrate_template_usage())