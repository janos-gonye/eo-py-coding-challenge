"""
Main module for the Public API application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from public_api import constants
from public_api.routers.ip import router as ip_router
from public_api.app_logging import setup_logging

setup_logging()

app = FastAPI(title="Public API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=constants.CORS_ALLOW_ORIGINS,
    allow_methods=constants.CORS_ALLOW_METHODS,
    allow_headers=constants.CORS_ALLOW_HEADERS,
)

app.include_router(ip_router)
