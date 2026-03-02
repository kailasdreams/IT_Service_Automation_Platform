"""Base ChatOps plugin."""
from typing import Dict, Any, Optional
from backend.plugins.base import BasePlugin, PluginType, PluginResult
import httpx


class BaseChatOpsPlugin(BasePlugin):
    """Base class for ChatOps integrations."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, PluginType.CHAT, config)
        self.webhook_url = self.config.get("webhook_url", "")
        self.api_key = self.config.get("api_key", "")
        self.client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self) -> PluginResult:
        """Initialize HTTP client."""
        try:
            await self.validate_config()
            self.client = httpx.AsyncClient(timeout=30)
            return PluginResult(success=True, data={"message": f"{self.name} initialized"})
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def send_message(self, channel: str, message: str, **kwargs) -> PluginResult:
        """Send message to channel."""
        raise NotImplementedError("Subclasses must implement send_message")
    
    async def send_alert(self, title: str, message: str, severity: str = "info", **kwargs) -> PluginResult:
        """Send alert/notification."""
        raise NotImplementedError("Subclasses must implement send_alert")
    
    async def execute(self, action: str, **kwargs) -> PluginResult:
        """Execute ChatOps action."""
        action_map = {
            "send_message": self.send_message,
            "send_alert": self.send_alert,
        }
        handler = action_map.get(action)
        if not handler:
            return PluginResult(success=False, error=f"Unknown action: {action}")
        try:
            return await handler(**kwargs)
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def cleanup(self) -> PluginResult:
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
        return PluginResult(success=True)
