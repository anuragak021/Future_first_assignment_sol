# main — FastAPI application entrypoint
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, health, trace
from app.config import getSettings
from app.observability.logging import configureLogging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configureLogging()
    logger.info("Secure AI Insights Assistant starting up")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Secure AI Insights Assistant",
    version="1.0.0",
    description="Multi-agent analytics assistant for internal entertainment data",
    lifespan=lifespan,
)

_origins = [o.strip() for o in getSettings().allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(trace.router, prefix="/api/v1", tags=["trace"])


@app.get("/")
async def root():
    return {"message": "Secure AI Insights Assistant API", "docs": "/docs"}
