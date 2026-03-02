"""Base ITSM plugin."""
from typing import Dict, Any, Optional
from backend.plugins.base import BasePlugin, PluginType, PluginResult
import httpx


class BaseITSMPlugin(BasePlugin):
    """Base class for ITSM connectors."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, PluginType.ITSM, config)
        self.api_url = self.config.get("api_url", "")
        self.api_key = self.config.get("api_key", "")
        self.client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self) -> PluginResult:
        """Initialize HTTP client."""
        try:
            await self.validate_config()
            self.client = httpx.AsyncClient(
                base_url=self.api_url,
                timeout=30,
                headers=self.get_auth_headers(),
            )
            return PluginResult(success=True, data={"message": f"{self.name} initialized"})
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def create_ticket(self, title: str, description: str, priority: str = "medium", **kwargs) -> PluginResult:
        """Create incident/ticket."""
        raise NotImplementedError("Subclasses must implement create_ticket")
    
    async def update_ticket(self, ticket_id: str, **kwargs) -> PluginResult:
        """Update ticket."""
        raise NotImplementedError("Subclasses must implement update_ticket")
    
    async def get_ticket(self, ticket_id: str) -> PluginResult:
        """Get ticket details."""
        raise NotImplementedError("Subclasses must implement get_ticket")
    
    async def search_tickets(self, filters: Optional[Dict[str, Any]] = None) -> PluginResult:
        """Search tickets."""
        raise NotImplementedError("Subclasses must implement search_tickets")
    
    async def execute(self, action: str, **kwargs) -> PluginResult:
        """Execute ITSM action."""
        action_map = {
            "create_ticket": self.create_ticket,
            "update_ticket": self.update_ticket,
            "get_ticket": self.get_ticket,
            "search_tickets": self.search_tickets,
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
