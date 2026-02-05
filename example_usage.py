"""
Example usage of AgentBridge
"""

import asyncio
from agentbridge import AgentBridge
from agentbridge.protocol import Message, MessageType


async def example_usage():
    """Example of how to use AgentBridge."""
    
    # Initialize the bridge
    bridge = AgentBridge()
    
    # Register adapters for different frameworks
    # Note: In practice, you would connect to running instances of these frameworks
    print("Connecting to agent frameworks...")
    
    # Example: Connect to CrewAI (assuming it's running at localhost:8000)
    try:
        crewai_adapter = bridge.connect_framework(
            framework_name="crewai", 
            endpoint="http://localhost:8000"
        )
    except Exception as e:
        print(f"CrewAI connection failed (expected if not running): {e}")
    
    # Example: Connect to LangGraph (assuming it's running at localhost:8001)  
    try:
        langgraph_adapter = bridge.connect_framework(
            framework_name="langgraph", 
            endpoint="http://localhost:8001"
        )
    except Exception as e:
        print(f"LangGraph connection failed (expected if not running): {e}")
    
    # Create a sample task message
    task_message = bridge.protocol.create_task_request(
        source="my_app",
        target="crewai",
        task_description="Analyze sales data and generate report",
        params={
            "dataset": "sales_q4_2023.csv",
            "report_type": "executive_summary"
        }
    )
    
    print(f"Created task message: {task_message.content}")
    
    # In a real scenario, you would send this to a connected framework
    # result = await bridge.send_message("my_app", "crewai", task_message)
    # print(f"Result: {result}")
    
    # Show bridge status
    status = bridge.get_status()
    print(f"Bridge status: {status}")
    
    print("\nExample completed successfully!")
    

if __name__ == "__main__":
    asyncio.run(example_usage())