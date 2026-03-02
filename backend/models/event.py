"""Event model for Event Flow / Ingestion."""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class EventStatus(str, Enum):
    RECEIVED = "received"
    ENRICHED = "enriched"
    CORRELATED = "correlated"
    PROCESSED = "processed"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class Event(Base):
    """Event from NMS/monitoring for processing pipeline."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source = Column(String(100), nullable=False)  # solarwinds, nagios, zabbix, etc.
    source_id = Column(String(255), nullable=True)  # external ID
    
    severity = Column(String(20), nullable=True)  # critical, major, minor, warning
    message = Column(Text, nullable=False)
    raw_payload = Column(JSON, nullable=True)
    
    status = Column(String(20), default=EventStatus.RECEIVED.value)
    
    # Enrichment data
    ci_id = Column(String(100), nullable=True)  # Configuration Item
    service_name = Column(String(255), nullable=True)
    impact_score = Column(Integer, nullable=True)
    
    # Correlation
    correlation_group = Column(String(100), nullable=True)
    root_cause_event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
