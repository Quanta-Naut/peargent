from peargent import create_agent, openai


def test_agent_uses_persona():
    agent = create_agent(
        name="friendly-greeter",
        persona="You are a kind assistant who always responds cheerfully.",
        description="Says hello in a friendly way.",
        model=openai("mock-gpt")
    )

    result = agent.run("Hello there!")
    assert "cheerfully" in result.lower()
