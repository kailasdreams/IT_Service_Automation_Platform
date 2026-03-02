"""Diagnostic plugins for L1/L2 troubleshooting."""
from backend.plugins.diagnostics.cisco_aci import CiscoACIPlugin
from backend.plugins.diagnostics.sdwan import SDWANPlugin
from backend.plugins.diagnostics.server import ServerPlugin
from backend.plugins.diagnostics.san_switch import SANSwitchPlugin
from backend.plugins.diagnostics.network_switch import NetworkSwitchPlugin
from backend.plugins.diagnostics.firewall import FirewallPlugin
from backend.plugins.diagnostics.f5_loadbalancer import F5LoadBalancerPlugin

__all__ = [
    "CiscoACIPlugin",
    "SDWANPlugin",
    "ServerPlugin",
    "SANSwitchPlugin",
    "NetworkSwitchPlugin",
    "FirewallPlugin",
    "F5LoadBalancerPlugin",
]
