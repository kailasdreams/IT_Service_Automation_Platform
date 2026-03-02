"""Incident Management ITIL plugin."""
from typing import Dict, Any, Optional
from backend.plugins.base import BasePlugin, PluginType, PluginResult
from sqlalchemy.ext.asyncio import AsyncSession


class IncidentManagementPlugin(BasePlugin):
    """ITIL Incident Management plugin."""
    
    version = "1.0.0"
    description = "ITIL Incident Management - auto-ticket creation, routing, SLA tracking, escalation"
    
    def __init__(self, name: str = "incident_management", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, PluginType.ITIL_PROCESS, config)
    
    async def initialize(self) -> PluginResult:
        """Initialize incident management plugin."""
        return PluginResult(success=True, data={"message": "Incident Management plugin initialized"})
    
    async def create_incident(self, event_data: Dict[str, Any], db: AsyncSession) -> PluginResult:
        """Create incident from event."""
        try:
            from backend.models import Incident, IncidentStatus, IncidentPriority
            
            priority_map = {
                "critical": IncidentPriority.CRITICAL,
                "high": IncidentPriority.HIGH,
                "medium": IncidentPriority.MEDIUM,
                "low": IncidentPriority.LOW,
            }
            
            incident = Incident(
                title=event_data.get("message", "Incident"),
                description=event_data.get("description", ""),
                priority=priority_map.get(event_data.get("priority", "medium").lower(), IncidentPriority.MEDIUM),
                status=IncidentStatus.NEW,
                source=event_data.get("source", "nms"),
                event_id=event_data.get("event_id"),
                created_by="system",
            )
            
            db.add(incident)
            await db.commit()
            await db.refresh(incident)
            
            # Auto-assignment based on rules
            await self._auto_assign(incident, event_data, db)
            
            return PluginResult(success=True, data={"incident_id": incident.id, "incident": incident})
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def execute(self, **kwargs) -> PluginResult:
        """Execute incident management action."""
        action = kwargs.get("action", "create_incident")
        if action == "create_incident":
            return await self.create_incident(kwargs.get("event_data", {}), kwargs.get("db"))
        return PluginResult(success=False, error=f"Unknown action: {action}")
    
    async def _auto_assign(self, incident, event_data: Dict[str, Any], db: AsyncSession):
        """Auto-assign incident based on rules."""
        # Simple rule: assign based on source
        source = event_data.get("source", "")
        if "network" in source.lower():
            incident.assigned_to = "network-team"
        elif "server" in source.lower():
            incident.assigned_to = "server-team"
        else:
            incident.assigned_to = "operations-team"
        await db.commit()
