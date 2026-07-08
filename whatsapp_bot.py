"""
WhatsApp Bot for Real Estate Lead Qualification Agent.
Uses Flask webhook to receive messages from WhatsApp Business API (Meta Cloud API).
"""

import logging
import requests
from flask import Flask, request, jsonify

import config
from database import get_or_create_lead, update_lead
from ai_engine import get_ai_response, get_initial_greeting

logger = logging.getLogger(__name__)

app = Flask(__name__)


def send_whatsapp_message(to: str, message: str) -> bool:
    """Send a message via WhatsApp Business API."""
    url = f"https://graph.facebook.com/v18.0/{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"Message sent to {to}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message to {to}: {e}")
        return False


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Verify webhook for WhatsApp Business API."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return challenge, 200
    else:
        logger.warning("Webhook verification failed")
        return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def receive_message():
    """Handle incoming WhatsApp messages."""
    data = request.get_json()

    if not data:
        return jsonify({"status": "no data"}), 400

    try:
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return jsonify({"status": "no messages"}), 200

        message = messages[0]
        from_number = message.get("from", "")
        message_type = message.get("type", "")

        if message_type != "text":
            send_whatsapp_message(from_number, "I can only process text messages. Please type your response.")
            return jsonify({"status": "non-text"}), 200

        user_message = message.get("text", {}).get("body", "")
        if not user_message:
            return jsonify({"status": "empty"}), 200

        process_whatsapp_message(from_number, user_message)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def process_whatsapp_message(phone_number: str, user_message: str):
    """Process an incoming WhatsApp message through the AI engine."""
    chat_id = f"wa_{phone_number}"

    lead = get_or_create_lead(chat_id, platform="whatsapp")
    conversation_history = lead.get("conversation_history", [])

    # First message — send greeting
    if not conversation_history:
        greeting = get_initial_greeting()
        conversation_history.append({"role": "assistant", "content": greeting})
        send_whatsapp_message(phone_number, greeting)
        update_lead(chat_id, conversation_history=conversation_history, phone=phone_number)
        return

    # Get AI response
    ai_message, metadata = get_ai_response(conversation_history, user_message)

    # Update conversation history
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": ai_message})

    # Prepare update data
    update_data = {"conversation_history": conversation_history}

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

    lead_score = metadata.get("lead_score", "unknown")
    if lead_score != "unknown":
        update_data["lead_score"] = lead_score

    if metadata.get("qualification_complete"):
        update_data["status"] = "qualified"
        if metadata.get("summary"):
            update_data["summary"] = metadata["summary"]

    update_lead(chat_id, **update_data)
    send_whatsapp_message(phone_number, ai_message)

    if metadata.get("qualification_complete"):
        send_whatsapp_message(
            phone_number,
            "✅ I have everything I need! Our team will reach out with personalized property recommendations soon."
        )
        logger.info(f"WhatsApp lead qualified: {phone_number}, score: {lead_score}")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "real-estate-whatsapp-bot"}), 200


def run_whatsapp_bot():
    """Start the WhatsApp bot webhook server."""
    if not config.WHATSAPP_TOKEN:
        print("⚠️  WhatsApp credentials not set. Running webhook server anyway for testing.")
        print("   Set WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_VERIFY_TOKEN")

    print(f"🚀 Starting {config.COMPANY_NAME} Lead Bot (WhatsApp)...")
    print(f"   Webhook: http://0.0.0.0:{config.WHATSAPP_PORT}/webhook")
    print(f"   Health:  http://0.0.0.0:{config.WHATSAPP_PORT}/health")
    print("   Press Ctrl+C to stop\n")

    app.run(host="0.0.0.0", port=config.WHATSAPP_PORT, debug=False)


if __name__ == "__main__":
    run_whatsapp_bot()
