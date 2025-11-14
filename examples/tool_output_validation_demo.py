"""
Tool Output Validation with Pydantic

Demonstrates how to validate tool outputs using Pydantic schemas for type safety.
"""

from pydantic import BaseModel, Field
from peargent import create_tool

print("=" * 80)
print("TOOL OUTPUT VALIDATION WITH PYDANTIC")
print("=" * 80 + "\n")

# Define Pydantic schemas for tool outputs

class WeatherData(BaseModel):
    """Schema for weather tool output"""
    temperature: float = Field(description="Temperature in Fahrenheit")
    condition: str = Field(description="Weather condition")
    humidity: int = Field(description="Humidity percentage", ge=0, le=100)
    wind_speed: float = Field(description="Wind speed in mph", ge=0)

class UserProfile(BaseModel):
    """Schema for user profile tool output"""
    user_id: int
    name: str
    email: str
    age: int = Field(ge=0, le=150)
    premium: bool

# Test 1: Tool with valid output
print("Test 1: Valid Output - Passes Validation")
print("-" * 80)

def get_weather_valid(city: str) -> dict:
    """Returns valid weather data"""
    return {
        "temperature": 72.5,
        "condition": "Sunny",
        "humidity": 45,
        "wind_speed": 10.2
    }

weather_tool = create_tool(
    name="get_weather",
    description="Get weather data for a city",
    input_parameters={"city": str},
    call_function=get_weather_valid,
    output_schema=WeatherData  # Validate output
)

result = weather_tool.run({"city": "San Francisco"})
print(f"Result type: {type(result)}")
print(f"Result: {result}")
print(f"\nAccess fields with type safety:")
print(f"  Temperature: {result.temperature}°F")
print(f"  Condition: {result.condition}")
print(f"  Humidity: {result.humidity}%")
print(f"  Wind: {result.wind_speed} mph")
print("\nValidation: PASSED\n")

# Test 2: Tool with invalid output (wrong type)
print("Test 2: Invalid Output - Type Error")
print("-" * 80)

def get_weather_invalid(city: str) -> dict:
    """Returns invalid weather data"""
    return {
        "temperature": "seventy two",  # Should be float!
        "condition": "Sunny",
        "humidity": 45,
        "wind_speed": 10.2
    }

weather_tool_invalid = create_tool(
    name="get_weather_invalid",
    description="Get weather (returns bad data)",
    input_parameters={"city": str},
    call_function=get_weather_invalid,
    output_schema=WeatherData,
    on_error="return_error"  # Gracefully handle validation error
)

result = weather_tool_invalid.run({"city": "Boston"})
print(f"Result: {result}")
print("Validation failed and returned error message!\n")

# Test 3: Tool with missing required field
print("Test 3: Invalid Output - Missing Field")
print("-" * 80)

def get_weather_incomplete(city: str) -> dict:
    """Returns incomplete weather data"""
    return {
        "temperature": 68.0,
        "condition": "Cloudy"
        # Missing: humidity, wind_speed
    }

weather_tool_incomplete = create_tool(
    name="get_weather_incomplete",
    description="Get weather (missing fields)",
    input_parameters={"city": str},
    call_function=get_weather_incomplete,
    output_schema=WeatherData,
    on_error="return_error"
)

result = weather_tool_incomplete.run({"city": "Chicago"})
print(f"Result: {result}")
print("Missing fields detected by validation!\n")

# Test 4: Tool with constraint violation
print("Test 4: Invalid Output - Constraint Violation")
print("-" * 80)

def get_weather_constraints(city: str) -> dict:
    """Returns data violating constraints"""
    return {
        "temperature": 72.0,
        "condition": "Sunny",
        "humidity": 150,  # Invalid! Must be 0-100
        "wind_speed": -5   # Invalid! Must be >= 0
    }

weather_tool_constraints = create_tool(
    name="get_weather_constraints",
    description="Get weather (violates constraints)",
    input_parameters={"city": str},
    call_function=get_weather_constraints,
    output_schema=WeatherData,
    on_error="return_error"
)

result = weather_tool_constraints.run({"city": "Miami"})
print(f"Result: {result}")
print("Constraint violations caught!\n")

# Test 5: Complex nested schema
print("Test 5: Complex Nested Schema")
print("-" * 80)

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class CompleteUserProfile(BaseModel):
    user_id: int
    name: str
    email: str
    address: Address  # Nested schema
    tags: list[str]

def get_user_profile(user_id: str) -> dict:
    """Returns complete user profile with nested data"""
    return {
        "user_id": 12345,
        "name": "John Doe",
        "email": "john@example.com",
        "address": {
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94102"
        },
        "tags": ["premium", "verified", "active"]
    }

user_tool = create_tool(
    name="get_user_profile",
    description="Get complete user profile",
    input_parameters={"user_id": str},
    call_function=get_user_profile,
    output_schema=CompleteUserProfile
)

result = user_tool.run({"user_id": "12345"})
print(f"Result type: {type(result)}")
print(f"User: {result.name}")
print(f"Email: {result.email}")
print(f"Address: {result.address.street}, {result.address.city}, {result.address.state}")
print(f"Tags: {', '.join(result.tags)}")
print("\nNested validation: PASSED\n")

print("=" * 80)
print("OUTPUT VALIDATION BENEFITS")
print("=" * 80)
print("""
WHY VALIDATE TOOL OUTPUTS?

1. TYPE SAFETY
   - Guarantees correct data types
   - Prevents runtime type errors
   - IDE autocomplete works

2. DATA QUALITY
   - Ensures required fields exist
   - Validates constraints (min/max, ranges)
   - Catches malformed API responses

3. EARLY ERROR DETECTION
   - Fails at tool level, not later
   - Clear error messages
   - Easier debugging

4. SELF-DOCUMENTING
   - Schema describes expected output
   - Clear contracts between tools
   - Better code maintainability

WHEN TO USE:

+ External API calls (validate API responses)
+ Database queries (validate data structure)
+ User input processing (validate before use)
+ Critical business logic (ensure correctness)
+ Complex data structures (nested objects/arrays)

WHEN NOT TO USE:

- Simple string/int returns
- Trusted internal functions
- Performance-critical paths (validation overhead)
- Prototyping (add later)

EXAMPLE USAGE:

class ToolOutput(BaseModel):
    field1: str
    field2: int
    field3: list[str]

tool = create_tool(
    name="my_tool",
    ...,
    output_schema=ToolOutput  # Validates every call
)

result = tool.run(args)
# result is now a validated ToolOutput instance!
# Access with type safety: result.field1, result.field2, etc.

BEST PRACTICE:
- Define schemas for all external tool integrations
- Use constraints (ge, le, min_length, etc.) for validation rules
- Combine with on_error="return_error" for graceful failures
- Use nested schemas for complex data structures
""")
