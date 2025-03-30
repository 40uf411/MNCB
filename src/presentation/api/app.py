"""
Main FastAPI application setup.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.presentation.api.v1.api import api_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="FastAPI Application",
        description="FastAPI application with PostgreSQL, DragonFlyDB, and JWT OAuth2 authentication",
        version="0.1.0",
    )
    
    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/")
    def root():
        """Root endpoint."""
        return {"message": "Welcome to the FastAPI application"}
    
    return app

app = create_app()
