"""Quick test to verify the AI engine works end-to-end."""

import sys
sys.path.insert(0, '.')

from ai_engine import get_ai_response, get_initial_greeting
import config

print(f"Testing AI Engine with model: {config.AI_MODEL}")
print("=" * 50)

# Test 1: Initial greeting
greeting = get_initial_greeting()
print(f"\n✅ Greeting: {greeting[:80]}...")

# Test 2: First conversation turn
conversation = [{"role": "assistant", "content": greeting}]
user_msg = "Hi, I'm looking to buy a house in Miami"

print(f"\n👤 User: {user_msg}")
response, metadata = get_ai_response(conversation, user_msg)
print(f"🤖 AI: {response}")
print(f"   Extracted: {metadata.get('extracted_data', {})}")
print(f"   Score: {metadata.get('lead_score')}")

# Test 3: Follow-up
conversation.append({"role": "user", "content": user_msg})
conversation.append({"role": "assistant", "content": response})

user_msg2 = "My budget is around 500k to 700k, and I need 3 bedrooms"
print(f"\n👤 User: {user_msg2}")
response2, metadata2 = get_ai_response(conversation, user_msg2)
print(f"🤖 AI: {response2}")
print(f"   Extracted: {metadata2.get('extracted_data', {})}")
print(f"   Score: {metadata2.get('lead_score')}")

print("\n" + "=" * 50)
print("✅ AI Engine test PASSED - All responses working!")
