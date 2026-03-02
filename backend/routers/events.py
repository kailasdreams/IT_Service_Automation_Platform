"""Event Flow / Ingestion API."""
from datetime import datetime
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from backend.database import get_db
from backend.models import Event, EventStatus

router = APIRouter()


# --- Schemas ---
class EventCreate(BaseModel):
    source: str
    source_id: Optional[str] = None
    severity: Optional[str] = None
    message: str
    raw_payload: Optional[dict] = None


class EventResponse(BaseModel):
    id: int
    source: str
    source_id: Optional[str]
    severity: Optional[str]
    message: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Endpoints ---
@router.get("", response_model=List[EventResponse])
async def list_events(
    source: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List events with optional filters."""
    q = select(Event)
    if source:
        q = q.where(Event.source == source)
    if status:
        q = q.where(Event.status == status)
    q = q.order_by(Event.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=EventResponse)
async def create_event(
    data: EventCreate,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a new event (from NMS webhook, API, etc.)."""
    event = Event(
        source=data.source,
        source_id=data.source_id,
        severity=data.severity,
        message=data.message,
        raw_payload=data.raw_payload,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/stats")
async def event_stats(db: AsyncSession = Depends(get_db)):
    """Get event statistics."""
    total = await db.execute(select(func.count(Event.id)))
    by_source = await db.execute(
        select(Event.source, func.count(Event.id)).group_by(Event.source)
    )
    by_status = await db.execute(
        select(Event.status, func.count(Event.id)).group_by(Event.status)
    )
    return {
        "total": total.scalar() or 0,
        "by_source": dict(by_source.all()),
        "by_status": dict(by_status.all()),
    }


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get event by ID."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch("/{event_id}/status")
async def update_event_status(
    event_id: int,
    status: str = Query(..., description="New status"),
    db: AsyncSession = Depends(get_db),
):
    """Update event status (e.g. after processing)."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.status = status
    if status == EventStatus.PROCESSED.value or status == EventStatus.RESOLVED.value:
        event.processed_at = datetime.utcnow()
    await db.commit()
    return {"ok": True, "status": status}
