"""
Main module for the Public API application.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from public_api.config import settings
from public_api.db import db
from public_api.routers.ip import router as ip_router
from public_api.app_logging import setup_logging
from public_api.models import create_tables
from public_api.ws import redis_listener, websocket_endpoint

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_instance: FastAPI):  # pylint: disable=unused-argument
    """Context manager for the application lifespan."""
    create_tables()
    # Start Redis listener in the background
    listener_task = asyncio.create_task(redis_listener())
    yield
    # Cleanup task on shutdown
    listener_task.cancel()
    try:
        await listener_task
        # We await the task to allow it to perform any internal 'finally' block cleanup.
        # This will always raise CancelledError once the task successfully terminates.
    except asyncio.CancelledError:
        logger.info("Redis listener task cancelled")


app = FastAPI(title="Public API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


@app.middleware("http")
async def db_connection_middleware(request: Request, call_next):
    """Manage Peewee database connection correctly per-request."""
    db.connect(reuse_if_open=True)
    try:
        return await call_next(request)
    finally:
        if not db.is_closed():
            db.close()


app.include_router(ip_router)

app.add_api_websocket_route("/ws", websocket_endpoint)
