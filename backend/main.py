from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from routes_enhanced import router
from services.utils import setup_logging
from config import settings

# Setup logging
setup_logging(log_dir=str(settings.LOG_DIR), log_level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Convert images to PDF with preprocessing and metadata support",
    version=settings.APP_VERSION,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Output directory: {settings.OUTPUT_DIR.absolute()}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "convert_multiple": "POST /convert",
            "convert_single": "POST /convert-single",
            "download": "GET /download/{filename}",
        },
    }


if __name__ == "__main__":
    import firebase_admin
    from firebase_admin import credentials
    cred=credentials.Certificate("/home/lmthp22/Dev/img-to-pdf-app/backend/serviceaccountkey.json")
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
