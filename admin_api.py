"""
Admin API for Real Estate Lead Qualification Agent.
Provides endpoints to view and manage leads.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

import config
from database import get_all_leads, get_lead_summary, get_or_create_lead

logger = logging.getLogger(__name__)

app = FastAPI(
    title=f"{config.COMPANY_NAME} - Lead Management API",
    description="API to manage and view qualified real estate leads",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": f"{config.COMPANY_NAME} Lead Qualification Agent",
        "version": "1.0.0",
        "endpoints": {
            "leads": "/api/leads",
            "lead_detail": "/api/leads/{chat_id}",
            "stats": "/api/stats",
            "health": "/health"
        }
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/leads")
def list_leads(status: Optional[str] = None, score: Optional[str] = None):
    """List all leads with optional filtering."""
    leads = get_all_leads(status=status)

    if score:
        leads = [l for l in leads if l.get("lead_score") == score]

    for lead in leads:
        lead.pop("conversation_history", None)

    return {"total": len(leads), "leads": leads}


@app.get("/api/leads/{chat_id}")
def get_lead_detail(chat_id: str):
    """Get detailed information about a specific lead."""
    lead = get_or_create_lead(chat_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.get("/api/leads/{chat_id}/summary")
def get_lead_summary_endpoint(chat_id: str):
    """Get a formatted summary of a specific lead."""
    summary = get_lead_summary(chat_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"summary": summary}


@app.get("/api/stats")
def get_stats():
    """Get overall lead statistics."""
    all_leads = get_all_leads()

    stats = {
        "total_leads": len(all_leads),
        "by_status": {},
        "by_score": {},
        "by_platform": {}
    }

    for lead in all_leads:
        status = lead.get("status", "unknown")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        score = lead.get("lead_score", "unknown")
        stats["by_score"][score] = stats["by_score"].get(score, 0) + 1

        platform = lead.get("platform", "unknown")
        stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1

    return stats


def run_admin_api():
    """Start the admin API server."""
    import uvicorn
    print(f"🚀 Starting Admin API on http://0.0.0.0:{config.ADMIN_PORT}")
    print(f"   Docs: http://0.0.0.0:{config.ADMIN_PORT}/docs")
    uvicorn.run(app, host="0.0.0.0", port=config.ADMIN_PORT)


if __name__ == "__main__":
    run_admin_api()
