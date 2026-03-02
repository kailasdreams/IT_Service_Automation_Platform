"""Base plugin interface and types."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


class PluginType(str, Enum):
    """Plugin categories."""
    NMS = "nms"  # Network Management System connectors
    ITSM = "itsm"  # IT Service Management connectors
    CHAT = "chat"  # ChatOps integrations
    DIAGNOSTIC = "diagnostic"  # L1/L2 diagnostic workflows
    EVENT_PROCESSOR = "event_processor"  # Event enrichment, correlation, decision
    ITIL_PROCESS = "itil_process"  # ITIL workflows
    CAPACITY = "capacity"  # Capacity planning and forecasting
    CLOUD = "cloud"  # Cloud platform integrations


@dataclass
class PluginResult:
    """Result from plugin execution."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata or {},
        }


class BasePlugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, name: str, plugin_type: PluginType, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.plugin_type = plugin_type
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass
    
    @abstractmethod
    async def initialize(self) -> PluginResult:
        """Initialize plugin (connect, validate config, etc.)."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> PluginResult:
        """Execute plugin main functionality."""
        pass
    
    async def validate_config(self) -> PluginResult:
        """Validate plugin configuration."""
        required_fields = self.get_required_config_fields()
        missing = [f for f in required_fields if f not in self.config]
        if missing:
            return PluginResult(
                success=False,
                error=f"Missing required config fields: {', '.join(missing)}"
            )
        return PluginResult(success=True)
    
    def get_required_config_fields(self) -> List[str]:
        """Return list of required configuration fields."""
        return []
    
    async def health_check(self) -> PluginResult:
        """Check plugin health/connectivity."""
        return PluginResult(success=True, data={"status": "healthy"})
    
    async def cleanup(self) -> PluginResult:
        """Cleanup resources on shutdown."""
        return PluginResult(success=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plugin info to dictionary."""
        return {
            "name": self.name,
            "type": self.plugin_type.value,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled,
            "config": self.config,
        }
