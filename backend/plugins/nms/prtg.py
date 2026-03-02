"""PRTG NMS plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.nms.base import BaseNMSPlugin
from backend.plugins.base import PluginResult
import base64


class PRTGPlugin(BaseNMSPlugin):
    """PRTG Network Monitor API connector."""
    
    version = "1.0.0"
    description = "PRTG NMS connector - REST API, Notifications integration"
    
    def get_required_config_fields(self) -> List[str]:
        return ["api_url", "username", "password"]
    
    def get_auth_headers(self) -> Dict[str, str]:
        """PRTG uses basic auth or passhash."""
        username = self.config.get("username", "")
        password = self.config.get("password", "")
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        }
    
    async def fetch_alerts(self, filters: Optional[Dict[str, Any]] = None) -> PluginResult:
        """Fetch alarms from PRTG."""
        try:
            url = "/api/table.json"
            params = {
                "content": "alarms",
                "columns": "objid,datetime,message,status,priority",
                **(filters or {}),
            }
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                alarms = data.get("alarms", [])
                alerts = [
                    {
                        "id": str(alarm.get("objid")),
                        "source": "prtg",
                        "severity": self._map_status(alarm.get("status")),
                        "message": alarm.get("message", ""),
                        "resource": alarm.get("device", ""),
                        "timestamp": alarm.get("datetime"),
                        "priority": alarm.get("priority"),
                        "raw": alarm,
                    }
                    for alarm in alarms
                ]
                return PluginResult(success=True, data={"alerts": alerts})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def fetch_metrics(self, resource_id: str, metric_names: List[str]) -> PluginResult:
        """Fetch sensor data from PRTG."""
        try:
            url = f"/api/table.json"
            params = {
                "content": "values",
                "id": resource_id,
                "columns": "datetime,name,value,unit",
            }
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                sensors = data.get("values", [])
                metrics = [
                    {
                        "name": sensor.get("name"),
                        "value": sensor.get("value"),
                        "unit": sensor.get("unit"),
                        "timestamp": sensor.get("datetime"),
                    }
                    for sensor in sensors
                    if not metric_names or sensor.get("name") in metric_names
                ]
                return PluginResult(success=True, data={"metrics": metrics})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def acknowledge_alert(self, alert_id: str) -> PluginResult:
        """Acknowledge alarm in PRTG."""
        try:
            url = f"/api/acknowledgealarm.htm"
            params = {"id": alert_id}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                return PluginResult(success=True, data={"message": "Alarm acknowledged"})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    def _map_status(self, status: str) -> str:
        """Map PRTG status to standard severity."""
        mapping = {
            "Down": "critical",
            "Warning": "major",
            "Unusual": "minor",
            "Up": "info",
        }
        return mapping.get(status, "minor")
