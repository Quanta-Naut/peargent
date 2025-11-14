"""
Test: Field Validators Included in Schema

Demonstrates that custom field validators are now included in the JSON schema
sent to the LLM, while still maintaining validation as a safety net.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal
from peargent import create_agent
from peargent.models import groq

# Define model with custom validators (WITH DOCSTRINGS!)
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

    @field_validator('cta_button')
    @classmethod
    def cta_must_be_action_oriented(cls, v):
        """CTA button must start with an action verb (e.g., 'Get', 'Try', 'Start', 'Upgrade', 'Learn')"""
        action_verbs = ['get', 'try', 'start', 'upgrade', 'learn', 'join', 'discover', 'explore', 'unlock']
        if not any(v.lower().startswith(verb) for verb in action_verbs):
            raise ValueError('CTA button must start with an action verb')
        return v


print("=" * 80)
print("TESTING: Field Validators in JSON Schema")
print("=" * 80 + "\n")

# First, let's see what the enhanced schema looks like
print("1. Enhanced JSON Schema (sent to LLM):")
print("-" * 80)

import json
agent = create_agent(
    name="EmailMarketer",
    description="Creates email marketing campaigns",
    persona="You are an email marketing expert who creates engaging campaigns.",
    model=groq("llama-3.3-70b-versatile"),
    output_schema=EmailCampaign,
    max_retries=3
)

# Get the JSON schema that's sent to the LLM
json_schema = agent._get_json_schema()
schema_dict = json.loads(json_schema)

# Show subject field with validation rules
print("\nSubject field schema:")
print(json.dumps(schema_dict['properties']['subject'], indent=2))

print("\nCTA button field schema:")
print(json.dumps(schema_dict['properties']['cta_button'], indent=2))

print("\n" + "=" * 80 + "\n")

# Now test the agent
print("2. Testing Agent with Validator-Enhanced Schema:")
print("-" * 80 + "\n")

campaign = agent.run("Create an email campaign to promote our new premium features to active users")

print("RESULT:")
print(f"Subject: {campaign.subject}")
print(f"CTA Button: {campaign.cta_button}")
print(f"Target Segment: {campaign.target_segment}")
print(f"Estimated Open Rate: {campaign.estimated_open_rate * 100:.1f}%")
print(f"\nBody Preview:\n{campaign.body[:200]}...")

print("\n" + "=" * 80 + "\n")

# Verify validation still works
print("3. Validation Safety Net Still Active:")
print("-" * 80 + "\n")

from pydantic import ValidationError

# Test 1: Try to create with spam words (should fail)
print("Test 1: Creating campaign with spam words...")
try:
    bad_campaign = EmailCampaign(
        subject="Free Premium Features - Buy Now!",  # Contains spam words
        body="This is a great offer you shouldn't miss",
        target_segment="active_users",
        cta_button="Get Started",
        estimated_open_rate=0.3
    )
    print("  ERROR: Should have failed but didn't!")
except ValidationError as e:
    print(f"  SUCCESS: Validation caught spam words [PASS]")
    print(f"  Error: {e.errors()[0]['msg']}")

print()

# Test 2: Try to create with bad CTA (should fail)
print("Test 2: Creating campaign with non-action CTA...")
try:
    bad_campaign = EmailCampaign(
        subject="Premium Features Available",
        body="This is a great offer you shouldn't miss",
        target_segment="active_users",
        cta_button="More Info",  # Doesn't start with action verb
        estimated_open_rate=0.3
    )
    print("  ERROR: Should have failed but didn't!")
except ValidationError as e:
    print(f"  SUCCESS: Validation caught bad CTA [PASS]")
    print(f"  Error: {e.errors()[0]['msg']}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
HOW IT WORKS NOW:

1. VALIDATORS IN SCHEMA (NEW!)
   - Field validators are extracted from Pydantic model
   - Validator docstrings added to field descriptions
   - LLM sees validation rules BEFORE generating response
   - Reduces wasted tokens on invalid attempts

2. VALIDATION SAFETY NET (KEPT!)
   - Pydantic validation still runs on LLM response
   - Catches any responses that violate rules
   - Auto-retry with error feedback (up to max_retries)
   - Guarantees output quality

3. BENEFITS:
   + LLM knows constraints upfront => Better first attempts
   + Validation catches mistakes => Guaranteed correctness
   + Clear error messages => Easy debugging
   + Two layers of protection => Production-ready

BEST PRACTICE:
- Add descriptive docstrings to your @field_validator methods
- These docstrings are sent to the LLM as validation rules
- Keep validators as safety net for reliability
""")
