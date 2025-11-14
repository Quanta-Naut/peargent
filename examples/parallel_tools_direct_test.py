"""
Direct Test of Parallel Tool Execution

Tests the parallel execution path directly by simulating LLM responses.
"""

import time
import json
from peargent import create_agent, create_tool
from peargent.models import groq

# Create simple tools with timing
def tool_a(x: str) -> str:
    print(f"  [Tool A] Starting...")
    time.sleep(1)
    print(f"  [Tool A] Completed!")
    return f"Result A: {x}"

def tool_b(y: str) -> str:
    print(f"  [Tool B] Starting...")
    time.sleep(1)
    print(f"  [Tool B] Completed!")
    return f"Result B: {y}"

def tool_c(z: str) -> str:
    print(f"  [Tool C] Starting...")
    time.sleep(1)
    print(f"  [Tool C] Completed!")
    return f"Result C: {z}"

# Create tools
tool1 = create_tool("tool_a", "Tool A", {"x": str}, tool_a)
tool2 = create_tool("tool_b", "Tool B", {"y": str}, tool_b)
tool3 = create_tool("tool_c", "Tool C", {"z": str}, tool_c)

# Create agent
agent = create_agent(
    name="TestAgent",
    description="Test agent for parallel execution",
    persona="You are a test agent.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[tool1, tool2, tool3]
)

print("=" * 80)
print("DIRECT PARALLEL EXECUTION TEST")
print("=" * 80 + "\n")

# Test the parsing of parallel tool calls
print("Test 1: Parse parallel tool call format")
print("-" * 80 + "\n")

parallel_json = json.dumps({
    "tools": [
        {"tool": "tool_a", "args": {"x": "test1"}},
        {"tool": "tool_b", "args": {"y": "test2"}},
        {"tool": "tool_c", "args": {"z": "test3"}}
    ]
})

print(f"Simulated LLM Response:\n{parallel_json}\n")

parsed = agent._parse_tool_call(parallel_json)
print(f"Parsed result: {parsed}\n")

if parsed and "tools" in parsed:
    print("SUCCESS: Parallel format recognized!\n")
    print(f"Number of tools to execute: {len(parsed['tools'])}\n")

    # Test parallel execution
    print("Test 2: Execute tools in parallel")
    print("-" * 80 + "\n")

    print("Starting parallel execution...")
    print("(Watch for all tools starting at once, not one by one)\n")

    start_time = time.time()

    results = agent._execute_tools_parallel(parsed['tools'])

    end_time = time.time()
    exec_time = end_time - start_time

    print(f"\nExecution completed in {exec_time:.2f}s\n")

    print("Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Tool: {result['tool']}")
        print(f"   Output: {result['output']}")
        print(f"   Error: {result['error']}\n")

    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print(f"""
Expected Behavior:
- Sequential: 1s + 1s + 1s = 3+ seconds
- Parallel: max(1s, 1s, 1s) = ~1 second

Actual Time: {exec_time:.2f}s

Result: {"PARALLEL EXECUTION WORKING!" if exec_time < 1.5 else "Still sequential - needs debugging"}

If all three tools started at the same time (you saw all "Starting..." messages
together), then parallel execution is working correctly!
""")

else:
    print("FAILED: Parallel format not recognized")

print("\n" + "=" * 80 + "\n")

# Test single tool call format still works
print("Test 3: Verify single tool call format still works")
print("-" * 80 + "\n")

single_json = json.dumps({
    "tool": "tool_a",
    "args": {"x": "single_test"}
})

print(f"Simulated LLM Response:\n{single_json}\n")

parsed = agent._parse_tool_call(single_json)
print(f"Parsed result: {parsed}\n")

if parsed and "tool" in parsed:
    print("SUCCESS: Single tool format still works!")
else:
    print("FAILED: Single tool format broken")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
