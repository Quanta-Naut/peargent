"""
Advanced Parallel Tool Execution Example

Demonstrates error handling, mixed success/failure, and real-world use cases.
"""

import time
import random
from peargent import create_agent, create_tool
from peargent.models import groq

# Create tools with varying behaviors
def reliable_tool(query: str) -> str:
    """Always succeeds"""
    time.sleep(0.5)
    return f"Reliable result for: {query}"

def slow_tool(query: str) -> str:
    """Slow but reliable"""
    time.sleep(2)
    return f"Slow result for: {query}"

def sometimes_fails_tool(query: str) -> str:
    """Randomly fails to test error handling"""
    time.sleep(0.5)
    if random.random() < 0.3:  # 30% chance of failure
        raise Exception("Simulated API error - rate limit exceeded")
    return f"Success result for: {query}"

def data_processor_tool(data: str) -> str:
    """Processes data"""
    time.sleep(0.5)
    return f"Processed: {data.upper()}"

# Create tools
tool1 = create_tool(
    name="reliable_tool",
    description="A reliable tool that always works",
    input_parameters={"query": str},
    call_function=reliable_tool
)

tool2 = create_tool(
    name="slow_tool",
    description="A slow but reliable tool",
    input_parameters={"query": str},
    call_function=slow_tool
)

tool3 = create_tool(
    name="sometimes_fails_tool",
    description="A tool that sometimes fails",
    input_parameters={"query": str},
    call_function=sometimes_fails_tool
)

tool4 = create_tool(
    name="data_processor",
    description="Processes and transforms data",
    input_parameters={"data": str},
    call_function=data_processor_tool
)

# Create agent
agent = create_agent(
    name="ResearchAgent",
    description="Conducts research using multiple tools",
    persona="You are a research assistant. Use tools to gather and process information efficiently.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[tool1, tool2, tool3, tool4]
)

print("=" * 80)
print("ADVANCED PARALLEL TOOL EXECUTION")
print("=" * 80 + "\n")

# Test: Call multiple tools in parallel, some may fail
print("Test: Calling multiple tools with potential failures")
print("-" * 80 + "\n")

print("Query: Research 'artificial intelligence' using all available tools in parallel.\n")

start_time = time.time()

try:
    result = agent.run(
        "Research 'artificial intelligence'. Use all available tools in parallel: "
        "reliable_tool, slow_tool, sometimes_fails_tool, and data_processor. "
        "Process the query 'AI research' with each tool simultaneously."
    )

    end_time = time.time()

    print(f"Result:\n{result}\n")
    print(f"Total execution time: {end_time - start_time:.2f}s")

except Exception as e:
    end_time = time.time()
    print(f"Error occurred: {e}")
    print(f"Time until error: {end_time - start_time:.2f}s")

print("\n" + "-" * 80 + "\n")

print("=" * 80)
print("KEY FEATURES DEMONSTRATED")
print("=" * 80)
print("""
1. ERROR HANDLING
   - Tools that fail return error messages
   - Other tools continue executing
   - Agent receives partial results

2. MIXED EXECUTION TIMES
   - Fast tools (0.5s) complete quickly
   - Slow tools (2s) don't block fast ones
   - Total time = slowest tool, not sum of all

3. RESILIENCE
   - One tool failure doesn't crash entire system
   - Agent can work with partial results
   - Errors are clearly reported

4. REAL-WORLD BENEFITS
   - API calls in parallel (weather, stock prices, news)
   - Database queries simultaneously
   - Independent computations at once
   - Massive time savings in data pipelines

EXAMPLE PARALLEL CALL:
{
  "tools": [
    {"tool": "reliable_tool", "args": {"query": "AI"}},
    {"tool": "slow_tool", "args": {"query": "AI"}},
    {"tool": "sometimes_fails_tool", "args": {"query": "AI"}},
    {"tool": "data_processor", "args": {"data": "AI research"}}
  ]
}

All 4 tools execute simultaneously:
- Sequential: 0.5 + 2 + 0.5 + 0.5 = 3.5s
- Parallel: max(0.5, 2, 0.5, 0.5) = 2s
- Speedup: 1.75x faster!
""")
