"""
AI Conversation Engine for Real Estate Lead Qualification.
Uses Google Gemini via OpenAI-compatible endpoint (FREE).
Only needs GOOGLE_API_KEY - no other setup required.
"""

import json
import logging
import time
from typing import Dict, Tuple

from openai import OpenAI
import config

logger = logging.getLogger(__name__)

# System prompt for the real estate qualification agent
SYSTEM_PROMPT = f"""You are a friendly and professional real estate assistant named {config.AGENT_NAME}. You work for {config.COMPANY_NAME}. Your job is to qualify leads by having a natural conversation.

IMPORTANT RULES:
1. Be conversational, warm, and professional — never sound robotic or like a form
2. Ask ONE question at a time, don't overwhelm the user
3. Use the information they give you naturally in follow-up questions
4. If they seem hesitant, acknowledge their concerns and gently guide them
5. Handle objections gracefully (e.g., "just browsing" → "No pressure at all! I'm just here to help whenever you're ready.")
6. Keep responses concise (2-3 sentences max)

QUALIFICATION FIELDS TO GATHER (in natural order):
- Name (introduce yourself first, then ask)
- Budget range (be tactful — "What range are you comfortable with?")
- Location preferences (city, neighborhood, or area)
- Timeline (when they're looking to move/buy)
- Property type (apartment, house, villa, condo, etc.)
- Bedrooms and bathrooms needed
- Any special requirements (parking, garden, pool, pet-friendly, etc.)

LEAD SCORING:
After gathering enough info, internally assess the lead:
- HOT: Has budget, timeline within 3 months, clear preferences
- WARM: Has some info, timeline 3-6 months, somewhat flexible
- COLD: Just browsing, no clear timeline, very vague preferences

RESPONSE FORMAT:
You MUST always respond in this exact JSON format (no other text):
{{
    "message": "Your conversational response to the user",
    "extracted_data": {{
        "name": null,
        "budget_min": null,
        "budget_max": null,
        "currency": "USD",
        "location_preferences": null,
        "timeline": null,
        "property_type": null,
        "bedrooms": null,
        "bathrooms": null,
        "special_requirements": null
    }},
    "lead_score": "unknown",
    "qualification_complete": false,
    "summary": null
}}

RULES FOR extracted_data:
- Only fill in fields that the user has EXPLICITLY mentioned in this conversation
- Keep null for fields not yet discussed
- Update fields if the user changes their mind
- budget_min and budget_max should be numbers only (no currency symbols)
- lead_score should be "hot", "warm", "cold", or "unknown"
- Set qualification_complete to true only when you have at least: name, budget, location, timeline, and property type
- When qualification_complete is true, provide a brief summary of the lead in the "summary" field"""


def get_client() -> OpenAI:
    """
    Get the AI client. Priority:
    1. Google Gemini (FREE) - if GOOGLE_API_KEY is set
    2. OpenAI-compatible API - if OPENAI_API_KEY and OPENAI_API_BASE are set
    """
    if config.GOOGLE_API_KEY:
        # Use Google Gemini via OpenAI-compatible endpoint (FREE)
        return OpenAI(
            api_key=config.GOOGLE_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    elif config.OPENAI_API_BASE:
        return OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_API_BASE)
    else:
        return OpenAI(api_key=config.OPENAI_API_KEY)


def get_model_name() -> str:
    """Get the model name to use."""
    return config.AI_MODEL


def get_ai_response(conversation_history: list, user_message: str, max_retries: int = 3) -> Tuple[str, Dict]:
    """Get AI response for the conversation."""
    client = get_client()
    model = get_model_name()

    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conversation_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )

            response_text = response.choices[0].message.content.strip()
            return _parse_response(response_text)

        except Exception as e:
            logger.error(f"AI API call failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return (
                    "I apologize, I'm experiencing a brief technical issue. Could you please repeat that?",
                    {"extracted_data": {}, "lead_score": "unknown", "qualification_complete": False, "summary": None}
                )

    return _fallback_response()


def _parse_response(response_text: str) -> Tuple[str, Dict]:
    """Parse AI response text into message and metadata."""
    # Clean up markdown code blocks if present
    if "```" in response_text:
        lines = response_text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        response_text = "\n".join(lines)

    # Try to find JSON in the response (model sometimes adds text before/after)
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    if json_start != -1 and json_end > json_start:
        response_text = response_text[json_start:json_end]

    try:
        parsed = json.loads(response_text)
        ai_message = parsed.get("message", "I'm here to help! Could you tell me more about what you're looking for?")
        extracted_data = parsed.get("extracted_data", {})
        lead_score = parsed.get("lead_score", "unknown")
        qualification_complete = parsed.get("qualification_complete", False)
        summary = parsed.get("summary", None)

        logger.info(f"AI response parsed. Score: {lead_score}, Complete: {qualification_complete}")

        return ai_message, {
            "extracted_data": extracted_data,
            "lead_score": lead_score,
            "qualification_complete": qualification_complete,
            "summary": summary
        }
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse JSON: {response_text[:100]}")
        return response_text, {
            "extracted_data": {},
            "lead_score": "unknown",
            "qualification_complete": False,
            "summary": None
        }


def _fallback_response() -> Tuple[str, Dict]:
    """Return a fallback response."""
    return "How can I help you with your property search?", {
        "extracted_data": {},
        "lead_score": "unknown",
        "qualification_complete": False,
        "summary": None
    }


def get_initial_greeting() -> str:
    """Get the initial greeting message."""
    return (
        f"Hi there! 👋 I'm {config.AGENT_NAME}, your real estate assistant from {config.COMPANY_NAME}.\n\n"
        f"I'd love to help you find your perfect property! Whether you're looking to buy, "
        f"rent, or just exploring options, I'm here to help.\n\n"
        f"What brings you here today?"
    )
