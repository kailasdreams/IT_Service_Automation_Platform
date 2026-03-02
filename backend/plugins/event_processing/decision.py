"""Decision Engine plugin."""
from typing import Dict, Any, Optional
from backend.plugins.base import BasePlugin, PluginType, PluginResult


class DecisionEnginePlugin(BasePlugin):
    """Decision engine plugin - rule evaluation, priority calculation, action selection."""
    
    version = "1.0.0"
    description = "Decision engine - rule evaluation, priority calculation, action selection, workflow selection"
    
    def __init__(self, name: str = "decision_engine", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, PluginType.EVENT_PROCESSOR, config)
        self.rules = self.config.get("rules", [])
    
    async def initialize(self) -> PluginResult:
        """Initialize decision engine."""
        return PluginResult(success=True, data={"message": "Decision engine initialized"})
    
    async def make_decision(self, event_data: Dict[str, Any]) -> PluginResult:
        """Make decision on event - auto-remediate, create ticket, or escalate."""
        try:
            # Rule Evaluation
            rule_result = self._evaluate_rules(event_data)
            
            # Priority Calculation
            priority = self._calculate_priority(event_data)
            
            # Action Selection
            action = self._select_action(event_data, rule_result)
            
            # Workflow Selection
            workflow = self._select_workflow(event_data, action)
            
            return PluginResult(
                success=True,
                data={
                    "priority": priority,
                    "action": action,
                    "workflow": workflow,
                    "rule_result": rule_result,
                }
            )
        except Exception as e:
            return PluginResult(success=False, error=str(e))
    
    async def execute(self, **kwargs) -> PluginResult:
        """Execute decision."""
        return await self.make_decision(kwargs.get("event_data", {}))
    
    def _evaluate_rules(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate business rules."""
        severity = event_data.get("severity", "medium")
        impact = event_data.get("impact_score", 5)
        
        # Simple rule: critical severity or high impact -> auto-remediate
        if severity == "critical" or impact >= 8:
            return {"action": "auto_remediate", "confidence": 0.9}
        
        # Medium severity -> create ticket
        if severity in ["high", "major"] or impact >= 5:
            return {"action": "create_ticket", "confidence": 0.8}
        
        # Low severity -> log only
        return {"action": "log", "confidence": 0.7}
    
    def _calculate_priority(self, event_data: Dict[str, Any]) -> str:
        """Calculate priority based on impact and urgency."""
        severity = event_data.get("severity", "medium")
        impact_score = event_data.get("impact_score", 5)
        urgency = event_data.get("urgency", "medium")
        
        if severity == "critical" or impact_score >= 8:
            return "critical"
        if severity in ["high", "major"] or impact_score >= 6:
            return "high"
        if severity == "medium" or impact_score >= 4:
            return "medium"
        return "low"
    
    def _select_action(self, event_data: Dict[str, Any], rule_result: Dict[str, Any]) -> str:
        """Select action: auto-remediate, create ticket, or escalate."""
        return rule_result.get("action", "create_ticket")
    
    def _select_workflow(self, event_data: Dict[str, Any], action: str) -> str:
        """Select appropriate workflow."""
        if action == "auto_remediate":
            return "diagnostic_l1"
        elif action == "create_ticket":
            return "incident_management"
        elif action == "escalate":
            return "escalation_workflow"
        return "default_workflow"
