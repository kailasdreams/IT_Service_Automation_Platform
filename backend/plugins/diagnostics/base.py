"""Base Diagnostic plugin."""
from typing import Dict, Any, Optional, List
from enum import Enum
from backend.plugins.base import BasePlugin, PluginType, PluginResult


class DiagnosticLevel(str, Enum):
    """Diagnostic level."""
    L1 = "l1"  # Automated first response
    L2 = "l2"  # Advanced root cause analysis


class BaseDiagnosticPlugin(BasePlugin):
    """Base class for diagnostic workflows."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, PluginType.DIAGNOSTIC, config)
        self.device_ip = self.config.get("device_ip", "")
        self.username = self.config.get("username", "")
        self.password = self.config.get("password", "")
    
    async def initialize(self) -> PluginResult:
        """Initialize diagnostic plugin."""
        try:
            await self.validate_config()
            return PluginResult(success=True, data={"message": f"{self.name} initialized"})
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def run_l1_diagnostics(self, resource_id: str, issue_type: str) -> PluginResult:
        """Run Level 1 diagnostics (automated first response)."""
        raise NotImplementedError("Subclasses must implement run_l1_diagnostics")
    
    async def run_l2_diagnostics(self, resource_id: str, issue_type: str) -> PluginResult:
        """Run Level 2 diagnostics (advanced root cause analysis)."""
        raise NotImplementedError("Subclasses must implement run_l2_diagnostics")
    
    async def execute_remediation(self, action: str, resource_id: str, **kwargs) -> PluginResult:
        """Execute remediation action."""
        raise NotImplementedError("Subclasses must implement execute_remediation")
    
    async def execute(self, level: str, resource_id: str, issue_type: str, **kwargs) -> PluginResult:
        """Execute diagnostic workflow."""
        if level == DiagnosticLevel.L1.value:
            return await self.run_l1_diagnostics(resource_id, issue_type)
        elif level == DiagnosticLevel.L2.value:
            return await self.run_l2_diagnostics(resource_id, issue_type)
        else:
            return PluginResult(success=False, error=f"Unknown diagnostic level: {level}")
