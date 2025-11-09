# peargent/core/state.py

from typing import Any, Dict, List, Optional

class State:
    """
    Shared key-value store + message history across the pool loop.
    Accessible by the router and the agents/tools.
    """
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self.kv: Dict[str, Any] = data or {}
        self.history: List[Dict[str, Any]] = []
        
    def add_message(self, role: str, content: str, agent: Optional[str] = None):
        self.history.append({
            "role": role,
            "content": content,
            "agent": agent
        })
        
    def get(self, key: str, default=None): return self.kv.get(key, default)
    def set(self, key: str, value: Any): self.kv[key] = value