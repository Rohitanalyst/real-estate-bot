"""
Database module for Real Estate Lead Qualification Agent.
Uses SQLite to store and manage leads.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List

import config

logger = logging.getLogger(__name__)


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with the leads table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE NOT NULL,
            platform TEXT NOT NULL DEFAULT 'telegram',
            name TEXT,
            phone TEXT,
            budget_min REAL,
            budget_max REAL,
            currency TEXT DEFAULT 'USD',
            location_preferences TEXT,
            timeline TEXT,
            property_type TEXT,
            bedrooms INTEGER,
            bathrooms INTEGER,
            special_requirements TEXT,
            lead_score TEXT DEFAULT 'unknown',
            status TEXT DEFAULT 'in_progress',
            conversation_history TEXT DEFAULT '[]',
            created_at TEXT,
            updated_at TEXT,
            summary TEXT
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def get_or_create_lead(chat_id: str, platform: str = "telegram") -> Dict:
    """Get existing lead or create a new one."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()

    if row:
        lead = dict(row)
        lead["conversation_history"] = json.loads(lead["conversation_history"] or "[]")
        conn.close()
        return lead

    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO leads (chat_id, platform, created_at, updated_at, conversation_history)
        VALUES (?, ?, ?, ?, '[]')
    """, (chat_id, platform, now, now))
    conn.commit()
    logger.info(f"New lead created: {chat_id} ({platform})")

    cursor.execute("SELECT * FROM leads WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    lead = dict(row)
    lead["conversation_history"] = []
    conn.close()
    return lead


def update_lead(chat_id: str, **kwargs):
    """Update lead fields."""
    conn = get_connection()
    cursor = conn.cursor()

    if "conversation_history" in kwargs:
        kwargs["conversation_history"] = json.dumps(kwargs["conversation_history"])

    kwargs["updated_at"] = datetime.now().isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [chat_id]

    cursor.execute(f"UPDATE leads SET {set_clause} WHERE chat_id = ?", values)
    conn.commit()
    conn.close()
    logger.debug(f"Lead updated: {chat_id}, fields: {list(kwargs.keys())}")


def get_all_leads(status: Optional[str] = None) -> List[Dict]:
    """Get all leads, optionally filtered by status."""
    conn = get_connection()
    cursor = conn.cursor()

    if status:
        cursor.execute("SELECT * FROM leads WHERE status = ? ORDER BY updated_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM leads ORDER BY updated_at DESC")

    rows = cursor.fetchall()
    leads = []
    for row in rows:
        lead = dict(row)
        lead["conversation_history"] = json.loads(lead["conversation_history"] or "[]")
        leads.append(lead)

    conn.close()
    return leads


def get_lead_summary(chat_id: str) -> Optional[str]:
    """Get a formatted summary for a specific lead."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    lead = dict(row)
    score_emoji = {"hot": "🔥", "warm": "🌤", "cold": "❄️"}.get(lead.get("lead_score", ""), "❓")

    parts = [f"📋 Lead: {lead.get('name', 'Unknown')} {score_emoji}"]
    parts.append(f"   Platform: {lead.get('platform', 'N/A')}")
    parts.append(f"   Score: {lead.get('lead_score', 'unknown').upper()}")
    parts.append(f"   Status: {lead.get('status', 'N/A')}")

    if lead.get("budget_min") or lead.get("budget_max"):
        currency = lead.get('currency', 'USD')
        bmin = f"{lead['budget_min']:,.0f}" if lead.get('budget_min') else '?'
        bmax = f"{lead['budget_max']:,.0f}" if lead.get('budget_max') else '?'
        parts.append(f"   Budget: {currency} {bmin} - {bmax}")

    if lead.get("location_preferences"):
        parts.append(f"   Location: {lead['location_preferences']}")
    if lead.get("timeline"):
        parts.append(f"   Timeline: {lead['timeline']}")
    if lead.get("property_type"):
        parts.append(f"   Property: {lead['property_type']}")
    if lead.get("bedrooms"):
        parts.append(f"   Bedrooms: {lead['bedrooms']}")
    if lead.get("bathrooms"):
        parts.append(f"   Bathrooms: {lead['bathrooms']}")
    if lead.get("special_requirements"):
        parts.append(f"   Special: {lead['special_requirements']}")
    if lead.get("summary"):
        parts.append(f"\n   Summary: {lead['summary']}")

    return "\n".join(parts)


# Initialize DB on import
init_db()
