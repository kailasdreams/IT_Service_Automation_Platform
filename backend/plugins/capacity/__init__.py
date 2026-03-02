"""Capacity Planning plugins."""
from backend.plugins.capacity.monitoring import CapacityMonitoringPlugin
from backend.plugins.capacity.forecasting import CapacityForecastingPlugin

__all__ = [
    "CapacityMonitoringPlugin",
    "CapacityForecastingPlugin",
]
