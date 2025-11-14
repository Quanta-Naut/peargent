"""
Structured Output Comparison

Shows the difference between agents with and without structured output.
"""

import json
from pydantic import BaseModel, Field
from peargent import create_agent, enable_tracing
from peargent.models import groq

# Define structured output schema
class ProductAnalysis(BaseModel):
    product_name: str = Field(description="Name of the product")
    category: str = Field(description="Product category")
    price_range: str = Field(description="Price range (budget/mid-range/premium)")
    features: list[str] = Field(description="Key features")
    target_audience: str = Field(description="Target audience")
    rating: int = Field(description="Rating from 1-10", ge=1, le=10)

# Enable tracing
tracer = enable_tracing()

print("=" * 80)
print("COMPARISON: WITH vs WITHOUT STRUCTURED OUTPUT")
print("=" * 80 + "\n")

# Query
query = "Analyze the iPhone 15 Pro as a product"

# ===== WITHOUT STRUCTURED OUTPUT =====
print("1. WITHOUT STRUCTURED OUTPUT (Regular Agent)")
print("-" * 80 + "\n")

agent_regular = create_agent(
    name="RegularAnalyst",
    description="Product analyst",
    persona="You are a product analyst. Provide analysis in a clear format.",
    model=groq("llama-3.3-70b-versatile"),
    tracing=True
)

response_regular = agent_regular.run(query)
print(f"Response type: {type(response_regular)}")
print(f"Response:\n{response_regular}\n")

print("Problems:")
print("  - Returns unstructured string")
print("  - Manual parsing needed")
print("  - No type safety")
print("  - Inconsistent format")
print("  - Risk of parsing errors")

print("\n" + "=" * 80 + "\n")

# ===== WITH STRUCTURED OUTPUT =====
print("2. WITH STRUCTURED OUTPUT (Schema-Validated Agent)")
print("-" * 80 + "\n")

agent_structured = create_agent(
    name="StructuredAnalyst",
    description="Product analyst with structured output",
    persona="You are a product analyst who provides structured analysis.",
    model=groq("llama-3.3-70b-versatile"),
    output_schema=ProductAnalysis,
    tracing=True
)

response_structured = agent_structured.run(query)
print(f"Response type: {type(response_structured)}")
print(f"\nProduct: {response_structured.product_name}")
print(f"Category: {response_structured.category}")
print(f"Price Range: {response_structured.price_range}")
print(f"Rating: {response_structured.rating}/10")
print(f"Target Audience: {response_structured.target_audience}")
print(f"\nFeatures:")
for feature in response_structured.features:
    print(f"  - {feature}")

print("\nBenefits:")
print("  + Returns typed Pydantic model")
print("  + No parsing needed")
print("  + Type-safe field access")
print("  + Guaranteed consistent format")
print("  + Auto-validation and retry")

print("\n" + "=" * 80)
print("CODE COMPARISON")
print("=" * 80)

print("""
WITHOUT STRUCTURED OUTPUT:
    response = agent.run("Analyze product")
    # Response is string, need manual parsing
    data = json.loads(response)  # May fail!
    name = data.get("product_name", "Unknown")  # No type safety
    rating = int(data.get("rating", 0))  # Manual conversion

WITH STRUCTURED OUTPUT:
    response = agent.run("Analyze product")
    # Response is ProductAnalysis model
    name = response.product_name  # Type-safe, autocomplete works
    rating = response.rating      # Already an int, validated 1-10
    # No parsing, no errors, just works!
""")

print("\n" + "=" * 80)
print("WHEN TO USE STRUCTURED OUTPUT")
print("=" * 80)
print("""
USE STRUCTURED OUTPUT WHEN:
  - Building production APIs
  - Need reliable, consistent data format
  - Want type safety and validation
  - Integrating with databases
  - Building complex workflows
  - Need to chain multiple agents

USE REGULAR OUTPUT WHEN:
  - Building simple chatbots
  - Want natural language responses
  - Don't need structured data
  - Prototyping quickly
""")

print("\n" + "=" * 80)
print("TRACING SUMMARY")
print("=" * 80 + "\n")

tracer.print_summary()
