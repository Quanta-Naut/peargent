from peargent import create_agent, openai, create_tool

def test_custom_tool_with_parameters():
    def repeat(text: str, times: int) -> str:
        return text * times

    repeat_tool = create_tool(
        name="repeat",
        description="Repeat text multiple times",
        input_parameters={"text": str, "times": int},
        call_function=repeat
    )

    agent = create_agent(
        name="repeat-agent",
        description="An agent that repeats text.",
        persona="You are a helpful assistant that can use tools to repeat text.",
        model=openai("gpt-5"),
        tools=[repeat_tool]
    )

    result = agent.run({
        "tool": "repeat",
        "args": {"text": "ha", "times": 3}
    })
    assert result == "hahaha"

