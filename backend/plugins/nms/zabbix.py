"""Zabbix NMS plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.nms.base import BaseNMSPlugin
from backend.plugins.base import PluginResult


class ZabbixPlugin(BaseNMSPlugin):
    """Zabbix API connector."""
    
    version = "1.0.0"
    description = "Zabbix NMS connector - REST API, Webhooks integration"
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.auth_token: Optional[str] = None
    
    async def initialize(self) -> PluginResult:
        """Initialize Zabbix connection and authenticate."""
        result = await super().initialize()
        if not result.success:
            return result
        
        # Zabbix uses JSON-RPC API
        try:
            auth_url = f"{self.api_url}/api_jsonrpc.php"
            auth_payload = {
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                    "user": self.config.get("username"),
                    "password": self.config.get("password"),
                },
                "id": 1,
            }
            response = await self.client.post(auth_url, json=auth_payload)
            
            if response.status_code == 200:
                result_data = response.json()
                if "result" in result_data:
                    self.auth_token = result_data["result"]
                    return PluginResult(success=True, data={"message": "Zabbix authenticated"})
                return PluginResult(success=False, error=result_data.get("error", {}).get("message", "Auth failed"))
            return PluginResult(success=False, error=f"Auth error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def _rpc_call(self, method: str, params: Dict[str, Any]) -> PluginResult:
        """Make Zabbix JSON-RPC call."""
        try:
            url = f"{self.api_url}/api_jsonrpc.php"
            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "auth": self.auth_token,
                "id": 1,
            }
            response = await self.client.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if "error" in result:
                    return PluginResult(success=False, error=result["error"].get("message", "RPC error"))
                return PluginResult(success=True, data=result.get("result"))
            return PluginResult(success=False, error=f"RPC error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def fetch_alerts(self, filters: Optional[Dict[str, Any]] = None) -> PluginResult:
        """Fetch triggers (alerts) from Zabbix."""
        try:
            params = {
                "output": "extend",
                "selectHosts": ["host"],
                "selectItems": ["name"],
                "filter": {"value": 1},  # Only active triggers
            }
            if filters:
                params.update(filters)
            
            result = await self._rpc_call("trigger.get", params)
            if not result.success:
                return result
            
            triggers = result.data or []
            alerts = [
                {
                    "id": str(trigger.get("triggerid")),
                    "source": "zabbix",
                    "severity": self._map_priority(trigger.get("priority")),
                    "message": trigger.get("description", ""),
                    "resource": trigger.get("hosts", [{}])[0].get("host", ""),
                    "timestamp": trigger.get("lastchange"),
                    "raw": trigger,
                }
                for trigger in triggers
            ]
            return PluginResult(success=True, data={"alerts": alerts})
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def fetch_metrics(self, resource_id: str, metric_names: List[str]) -> PluginResult:
        """Fetch metrics from Zabbix."""
        try:
            params = {
                "output": "extend",
                "hostids": resource_id,
                "search": {"name": metric_names[0] if metric_names else ""},
            }
            result = await self._rpc_call("item.get", params)
            if not result.success:
                return result
            
            # Get history values
            items = result.data or []
            metrics = []
            for item in items[:len(metric_names)]:
                history_params = {
                    "itemids": item.get("itemid"),
                    "history": 0,  # Numeric values
                    "limit": 1,
                }
                history_result = await self._rpc_call("history.get", history_params)
                if history_result.success and history_result.data:
                    metrics.append({
                        "name": item.get("name"),
                        "value": history_result.data[0].get("value"),
                        "timestamp": history_result.data[0].get("clock"),
                    })
            
            return PluginResult(success=True, data={"metrics": metrics})
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def acknowledge_alert(self, alert_id: str) -> PluginResult:
        """Acknowledge trigger in Zabbix."""
        try:
            params = {
                "eventids": alert_id,
                "action": 1,  # Acknowledge
                "message": "Acknowledged by AMFI platform",
            }
            return await self._rpc_call("event.acknowledge", params)
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    def _map_priority(self, priority: str) -> str:
        """Map Zabbix priority to standard severity."""
        mapping = {
            "0": "info",
            "1": "minor",
            "2": "major",
            "3": "major",
            "4": "critical",
            "5": "critical",
        }
        return mapping.get(str(priority), "minor")
