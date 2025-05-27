from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

from app.models.database import create_tables, connect_db, disconnect_db
from app.api.domains import router as domains_router
from app.api.notifications import router as notifications_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting DomainPing API...")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")
    
    # Connect to database
    await connect_db()
    logger.info("Database connected")
    
    yield
    
    # Shutdown
    logger.info("Shutting down DomainPing API...")
    await disconnect_db()
    logger.info("Database disconnected")

# Create FastAPI app
app = FastAPI(
    title="DomainPing API",
    description="Never lose a domain again! Comprehensive domain renewal reminder service.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
# Build allowed origins list
allowed_origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
    "https://domainping-frontend.fly.dev",  # Fly.io frontend
    "https://dlzn4ikotqjx.cloudfront.net",  # CloudFront distribution
]

# Add environment-specific URLs
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

cloudfront_url = os.getenv("CLOUDFRONT_URL")
if cloudfront_url and cloudfront_url not in allowed_origins:
    allowed_origins.append(cloudfront_url)

# Filter out empty strings
allowed_origins = [url for url in allowed_origins if url]

logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(domains_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DomainPing API",
        "version": "1.0.0",
        "description": "Never lose a domain again! 🛡️",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Fly.io"""
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "DomainPing API",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 