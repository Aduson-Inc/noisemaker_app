"""
NoiseMaker Backend API - FastAPI Application
Production-ready REST API with DynamoDB integration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
# Uses client IP address for rate limiting
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="NoiseMaker API",
    description="Automated social media promotion for music artists",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Attach rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local frontend
        "http://localhost:3001",  # Alternative local port
        "https://noisemaker.doowopp.com",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API status check"""
    return {
        "message": "NoiseMaker API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "noisemaker-api"
    }

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# Import and include routers
from routes import auth, platforms, dashboard, payment, frank_art, songs, templates

# Auth routes
app.include_router(auth.router)

# Songs routes
app.include_router(songs.router)

# Platform OAuth routes (includes 2 routers)
platform_routers = platforms.get_routers()
for platform_router in platform_routers:
    app.include_router(platform_router)

# Dashboard routes (includes 2 routers)
dashboard_routers = dashboard.get_routers()
for dashboard_router in dashboard_routers:
    app.include_router(dashboard_router)

# Payment routes
app.include_router(payment.router)

# Frank's Garage routes (AI-generated artwork marketplace)
app.include_router(frank_art.router)

# Admin template management routes
app.include_router(templates.router)

logger.info("NoiseMaker API initialized successfully with all routes")
