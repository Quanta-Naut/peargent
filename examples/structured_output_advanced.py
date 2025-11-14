"""
Advanced Structured Output Examples

Demonstrates validation, error handling, and practical use cases.
"""

import json
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from peargent import create_agent
from peargent.models import groq

# ===== EXAMPLE 1: Custom Validation =====
print("=" * 80)
print("EXAMPLE 1: Custom Field Validation")
print("=" * 80 + "\n")

class EmailCampaign(BaseModel):
    subject: str = Field(description="Email subject line", min_length=5, max_length=100)
    body: str = Field(description="Email body content", min_length=20)
    target_segment: Literal["new_users", "active_users", "premium_users"] = Field(
        description="Target audience segment"
    )
    cta_button: str = Field(description="Call-to-action button text", max_length=30)
    estimated_open_rate: float = Field(description="Estimated open rate", ge=0.0, le=1.0)

    @field_validator('subject')
    @classmethod
    def subject_must_not_have_spam_words(cls, v):
        """Subject must not contain spam-triggering words: 'free', 'click here', 'buy now', 'limited time'"""
        spam_words = ['free', 'click here', 'buy now', 'limited time']
        if any(word in v.lower() for word in spam_words):
            raise ValueError('Subject contains spam-triggering words')
        return v

agent = create_agent(
    name="EmailMarketer",
    description="Creates email marketing campaigns",
    persona="You are an email marketing expert. Create engaging, non-spammy campaigns.",
    model=groq("llama-3.3-70b-versatile"),
    output_schema=EmailCampaign,
    max_retries=3
)

campaign = agent.run("Create an email campaign to promote our new premium features to active users")

print(f"Subject: {campaign.subject}")
print(f"Target: {campaign.target_segment}")
print(f"CTA: {campaign.cta_button}")
print(f"Estimated Open Rate: {campaign.estimated_open_rate * 100:.1f}%")
print(f"\nBody:\n{campaign.body[:200]}...")

print("\n" + "=" * 80 + "\n")

# ===== EXAMPLE 2: Optional Fields =====
print("EXAMPLE 2: Optional Fields and Defaults")
print("=" * 80 + "\n")

class TaskPlan(BaseModel):
    title: str = Field(description="Task title")
    description: str = Field(description="Task description")
    priority: Literal["low", "medium", "high", "urgent"] = Field(default="medium")
    estimated_hours: Optional[float] = Field(default=None, description="Estimated hours to complete")
    dependencies: List[str] = Field(default_factory=list, description="List of dependencies")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")

agent = create_agent(
    name="TaskPlanner",
    description="Creates task plans",
    persona="You are a project manager who creates detailed task plans.",
    model=groq("llama-3.3-70b-versatile"),
    output_schema=TaskPlan
)

task = agent.run("Create a task plan for implementing user authentication")

print(f"Task: {task.title}")
print(f"Priority: {task.priority}")
print(f"Estimated Hours: {task.estimated_hours or 'Not estimated'}")
print(f"Description: {task.description}")
print(f"Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}")
print(f"Tags: {', '.join(task.tags) if task.tags else 'None'}")

print("\n" + "=" * 80 + "\n")

# ===== EXAMPLE 3: Error Handling =====
print("EXAMPLE 3: Validation and Error Handling")
print("=" * 80 + "\n")

class StrictRating(BaseModel):
    score: int = Field(description="Rating score", ge=1, le=5)
    review: str = Field(description="Review text", min_length=10, max_length=500)
    verified_purchase: bool = Field(description="Whether this is a verified purchase")

agent = create_agent(
    name="Reviewer",
    description="Creates product reviews",
    persona="You are a product reviewer.",
    model=groq("llama-3.3-70b-versatile"),
    output_schema=StrictRating,
    max_retries=3  # Will retry up to 3 times if validation fails
)

try:
    rating = agent.run("Review this product: Great headphones, very comfortable")
    print(f"Score: {rating.score}/5")
    print(f"Verified: {rating.verified_purchase}")
    print(f"Review: {rating.review}")
    print("\nValidation: SUCCESS")
except ValueError as e:
    print(f"Validation: FAILED - {e}")

print("\n" + "=" * 80 + "\n")

# ===== EXAMPLE 4: Serialization =====
print("EXAMPLE 4: Serialization and Integration")
print("=" * 80 + "\n")

class APIResponse(BaseModel):
    status: Literal["success", "error"] = Field(description="Response status")
    message: str = Field(description="Response message")
    data: dict = Field(description="Response data")
    timestamp: str = Field(description="ISO timestamp")

agent = create_agent(
    name="APIGenerator",
    description="Generates API responses",
    persona="You are an API response generator.",
    model=groq("llama-3.3-70b-versatile"),
    output_schema=APIResponse
)

api_response = agent.run("Generate a success response for user login with user ID 12345")

print("Pydantic Model:")
print(f"  status: {api_response.status}")
print(f"  message: {api_response.message}")

print("\nAs Dictionary:")
response_dict = api_response.model_dump()
print(f"  {response_dict}")

print("\nAs JSON:")
response_json = api_response.model_dump_json(indent=2)
print(response_json)

print("\nUse Cases:")
print("  - Return from FastAPI endpoints")
print("  - Store in database")
print("  - Send to message queue")
print("  - Cache in Redis")
print("  - Log to file")

print("\n" + "=" * 80)
print("KEY TAKEAWAYS")
print("=" * 80)
print("""
1. VALIDATION
   - Field constraints (min/max, ge/le)
   - Custom validators with @field_validator
   - Literal types for enums
   - Automatic retry on validation failure

2. FLEXIBILITY
   - Optional fields with defaults
   - Complex nested structures
   - Lists and arrays
   - Type unions

3. RELIABILITY
   - max_retries parameter controls retry attempts
   - Clear error messages on failure
   - Guaranteed data quality

4. INTEGRATION
   - model_dump() for dictionaries
   - model_dump_json() for JSON
   - Direct database ORM mapping
   - API response generation

5. PRODUCTION READY
   - Type-safe code
   - No parsing errors
   - Consistent output format
   - Easy to test and maintain
""")
