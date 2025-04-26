from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging

# Import models first to ensure they are registered properly
import app.models
from app.db import Base, engine
from app.core.config import settings
import asyncio

# Import API routes after models
from app.api import auth, participants, sms, fitbit, message_content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize database
async def init_db():
    async with engine.begin() as conn:
        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


def create_app() -> FastAPI:
    """
    Factory function to create FastAPI application
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # Create startup event to initialize database
    @app.on_event("startup")
    async def startup_event():
        await init_db()
    
    # Set up CORS middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        # Allow all origins in development
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Include routers
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    app.include_router(participants.router, prefix=settings.API_V1_STR)
    app.include_router(sms.router, prefix=settings.API_V1_STR)
    app.include_router(fitbit.router, prefix=settings.API_V1_STR)
    app.include_router(message_content.router, prefix=settings.API_V1_STR)
    
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")
    
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}
    
    logger.info("Application started")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
