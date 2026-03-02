"""NMS (Network Management System) plugins."""
from backend.plugins.nms.solarwinds import SolarWindsPlugin
from backend.plugins.nms.nagios import NagiosPlugin
from backend.plugins.nms.zabbix import ZabbixPlugin
from backend.plugins.nms.prtg import PRTGPlugin
from backend.plugins.nms.prometheus import PrometheusPlugin

__all__ = [
    "SolarWindsPlugin",
    "NagiosPlugin",
    "ZabbixPlugin",
    "PRTGPlugin",
    "PrometheusPlugin",
]
