"""Nagios NMS plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.nms.base import BaseNMSPlugin
from backend.plugins.base import PluginResult
import base64


class NagiosPlugin(BaseNMSPlugin):
    """Nagios Core/XI API connector."""
    
    version = "1.0.0"
    description = "Nagios NMS connector - NRPE, REST API integration"
    
    def get_required_config_fields(self) -> List[str]:
        return ["api_url", "username", "password"]
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Nagios uses basic auth."""
        username = self.config.get("username", "")
        password = self.config.get("password", "")
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        }
    
    async def fetch_alerts(self, filters: Optional[Dict[str, Any]] = None) -> PluginResult:
        """Fetch alerts from Nagios."""
        try:
            # Nagios XI API endpoint
            url = "/nagiosxi/api/v1/objects/hoststatus"
            params = filters or {}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                alerts = []
                
                # Process host statuses
                for host in data.get("hoststatus", []):
                    if host.get("status") != "UP":
                        alerts.append({
                            "id": f"host_{host.get('host_id')}",
                            "source": "nagios",
                            "severity": self._map_status(host.get("status")),
                            "message": host.get("status_information", ""),
                            "resource": host.get("host_name"),
                            "timestamp": host.get("last_check"),
                            "raw": host,
                        })
                
                # Also check service statuses
                service_url = "/nagiosxi/api/v1/objects/servicestatus"
                service_response = await self.client.get(service_url, params=params)
                if service_response.status_code == 200:
                    service_data = service_response.json()
                    for service in service_data.get("servicestatus", []):
                        if service.get("status") != "OK":
                            alerts.append({
                                "id": f"service_{service.get('service_id')}",
                                "source": "nagios",
                                "severity": self._map_status(service.get("status")),
                                "message": service.get("status_information", ""),
                                "resource": f"{service.get('host_name')}/{service.get('service_name')}",
                                "timestamp": service.get("last_check"),
                                "raw": service,
                            })
                
                return PluginResult(success=True, data={"alerts": alerts})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def fetch_metrics(self, resource_id: str, metric_names: List[str]) -> PluginResult:
        """Fetch metrics from Nagios."""
        try:
            # Nagios performance data
            url = f"/nagiosxi/api/v1/objects/perfdata"
            params = {"host": resource_id}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                perfdata = response.json()
                return PluginResult(success=True, data={"metrics": perfdata})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def acknowledge_alert(self, alert_id: str) -> PluginResult:
        """Acknowledge alert in Nagios."""
        try:
            url = "/nagiosxi/api/v1/commands/acknowledge"
            data = {"alert_id": alert_id}
            response = await self.client.post(url, json=data)
            
            if response.status_code == 200:
                return PluginResult(success=True, data={"message": "Alert acknowledged"})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    def _map_status(self, status: str) -> str:
        """Map Nagios status to standard severity."""
        mapping = {
            "DOWN": "critical",
            "CRITICAL": "critical",
            "WARNING": "major",
            "UNKNOWN": "minor",
            "UP": "info",
            "OK": "info",
        }
        return mapping.get(status.upper(), "minor")
