"""SolarWinds NMS plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.nms.base import BaseNMSPlugin
from backend.plugins.base import PluginResult


class SolarWindsPlugin(BaseNMSPlugin):
    """SolarWinds Orion API connector."""
    
    version = "1.0.0"
    description = "SolarWinds Orion NMS connector - SNMP, REST API integration"
    
    def get_required_config_fields(self) -> List[str]:
        return ["api_url", "api_key", "username", "password"]
    
    def get_auth_headers(self) -> Dict[str, str]:
        """SolarWinds uses basic auth or token."""
        if self.config.get("use_token"):
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        return {
            "Content-Type": "application/json",
        }
    
    async def initialize(self) -> PluginResult:
        """Initialize SolarWinds connection."""
        result = await super().initialize()
        if not result.success:
            return result
        
        # Authenticate and get token if needed
        if not self.config.get("use_token"):
            try:
                auth_url = f"{self.api_url}/api/Account/Login"
                auth_data = {
                    "username": self.config.get("username"),
                    "password": self.config.get("password"),
                }
                response = await self.client.post(auth_url, json=auth_data)
                if response.status_code == 200:
                    token_data = response.json()
                    self.api_key = token_data.get("access_token", self.api_key)
                    self.client.headers.update(self.get_auth_headers())
            except Exception as e:
                return PluginResult(success=False, error=f"Authentication failed: {str(e)}")
        
        return PluginResult(success=True, data={"message": "SolarWinds initialized"})
    
    async def fetch_alerts(self, filters: Optional[Dict[str, Any]] = None) -> PluginResult:
        """Fetch alerts from SolarWinds."""
        try:
            url = "/api/Alert/ActiveAlerts"
            params = filters or {}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                alerts = response.json()
                # Transform to standard format
                transformed = [
                    {
                        "id": alert.get("AlertID"),
                        "source": "solarwinds",
                        "severity": self._map_severity(alert.get("Severity")),
                        "message": alert.get("Message"),
                        "resource": alert.get("EntityCaption"),
                        "timestamp": alert.get("TriggeredDateTime"),
                        "raw": alert,
                    }
                    for alert in alerts
                ]
                return PluginResult(success=True, data={"alerts": transformed})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def fetch_metrics(self, resource_id: str, metric_names: List[str]) -> PluginResult:
        """Fetch metrics from SolarWinds."""
        try:
            url = f"/api/Orion/Statistics/GetStatistics"
            data = {
                "entityId": resource_id,
                "statisticNames": metric_names,
            }
            response = await self.client.post(url, json=data)
            
            if response.status_code == 200:
                metrics = response.json()
                return PluginResult(success=True, data={"metrics": metrics})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def acknowledge_alert(self, alert_id: str) -> PluginResult:
        """Acknowledge alert in SolarWinds."""
        try:
            url = f"/api/Alert/AcknowledgeAlert"
            data = {"alertId": alert_id}
            response = await self.client.post(url, json=data)
            
            if response.status_code == 200:
                return PluginResult(success=True, data={"message": "Alert acknowledged"})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    def _map_severity(self, severity: str) -> str:
        """Map SolarWinds severity to standard levels."""
        mapping = {
            "Critical": "critical",
            "Warning": "major",
            "Information": "minor",
        }
        return mapping.get(severity, "minor")
