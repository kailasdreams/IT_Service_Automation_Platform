"""Plugin loader - registers all plugins."""
from backend.plugins.registry import registry

# NMS Plugins
from backend.plugins.nms import (
    SolarWindsPlugin,
    NagiosPlugin,
    ZabbixPlugin,
    PRTGPlugin,
    PrometheusPlugin,
)

# ITSM Plugins
from backend.plugins.itsm import (
    ServiceNowPlugin,
    JiraPlugin,
    BMCRemedyPlugin,
)

# ChatOps Plugins
from backend.plugins.chatops import (
    SlackPlugin,
    MSTeamsPlugin,
    PagerDutyPlugin,
)

# Diagnostic Plugins
from backend.plugins.diagnostics import (
    CiscoACIPlugin,
    SDWANPlugin,
    ServerPlugin,
    SANSwitchPlugin,
    NetworkSwitchPlugin,
    FirewallPlugin,
    F5LoadBalancerPlugin,
)

# Event Processing Plugins
from backend.plugins.event_processing import (
    EventEnrichmentPlugin,
    EventCorrelationPlugin,
    DecisionEnginePlugin,
)

# ITIL Process Plugins
from backend.plugins.itil_process import (
    IncidentManagementPlugin,
    ProblemManagementPlugin,
    ChangeManagementPlugin,
)

# Capacity Plugins
from backend.plugins.capacity import (
    CapacityMonitoringPlugin,
    CapacityForecastingPlugin,
)


def load_all_plugins():
    """Register all plugin classes."""
    # NMS
    registry.register(SolarWindsPlugin, "solarwinds")
    registry.register(NagiosPlugin, "nagios")
    registry.register(ZabbixPlugin, "zabbix")
    registry.register(PRTGPlugin, "prtg")
    registry.register(PrometheusPlugin, "prometheus")
    
    # ITSM
    registry.register(ServiceNowPlugin, "servicenow")
    registry.register(JiraPlugin, "jira")
    registry.register(BMCRemedyPlugin, "bmc_remedy")
    
    # ChatOps
    registry.register(SlackPlugin, "slack")
    registry.register(MSTeamsPlugin, "teams")
    registry.register(PagerDutyPlugin, "pagerduty")
    
    # Diagnostics
    registry.register(CiscoACIPlugin, "cisco_aci")
    registry.register(SDWANPlugin, "sdwan")
    registry.register(ServerPlugin, "server")
    registry.register(SANSwitchPlugin, "san_switch")
    registry.register(NetworkSwitchPlugin, "network_switch")
    registry.register(FirewallPlugin, "firewall")
    registry.register(F5LoadBalancerPlugin, "f5_loadbalancer")
    
    # Event Processing
    registry.register(EventEnrichmentPlugin, "event_enrichment")
    registry.register(EventCorrelationPlugin, "event_correlation")
    registry.register(DecisionEnginePlugin, "decision_engine")
    
    # ITIL Processes
    registry.register(IncidentManagementPlugin, "incident_management")
    registry.register(ProblemManagementPlugin, "problem_management")
    registry.register(ChangeManagementPlugin, "change_management")
    
    # Capacity
    registry.register(CapacityMonitoringPlugin, "capacity_monitoring")
    registry.register(CapacityForecastingPlugin, "capacity_forecasting")


# Auto-load on import
load_all_plugins()
