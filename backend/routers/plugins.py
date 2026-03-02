"""Plugin management API."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from backend.database import get_db
from backend.models import Integration
from backend.plugins.registry import registry
from backend.plugins.base import PluginType
from backend.plugins.loader import load_all_plugins

router = APIRouter()

# Ensure plugins are loaded
load_all_plugins()


class PluginInfo(BaseModel):
    """Plugin information."""
    name: str
    type: str
    version: str
    description: str
    enabled: bool
    config: Optional[Dict[str, Any]] = None


class PluginExecuteRequest(BaseModel):
    """Plugin execution request."""
    plugin_name: str
    action: str
    parameters: Optional[Dict[str, Any]] = None


@router.get("/list", response_model=List[str])
async def list_plugin_classes():
    """List all available plugin classes."""
    return registry.list_plugin_classes()


@router.get("/instances", response_model=List[PluginInfo])
async def list_plugin_instances():
    """List all plugin instances."""
    plugins = registry.list_plugins()
    return [PluginInfo(**p) for p in plugins]


@router.get("/instances/{plugin_name}", response_model=PluginInfo)
async def get_plugin_instance(plugin_name: str):
    """Get plugin instance by name."""
    plugin = registry.get_plugin(plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return PluginInfo(**plugin.to_dict())


@router.get("/by-type/{plugin_type}", response_model=List[PluginInfo])
async def get_plugins_by_type(plugin_type: str):
    """Get plugins by type."""
    try:
        ptype = PluginType(plugin_type)
        plugins = registry.get_plugins_by_type(ptype)
        return [PluginInfo(**p.to_dict()) for p in plugins]
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid plugin type: {plugin_type}")


@router.post("/create")
async def create_plugin_instance(
    name: str,
    plugin_type: str,
    config: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
):
    """Create plugin instance from integration."""
    try:
        ptype = PluginType(plugin_type)
        plugin = registry.create_plugin(name, ptype, config)
        
        if not plugin:
            raise HTTPException(status_code=400, detail=f"Could not create plugin: {name}")
        
        # Initialize plugin
        init_result = await plugin.initialize()
        if not init_result.success:
            raise HTTPException(status_code=400, detail=f"Plugin initialization failed: {init_result.error}")
        
        # Add to registry
        registry.add_plugin(plugin)
        
        # Optionally save to database
        integration = Integration(
            name=name,
            type=plugin_type,
            enabled=plugin.enabled,
            config=config or {},
        )
        db.add(integration)
        await db.commit()
        await db.refresh(integration)
        
        return {
            "message": "Plugin created",
            "plugin": plugin.to_dict(),
            "integration_id": integration.id,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid plugin type: {plugin_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_plugin(request: PluginExecuteRequest):
    """Execute plugin action."""
    plugin = registry.get_plugin(request.plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    if not plugin.enabled:
        raise HTTPException(status_code=400, detail="Plugin is disabled")
    
    try:
        result = await plugin.execute(action=request.action, **(request.parameters or {}))
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize-all")
async def initialize_all_plugins():
    """Initialize all enabled plugins."""
    results = await registry.initialize_all()
    return {
        "message": "Initialization completed",
        "results": {name: r.to_dict() for name, r in results.items()},
    }


@router.post("/health-check-all")
async def health_check_all_plugins():
    """Health check all enabled plugins."""
    results = await registry.health_check_all()
    return {
        "message": "Health check completed",
        "results": {name: r.to_dict() for name, r in results.items()},
    }


@router.post("/load-from-integrations")
async def load_plugins_from_integrations(db: AsyncSession = Depends(get_db)):
    """Load plugin instances from database integrations."""
    result = await db.execute(select(Integration).where(Integration.enabled == True))
    integrations = result.scalars().all()
    
    loaded = []
    errors = []
    
    for integration in integrations:
        try:
            plugin = registry.create_plugin(integration.name, PluginType(integration.type), integration.config)
            if plugin:
                init_result = await plugin.initialize()
                if init_result.success:
                    registry.add_plugin(plugin)
                    loaded.append(integration.name)
                else:
                    errors.append(f"{integration.name}: {init_result.error}")
            else:
                errors.append(f"{integration.name}: Could not create plugin")
        except Exception as e:
            errors.append(f"{integration.name}: {str(e)}")
    
    return {
        "message": "Plugins loaded from integrations",
        "loaded": loaded,
        "errors": errors,
    }
