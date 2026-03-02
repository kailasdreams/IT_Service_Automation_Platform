"""BMC Remedy ITSM plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.itsm.base import BaseITSMPlugin
from backend.plugins.base import PluginResult


class BMCRemedyPlugin(BaseITSMPlugin):
    """BMC Remedy ITSM connector."""
    
    version = "1.0.0"
    description = "BMC Remedy ITSM connector - SOAP, REST API integration"
    
    def get_required_config_fields(self) -> List[str]:
        return ["api_url", "username", "password"]
    
    async def create_ticket(self, title: str, description: str, priority: str = "medium", **kwargs) -> PluginResult:
        """Create incident in BMC Remedy."""
        try:
            # BMC Remedy REST API
            url = f"{self.api_url}/api/arsys/v1/entry/HPD:IncidentInterface_Create"
            priority_map = {
                "critical": "1-Critical",
                "high": "2-High",
                "medium": "3-Medium",
                "low": "4-Low",
            }
            data = {
                "values": {
                    "Summary": title,
                    "Description": description,
                    "Urgency": priority_map.get(priority.lower(), "3-Medium"),
                    "Impact": kwargs.get("impact", "3-Medium"),
                    **kwargs.get("values", {}),
                }
            }
            response = await self.client.post(url, json=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                return PluginResult(
                    success=True,
                    data={
                        "ticket_id": result.get("values", {}).get("Incident Number"),
                        "ticket": result,
                    }
                )
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def update_ticket(self, ticket_id: str, **kwargs) -> PluginResult:
        """Update BMC Remedy incident."""
        try:
            url = f"{self.api_url}/api/arsys/v1/entry/HPD:IncidentInterface/{ticket_id}"
            data = {"values": kwargs}
            response = await self.client.put(url, json=data)
            
            if response.status_code == 200:
                ticket = response.json()
                return PluginResult(success=True, data={"ticket": ticket})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def get_ticket(self, ticket_id: str) -> PluginResult:
        """Get BMC Remedy incident."""
        try:
            url = f"{self.api_url}/api/arsys/v1/entry/HPD:IncidentInterface/{ticket_id}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                ticket = response.json()
                return PluginResult(success=True, data={"ticket": ticket})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def search_tickets(self, filters: Optional[Dict[str, Any]] = None) -> PluginResult:
        """Search BMC Remedy incidents."""
        try:
            url = f"{self.api_url}/api/arsys/v1/entry/HPD:IncidentInterface"
            params = filters or {}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                results = response.json()
                tickets = results.get("entries", [])
                return PluginResult(success=True, data={"tickets": tickets})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
