"""Plugin system for IT Service Automation Platform."""
from backend.plugins.base import BasePlugin, PluginType, PluginResult
from backend.plugins.registry import PluginRegistry

__all__ = ["BasePlugin", "PluginType", "PluginResult", "PluginRegistry"]
