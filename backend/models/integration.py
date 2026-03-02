"""Integration configuration model."""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, JSON
from backend.database import Base


class IntegrationType(str, Enum):
    NMS = "nms"
    ITSM = "itsm"
    CHAT = "chat"
    CLOUD = "cloud"


class Integration(Base):
    """Integration connector configuration (NMS, ITSM, etc.)."""
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # SolarWinds, ServiceNow, etc.
    type = Column(String(20), nullable=False)  # nms, itsm, chat, cloud
    
    enabled = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)  # API URL, keys, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
