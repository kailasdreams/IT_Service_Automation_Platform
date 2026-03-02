"""Incident Management model."""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from backend.database import Base


class IncidentStatus(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Incident(Base):
    """Incident/Ticket model for ITIL Incident Management."""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.NEW)
    priority = Column(SQLEnum(IncidentPriority), default=IncidentPriority.MEDIUM)
    
    source = Column(String(100), nullable=True)  # NMS, manual, api, etc.
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    
    assigned_to = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    resolution_notes = Column(Text, nullable=True)
