"""Plugin registry and manager."""
from typing import Dict, List, Optional, Type
from backend.plugins.base import BasePlugin, PluginType, PluginResult


class PluginRegistry:
    """Central registry for all plugins."""
    
    _instance: Optional['PluginRegistry'] = None
    _plugins: Dict[str, BasePlugin] = {}
    _plugin_classes: Dict[str, Type[BasePlugin]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, plugin_class: Type[BasePlugin], name: Optional[str] = None):
        """Register a plugin class."""
        plugin_name = name or plugin_class.__name__.lower().replace("plugin", "")
        self._plugin_classes[plugin_name] = plugin_class
    
    def create_plugin(
        self,
        name: str,
        plugin_type: PluginType,
        config: Optional[Dict] = None
    ) -> Optional[BasePlugin]:
        """Create plugin instance from registry."""
        # Try to find by name first
        plugin_class = self._plugin_classes.get(name)
        if not plugin_class:
            # Try to find by type
            for cls_name, cls in self._plugin_classes.items():
                if hasattr(cls, 'plugin_type') and cls.plugin_type == plugin_type:
                    plugin_class = cls
                    break
        
        if plugin_class:
            return plugin_class(name=name, plugin_type=plugin_type, config=config)
        return None
    
    def add_plugin(self, plugin: BasePlugin):
        """Add plugin instance to registry."""
        self._plugins[plugin.name] = plugin
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get plugin by name."""
        return self._plugins.get(name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[BasePlugin]:
        """Get all plugins of a specific type."""
        return [p for p in self._plugins.values() if p.plugin_type == plugin_type]
    
    def list_plugins(self) -> List[Dict]:
        """List all registered plugins."""
        return [p.to_dict() for p in self._plugins.values()]
    
    def list_plugin_classes(self) -> List[str]:
        """List all registered plugin class names."""
        return list(self._plugin_classes.keys())
    
    async def initialize_all(self) -> Dict[str, PluginResult]:
        """Initialize all enabled plugins."""
        results = {}
        for name, plugin in self._plugins.items():
            if plugin.enabled:
                try:
                    result = await plugin.initialize()
                    results[name] = result
                except Exception as e:
                    results[name] = PluginResult(
                        success=False,
                        error=f"Initialization error: {str(e)}"
                    )
        return results
    
    async def health_check_all(self) -> Dict[str, PluginResult]:
        """Health check all enabled plugins."""
        results = {}
        for name, plugin in self._plugins.items():
            if plugin.enabled:
                try:
                    result = await plugin.health_check()
                    results[name] = result
                except Exception as e:
                    results[name] = PluginResult(
                        success=False,
                        error=f"Health check error: {str(e)}"
                    )
        return results


# Global registry instance
registry = PluginRegistry()
