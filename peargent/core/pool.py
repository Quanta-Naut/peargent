# peargent/core/pool.py

from typing import List, Dict, Optional
from .state import State
from .router import RouterFn, RouterResult
from .stopping import limit_steps

class Pool:
    def __init__(
        self,
        agents: List,
        default_model=None,
        router: Optional[RouterFn] = None,
        max_iter: int = 5,
        default_state: Optional[State] = None,
    ):
        self.agents_dict: Dict[str, any] = {a.name: a for a in agents}
        self.agents_names = list(self.agents_dict.keys())
        self.default_model = default_model
        self.router = router or (lambda state, call_count, last: RouterResult(None))
        self.max_iter = max_iter
        self.state = default_state or State()
        
    def run(self, user_input: str):
        self.state.add_message(role="user", content=user_input, agent=None)
        
        last_result = None
        call_count = 0
        current_input = user_input
        
        while call_count < self.max_iter:
            
            route = self.router(self.state, call_count=call_count, last_result=last_result)
            if not route or route.next_agent_name is None:
                break
            
            agent = self.agents_dict.get(route.next_agent_name)
            if not agent:
                raise ValueError(f"Router selected unknown agent '{route.next_agent_name}'")
            
            # Use the current input (which could be from previous agent's output)
            agent_input = current_input
            output = agent.run(agent_input)
            
            self.state.add_message("assistant", str(output), agent=agent.name)
            last_result = {
                "agent": agent.name,
                "output": output
            }
            
            # Set the output as input for the next agent
            current_input = str(output)
            call_count += 1
            
        final = next((m["content"] for m in reversed(self.state.history) if m["role"] == "assistant"), "")
        return final