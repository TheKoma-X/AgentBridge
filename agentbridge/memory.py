"""
Memory management for AgentBridge.
Provides vector storage and retrieval capabilities.
"""

import json
import math
import os
import sqlite3
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field, asdict

@dataclass
class MemoryEntry:
    """A single memory entry."""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    id: str = field(default_factory=lambda: f"mem_{datetime.now().timestamp()}_{os.urandom(4).hex()}")

class VectorMemory:
    """
    A persistent vector memory implementation using SQLite.
    Stores content and metadata in SQLite, and performs vector similarity search in-memory or via SQL extensions if available.
    """
    
    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path or "agent_memory.db"
        self._init_db()
            
    def _init_db(self):
        """Initialize the SQLite database."""
        try:
            with sqlite3.connect(self.persistence_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        metadata TEXT,
                        embedding TEXT,
                        timestamp REAL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
        except Exception as e:
            print(f"Error initializing memory DB: {e}")

    def add(self, content: str, embedding: Optional[List[float]] = None, metadata: Dict[str, Any] = None) -> str:
        """Add a memory entry."""
        entry = MemoryEntry(
            content=content,
            embedding=embedding,
            metadata=metadata or {}
        )
        
        try:
            with sqlite3.connect(self.persistence_path) as conn:
                conn.execute(
                    "INSERT INTO memories (id, content, metadata, embedding, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (
                        entry.id,
                        entry.content,
                        json.dumps(entry.metadata),
                        json.dumps(entry.embedding) if entry.embedding else None,
                        entry.timestamp
                    )
                )
        except Exception as e:
            print(f"Error adding memory: {e}")
            
        return entry.id
        
    def search(self, query_embedding: List[float], top_k: int = 5, threshold: float = 0.0) -> List[Tuple[MemoryEntry, float]]:
        """
        Search for memories similar to the query embedding.
        Loads vectors into memory for cosine similarity calculation (simplistic approach for small-medium datasets).
        """
        if not query_embedding:
            return []
            
        results = []
        
        try:
            with sqlite3.connect(self.persistence_path) as conn:
                cursor = conn.execute("SELECT id, content, metadata, embedding, timestamp FROM memories WHERE embedding IS NOT NULL")
                
                for row in cursor:
                    try:
                        embedding = json.loads(row[3])
                        similarity = self._cosine_similarity(query_embedding, embedding)
                        
                        if similarity >= threshold:
                            entry = MemoryEntry(
                                id=row[0],
                                content=row[1],
                                metadata=json.loads(row[2]) if row[2] else {},
                                embedding=embedding,
                                timestamp=row[4]
                            )
                            results.append((entry, similarity))
                    except Exception:
                        continue
                        
        except Exception as e:
            print(f"Error searching memory: {e}")
            return []
                
        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
        
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(a * a for a in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)

    def load(self):
        """No-op for SQLite implementation as data is loaded on demand."""
        pass
    
    def save(self):
        """No-op for SQLite implementation as data is saved immediately."""
        pass

class MemoryManager:
    """Manager for system-wide memory."""
    
    def __init__(self, config: Any = None):
        # Handle both dict and BridgeConfig object
        if hasattr(config, 'to_dict'):
            self.config = config.to_dict()
        else:
            self.config = config or {}
            
        # Determine DB path
        db_path = self.config.get("memory_path", "agent_memory.db")
        if db_path.endswith(".json"):
            db_path = db_path.replace(".json", ".db")
            
        self.vector_store = VectorMemory(
            persistence_path=db_path
        )
        
    def remember(self, content: str, metadata: Dict[str, Any] = None):
        """Store a piece of information."""
        # In a real implementation, we would generate an embedding here
        # For this demo, we'll store it without embedding or use a dummy one
        dummy_embedding = [0.1] * 128  # Placeholder
        return self.vector_store.add(content, dummy_embedding, metadata)
        
    def recall(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant information."""
        # In a real implementation, we would embed the query
        dummy_query_embedding = [0.1] * 128  # Placeholder
        
        results = self.vector_store.search(dummy_query_embedding, top_k=top_k)
        
        return [
            {
                "content": r[0].content,
                "metadata": r[0].metadata,
                "similarity": r[1],
                "timestamp": r[0].timestamp
            }
            for r in results
        ]
