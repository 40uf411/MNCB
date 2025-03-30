"""
API router setup for v1 endpoints.
"""
from fastapi import APIRouter

from src.presentation.api.v1.endpoints import auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
