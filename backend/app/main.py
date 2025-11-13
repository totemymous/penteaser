"""
XSS Assistant - FastAPI Application Entry Point

This is the main application file for the XSS Assistant backend.
It sets up the FastAPI app, includes routers, and configures middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .config import settings
from .database import engine, Base
from .routers import health, targets, sessions, reports

# Create database tables (for demo - use Alembic migrations in production)
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Human-in-the-loop XSS testing assistant for authorized penetration testing",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(targets.router)
app.include_router(sessions.router)
app.include_router(reports.router)

# Mount frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_dashboard():
        """Serve the dashboard UI"""
        index_path = os.path.join(frontend_path, "index.html")
        return FileResponse(index_path)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🚀 {settings.app_name} v{settings.app_version} starting...")
    print(f"📝 API docs available at: /docs")
    print(f"🔍 Health check: /health")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print(f"👋 {settings.app_name} shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
