from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.config import settings
from app.core.logging import get_logger, setup_logging
from app.core.middleware import RequestIDMiddleware
from app.database import engine

# Initialize structured logging
setup_logging()
logger = get_logger(__name__)

# Upload directory
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Rate limiter - uses IP address as key
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application", extra={"environment": settings.environment})

    logger.info("Upload directories ready", extra={"path": str(UPLOAD_DIR)})

    yield

    # Shutdown
    logger.info("Shutting down application")
    await engine.dispose()


app = FastAPI(
    title="Organizy API",
    description="Backend API for Organizy",
    version="1.0.0",
    lifespan=lifespan,
)

# Log validation errors with full details
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        "Validation error",
        extra={
            "path": request.url.path,
            "errors": exc.errors(),
            "body": exc.body,
        },
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request ID middleware (added first, runs last)
app.add_middleware(RequestIDMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Cookie", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
