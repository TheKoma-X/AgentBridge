"""
Memory management for AgentBridge.
Provides vector storage and retrieval capabilities.
"""

import json
import math
import os
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
    A lightweight, pure-Python vector memory implementation.
    Does not require numpy or external vector databases.
    """
    
    def __init__(self, persistence_path: Optional[str] = None):
        self.memories: List[MemoryEntry] = []
        self.persistence_path = persistence_path
        
        if self.persistence_path and os.path.exists(self.persistence_path):
            self.load()
            
    def add(self, content: str, embedding: Optional[List[float]] = None, metadata: Dict[str, Any] = None) -> str:
        """Add a memory entry."""
        entry = MemoryEntry(
            content=content,
            embedding=embedding,
            metadata=metadata or {}
        )
        self.memories.append(entry)
        
        if self.persistence_path:
            self.save()
            
        return entry.id
        
    def search(self, query_embedding: List[float], top_k: int = 5, threshold: float = 0.0) -> List[Tuple[MemoryEntry, float]]:
        """
        Search for memories similar to the query embedding.
        Uses cosine similarity.
        """
        if not query_embedding:
            return []
            
        results = []
        
        for memory in self.memories:
            if not memory.embedding:
                continue
                
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, memory.embedding)
            
            if similarity >= threshold:
                results.append((memory, similarity))
                
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
        
    def save(self):
        """Save memories to disk."""
        if not self.persistence_path:
            return
            
        data = [asdict(m) for m in self.memories]
        try:
            with open(self.persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
            
    def load(self):
        """Load memories from disk."""
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
            
        try:
            with open(self.persistence_path, 'r') as f:
                data = json.load(f)
                
            self.memories = []
            for item in data:
                self.memories.append(MemoryEntry(**item))
        except Exception as e:
            print(f"Error loading memory: {e}")

class MemoryManager:
    """Manager for system-wide memory."""
    
    def __init__(self, config: Any = None):
        # Handle both dict and BridgeConfig object
        if hasattr(config, 'to_dict'):
            self.config = config.to_dict()
        else:
            self.config = config or {}
            
        self.vector_store = VectorMemory(
            persistence_path=self.config.get("memory_path", "agent_memory.json")
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
