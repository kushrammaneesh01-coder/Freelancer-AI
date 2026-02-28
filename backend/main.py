<<<<<<< HEAD
﻿"""
FastAPI Main Application - PRODUCTION READY
Includes: Rate limiting, logging, security headers, CORS, error handling
"""
import logging
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from collections import defaultdict
import threading

from backend.api.routes import router
from backend.config import settings

# ─── Logging Setup ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ai-freelancing-agency")

# ─── Rate Limiter (In-memory, per IP) ───────────────────────
_rate_limit_store: dict = defaultdict(list)
_rate_limit_lock = threading.Lock()

def is_rate_limited(ip: str, limit: int, window_seconds: int = 60) -> bool:
    now = time.time()
    with _rate_limit_lock:
        timestamps = _rate_limit_store[ip]
        # Remove old timestamps outside the window
        _rate_limit_store[ip] = [t for t in timestamps if now - t < window_seconds]
        if len(_rate_limit_store[ip]) >= limit:
            return True
        _rate_limit_store[ip].append(now)
    return False

# ─── App Creation ────────────────────────────────────────────
app = FastAPI(
    title="AI Freelancing Automation Agency",
    description="Multi-agent AI system for automating freelance job discovery and proposal generation",
    version="1.0.0",
    debug=settings.DEBUG,
    # In production, hide docs unless DEBUG
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# ─── Middlewares ─────────────────────────────────────────────

# CORS - restrict to allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Per-IP rate limiting middleware"""
    ip = request.client.host if request.client else "unknown"
    if is_rate_limited(ip, limit=settings.RATE_LIMIT_PER_MINUTE):
        logger.warning(f"Rate limit exceeded for IP: {ip}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please slow down."}
        )
    response = await call_next(request)
    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add production security headers"""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Request/response logging"""
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} "
        f"| status={response.status_code} | {duration}ms "
        f"| ip={request.client.host if request.client else 'unknown'}"
    )
    return response


# ─── Routes ─────────────────────────────────────────────────
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "AI Freelancing Automation Agency API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "debug": settings.DEBUG}


# ─── Exception Handlers ──────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )


# ─── Startup / Shutdown Events ───────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("🚀 AI Freelancing Agency starting up...")
    logger.info(f"   DEBUG mode: {settings.DEBUG}")
    logger.info(f"   Rate limit: {settings.RATE_LIMIT_PER_MINUTE} req/min")
    logger.info(f"   CORS origins: {settings.get_allowed_origins()}")
    logger.info("=" * 50)
    # Auto-create DB tables on startup
    try:
        from backend.models import Base
        from backend.db.session import engine
        Base.metadata.create_all(bind=engine)
        logger.info("Success: Database tables ready")
    except Exception as e:
        logger.error(f"Error: DB setup error: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 AI Freelancing Agency shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
        log_level="info",
    )
=======
from fastapi import FastAPI
from backend.auth.auth_routes import router as auth_router

app = FastAPI(title="AI Freelancing Automation Agency")

app.include_router(auth_router, prefix="/auth")

@app.get("/")
def root():
    return {"status": "AI Freelancing SaaS running"}
from fastapi import FastAPI
from backend.api.routes import router as api_router
from backend.auth.auth_routes import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(api_router, prefix="/api")
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
