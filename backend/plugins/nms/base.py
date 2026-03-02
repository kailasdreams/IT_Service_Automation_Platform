"""Base NMS plugin."""
from typing import Dict, Any, Optional, List
from backend.plugins.base import BasePlugin, PluginType, PluginResult
import httpx
from datetime import datetime


class BaseNMSPlugin(BasePlugin):
    """Base class for NMS connectors."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, PluginType.NMS, config)
        self.api_url = self.config.get("api_url", "")
        self.api_key = self.config.get("api_key", "")
        self.timeout = self.config.get("timeout", 30)
        self.client: Optional[httpx.AsyncClient] = None
    
    def get_required_config_fields(self) -> List[str]:
        return ["api_url", "api_key"]
    
    async def initialize(self) -> PluginResult:
        """Initialize HTTP client."""
        try:
            await self.validate_config()
            self.client = httpx.AsyncClient(
                base_url=self.api_url,
                timeout=self.timeout,
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
    
    async def fetch_alerts(self, filters: Optional[Dict[str, Any]] = None) -> PluginResult:
        """Fetch alerts/alarms from NMS."""
        raise NotImplementedError("Subclasses must implement fetch_alerts")
    
    async def fetch_metrics(self, resource_id: str, metric_names: List[str]) -> PluginResult:
        """Fetch metrics for a resource."""
        raise NotImplementedError("Subclasses must implement fetch_metrics")
    
    async def acknowledge_alert(self, alert_id: str) -> PluginResult:
        """Acknowledge an alert."""
        raise NotImplementedError("Subclasses must implement acknowledge_alert")
    
    async def health_check(self) -> PluginResult:
        """Check NMS connectivity."""
        if not self.client:
            return PluginResult(success=False, error="Plugin not initialized")
        try:
            # Try a simple API call
            response = await self.client.get("/health", timeout=5)
            if response.status_code == 200:
                return PluginResult(success=True, data={"status": "healthy"})
            return PluginResult(success=False, error=f"Health check failed: {response.status_code}")
        except Exception as e:
            return PluginResult(success=False, error=f"Health check error: {str(e)}")
    
    async def cleanup(self) -> PluginResult:
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
        return PluginResult(success=True)
    
    async def execute(self, action: str, **kwargs) -> PluginResult:
        """Execute NMS action."""
        action_map = {
            "fetch_alerts": self.fetch_alerts,
            "fetch_metrics": self.fetch_metrics,
            "acknowledge_alert": self.acknowledge_alert,
        }
        handler = action_map.get(action)
        if not handler:
            return PluginResult(success=False, error=f"Unknown action: {action}")
        try:
            return await handler(**kwargs)
        except Exception as e:
            return PluginResult(success=False, error=str(e))
