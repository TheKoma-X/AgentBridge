"""
Evaluation and Simulation system for AgentBridge.
Provides trace recording and replay capabilities.
"""

import json
import os
import time
import sqlite3
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
    """Records system interactions for later analysis using SQLite."""
    
    def __init__(self, storage_dir: str = "traces", max_traces: int = 1000):
        self.storage_dir = storage_dir
        self.db_path = os.path.join(storage_dir, "traces.db")
        self.current_session_id = f"session_{int(time.time())}"
        self.max_traces = max_traces
        
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            
        self._init_db()
        
    def _init_db(self):
        """Initialize the SQLite database for traces."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS traces (
                        id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        timestamp REAL,
                        source TEXT,
                        target TEXT,
                        message TEXT,
                        result TEXT,
                        duration REAL,
                        success INTEGER,
                        error TEXT
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON traces(session_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON traces(timestamp)")
                
                # Span table for distributed tracing
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS spans (
                        id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        operation TEXT,
                        start_time REAL,
                        end_time REAL,
                        duration REAL,
                        parent_span_id TEXT,
                        attributes TEXT,
                        error TEXT
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_span_session ON spans(session_id)")
        except Exception as e:
            print(f"Error initializing trace DB: {e}")
            
    def start_span(self, operation_name: str, parent_span_id: str = None) -> str:
        """Start a new tracing span."""
        span_id = f"span_{int(time.time())}_{os.urandom(4).hex()}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO spans (id, session_id, operation, start_time, parent_span_id, attributes) VALUES (?, ?, ?, ?, ?, ?)",
                    (span_id, self.current_session_id, operation_name, time.time(), parent_span_id, "{}")
                )
        except Exception as e:
            print(f"Error starting span: {e}")
            
        return span_id
    
    def end_span(self, span_id: str, attributes: Dict[str, Any] = None, error: str = None):
        """End a tracing span."""
        try:
            end_time = time.time()
            with sqlite3.connect(self.db_path) as conn:
                # Get start time to calculate duration
                cursor = conn.execute("SELECT start_time FROM spans WHERE id = ?", (span_id,))
                row = cursor.fetchone()
                
                if row:
                    start_time = row[0]
                    duration = end_time - start_time
                    
                    # Update attributes if needed
                    current_attrs = {} # Ideally we'd fetch and merge, simplifying for now
                    if attributes:
                        current_attrs.update(attributes)
                    
                    conn.execute(
                        "UPDATE spans SET end_time = ?, duration = ?, error = ?, attributes = ? WHERE id = ?",
                        (end_time, duration, error, json.dumps(current_attrs), span_id)
                    )
        except Exception as e:
            print(f"Error ending span: {e}")
    
    def record(self, 
               source: str, 
               target: str, 
               message: Dict[str, Any], 
               result: Any = None,
               duration: float = 0.0,
               success: bool = True,
               error: str = None,
               span_id: str = None):
        """Record an interaction."""
        trace = InteractionTrace(
            id=f"trace_{int(time.time())}_{os.urandom(4).hex()}",
            timestamp=time.time(),
            source=source,
            target=target,
            message=message,
            result=result,
            duration=duration,
            success=success,
            error=error
        )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO traces (
                        id, session_id, timestamp, source, target, message, result, duration, success, error
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        trace.id,
                        self.current_session_id,
                        trace.timestamp,
                        trace.source,
                        trace.target,
                        json.dumps(trace.message),
                        json.dumps(trace.result) if trace.result else None,
                        trace.duration,
                        1 if trace.success else 0,
                        trace.error
                    )
                )
        except Exception as e:
            print(f"Error recording trace: {e}")
            
    def get_traces(self, session_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve traces for a session."""
        target_session = session_id or self.current_session_id
        results = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Need to use row factory or manual mapping
                cursor = conn.execute(
                    "SELECT id, timestamp, source, target, message, result, duration, success, error FROM traces WHERE session_id = ? ORDER BY timestamp",
                    (target_session,)
                )
                
                for row in cursor:
                    results.append({
                        "id": row[0],
                        "timestamp": row[1],
                        "source": row[2],
                        "target": row[3],
                        "message": json.loads(row[4]) if row[4] else {},
                        "result": json.loads(row[5]) if row[5] else None,
                        "duration": row[6],
                        "success": bool(row[7]),
                        "error": row[8]
                    })
        except Exception as e:
            print(f"Error retrieving traces: {e}")
            
        return results

class LLMEvaluator:
    """Evaluates interactions using an LLM (LLM-as-a-Judge)."""
    
    def __init__(self, model_manager=None):
        self.model_manager = model_manager
        
    async def evaluate_interaction(self, trace: Dict[str, Any], criteria: List[str] = None) -> Dict[str, Any]:
        """Evaluate a single interaction trace."""
        if not self.model_manager:
            return {"error": "No model manager available"}
            
        criteria = criteria or ["accuracy", "relevance", "safety"]
        
        prompt = f"""
        Please evaluate the following AI agent interaction:
        
        Source: {trace.get('source')}
        Target: {trace.get('target')}
        Input: {json.dumps(trace.get('message', {}))}
        Output: {json.dumps(trace.get('result', {}))}
        
        Evaluate based on these criteria: {', '.join(criteria)}.
        Return a JSON object with a score (0-10) and reasoning for each criterion.
        """
        
        # In a real implementation, we would call the model manager here
        # For now, return a mock evaluation
        return {
            "evaluation_id": f"eval_{int(time.time())}",
            "trace_id": trace.get("id"),
            "scores": {c: 8.5 for c in criteria},  # Mock scores
            "reasoning": "This is a simulated evaluation.",
            "timestamp": time.time()
        }

class EvaluationEngine:
    """Engine for running evaluations."""
    
    def __init__(self, recorder: TraceRecorder, model_manager=None):
        self.recorder = recorder
        self.evaluator = LLMEvaluator(model_manager)
        
    def analyze_session(self, session_id: str = None) -> Dict[str, Any]:
        """Analyze a recording session (quantitative metrics)."""
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
        
    async def run_qualitative_evaluation(self, session_id: str = None) -> Dict[str, Any]:
        """Run qualitative evaluation on a session using LLM."""
        traces = self.recorder.get_traces(session_id)
        if not traces:
            return {"error": "No traces found"}
            
        evaluations = []
        for trace in traces:
            # Skip traces that were errors
            if not trace.get("success", True):
                continue
                
            eval_result = await self.evaluator.evaluate_interaction(trace)
            evaluations.append(eval_result)
            
        return {
            "session_id": session_id or self.recorder.current_session_id,
            "evaluations_count": len(evaluations),
            "evaluations": evaluations
        }
