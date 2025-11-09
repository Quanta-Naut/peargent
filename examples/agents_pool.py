from peargent import create_agent, create_pool, create_tool, limit_steps
from peargent.models import gemini

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
        description="Generates interesting facts using available tools.",
        persona="You are a fact generator. When asked for a fact, use the fact_generator tool to generate an interesting fact. Always use the tool to provide facts rather than making them up yourself.",
        model=gemini("gemini-2.5-flash"),
        tools=[fact_generator],
        stop=limit_steps(5),
    )

    summarize = create_agent(
        name="summary",
        persona="You are a summary writer. Take the input and write a tight, readable summary or reformat it nicely. If the input is already a fact, present it in an engaging way.",
        description="Summarizer and formatter",
        model=gemini("gemini-2.5-flash"),
        stop=limit_steps(3),
    )

    pool = create_pool(
        agents=[search, summarize],
        max_iter=4,
    )
    
    answer = pool.run(input)
    return answer

if __name__ == "__main__":
    result = test_agent_pool("Say me a fact!")
    print("Agent Result:", result)
