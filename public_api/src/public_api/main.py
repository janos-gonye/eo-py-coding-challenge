"""
Main module for the Public API application.
"""

from fastapi import FastAPI
from public_api.routers.ip import router as ip_router

from public_api.app_logging import setup_logging

setup_logging()

app = FastAPI(title="Public API")

app.include_router(ip_router)
