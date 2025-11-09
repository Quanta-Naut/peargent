# core/agent.py

from jinja2 import Environment, FileSystemLoader
import os

from peargent.core.stopping import limit_steps


class Agent:
    def __init__(self, name, model, persona, description, tools, stop=None):
        self.name = name
        self.model = model
        self.persona = persona
        self.description = description
        self.tools = {tool.name: tool for tool in tools}
        self.stop_conditions = stop or limit_steps(5)

        self.tool_schemas = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    k: v.__name__ if isinstance(v, type) else str(v)
                    for k, v in tool.input_parameters.items()
                },
            }
            for tool in tools
        ]

        self.jinja_env = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), "..", "templates")
            )
        )

    def _render_tools_prompt(self):
        template = self.jinja_env.get_template("tools_prompt.j2")
        return template.render(tools=self.tool_schemas)

    def _build_initial_prompt(self, user_input: str):
        tools_prompt = self._render_tools_prompt()
        memory_str = "\n".join(
            [
                f"{item['role'].capitalize()}: {item['content']}"
                for item in self.temporary_memory
            ]
        )
        return f"{self.persona}\n\n{tools_prompt}\n\n{memory_str}\n\nAssistant:"

    def _add_to_memory(self, role: str, content: str):
        self.temporary_memory.append({"role": role, "content": content})

    def run(self, input_data: str):
        self.temporary_memory = []

        self._add_to_memory("user", input_data)

        prompt = self._build_initial_prompt(input_data)

        step = 0

        while True:
            # Increment step counter
            step += 1

            response = self.model.generate(prompt)

            self._add_to_memory("assistant", response)

            tool_call = self._parse_tool_call(response)
            if tool_call:
                tool_name = tool_call["tool"]
                args = tool_call["args"]

                if tool_name not in self.tools:
                    raise ValueError(f"Tool '{tool_name}' not found in agent's toolset.")

                tool_output = self.tools[tool_name].run(args)
                
                # Store tool result in a structured way
                self._add_to_memory("tool", {
                    "name": tool_name,
                    "args": args,
                    "output": tool_output
                })

                if self.stop_conditions.should_stop(step - 1, self.temporary_memory):
                    return f"Stopped after {step} steps due to stop condition."

                # Build follow-up prompt with full memory context and separate tool result
                tools_prompt = self._render_tools_prompt()
                conversation_history = "\n".join(
                    [f"{item['role'].capitalize()}: {item['content']}" if item['role'] != "tool" 
                    else f"Tool '{item['content']['name']}' called with args:\n{item['content']['args']}\nOutput:\n{item['content']['output']}"
                    for item in self.temporary_memory]
                )

                prompt = (
                    f"{self.persona}\n\n{tools_prompt}\n\n"
                    f"Conversation History:\n{conversation_history}\n\n"
                    f"Assistant: Based on the most recent tool output shown above, either:\n"
                    f"1. Use another tool.\n"
                    f"2. Or provide the best final answer to the user's request in natural language.\n"
                    f"Remember to reference the tool result if relevant."
                )

                continue  # Go to next loop iteration
            
            # No tool call, return final answer
            print(self.temporary_memory)
            return response

    def _parse_tool_call(self, llm_output: str):
        """Check if LLM output is a tool call JSON."""
        import json
        import re
        # First try to parse as plain JSON
        try:
            structured_response = json.loads(llm_output.strip())
            if (
                isinstance(structured_response, dict)
                and "tool" in structured_response
                and "args" in structured_response
            ):
                return structured_response
        except (json.JSONDecodeError, TypeError):
            pass

        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, llm_output, re.DOTALL)
        
        if match:
            json_content = match.group(1)
            try:
                structured_response = json.loads(json_content)
                if (
                    isinstance(structured_response, dict)
                    and "tool" in structured_response
                    and "args" in structured_response
                ):
                    return structured_response
            except (json.JSONDecodeError, TypeError):
                pass

        return None  # Not a tool call
