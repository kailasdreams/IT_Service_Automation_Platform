"""Slack ChatOps plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.chatops.base import BaseChatOpsPlugin
from backend.plugins.base import PluginResult


class SlackPlugin(BaseChatOpsPlugin):
    """Slack integration plugin."""
    
    version = "1.0.0"
    description = "Slack ChatOps connector - API, Webhooks, Bot integration"
    
    def get_required_config_fields(self) -> List[str]:
        return ["webhook_url"]  # or api_key for bot
    
    async def send_message(self, channel: str, message: str, **kwargs) -> PluginResult:
        """Send message to Slack channel."""
        try:
            if self.webhook_url:
                # Webhook method
                payload = {
                    "channel": channel,
                    "text": message,
                    **kwargs,
                }
                response = await self.client.post(self.webhook_url, json=payload)
            else:
                # Bot API method
                url = "https://slack.com/api/chat.postMessage"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {
                    "channel": channel,
                    "text": message,
                    **kwargs,
                }
                response = await self.client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    return PluginResult(success=True, data={"message": "Sent to Slack"})
                return PluginResult(success=False, error=result.get("error", "Unknown error"))
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def send_alert(self, title: str, message: str, severity: str = "info", **kwargs) -> PluginResult:
        """Send formatted alert to Slack."""
        try:
            color_map = {
                "critical": "#FF0000",
                "high": "#FF6600",
                "major": "#FF9900",
                "medium": "#FFCC00",
                "minor": "#FFFF00",
                "info": "#00CCFF",
            }
            payload = {
                "attachments": [
                    {
                        "color": color_map.get(severity.lower(), "#00CCFF"),
                        "title": title,
                        "text": message,
                        "fields": kwargs.get("fields", []),
                        "footer": "AMFI Platform",
                        "ts": kwargs.get("timestamp"),
                    }
                ],
                **kwargs,
            }
            return await self.send_message(kwargs.get("channel", "#alerts"), "", **payload)
        except Exception as e:
            return PluginResult(success=False, error=str(e))
