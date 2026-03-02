"""PagerDuty ChatOps plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.chatops.base import BaseChatOpsPlugin
from backend.plugins.base import PluginResult


class PagerDutyPlugin(BaseChatOpsPlugin):
    """PagerDuty integration plugin."""
    
    version = "1.0.0"
    description = "PagerDuty ChatOps connector - Events API v2 integration"
    
    def get_required_config_fields(self) -> List[str]:
        return ["api_key", "integration_key"]
    
    async def send_message(self, channel: str, message: str, **kwargs) -> PluginResult:
        """PagerDuty doesn't support general messages, use send_alert."""
        return PluginResult(success=False, error="Use send_alert for PagerDuty")
    
    async def send_alert(self, title: str, message: str, severity: str = "info", **kwargs) -> PluginResult:
        """Send incident/alert to PagerDuty."""
        try:
            integration_key = self.config.get("integration_key", "")
            url = "https://events.pagerduty.com/v2/enqueue"
            
            severity_map = {
                "critical": "critical",
                "high": "error",
                "major": "error",
                "medium": "warning",
                "minor": "warning",
                "info": "info",
            }
            
            payload = {
                "routing_key": integration_key,
                "event_action": kwargs.get("action", "trigger"),  # trigger, acknowledge, resolve
                "payload": {
                    "summary": title,
                    "source": kwargs.get("source", "AMFI Platform"),
                    "severity": severity_map.get(severity.lower(), "info"),
                    "custom_details": {
                        "message": message,
                        **kwargs.get("details", {}),
                    },
                },
            }
            
            if kwargs.get("dedup_key"):
                payload["dedup_key"] = kwargs["dedup_key"]
            
            headers = {"Content-Type": "application/json"}
            response = await self.client.post(url, headers=headers, json=payload)
            
            if response.status_code == 202:
                result = response.json()
                return PluginResult(
                    success=True,
                    data={
                        "message": "Alert sent to PagerDuty",
                        "dedup_key": result.get("dedup_key"),
                        "status": result.get("status"),
                    }
                )
            return PluginResult(success=False, error=f"API error: {response.status_code} - {response.text}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def acknowledge_incident(self, dedup_key: str) -> PluginResult:
        """Acknowledge PagerDuty incident."""
        return await self.send_alert("", "", action="acknowledge", dedup_key=dedup_key)
    
    async def resolve_incident(self, dedup_key: str) -> PluginResult:
        """Resolve PagerDuty incident."""
        return await self.send_alert("", "", action="resolve", dedup_key=dedup_key)
