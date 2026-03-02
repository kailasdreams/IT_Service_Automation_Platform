"""Incident Management API."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from backend.database import get_db
from backend.models import Incident, IncidentStatus, IncidentPriority

router = APIRouter()


# --- Schemas ---
class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: IncidentPriority = IncidentPriority.MEDIUM
    source: Optional[str] = "manual"


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IncidentStatus] = None
    priority: Optional[IncidentPriority] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    source: Optional[str]
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Endpoints ---
@router.get("", response_model=List[IncidentResponse])
async def list_incidents(
    status: Optional[IncidentStatus] = None,
    priority: Optional[IncidentPriority] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List incidents with optional filters."""
    q = select(Incident)
    if status:
        q = q.where(Incident.status == status)
    if priority:
        q = q.where(Incident.priority == priority)
    q = q.order_by(Incident.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=IncidentResponse)
async def create_incident(
    data: IncidentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new incident."""
    incident = Incident(
        title=data.title,
        description=data.description,
        priority=data.priority,
        source=data.source,
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident


@router.get("/stats")
async def incident_stats(db: AsyncSession = Depends(get_db)):
    """Get incident statistics for dashboard."""
    total = await db.execute(select(func.count(Incident.id)))
    by_status = await db.execute(
        select(Incident.status, func.count(Incident.id))
        .group_by(Incident.status)
    )
    by_priority = await db.execute(
        select(Incident.priority, func.count(Incident.id))
        .group_by(Incident.priority)
    )
    return {
        "total": total.scalar() or 0,
        "by_status": dict(by_status.all()),
        "by_priority": dict(by_priority.all()),
    }


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get incident by ID."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update incident."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(incident, k, v)
    if data.status == IncidentStatus.RESOLVED or data.status == IncidentStatus.CLOSED:
        incident.resolved_at = datetime.utcnow()
    await db.commit()
    await db.refresh(incident)
    return incident


@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete incident."""
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    await db.delete(incident)
    await db.commit()
    return {"ok": True}
