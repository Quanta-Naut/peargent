#peargent/core/tool.py

from typing import Any, Dict

class Tool:
    def __init__(self, name: str, description: str, input_parameters: Dict[str, type], call_function):
        self.name = name
        self.description = description
        self.input_parameters = input_parameters # {"param_name": type}
        self.call_function = call_function
    
    def run(self, args: Dict[str, Any]) -> Any:
        for key, expected_type in self.input_parameters.items():
            if key not in args:
                raise ValueError(f"Missing required parameter '{key}' for tool '{self.name}'")
            if not isinstance(args[key], expected_type):
                raise TypeError(f"Parameter '{key}' should be of type {expected_type}, got {type(args[key])}")
            
        return self.call_function(**args)