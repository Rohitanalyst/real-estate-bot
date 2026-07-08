"""
Main entry point for the Real Estate Lead Qualification Agent.
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        🏠 Real Estate Lead Qualification Agent 🏠           ║
║                                                              ║
║   AI-powered lead qualification for WhatsApp & Telegram      ║
║   Powered by Gemini 3 Flash (FREE) via OpenAI API           ║
╚══════════════════════════════════════════════════════════════╝
    """)


def main():
    print_banner()

    if len(sys.argv) < 2:
        print("Usage: python main.py [telegram|whatsapp|admin|demo]")
        print()
        print("  telegram  - Start Telegram bot (needs TELEGRAM_BOT_TOKEN)")
        print("  whatsapp  - Start WhatsApp webhook server")
        print("  admin     - Start Admin API server")
        print("  demo      - Run interactive demo in terminal (works immediately!)")
        print()
        print("Quick start:")
        print("  python main.py demo")
        print()
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "telegram":
        from telegram_bot import run_telegram_bot
        run_telegram_bot()

    elif mode == "whatsapp":
        from whatsapp_bot import run_whatsapp_bot
        run_whatsapp_bot()

    elif mode == "admin":
        from admin_api import run_admin_api
        run_admin_api()

    elif mode == "demo":
        run_demo()

    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


def run_demo():
    """Run an interactive demo in the terminal with live AI."""
    import config
    from database import get_or_create_lead, update_lead, get_lead_summary
    from ai_engine import get_ai_response, get_initial_greeting

    print(f"\n🎮 LIVE DEMO - Chat with {config.AGENT_NAME} from {config.COMPANY_NAME}")
    print(f"   Model: {config.AI_MODEL}")
    print("=" * 55)
    print("   Type your messages naturally. Commands:")
    print("   'quit'   - Exit")
    print("   'status' - See your lead profile")
    print("   'reset'  - Start over")
    print("=" * 55)

    chat_id = "demo_user"
    lead = get_or_create_lead(chat_id, platform="demo")
    conversation_history = lead.get("conversation_history", [])

    # Initial greeting
    greeting = get_initial_greeting()
    print(f"\n🤖 {config.AGENT_NAME}: {greeting}\n")
    conversation_history.append({"role": "assistant", "content": greeting})
    update_lead(chat_id, conversation_history=conversation_history)

    while True:
        try:
            user_input = input("👤 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("\n👋 Thanks for chatting! Goodbye!")
            break

        if user_input.lower() == "status":
            summary = get_lead_summary(chat_id)
            print(f"\n{summary}\n")
            continue

        if user_input.lower() == "reset":
            conversation_history = []
            update_lead(
                chat_id, conversation_history=[], status="in_progress",
                lead_score="unknown", budget_min=None, budget_max=None,
                location_preferences=None, timeline=None, property_type=None,
                bedrooms=None, bathrooms=None, special_requirements=None, summary=None
            )
            greeting = get_initial_greeting()
            conversation_history.append({"role": "assistant", "content": greeting})
            print(f"\n🔄 Reset!\n\n🤖 {config.AGENT_NAME}: {greeting}\n")
            continue

        # Get AI response
        print(f"\n🤖 {config.AGENT_NAME}: ", end="", flush=True)
        ai_message, metadata = get_ai_response(conversation_history, user_input)
        print(f"{ai_message}\n")

        # Update conversation
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": ai_message})

        # Update database
        update_data = {"conversation_history": conversation_history}
        extracted = metadata.get("extracted_data", {})
        if extracted:
            for field in ["name", "budget_min", "budget_max", "currency",
                         "location_preferences", "timeline", "property_type",
                         "bedrooms", "bathrooms", "special_requirements"]:
                value = extracted.get(field)
                if value is not None:
                    update_data[field] = value

        lead_score = metadata.get("lead_score", "unknown")
        if lead_score != "unknown":
            update_data["lead_score"] = lead_score

        if metadata.get("qualification_complete"):
            update_data["status"] = "qualified"
            if metadata.get("summary"):
                update_data["summary"] = metadata["summary"]

        update_lead(chat_id, **update_data)

        if metadata.get("qualification_complete"):
            print("✅ Lead qualification complete!")
            summary = get_lead_summary(chat_id)
            print(f"\n{summary}\n")


if __name__ == "__main__":
    main()
