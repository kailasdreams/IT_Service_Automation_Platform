"""API Gateway – info and health for the gateway layer."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/info")
async def gateway_info():
    """API Gateway information (centralized entry point)."""
    return {
        "gateway": "API Gateway",
        "version": "1.0.0",
        "description": "Centralized entry point for all API requests with authentication and rate limiting",
        "endpoints": {
            "incidents": "/api/incidents",
            "events": "/api/events",
            "integrations": "/api/integrations",
            "auth": "/api/auth",
            "metrics": "/api/metrics",
            "plugins": "/api/plugins",
            "chatbot": "/api/chatbot",
        },
        "docs": "/docs",
    }
