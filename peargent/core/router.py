# peargent/core/router.py

from typing import Callable, Optional, List
from .state import State

class RouterResult:
    def __init__(self, next_agent_name: Optional[str]):
        self.next_agent_name = next_agent_name
        
RouterFn = Callable[[State, int, Optional[dict]], RouterResult] # (state, call_count, last_result) -> RouterResult

def round_robin_router(agent_names: List[str]) -> RouterFn:
    def _router(state: State, call_count: int, last_result: Optional[dict]) -> RouterResult:
        if call_count >= len(agent_names):
            return RouterResult(None)
        return RouterResult(agent_names[call_count % len(agent_names)])
    return _router