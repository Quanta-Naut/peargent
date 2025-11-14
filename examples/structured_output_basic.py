"""
Basic Structured Output Example

Demonstrates how to use Pydantic models to get type-safe, validated responses.
"""

from pydantic import BaseModel, Field
from peargent import create_agent
from peargent.models import groq

# Define your output schema
class MovieReview(BaseModel):
    title: str = Field(description="Movie title")
    rating: int = Field(description="Rating from 1-10", ge=1, le=10)
    summary: str = Field(description="Brief summary of the movie")
    pros: list[str] = Field(description="List of positive aspects")
    cons: list[str] = Field(description="List of negative aspects")
    recommended: bool = Field(description="Whether you recommend this movie")


# Create agent with structured output
agent = create_agent(
    name="MovieCritic",
    description="A professional movie critic",
    persona="You are a professional movie critic who provides detailed, honest reviews.",
    model=groq("llama-3.3-70b-versatile"),
    output_schema=MovieReview,  # Enforce structured output
    tracing=True
)

print("=" * 80)
print("STRUCTURED OUTPUT EXAMPLE - Movie Review")
print("=" * 80 + "\n")

# Run agent - returns MovieReview instance, not string!
review = agent.run("Review the movie Inception (2010)")

print("Type:", type(review))
print("=" * 80 + "\n")

# Access fields with type safety
print(f"Title: {review.title}")
print(f"Rating: {review.rating}/10")
print(f"Recommended: {review.recommended}")
print(f"\nSummary:\n{review.summary}")
print(f"\nPros:")
for pro in review.pros:
    print(f"  + {pro}")
print(f"\nCons:")
for con in review.cons:
    print(f"  - {con}")

print("\n" + "=" * 80)
print("BENEFITS OF STRUCTURED OUTPUT")
print("=" * 80)
print("""
1. TYPE SAFETY
   - Returns Pydantic model, not string
   - IDE autocomplete and type checking
   - No manual parsing needed

2. VALIDATION
   - Automatically validates against schema
   - Field constraints enforced (e.g., rating 1-10)
   - Clear error messages on invalid data

3. RELIABILITY
   - Auto-retry on malformed responses (up to max_retries)
   - Guaranteed JSON format
   - No parsing errors in production

4. EASY TO USE
   review.title          # Direct field access
   review.rating         # Type-safe integers
   review.recommended    # Boolean, not string "true"

5. SERIALIZATION
   review.model_dump()        # Convert to dict
   review.model_dump_json()   # Convert to JSON string
""")
