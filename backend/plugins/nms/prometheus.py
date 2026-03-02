"""Prometheus NMS plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.nms.base import BaseNMSPlugin
from backend.plugins.base import PluginResult


class PrometheusPlugin(BaseNMSPlugin):
    """Prometheus API connector."""
    
    version = "1.0.0"
    description = "Prometheus NMS connector - HTTP, Alertmanager integration"
    
    def get_required_config_fields(self) -> List[str]:
        return ["api_url"]
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Prometheus may use bearer token or basic auth."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def fetch_alerts(self, filters: Optional[Dict[str, Any]] = None) -> PluginResult:
        """Fetch alerts from Alertmanager."""
        try:
            # Check Alertmanager for active alerts
            alertmanager_url = self.config.get("alertmanager_url", f"{self.api_url}/api/v1/alerts")
            response = await self.client.get(alertmanager_url)
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get("data", [])
                transformed = [
                    {
                        "id": alert.get("fingerprint", ""),
                        "source": "prometheus",
                        "severity": self._map_severity(alert.get("labels", {}).get("severity", "warning")),
                        "message": alert.get("annotations", {}).get("summary", ""),
                        "resource": alert.get("labels", {}).get("instance", ""),
                        "timestamp": alert.get("startsAt"),
                        "raw": alert,
                    }
                    for alert in alerts
                    if alert.get("status", {}).get("state") == "active"
                ]
                return PluginResult(success=True, data={"alerts": transformed})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def fetch_metrics(self, resource_id: str, metric_names: List[str]) -> PluginResult:
        """Query Prometheus metrics."""
        try:
            # Build PromQL query
            queries = []
            for metric_name in metric_names:
                query = f"{metric_name}{{instance='{resource_id}'}}"
                queries.append(query)
            
            metrics = []
            for query in queries:
                url = f"{self.api_url}/api/v1/query"
                params = {"query": query}
                response = await self.client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        results = data.get("data", {}).get("result", [])
                        for result in results:
                            metrics.append({
                                "name": result.get("metric", {}).get("__name__", ""),
                                "value": result.get("value", [None, None])[1],
                                "timestamp": result.get("value", [None, None])[0],
                                "labels": result.get("metric", {}),
                            })
            
            return PluginResult(success=True, data={"metrics": metrics})
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def acknowledge_alert(self, alert_id: str) -> PluginResult:
        """Acknowledge alert in Alertmanager."""
        try:
            # Alertmanager silence API
            url = f"{self.config.get('alertmanager_url', self.api_url)}/api/v2/silences"
            data = {
                "matchers": [{"name": "alertname", "value": alert_id}],
                "startsAt": "now",
                "endsAt": "1h",
                "comment": "Acknowledged by AMFI platform",
            }
            response = await self.client.post(url, json=data)
            
            if response.status_code == 200:
                return PluginResult(success=True, data={"message": "Alert silenced/acknowledged"})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    def _map_severity(self, severity: str) -> str:
        """Map Prometheus severity to standard levels."""
        mapping = {
            "critical": "critical",
            "warning": "major",
            "info": "minor",
        }
        return mapping.get(severity.lower(), "minor")
