"""Success Metrics & Dashboard API."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import Incident, Event

router = APIRouter()


@router.get("/dashboard")
async def dashboard_metrics(db: AsyncSession = Depends(get_db)):
    """Aggregated metrics for dashboard."""
    # Incident counts
    total_incidents = await db.execute(select(func.count(Incident.id)))
    open_incidents = await db.execute(
        select(func.count(Incident.id)).where(
            Incident.status.in_(["new", "assigned", "in_progress", "pending"])
        )
    )
    since = datetime.utcnow() - timedelta(days=1)
    resolved_today = await db.execute(
        select(func.count(Incident.id)).where(
            Incident.status.in_(["resolved", "closed"]),
            Incident.resolved_at >= since,
        )
    )
    
    # Event counts
    total_events = await db.execute(select(func.count(Event.id)))
    events_today = await db.execute(
        select(func.count(Event.id)).where(Event.created_at >= since)
    )
    
    return {
        "incidents": {
            "total": total_incidents.scalar() or 0,
            "open": open_incidents.scalar() or 0,
            "resolved_today": resolved_today.scalar() or 0,
        },
        "events": {
            "total": total_events.scalar() or 0,
            "today": events_today.scalar() or 0,
        },
        "targets": {
            "platform_uptime": "99.9%",
            "api_response_p95": "<500ms",
            "event_to_ticket": "<10s",
            "auto_remediation_success": ">90%",
            "sla_compliance": ">99%",
        },
    }


@router.get("/targets")
async def target_metrics():
    """Target success metrics from architecture."""
    return {
        "technical": [
            {"label": "Platform Uptime", "value": "99.9%"},
            {"label": "API Response Time (p95)", "value": "<500ms"},
            {"label": "Event-to-Ticket Time", "value": "<10s"},
            {"label": "Auto-Remediation Success", "value": ">90%"},
            {"label": "False Positive Rate", "value": "<1%"},
        ],
        "business": [
            {"label": "Manual Ticket Reduction", "value": "50%"},
            {"label": "MTTR Reduction", "value": "60%"},
            {"label": "Operational Cost Savings", "value": "40%"},
            {"label": "SLA Compliance", "value": ">99%"},
            {"label": "Customer Satisfaction", "value": ">95%"},
        ],
        "growth": [
            {"label": "Net Retention Rate", "value": ">80%"},
            {"label": "Monthly Customer Growth", "value": "25%"},
            {"label": "Time to Value", "value": "<30 days"},
            {"label": "Platform Adoption Rate", "value": ">85%"},
        ],
    }
