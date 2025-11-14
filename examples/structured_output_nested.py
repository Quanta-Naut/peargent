"""
Nested Structured Output Example

Demonstrates complex nested Pydantic models for advanced use cases.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from peargent import create_agent
from peargent.models import groq

# Define nested models
class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class PhoneNumber(BaseModel):
    type: str = Field(description="Type: mobile, home, or work")
    number: str

class Person(BaseModel):
    name: str = Field(description="Full name")
    age: int = Field(description="Age in years", ge=0, le=150)
    email: str = Field(description="Email address")
    address: Address = Field(description="Residential address")
    phone_numbers: List[PhoneNumber] = Field(description="List of phone numbers")
    occupation: str = Field(description="Current occupation")
    hobbies: List[str] = Field(description="List of hobbies")
    bio: str = Field(description="Short biography")

# Create agent
agent = create_agent(
    name="ProfileExtractor",
    description="Extracts structured person information",
    persona="You are an expert at extracting and structuring person information.",
    model=groq("llama-3.3-70b-versatile"),
    output_schema=Person,
    tracing=True
)

print("=" * 80)
print("NESTED STRUCTURED OUTPUT - Person Profile")
print("=" * 80 + "\n")

# Query with unstructured text
query = """
Create a profile for: John Smith is a 34-year-old software engineer living in
San Francisco. His email is john.smith@example.com. He lives at 123 Market Street,
San Francisco, CA 94102. You can reach him on his mobile at 415-555-1234 or his
work phone at 415-555-5678. In his free time, he enjoys hiking, photography, and
playing guitar. John has been working in tech for over 10 years, specializing in
distributed systems and cloud architecture.
"""

# Run agent - returns Person instance with nested models!
person = agent.run(query)

print("Type:", type(person))
print("=" * 80 + "\n")

# Access nested fields with type safety
print(f"Name: {person.name}")
print(f"Age: {person.age}")
print(f"Email: {person.email}")
print(f"Occupation: {person.occupation}")

print(f"\nAddress:")
print(f"  {person.address.street}")
print(f"  {person.address.city}, {person.address.state} {person.address.zip_code}")

print(f"\nPhone Numbers:")
for phone in person.phone_numbers:
    print(f"  {phone.type}: {phone.number}")

print(f"\nHobbies:")
for hobby in person.hobbies:
    print(f"  - {hobby}")

print(f"\nBio:\n{person.bio}")

print("\n" + "=" * 80)

# Convert to dict or JSON
person_dict = person.model_dump()
person_json = person.model_dump_json(indent=2)

print("As Dictionary:")
print(f"Keys: {list(person_dict.keys())}")
print(f"\nAs JSON (first 200 chars):\n{person_json[:200]}...")

print("\n" + "=" * 80)
print("NESTED MODELS - KEY BENEFITS")
print("=" * 80)
print("""
1. COMPLEX STRUCTURES
   - Nested objects (Address, PhoneNumber)
   - Arrays of nested objects
   - Optional fields supported

2. FULL VALIDATION
   - Each nested model validated independently
   - Type checking at all levels
   - Constraint validation (age 0-150)

3. CLEAN CODE
   person.address.city           # No dict lookups
   person.phone_numbers[0].type  # Type-safe nested access

4. EASY SERIALIZATION
   person.model_dump()       # Convert entire tree to dict
   person.model_dump_json()  # Convert to JSON string

5. PERFECT FOR
   - API responses
   - Database records
   - Complex data extraction
   - Multi-step workflows
""")
