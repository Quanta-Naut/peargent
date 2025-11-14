"""
Tool Error Handling Strategies Demonstration

Shows the three error handling modes: raise, return_error, return_none
"""

from peargent import create_tool, create_agent
from peargent.models import groq

print("=" * 80)
print("TOOL ERROR HANDLING STRATEGIES")
print("=" * 80 + "\n")

# Create a tool that always fails
def failing_tool(x: str) -> str:
    """A tool that always fails"""
    raise Exception("This tool always fails!")

# Strategy 1: RAISE (default) - Strict mode
print("Strategy 1: on_error='raise' (Default - Strict Mode)")
print("-" * 80)

tool_raise = create_tool(
    name="strict_tool",
    description="Strict tool that crashes on error",
    input_parameters={"x": str},
    call_function=failing_tool,
    on_error="raise"  # Default behavior
)

try:
    result = tool_raise.run({"x": "test"})
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception raised: {type(e).__name__}: {e}")
    print("Execution stopped!")

print("\nUse case:")
print("  - Critical tools that MUST succeed")
print("  - Fail-fast approach")
print("  - Testing and development")
print()

# Strategy 2: RETURN_ERROR - Graceful mode
print("Strategy 2: on_error='return_error' (Graceful Mode)")
print("-" * 80)

tool_return_error = create_tool(
    name="graceful_tool",
    description="Graceful tool that returns error messages",
    input_parameters={"x": str},
    call_function=failing_tool,
    on_error="return_error"  # Return error message as string
)

result = tool_return_error.run({"x": "test"})
print(f"Result: {result}")
print("No exception! Execution continues!")

print("\nUse case:")
print("  - Optional features")
print("  - Tools that might fail but shouldn't crash the agent")
print("  - Agents that can work with partial results")
print()

# Strategy 3: RETURN_NONE - Silent mode
print("Strategy 3: on_error='return_none' (Silent Mode)")
print("-" * 80)

tool_return_none = create_tool(
    name="silent_tool",
    description="Silent tool that returns None on error",
    input_parameters={"x": str},
    call_function=failing_tool,
    on_error="return_none"  # Return None silently
)

result = tool_return_none.run({"x": "test"})
print(f"Result: {result}")
print("Returns None silently!")

print("\nUse case:")
print("  - Nice-to-have features")
print("  - Tools where absence of result is acceptable")
print("  - Telemetry/logging tools")
print()

# Real-world example: Agent with mixed error handling
print("=" * 80)
print("REAL-WORLD EXAMPLE: Agent with Mixed Error Strategies")
print("=" * 80 + "\n")

# Critical tool - must succeed
def get_user_data(user_id: str) -> str:
    """Critical: Get user data"""
    if user_id == "bad":
        raise Exception("User not found")
    return f"User data for {user_id}"

critical_tool = create_tool(
    name="get_user",
    description="Get user data (CRITICAL)",
    input_parameters={"user_id": str},
    call_function=get_user_data,
    on_error="raise"  # Must succeed
)

# Optional tool - nice to have
def get_recommendations(user_id: str) -> str:
    """Optional: Get recommendations"""
    raise Exception("Recommendation service down")

optional_tool = create_tool(
    name="get_recommendations",
    description="Get product recommendations (OPTIONAL)",
    input_parameters={"user_id": str},
    call_function=get_recommendations,
    on_error="return_error"  # Can fail gracefully
)

# Analytics tool - can be silent
def log_analytics(event: str) -> str:
    """Analytics: Log event"""
    raise Exception("Analytics service unavailable")

analytics_tool = create_tool(
    name="log_analytics",
    description="Log analytics event",
    input_parameters={"event": str},
    call_function=log_analytics,
    on_error="return_none"  # Silent failure OK
)

# Create agent with all three tools
agent = create_agent(
    name="UserAgent",
    description="Handles user requests",
    persona="You help users. Use tools to fetch data.",
    model=groq("llama-3.3-70b-versatile"),
    tools=[critical_tool, optional_tool, analytics_tool]
)

print("Agent has 3 tools:")
print("  1. get_user (on_error='raise') - MUST succeed")
print("  2. get_recommendations (on_error='return_error') - Can fail gracefully")
print("  3. log_analytics (on_error='return_none') - Silent failure\n")

print("Scenario: get_user succeeds, recommendations fails, analytics fails")
print("-" * 80)
print("Expected behavior:")
print("  - User data retrieved successfully")
print("  - Recommendations fail but return error message")
print("  - Analytics fails silently (returns None)")
print("  - Agent continues and provides response with available data")

print("\n" + "=" * 80)
print("ERROR HANDLING DECISION TREE")
print("=" * 80)
print("""
Does tool failure break the entire operation?
  |
  +-- YES => on_error="raise"
  |
  +-- NO => Can agent still provide useful response?
              |
              +-- YES => on_error="return_error"
              |
              +-- NO => on_error="return_none"

EXAMPLES:

RAISE:
- Authentication
- Database writes
- Payment processing
- Required user data

RETURN_ERROR:
- Product recommendations
- Optional features
- Third-party integrations
- Cache misses (with fallback)

RETURN_NONE:
- Analytics/telemetry
- Logging
- Notifications
- Performance metrics

GOLDEN RULE:
The more critical the tool, the stricter the error handling!
""")
