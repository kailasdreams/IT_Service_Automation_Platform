"""IT Service Automation Platform - FastAPI Application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import init_db
from backend.models import Incident, Event, Integration, User  # noqa: F401 - register models
from backend.routers import incidents, events, integrations, auth, metrics, plugins, gateway, chatbot
from backend.gateway import RateLimitMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    await init_db()
    yield
    # shutdown cleanup if needed


app = FastAPI(
    title=settings.app_name,
    description="Comprehensive Architecture for ITIL Process Automation, NMS Integration & Automated Troubleshooting",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

app.include_router(gateway.router, prefix="/api/gateway", tags=["API Gateway"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["ChatBot"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(plugins.router, prefix="/api/plugins", tags=["Plugins"])


@app.get("/")
async def root():
    return {
        "message": "IT Service Automation Platform API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy"}
