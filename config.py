"""
Configuration for Real Estate Lead Qualification Agent.
All settings are centralized here.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# ============================================================
# AI MODEL CONFIGURATION
# Uses Google Gemini (FREE) via OpenAI-compatible endpoint
# Only needs GOOGLE_API_KEY from https://aistudio.google.com/apikey
# ============================================================
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "")

# ============================================================
# TELEGRAM CONFIGURATION
# Get token from @BotFather on Telegram
# ============================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ============================================================
# WHATSAPP BUSINESS API CONFIGURATION
# Get from Meta for Developers dashboard
# ============================================================
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my-verify-token")

# ============================================================
# SERVER CONFIGURATION
# ============================================================
WHATSAPP_PORT = int(os.getenv("WHATSAPP_PORT", "5000"))
ADMIN_PORT = int(os.getenv("ADMIN_PORT", "8000"))

# ============================================================
# DATABASE
# ============================================================
DB_PATH = os.getenv("DB_PATH", "leads.db")

# ============================================================
# AGENT PERSONALITY
# ============================================================
AGENT_NAME = os.getenv("AGENT_NAME", "Alex")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Premium Properties")

# ============================================================
# LOGGING
# ============================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
