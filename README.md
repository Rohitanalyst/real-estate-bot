# 🏠 Real Estate Lead Qualification Agent

An AI-powered chatbot that qualifies real estate leads through natural conversation on **WhatsApp** and **Telegram**. Powered by **Gemini 3 Flash** (free/cheapest model) via OpenAI-compatible API.

## Features

- **Works Out of the Box** — No paid API keys needed for the AI engine
- **Natural Conversation** — Engages leads conversationally, not like a boring form
- **Multi-Platform** — Telegram bot + WhatsApp Business API
- **AI-Powered** — Uses Gemini 3 Flash for intelligent, context-aware responses
- **Lead Scoring** — Automatically classifies leads as Hot 🔥, Warm 🌤, or Cold ❄️
- **Structured Data Extraction** — Pulls budget, location, timeline from natural language
- **SQLite Storage** — Stores all leads and full conversation history
- **Admin API** — FastAPI dashboard with docs at `/docs`
- **Production Ready** — Proper logging, error handling, retry logic, config management

## Architecture

```
┌─────────────┐     ┌─────────────────────┐     ┌──────────────┐
│  Telegram   │────▶│                     │────▶│   SQLite DB  │
│  Bot API    │     │    AI Engine         │     └──────────────┘
└─────────────┘     │  (Gemini 3 Flash)    │
                    │                     │     ┌──────────────┐
┌─────────────┐     │  • Qualification     │────▶│  Admin API   │
│  WhatsApp   │────▶│  • Lead Scoring      │     │  (FastAPI)   │
│  Cloud API  │     │  • Data Extraction   │     └──────────────┘
└─────────────┘     └─────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
cd real-estate-agent
pip install -r requirements.txt
```

### 2. Run Demo (Works Immediately!)

```bash
python main.py demo
```

This starts a live interactive conversation with the AI agent in your terminal. No additional setup needed.

### 3. Run Telegram Bot

```bash
export TELEGRAM_BOT_TOKEN="your-token-from-botfather"
python main.py telegram
```

### 4. Run WhatsApp Bot

```bash
export WHATSAPP_TOKEN="your-meta-token"
export WHATSAPP_PHONE_NUMBER_ID="your-id"
python main.py whatsapp
```

### 5. Run Admin Dashboard

```bash
python main.py admin
# Visit http://localhost:8000/docs for interactive API docs
```

## Setup Guides

### Telegram Bot (2 minutes)

1. Open Telegram → search **@BotFather**
2. Send `/newbot` → choose name and username
3. Copy the token
4. `export TELEGRAM_BOT_TOKEN="your-token"`
5. `python main.py telegram`
6. Find your bot on Telegram and send `/start`

### WhatsApp Business API

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create an app → add WhatsApp product
3. Get access token + phone number ID
4. Set up webhook URL → `https://your-server.com/webhook`
5. Set env vars and run `python main.py whatsapp`

> For local development, use ngrok: `ngrok http 5000`

## Lead Qualification Flow

The AI gathers these fields through natural conversation:

| Field | Description | Example |
|-------|-------------|---------|
| Name | Lead's name | "Sarah Johnson" |
| Budget | Min-max range | $400,000 - $600,000 |
| Location | Preferred areas | "Downtown Miami" |
| Timeline | When to move/buy | "Within 2-3 months" |
| Property Type | House, apt, etc. | "Single-family house" |
| Bedrooms | Number needed | 3 |
| Bathrooms | Number needed | 2 |
| Special | Any extras | "Backyard, garage, pool" |

## Lead Scoring

| Score | Criteria |
|-------|----------|
| 🔥 Hot | Has budget + timeline < 3 months + clear preferences |
| 🌤 Warm | Some info + timeline 3-6 months + somewhat flexible |
| ❄️ Cold | Just browsing + no timeline + vague preferences |

## Admin API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads` | List all leads (filter: `?status=qualified&score=hot`) |
| GET | `/api/leads/{id}` | Get lead details + conversation history |
| GET | `/api/leads/{id}/summary` | Get formatted summary |
| GET | `/api/stats` | Lead statistics by status/score/platform |
| GET | `/health` | Health check |

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Begin conversation |
| `/help` | Show help |
| `/status` | View your profile |
| `/reset` | Start over |
| `/leads` | (Admin) View all leads |

## Project Structure

```
real-estate-agent/
├── main.py              # Entry point + demo mode
├── config.py            # Centralized configuration
├── ai_engine.py         # AI conversation engine (Gemini Flash)
├── telegram_bot.py      # Telegram bot handler
├── whatsapp_bot.py      # WhatsApp webhook handler
├── admin_api.py         # FastAPI admin dashboard
├── database.py          # SQLite database operations
├── test_ai.py           # AI engine test script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Configuration

All settings in `config.py` or via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_MODEL` | `gemini-3-flash-preview` | LLM model to use |
| `AGENT_NAME` | `Alex` | Bot's display name |
| `COMPANY_NAME` | `Premium Properties` | Your company name |
| `DB_PATH` | `leads.db` | SQLite database path |
| `TELEGRAM_BOT_TOKEN` | — | From @BotFather |
| `WHATSAPP_TOKEN` | — | Meta access token |
| `ADMIN_PORT` | `8000` | Admin API port |

## Customization

### Change AI Personality
Edit `SYSTEM_PROMPT` in `ai_engine.py` or set `AGENT_NAME` / `COMPANY_NAME` env vars.

### Change AI Model
Set `AI_MODEL` env var to any supported model (e.g., `gpt-5-nano`, `gpt-5-mini`).

### Add More Qualification Fields
1. Add column in `database.py` → `init_db()`
2. Update system prompt in `ai_engine.py`
3. Update field mappings in bot handlers

## License

MIT License
