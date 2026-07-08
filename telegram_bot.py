"""
Telegram Bot for Real Estate Lead Qualification Agent.
Handles incoming messages and routes them through the AI engine.
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import config
from database import get_or_create_lead, update_lead, get_lead_summary, get_all_leads
from ai_engine import get_ai_response, get_initial_greeting

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    chat_id = str(update.effective_chat.id)
    lead = get_or_create_lead(chat_id, platform="telegram")

    # Set name if available from Telegram profile
    user = update.effective_user
    if user and user.first_name:
        name = user.first_name
        if user.last_name:
            name += f" {user.last_name}"
        update_lead(chat_id, name=name)

    greeting = get_initial_greeting()

    # Store greeting in conversation history
    conversation_history = lead.get("conversation_history", [])
    conversation_history.append({"role": "assistant", "content": greeting})
    update_lead(chat_id, conversation_history=conversation_history)

    await update.message.reply_text(greeting)
    logger.info(f"New conversation started: {chat_id}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        f"🏠 {config.COMPANY_NAME} - Real Estate Assistant\n\n"
        "I can help you find your perfect property! Just chat with me naturally "
        "and I'll help match you with the right options.\n\n"
        "Commands:\n"
        "/start - Start a new conversation\n"
        "/status - Check your current profile\n"
        "/reset - Reset your conversation\n"
        "/help - Show this help message\n\n"
        "Just tell me what you're looking for!"
    )
    await update.message.reply_text(help_text)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    chat_id = str(update.effective_chat.id)
    summary = get_lead_summary(chat_id)

    if summary:
        await update.message.reply_text(summary)
    else:
        await update.message.reply_text(
            "I don't have any information about you yet. "
            "Send /start to begin your property search!"
        )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reset command."""
    chat_id = str(update.effective_chat.id)
    update_lead(
        chat_id,
        conversation_history=[],
        status="in_progress",
        lead_score="unknown",
        budget_min=None,
        budget_max=None,
        location_preferences=None,
        timeline=None,
        property_type=None,
        bedrooms=None,
        bathrooms=None,
        special_requirements=None,
        summary=None
    )

    greeting = get_initial_greeting()
    await update.message.reply_text(f"🔄 Conversation reset!\n\n{greeting}")
    logger.info(f"Conversation reset: {chat_id}")


async def leads_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leads command - admin view of all leads."""
    leads = get_all_leads()

    if not leads:
        await update.message.reply_text("No leads in the system yet.")
        return

    response_parts = ["📊 All Leads:\n"]
    for lead in leads[:10]:
        score_emoji = {"hot": "🔥", "warm": "🌤", "cold": "❄️"}.get(lead.get("lead_score", ""), "❓")
        name = lead.get("name", "Unknown")
        status = lead.get("status", "unknown")
        response_parts.append(f"{score_emoji} {name} - {status} ({lead.get('lead_score', 'unknown')})")

    await update.message.reply_text("\n".join(response_parts))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    chat_id = str(update.effective_chat.id)
    user_message = update.message.text

    if not user_message:
        return

    # Get or create lead
    lead = get_or_create_lead(chat_id, platform="telegram")
    conversation_history = lead.get("conversation_history", [])

    # If no conversation history, add initial greeting context
    if not conversation_history:
        greeting = get_initial_greeting()
        conversation_history.append({"role": "assistant", "content": greeting})

    # Show typing indicator
    await update.effective_chat.send_action("typing")

    # Get AI response
    ai_message, metadata = get_ai_response(conversation_history, user_message)

    # Update conversation history
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": ai_message})

    # Prepare update data
    update_data = {"conversation_history": conversation_history}

    # Extract and update lead data
    extracted = metadata.get("extracted_data", {})
    if extracted:
        field_mapping = {
            "name": "name",
            "budget_min": "budget_min",
            "budget_max": "budget_max",
            "currency": "currency",
            "location_preferences": "location_preferences",
            "timeline": "timeline",
            "property_type": "property_type",
            "bedrooms": "bedrooms",
            "bathrooms": "bathrooms",
            "special_requirements": "special_requirements",
        }

        for ai_field, db_field in field_mapping.items():
            value = extracted.get(ai_field)
            if value is not None:
                update_data[db_field] = value

    # Update lead score
    lead_score = metadata.get("lead_score", "unknown")
    if lead_score != "unknown":
        update_data["lead_score"] = lead_score

    # Check if qualification is complete
    if metadata.get("qualification_complete"):
        update_data["status"] = "qualified"
        if metadata.get("summary"):
            update_data["summary"] = metadata["summary"]

    # Save to database
    update_lead(chat_id, **update_data)

    # Send response
    await update.message.reply_text(ai_message)

    # If qualification complete, send notification
    if metadata.get("qualification_complete"):
        await update.message.reply_text(
            "✅ Great news! I have all the information I need to start finding "
            "properties that match your criteria. Our team will be in touch shortly "
            "with personalized recommendations!\n\n"
            "Feel free to ask me anything else or use /status to see your profile."
        )
        logger.info(f"Lead qualified: {chat_id}, score: {lead_score}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error: {context.error}")


def run_telegram_bot():
    """Start the Telegram bot."""
    if not config.TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set!")
        print("   Get one from @BotFather on Telegram")
        print("   Then: export TELEGRAM_BOT_TOKEN='your-token'")
        return

    print(f"🚀 Starting {config.COMPANY_NAME} Lead Bot (Telegram)...")
    print(f"   Model: {config.AI_MODEL}")
    print("   Press Ctrl+C to stop\n")

    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("leads", leads_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_error_handler(error_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_telegram_bot()
