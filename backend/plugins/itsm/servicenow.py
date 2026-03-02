"""ServiceNow ITSM plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.itsm.base import BaseITSMPlugin
from backend.plugins.base import PluginResult
import base64


class ServiceNowPlugin(BaseITSMPlugin):
    """ServiceNow ITSM connector."""
    
    version = "1.0.0"
    description = "ServiceNow ITSM connector - REST API, Import Sets integration"
    
    def get_required_config_fields(self) -> List[str]:
        return ["api_url", "username", "password"]
    
    def get_auth_headers(self) -> Dict[str, str]:
        """ServiceNow uses basic auth."""
        username = self.config.get("username", "")
        password = self.config.get("password", "")
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def create_ticket(self, title: str, description: str, priority: str = "medium", **kwargs) -> PluginResult:
        """Create incident in ServiceNow."""
        try:
            url = "/api/now/table/incident"
            priority_map = {
                "critical": "1",
                "high": "2",
                "medium": "3",
                "low": "4",
            }
            data = {
                "short_description": title,
                "description": description,
                "urgency": priority_map.get(priority.lower(), "3"),
                "impact": kwargs.get("impact", "3"),
                **kwargs,
            }
            response = await self.client.post(url, json=data)
            
            if response.status_code in [200, 201]:
                ticket = response.json().get("result", {})
                return PluginResult(
                    success=True,
                    data={
                        "ticket_id": ticket.get("sys_id"),
                        "number": ticket.get("number"),
                        "ticket": ticket,
                    }
                )
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def update_ticket(self, ticket_id: str, **kwargs) -> PluginResult:
        """Update ServiceNow incident."""
        try:
            url = f"/api/now/table/incident/{ticket_id}"
            response = await self.client.patch(url, json=kwargs)
            
            if response.status_code == 200:
                ticket = response.json().get("result", {})
                return PluginResult(success=True, data={"ticket": ticket})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def get_ticket(self, ticket_id: str) -> PluginResult:
        """Get ServiceNow incident."""
        try:
            url = f"/api/now/table/incident/{ticket_id}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                ticket = response.json().get("result", {})
                return PluginResult(success=True, data={"ticket": ticket})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def search_tickets(self, filters: Optional[Dict[str, Any]] = None) -> PluginResult:
        """Search ServiceNow incidents."""
        try:
            url = "/api/now/table/incident"
            params = filters or {}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                tickets = response.json().get("result", [])
                return PluginResult(success=True, data={"tickets": tickets})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
