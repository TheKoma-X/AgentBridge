"""
Workflow Engine for AgentBridge - Define and execute cross-framework workflows
"""

import asyncio
import json
from enum import Enum
from typing import Dict, Any, List, Optional, Callable, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from .protocol import Message, MessageType
from .logging import get_logger

# Avoid circular import
if TYPE_CHECKING:
    from .bridge import AgentBridge


class WorkflowStatus(Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """Status of a workflow task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskDefinition:
    """Definition of a task in a workflow."""
    id: str
    framework: str
    operation: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Task IDs this task depends on
    timeout: int = 300  # 5 minutes default
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class WorkflowDefinition:
    """Definition of a complete workflow."""
    id: str
    name: str
    description: str
    tasks: List[TaskDefinition]
    start_tasks: List[str] = field(default_factory=list)  # Tasks with no dependencies
    end_tasks: List[str] = field(default_factory=list)    # Tasks with no dependents
    timeout: int = 3600  # 1 hour default
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecution:
    """Execution instance of a task."""
    task_def: TaskDefinition
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class WorkflowExecution:
    """Execution instance of a workflow."""
    workflow_def: WorkflowDefinition
    id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    task_executions: Dict[str, TaskExecution] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)  # Shared workflow variables
    error: Optional[str] = None


class WorkflowEngine:
    """
    Workflow engine for executing cross-framework workflows through AgentBridge
    """
    
    def __init__(self, bridge: 'AgentBridge'):
        self.bridge = bridge
        self.logger = get_logger()
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.task_results: Dict[str, Dict[str, Any]] = {}  # Cache task results
    
    def register_workflow(self, workflow_def: WorkflowDefinition):
        """Register a workflow definition."""
        self.workflow_definitions[workflow_def.id] = workflow_def
        self._calculate_start_end_tasks(workflow_def)
        self.logger.info("WorkflowEngine", f"Registered workflow: {workflow_def.name}")
    
    def _calculate_start_end_tasks(self, workflow_def: WorkflowDefinition):
        """Calculate start and end tasks for a workflow."""
        all_task_ids = {task.id for task in workflow_def.tasks}
        
        # Find tasks with no dependencies (start tasks)
        start_tasks = []
        for task in workflow_def.tasks:
            if not task.dependencies or set(task.dependencies).isdisjoint(all_task_ids):
                start_tasks.append(task.id)
        
        # Find tasks that are not depended on by any other task (end tasks)
        dependent_tasks = set()
        for task in workflow_def.tasks:
            for dep in task.dependencies:
                dependent_tasks.add(dep)
        
        end_tasks = [task.id for task in workflow_def.tasks if task.id not in dependent_tasks]
        
        workflow_def.start_tasks = start_tasks
        workflow_def.end_tasks = end_tasks
    
    def _resolve_inputs(self, task_def: TaskDefinition, workflow_execution: WorkflowExecution) -> Dict[str, Any]:
        """Resolve task inputs using workflow variables and previous task results."""
        resolved_inputs = {}
        
        for key, value in task_def.inputs.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # This is a variable reference like ${variable_name} or ${task_id.output_name}
                var_path = value[2:-1]  # Remove ${ and }
                
                if "." in var_path:
                    # Task output reference: task_id.output_name
                    task_id, output_name = var_path.split(".", 1)
                    if task_id in workflow_execution.task_executions:
                        task_exec = workflow_execution.task_executions[task_id]
                        if task_exec.status == TaskStatus.COMPLETED and task_exec.result:
                            if isinstance(task_exec.result, dict) and output_name in task_exec.result:
                                resolved_inputs[key] = task_exec.result[output_name]
                            else:
                                resolved_inputs[key] = task_exec.result
                        else:
                            resolved_inputs[key] = value  # Keep unresolved if task not completed
                else:
                    # Workflow variable reference
                    if var_path in workflow_execution.variables:
                        resolved_inputs[key] = workflow_execution.variables[var_path]
                    else:
                        resolved_inputs[key] = value  # Keep unresolved if variable not found
            else:
                # Literal value
                resolved_inputs[key] = value
        
        return resolved_inputs
    
    async def _execute_task(self, task_def: TaskDefinition, workflow_execution: WorkflowExecution) -> Any:
        """Execute a single task."""
        task_exec = TaskExecution(task_def=task_def)
        task_exec.started_at = datetime.now()
        task_exec.status = TaskStatus.RUNNING
        
        # Store task execution in workflow
        workflow_execution.task_executions[task_def.id] = task_exec
        
        try:
            # Resolve inputs
            resolved_inputs = self._resolve_inputs(task_def, workflow_execution)
            
            # Create message for the task
            message = Message(
                type=MessageType.TASK_REQUEST,
                source="workflow_engine",
                target=task_def.framework,
                content={
                    "operation": task_def.operation,
                    "inputs": resolved_inputs,
                    "task_id": task_def.id
                },
                timestamp=task_exec.started_at.timestamp()
            )
            
            # Execute the task via the bridge
            result = await self.bridge.send_message("workflow_engine", task_def.framework, message)
            
            task_exec.result = result
            task_exec.status = TaskStatus.COMPLETED
            task_exec.completed_at = datetime.now()
            
            # Update workflow variables if this task has outputs
            if task_def.outputs and isinstance(result, dict):
                for output_name in task_def.outputs:
                    if output_name in result:
                        workflow_execution.variables[f"{task_def.id}.{output_name}"] = result[output_name]
            
            self.logger.info("WorkflowEngine", f"Task {task_def.id} completed successfully")
            return result
            
        except Exception as e:
            task_exec.error = str(e)
            task_exec.status = TaskStatus.FAILED
            task_exec.completed_at = datetime.now()
            
            self.logger.error("WorkflowEngine", f"Task {task_def.id} failed: {str(e)}")
            raise
    
    async def _check_dependencies_met(self, task_def: TaskDefinition, workflow_execution: WorkflowExecution) -> bool:
        """Check if all dependencies for a task are met."""
        for dep_task_id in task_def.dependencies:
            if dep_task_id not in workflow_execution.task_executions:
                return False  # Dependency task hasn't started
            
            dep_task_exec = workflow_execution.task_executions[dep_task_id]
            if dep_task_exec.status != TaskStatus.COMPLETED:
                return False  # Dependency task hasn't completed
        
        return True
    
    async def _get_ready_tasks(self, workflow_execution: WorkflowExecution) -> List[TaskDefinition]:
        """Get tasks that are ready to run (dependencies satisfied)."""
        ready_tasks = []
        
        for task_def in workflow_execution.workflow_def.tasks:
            if task_def.id not in workflow_execution.task_executions:
                # Task hasn't started yet
                if await self._check_dependencies_met(task_def, workflow_execution):
                    ready_tasks.append(task_def)
        
        return ready_tasks
    
    async def execute_workflow(self, workflow_id: str, input_variables: Optional[Dict[str, Any]] = None) -> str:
        """Execute a workflow asynchronously."""
        if workflow_id not in self.workflow_definitions:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow_def = self.workflow_definitions[workflow_id]
        
        # Create execution instance
        execution_id = str(uuid.uuid4())
        workflow_execution = WorkflowExecution(
            workflow_def=workflow_def,
            id=execution_id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now(),
            variables=input_variables or {}
        )
        
        # Store execution
        self.active_executions[execution_id] = workflow_execution
        
        self.logger.info("WorkflowEngine", f"Started workflow execution: {execution_id} for workflow: {workflow_def.name}")
        
        try:
            # Execute workflow until completion
            while workflow_execution.status == WorkflowStatus.RUNNING:
                # Get tasks that are ready to run
                ready_tasks = await self._get_ready_tasks(workflow_execution)
                
                if not ready_tasks:
                    # Check if workflow is complete
                    completed_tasks = [
                        task_exec for task_exec in workflow_execution.task_executions.values()
                        if task_exec.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]
                    ]
                    
                    if len(completed_tasks) == len(workflow_def.tasks):
                        # All tasks completed
                        workflow_execution.status = WorkflowStatus.COMPLETED
                        workflow_execution.completed_at = datetime.now()
                        break
                    else:
                        # Wait briefly before checking again
                        await asyncio.sleep(0.1)
                        continue
                
                # Execute ready tasks concurrently
                tasks_to_run = []
                for task_def in ready_tasks:
                    tasks_to_run.append(self._execute_task(task_def, workflow_execution))
                
                # Run tasks concurrently
                results = await asyncio.gather(*tasks_to_run, return_exceptions=True)
                
                # Check for failures
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        # Mark workflow as failed
                        workflow_execution.status = WorkflowStatus.FAILED
                        workflow_execution.error = str(result)
                        workflow_execution.completed_at = datetime.now()
                        
                        self.logger.error("WorkflowEngine", f"Workflow {execution_id} failed: {str(result)}")
                        break
                else:
                    # If no failures, continue the loop
                    continue
                
                break  # Break if workflow failed
            
            self.logger.info("WorkflowEngine", f"Workflow execution {execution_id} finished with status: {workflow_execution.status.value}")
            return execution_id
            
        except Exception as e:
            workflow_execution.status = WorkflowStatus.FAILED
            workflow_execution.error = str(e)
            workflow_execution.completed_at = datetime.now()
            
            self.logger.error("WorkflowEngine", f"Workflow execution {execution_id} failed with exception: {str(e)}")
            raise
        finally:
            # Cleanup if workflow completed
            if workflow_execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                del self.active_executions[execution_id]
    
    async def cancel_workflow(self, execution_id: str):
        """Cancel a running workflow."""
        if execution_id not in self.active_executions:
            raise ValueError(f"Workflow execution {execution_id} not found")
        
        workflow_execution = self.active_executions[execution_id]
        workflow_execution.status = WorkflowStatus.CANCELLED
        workflow_execution.completed_at = datetime.now()
        
        # Remove from active executions
        del self.active_executions[execution_id]
        
        self.logger.info("WorkflowEngine", f"Cancelled workflow execution: {execution_id}")
    
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get the status of a workflow execution."""
        return self.active_executions.get(execution_id)
    
    def get_workflow_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed workflow."""
        execution = self.active_executions.get(execution_id)
        if execution and execution.status == WorkflowStatus.COMPLETED:
            return {
                "status": execution.status.value,
                "variables": execution.variables,
                "task_results": {
                    task_id: task_exec.result 
                    for task_id, task_exec in execution.task_executions.items()
                    if task_exec.status == TaskStatus.COMPLETED
                },
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
            }
        
        return None


class WorkflowBuilder:
    """Helper class to build workflows programmatically."""
    
    def __init__(self):
        self.tasks: List[TaskDefinition] = []
        self.task_count = 0
    
    def add_task(self, framework: str, operation: str, 
                 inputs: Optional[Dict[str, Any]] = None,
                 outputs: Optional[List[str]] = None,
                 dependencies: Optional[List[str]] = None,
                 timeout: int = 300,
                 retry_attempts: int = 3) -> 'WorkflowBuilder':
        """Add a task to the workflow."""
        task_id = f"task_{self.task_count}"
        self.task_count += 1
        
        task = TaskDefinition(
            id=task_id,
            framework=framework,
            operation=operation,
            inputs=inputs or {},
            outputs=outputs or [],
            dependencies=dependencies or [],
            timeout=timeout,
            retry_attempts=retry_attempts
        )
        
        self.tasks.append(task)
        return self
    
    def build(self, workflow_id: str, name: str, description: str = "") -> WorkflowDefinition:
        """Build the workflow definition."""
        workflow_def = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            tasks=self.tasks.copy()
        )
        
        # Reset for next workflow
        self.tasks = []
        self.task_count = 0
        
        return workflow_def