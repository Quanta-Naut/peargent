"""
Basic Parallel Tool Execution Example

Demonstrates how agents can call multiple tools simultaneously for faster execution.
"""

import time
from peargent import create_agent, create_tool, enable_tracing
from peargent.models import groq

# Enable tracing
tracer = enable_tracing()

# Create multiple tools that simulate different operations
def get_weather(city: str) -> str:
    """Simulate weather API call"""
    time.sleep(1)  # Simulate API latency
    return f"Weather in {city}: Sunny, 72°F"

def calculate_distance(city1: str, city2: str) -> str:
    """Simulate distance calculation"""
    time.sleep(1)  # Simulate computation time
    return f"Distance from {city1} to {city2}: 350 miles"

def get_population(city: str) -> str:
    """Simulate population lookup"""
    time.sleep(1)  # Simulate database query
    return f"Population of {city}: 500,000"

def get_time_zone(city: str) -> str:
    """Simulate timezone lookup"""
    time.sleep(1)  # Simulate API call
    return f"Timezone for {city}: PST (UTC-8)"

# Create tools
weather_tool = create_tool(
    name="get_weather",
    description="Get current weather for a city",
    input_parameters={"city": str},
    call_function=get_weather
)

distance_tool = create_tool(
    name="calculate_distance",
    description="Calculate distance between two cities",
    input_parameters={"city1": str, "city2": str},
    call_function=calculate_distance
)

population_tool = create_tool(
    name="get_population",
    description="Get population of a city",
    input_parameters={"city": str},
    call_function=get_population
)

timezone_tool = create_tool(
    name="get_time_zone",
    description="Get timezone for a city",
    input_parameters={"city": str},
    call_function=get_time_zone
)

# Create agent with all tools
agent = create_agent(
    name="CityInfoAgent",
    description="Provides comprehensive city information",
    persona="You are a helpful assistant that provides city information using available tools.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[weather_tool, distance_tool, population_tool, timezone_tool],
    tracing=True
)

print("=" * 80)
print("PARALLEL TOOL EXECUTION DEMO")
print("=" * 80 + "\n")

# Test 1: Sequential tool calls (old way - if LLM chooses to call one by one)
print("Test 1: Asking for city information")
print("-" * 80 + "\n")

start_time = time.time()

result = agent.run(
    "I need information about San Francisco. Get me the weather, population, and timezone. "
    "Use multiple tools at once if possible to save time."
)

end_time = time.time()

print(f"\nResult:\n{result}\n")
print(f"Execution time: {end_time - start_time:.2f}s")
print("-" * 80 + "\n")

# Test 2: Complex query requiring multiple tools
print("Test 2: Complex multi-city query")
print("-" * 80 + "\n")

start_time = time.time()

result = agent.run(
    "Compare San Francisco and Los Angeles. Get weather for both cities, "
    "calculate the distance between them, and get population for both. "
    "Execute all tool calls in parallel for faster results."
)

end_time = time.time()

print(f"\nResult:\n{result}\n")
print(f"Execution time: {end_time - start_time:.2f}s")
print("-" * 80 + "\n")

print("=" * 80)
print("PERFORMANCE ANALYSIS")
print("=" * 80)
print("""
SEQUENTIAL vs PARALLEL EXECUTION:

Sequential (old way):
- Tool 1: 1s
- Tool 2: 1s
- Tool 3: 1s
- Tool 4: 1s
Total: 4+ seconds

Parallel (new way):
- All tools: ~1s (executed simultaneously)
Total: 1-2 seconds

SPEEDUP: Up to 4x faster!

The agent can now call multiple tools simultaneously using:
{
  "tools": [
    {"tool": "get_weather", "args": {"city": "San Francisco"}},
    {"tool": "get_population", "args": {"city": "San Francisco"}},
    {"tool": "get_time_zone", "args": {"city": "San Francisco"}}
  ]
}

All three tools execute in parallel, dramatically reducing latency!
""")

print("\n" + "=" * 80)
print("TRACING SUMMARY")
print("=" * 80 + "\n")

tracer.print_summary()
