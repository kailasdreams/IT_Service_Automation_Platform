"""Microsoft Teams ChatOps plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.chatops.base import BaseChatOpsPlugin
from backend.plugins.base import PluginResult


class MSTeamsPlugin(BaseChatOpsPlugin):
    """Microsoft Teams integration plugin."""
    
    version = "1.0.0"
    description = "Microsoft Teams ChatOps connector - Graph API, Connectors integration"
    
    def get_required_config_fields(self) -> List[str]:
        return ["webhook_url"]  # or api_key for Graph API
    
    async def send_message(self, channel: str, message: str, **kwargs) -> PluginResult:
        """Send message to Teams channel."""
        try:
            if self.webhook_url:
                # Incoming Webhook
                payload = {
                    "@type": "MessageCard",
                    "@context": "https://schema.org/extensions",
                    "summary": kwargs.get("summary", message),
                    "themeColor": kwargs.get("color", "0078D4"),
                    "sections": [
                        {
                            "activityTitle": kwargs.get("title", "Notification"),
                            "text": message,
                        }
                    ],
                }
                response = await self.client.post(self.webhook_url, json=payload)
            else:
                # Graph API method
                url = f"https://graph.microsoft.com/v1.0/teams/{channel}/channels/{channel}/messages"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {
                    "body": {
                        "contentType": "html",
                        "content": message,
                    }
                }
                response = await self.client.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                return PluginResult(success=True, data={"message": "Sent to Teams"})
            return PluginResult(success=False, error=f"API error: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def send_alert(self, title: str, message: str, severity: str = "info", **kwargs) -> PluginResult:
        """Send formatted alert to Teams."""
        try:
            color_map = {
                "critical": "FF0000",
                "high": "FF6600",
                "major": "FF9900",
                "medium": "FFCC00",
                "minor": "FFFF00",
                "info": "00CCFF",
            }
            payload = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": title,
                "themeColor": color_map.get(severity.lower(), "00CCFF"),
                "sections": [
                    {
                        "activityTitle": title,
                        "activitySubtitle": severity.upper(),
                        "text": message,
                        "facts": kwargs.get("facts", []),
                    }
                ],
            }
            return await self.send_message(kwargs.get("channel", ""), "", **payload)
        except Exception as e:
            return PluginResult(success=False, error=str(e))
