"""
Tool Retry and Exponential Backoff Demonstration

Shows how tools automatically retry on failure with configurable backoff strategies.
"""

import time
import random
from peargent import create_tool

print("=" * 80)
print("TOOL RETRY AND EXPONENTIAL BACKOFF DEMONSTRATION")
print("=" * 80 + "\n")

# Simulate a flaky API that sometimes fails
attempt_count = {"count": 0}

def flaky_api(endpoint: str) -> str:
    """Simulates an API that fails randomly"""
    attempt_count["count"] += 1
    current_attempt = attempt_count["count"]

    print(f"  [Attempt {current_attempt}] Calling API: {endpoint}")

    # 60% chance of failure
    if random.random() < 0.6:
        print(f"  [Attempt {current_attempt}] FAILED - API returned 503 Service Unavailable")
        raise Exception("API Error: 503 Service Unavailable")

    print(f"  [Attempt {current_attempt}] SUCCESS!")
    return f"Data from {endpoint}"

# Test 1: No retries - fails on first attempt
print("Test 1: No Retries (Default)")
print("-" * 80)

attempt_count["count"] = 0
tool_no_retry = create_tool(
    name="flaky_api_no_retry",
    description="Flaky API without retries",
    input_parameters={"endpoint": str},
    call_function=flaky_api,
    on_error="return_error"  # Don't crash, return error
)

result = tool_no_retry.run({"endpoint": "/users"})
print(f"\nResult: {result}")
print(f"Total attempts: {attempt_count['count']}\n")

# Test 2: With retries - keeps trying until success
print("Test 2: With Retries (max_retries=5)")
print("-" * 80)

attempt_count["count"] = 0
tool_with_retry = create_tool(
    name="flaky_api_with_retry",
    description="Flaky API with retries",
    input_parameters={"endpoint": str},
    call_function=flaky_api,
    max_retries=5,           # Try up to 5 times
    retry_delay=0.5,         # Wait 0.5s between retries
    retry_backoff=False,     # Fixed delay
    on_error="return_error"
)

start = time.time()
result = tool_with_retry.run({"endpoint": "/products"})
elapsed = time.time() - start

print(f"\nResult: {result}")
print(f"Total attempts: {attempt_count['count']}")
print(f"Time taken: {elapsed:.2f}s\n")

# Test 3: Exponential backoff - increasing delays
print("Test 3: Exponential Backoff")
print("-" * 80)
print("Delays: 1s, 2s, 4s, 8s (exponentially increasing)\n")

def failing_service(x: str) -> str:
    """Always fails to demonstrate backoff timing"""
    raise Exception("Service temporarily unavailable")

tool_exponential = create_tool(
    name="service_exponential",
    description="Service with exponential backoff",
    input_parameters={"x": str},
    call_function=failing_service,
    max_retries=3,
    retry_delay=1.0,        # Start with 1s
    retry_backoff=True,     # Enable exponential backoff
    on_error="return_error"
)

start = time.time()
result = tool_exponential.run({"x": "test"})
elapsed = time.time() - start

print(f"\nResult: {result}")
print(f"Time taken: {elapsed:.2f}s")
print(f"Expected: ~15s (1s + 2s + 4s + 8s)")
print("Actual delays increased exponentially!\n")

# Test 4: Fixed delay vs Exponential backoff comparison
print("Test 4: Fixed vs Exponential Backoff Comparison")
print("-" * 80)

print("\nFIXED DELAY (retry_backoff=False):")
print("Attempt 1: Immediate")
print("Attempt 2: Wait 1s")
print("Attempt 3: Wait 1s (same)")
print("Attempt 4: Wait 1s (same)")
print("Total delay: 3s")

print("\nEXPONENTIAL BACKOFF (retry_backoff=True):")
print("Attempt 1: Immediate")
print("Attempt 2: Wait 1s  (1 * 2^0)")
print("Attempt 3: Wait 2s  (1 * 2^1)")
print("Attempt 4: Wait 4s  (1 * 2^2)")
print("Total delay: 7s")

# Test 5: Retry with timeout
print("\n" + "-" * 80)
print("Test 5: Retry + Timeout Combined")
print("-" * 80)

def slow_and_flaky(x: str) -> str:
    """Sometimes slow, sometimes fails"""
    if random.random() < 0.3:
        print("  [Tool] Hanging (simulating timeout)...")
        time.sleep(5)  # Simulate hang
        return "Success"
    else:
        print("  [Tool] Failing (simulating error)...")
        raise Exception("Random failure")

tool_combined = create_tool(
    name="slow_flaky_tool",
    description="Slow and flaky tool",
    input_parameters={"x": str},
    call_function=slow_and_flaky,
    timeout=2.0,           # Timeout after 2s
    max_retries=3,         # Retry 3 times
    retry_delay=0.5,
    on_error="return_error"
)

result = tool_combined.run({"x": "test"})
print(f"\nResult: {result}")
print("Tool will retry on both timeouts AND errors!\n")

print("=" * 80)
print("RETRY STRATEGIES SUMMARY")
print("=" * 80)
print("""
WHEN TO USE RETRIES:

1. FLAKY APIS
   - External services that occasionally fail
   - Network timeouts
   - Rate limiting (with backoff)

2. TRANSIENT ERRORS
   - Database connection issues
   - Temporary service unavailability
   - Resource contention

BACKOFF STRATEGIES:

1. FIXED DELAY
   retry_backoff=False
   - Same delay between all retries
   - Predictable timing
   - Use: Stable services, testing

2. EXPONENTIAL BACKOFF
   retry_backoff=True
   - Delay doubles each retry: 1s, 2s, 4s, 8s...
   - Reduces server load
   - Use: Production APIs, rate-limited services

CONFIGURATION:

# Conservative (quick retries)
max_retries=2, retry_delay=0.5, retry_backoff=False

# Moderate (balanced)
max_retries=3, retry_delay=1.0, retry_backoff=True

# Aggressive (many retries, long waits)
max_retries=5, retry_delay=2.0, retry_backoff=True

BEST PRACTICES:
- Use exponential backoff for production
- Don't retry on authentication errors (they won't change)
- Log retry attempts for monitoring
- Set max_retries based on acceptable latency
""")
