# peargent/tools/__init__.py

from .math_tool import MathTool

calculator = MathTool()

BUILTIN_TOOLS = {
    "calculator": calculator,
}

def get_tool_by_name(name: str):
    try:
        return BUILTIN_TOOLS[name]
    except KeyError:
        raise ValueError(f"Tool '{name}' not found in built-in tools.")