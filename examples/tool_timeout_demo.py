"""
Tool Timeout Demonstration

Shows how to prevent tools from hanging indefinitely with timeout settings.
"""

import time
from peargent import create_tool

print("=" * 80)
print("TOOL TIMEOUT DEMONSTRATION")
print("=" * 80 + "\n")

# Create a slow tool that simulates a long-running operation
def slow_operation(duration: int) -> str:
    """Simulates a slow operation (e.g., API call, database query)"""
    print(f"  [Tool] Starting slow operation ({duration}s)...")
    time.sleep(duration)
    print(f"  [Tool] Operation completed!")
    return f"Result after {duration}s"

# Test 1: Tool with no timeout (completes successfully)
print("Test 1: No Timeout - Operation completes normally")
print("-" * 80)

tool_no_timeout = create_tool(
    name="slow_tool",
    description="A slow tool",
    input_parameters={"duration": int},
    call_function=slow_operation
)

start = time.time()
try:
    result = tool_no_timeout.run({"duration": 2})
    elapsed = time.time() - start
    print(f"Result: {result}")
    print(f"Time taken: {elapsed:.2f}s")
    print("Status: SUCCESS\n")
except Exception as e:
    elapsed = time.time() - start
    print(f"Error: {e}")
    print(f"Time taken: {elapsed:.2f}s")
    print("Status: FAILED\n")

# Test 2: Tool with timeout (operation times out)
print("Test 2: With Timeout - Operation exceeds limit")
print("-" * 80)

tool_with_timeout = create_tool(
    name="slow_tool_timeout",
    description="A slow tool with timeout",
    input_parameters={"duration": int},
    call_function=slow_operation,
    timeout=1.0  # 1 second timeout
)

start = time.time()
try:
    result = tool_with_timeout.run({"duration": 3})  # Try to run for 3s
    elapsed = time.time() - start
    print(f"Result: {result}")
    print(f"Time taken: {elapsed:.2f}s")
    print("Status: SUCCESS\n")
except TimeoutError as e:
    elapsed = time.time() - start
    print(f"Error: {e}")
    print(f"Time taken: {elapsed:.2f}s")
    print("Status: TIMED OUT (as expected)\n")

# Test 3: Tool with timeout and graceful error handling
print("Test 3: Timeout with Graceful Error Handling")
print("-" * 80)

tool_graceful = create_tool(
    name="slow_tool_graceful",
    description="A slow tool with graceful timeout handling",
    input_parameters={"duration": int},
    call_function=slow_operation,
    timeout=1.0,
    on_error="return_error"  # Return error message instead of raising
)

start = time.time()
result = tool_graceful.run({"duration": 3})  # Will timeout
elapsed = time.time() - start
print(f"Result: {result}")
print(f"Time taken: {elapsed:.2f}s")
print("Status: GRACEFUL FAILURE (returned error message)\n")

# Test 4: Per-call timeout override
print("Test 4: Override Timeout Per Call")
print("-" * 80)

tool_override = create_tool(
    name="configurable_tool",
    description="Tool with configurable timeout",
    input_parameters={"duration": int},
    call_function=slow_operation,
    timeout=2.0  # Default: 2 seconds
)

print("Using default timeout (2s) for 1s operation:")
start = time.time()
result = tool_override.run({"duration": 1})
elapsed = time.time() - start
print(f"Result: {result}")
print(f"Time: {elapsed:.2f}s\n")

print("Overriding timeout to 0.5s for 1s operation:")
start = time.time()
try:
    result = tool_override.run({"duration": 1}, timeout_override=0.5)
    print(f"Result: {result}")
except TimeoutError as e:
    elapsed = time.time() - start
    print(f"Error: {e}")
    print(f"Time: {elapsed:.2f}s (timed out as expected)")

print("\n" + "=" * 80)
print("TIMEOUT SUMMARY")
print("=" * 80)
print("""
TIMEOUT STRATEGIES:

1. NO TIMEOUT (default)
   - Tool runs until completion
   - Risk: May hang indefinitely
   - Use: Trusted, fast tools

2. WITH TIMEOUT
   - Tool is cancelled if it exceeds limit
   - Raises TimeoutError by default
   - Use: External APIs, slow operations

3. TIMEOUT + GRACEFUL ERROR HANDLING
   - Timeout occurs, but returns error message instead of crashing
   - on_error="return_error"
   - Use: Optional features that shouldn't break the flow

4. PER-CALL TIMEOUT OVERRIDE
   - Override default timeout for specific calls
   - tool.run(args, timeout_override=X)
   - Use: Different timeout needs per call

BEST PRACTICES:
- Set timeouts for all external API calls
- Use graceful error handling for non-critical tools
- Start with generous timeouts, then tune based on metrics
- Override timeouts for known slow operations
""")
