"""
Evaluation and Simulation system for AgentBridge.
Provides trace recording and replay capabilities.
"""

import json
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

@dataclass
class InteractionTrace:
    """A record of a single interaction."""
    id: str
    timestamp: float
    source: str
    target: str
    message: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    duration: float = 0.0
    success: bool = True
    error: Optional[str] = None

class TraceRecorder:
    """Records system interactions for later analysis."""
    
    def __init__(self, storage_dir: str = "traces"):
        self.storage_dir = storage_dir
        self.current_session_id = f"session_{int(time.time())}"
        self.traces: List[InteractionTrace] = []
        
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            
    def record(self, 
               source: str, 
               target: str, 
               message: Dict[str, Any], 
               result: Any = None,
               duration: float = 0.0,
               success: bool = True,
               error: str = None):
        """Record an interaction."""
        trace = InteractionTrace(
            id=f"trace_{len(self.traces)}",
            timestamp=time.time(),
            source=source,
            target=target,
            message=message,
            result=result,
            duration=duration,
            success=success,
            error=error
        )
        self.traces.append(trace)
        self._save_trace(trace)
        
    def _save_trace(self, trace: InteractionTrace):
        """Save a single trace to disk."""
        session_dir = os.path.join(self.storage_dir, self.current_session_id)
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
            
        filename = os.path.join(session_dir, f"{trace.id}.json")
        try:
            with open(filename, 'w') as f:
                json.dump(asdict(trace), f, indent=2)
        except Exception as e:
            print(f"Error saving trace: {e}")
            
    def get_traces(self, session_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve traces for a session."""
        target_session = session_id or self.current_session_id
        session_dir = os.path.join(self.storage_dir, target_session)
        
        if not os.path.exists(session_dir):
            return []
            
        results = []
        try:
            for filename in sorted(os.listdir(session_dir)):
                if filename.endswith(".json"):
                    with open(os.path.join(session_dir, filename), 'r') as f:
                        results.append(json.load(f))
        except Exception as e:
            print(f"Error reading traces: {e}")
            
        return results

class EvaluationEngine:
    """Engine for running evaluations."""
    
    def __init__(self, recorder: TraceRecorder):
        self.recorder = recorder
        
    def analyze_session(self, session_id: str = None) -> Dict[str, Any]:
        """Analyze a recording session."""
        traces = self.recorder.get_traces(session_id)
        if not traces:
            return {"error": "No traces found"}
            
        total_duration = sum(t.get("duration", 0) for t in traces)
        success_count = sum(1 for t in traces if t.get("success", True))
        error_count = len(traces) - success_count
        
        return {
            "session_id": session_id or self.recorder.current_session_id,
            "total_interactions": len(traces),
            "success_rate": success_count / len(traces) if traces else 0,
            "avg_duration": total_duration / len(traces) if traces else 0,
            "total_duration": total_duration,
            "error_count": error_count
        }
