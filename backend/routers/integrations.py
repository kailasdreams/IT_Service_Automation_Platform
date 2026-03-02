"""Integrations configuration API."""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from backend.database import get_db
from backend.models import Integration

router = APIRouter()


# --- Schemas ---
class IntegrationCreate(BaseModel):
    name: str
    type: str  # nms, itsm, chat, cloud
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None


class IntegrationUpdate(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class IntegrationResponse(BaseModel):
    id: int
    name: str
    type: str
    enabled: bool
    config: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# --- Endpoints ---
@router.get("", response_model=List[IntegrationResponse])
async def list_integrations(
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List configured integrations."""
    q = select(Integration)
    if type:
        q = q.where(Integration.type == type)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=IntegrationResponse)
async def create_integration(
    data: IntegrationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a new integration."""
    integration = Integration(
        name=data.name,
        type=data.type,
        enabled=data.enabled,
        config=data.config,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get integration by ID."""
    result = await db.execute(select(Integration).where(Integration.id == integration_id))
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    data: IntegrationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update integration."""
    result = await db.execute(select(Integration).where(Integration.id == integration_id))
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(integration, k, v)
    await db.commit()
    await db.refresh(integration)
    return integration


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete integration."""
    result = await db.execute(select(Integration).where(Integration.id == integration_id))
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    await db.delete(integration)
    await db.commit()
    return {"ok": True}
