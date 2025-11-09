from peargent import create_agent, create_pool, create_tool, limit_steps
from peargent.models import openai, groq, gemini
from peargent.tools import calculator


def test_agent_pool(input: str):
    def fact_generator_tool(text: str) -> str:
        return "Humans finally reached Mars on 27th Feb 2300."

    fact_generator = create_tool(
        name="fact_generator",
        description="Generates facts about various topics   ",
        input_parameters={"text": str},
        call_function=fact_generator_tool,
    )

    search = create_agent(
        name="search",
        description="Performs fact generation.",
        persona="Find fresh facts using the fact_generator tool. You are not allowed to provide any facts on your own. Use the tool to generate facts.",
        model=gemini("gemini-2.5-flash"),
        tools=[fact_generator],
        stop=limit_steps(15),
    )
    
    answer = search.run(input)
    return answer

if __name__ == "__main__":
    result = test_agent_pool("Generate facts. Use the fact_generator tool")
    print("Agent Result:", result)
