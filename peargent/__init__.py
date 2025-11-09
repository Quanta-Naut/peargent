# my_agent_lib/__init__.py

from os import name
from typing import Optional
from dotenv import load_dotenv

from peargent.core.router import round_robin_router
from peargent.core.state import State

load_dotenv()

from .core.agent import Agent
from .core.tool import Tool
from .tools import get_tool_by_name
from peargent.core.router import RouterResult
from .core.stopping import limit_steps, StepLimitCondition
from .core.pool import Pool

def create_agent(name: str, description: str, persona: str, model, tools=None, stop = None):
    parsed_tools = []
    for t in tools or []:
        if isinstance(t, str):
            parsed_tools.append(get_tool_by_name(t))
        elif isinstance(t, Tool):
            parsed_tools.append(t)
        else:
            raise ValueError("Tools must be instances of the Tool class.")

    return Agent(name=name, description=description, persona=persona, model=model, tools=parsed_tools, stop=stop)

def create_tool(name: str, description: str, input_parameters: dict, call_function):
    return Tool(name=name, description=description, input_parameters=input_parameters, call_function=call_function)

def create_pool(agents, default_model=None, router=None, max_iter=5, default_state=None):
    return Pool(
        agents=agents,
        default_model=default_model,
        router=router or round_robin_router([agent.name for agent in agents]),
        max_iter=max_iter,
        default_state=default_state or State()
    )
