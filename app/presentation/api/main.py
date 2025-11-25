"""
FastAPI Main Application Entry Point

This is where everything comes together. I use a factory pattern (create_app) instead of
directly instantiating the app because it makes testing cleaner and allows for different
configurations across environments. The middleware stack runs in order: correlation IDs first
(so every request gets tracked), then CORS, then rate limiting and security headers.

Security is flexible here - if you don't set API_KEY or JWT_SECRET, the endpoints are wide open
for local development. In production you definitely want to set those environment variables.

The rate limiter defaults to Redis if available but falls back to in-memory counters, which means
you can scale horizontally without worrying about coordinating state across instances.
"""
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.presentation.api.routers import (
    profile_router,
    job_router,
    application_router,
    document_router,
    analytics_router,
    auth_router
)
from app.presentation.api.security import require_auth
from app.infrastructure.cache.redis_rate_limiter import redis_rate_limiter
from app.infrastructure.logging.structured_logger import (
    setup_logging, CorrelationIdMiddleware, get_logger
)
import os

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Application factory for FastAPI instance.
    
    Why factory pattern instead of module-level app?
    - Tests can create isolated instances with different configs
    - Environment-specific settings can be injected cleanly
    - Multiple apps can coexist (e.g., admin panel, public API)
    
    Middleware order matters: CorrelationIdMiddleware must run first so that
    logging within rate limiting and routers includes the correlation ID.
    """
    # Setup structured logging - outputs JSON in production for easier parsing by log aggregators
    log_level = os.getenv("LOG_LEVEL", "INFO")
    structured = os.getenv("STRUCTURED_LOGS", "true").lower() == "true"
    setup_logging(log_level, structured)
    
    app = FastAPI(
        title="The Unicorn Hunter",
        version="2.0.0",
        description="AI-Powered Job Application Tracker - Hunt down your dream unicorn job with intelligent 8-Factor Match Scoring"
    )

    # Correlation IDs first - every request gets a unique ID for tracing across services
    app.add_middleware(CorrelationIdMiddleware)

    # CORS wide open for now - tighten this in production by specifying allowed origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Replace with actual frontend domains in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Auth router doesn't need global security deps - it handles register/login/refresh internally
    app.include_router(auth_router.router)

    # Apply security conditionally - if neither API_KEY nor JWT_SECRET is set, endpoints stay open
    # This is intentional for local dev but you should never deploy without setting at least JWT_SECRET
    security_deps = []
    if os.getenv("API_KEY") or os.getenv("JWT_SECRET"):
        security_deps = [Depends(require_auth)]

    app.include_router(profile_router.router, dependencies=security_deps)
    app.include_router(job_router.router, dependencies=security_deps)
    app.include_router(application_router.router, dependencies=security_deps)
    app.include_router(document_router.router, dependencies=security_deps)
    app.include_router(analytics_router.router, dependencies=security_deps)

    @app.middleware("http")
    async def apply_rate_limit_and_headers(request: Request, call_next):
        """
        Combined middleware for rate limiting + security headers.
        
        Rate limiting uses Redis if available (set REDIS_URL env var) and falls back to
        in-memory counters. The fallback isn't ideal for multi-instance deployments but
        prevents the app from crashing if Redis is down.
        
        Security headers follow OWASP recommendations:
        - CSP prevents XSS by restricting script sources
        - HSTS forces HTTPS (only enabled if HTTPS_ENABLED=true)
        - X-Frame-Options prevents clickjacking
        - X-Content-Type-Options prevents MIME sniffing attacks
        """
        # Dynamic rate limit adjustment from env var (useful for load testing without redeploying)
        rpm = os.getenv("RATE_LIMIT_RPM")
        if rpm:
            try:
                redis_rate_limiter.requests_per_minute = int(rpm)
            except ValueError:
                pass  # Ignore invalid values and keep default
            try:
                await redis_rate_limiter.check_rate_limit(request)
            except HTTPException as e:
                logger.warning(f"Rate limit exceeded for {request.client.host}")
                return JSONResponse({"detail": e.detail}, status_code=e.status_code)
        
        response = await call_next(request)
        
        # Standard security headers - these apply to all responses
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        
        # CSP can be strict in prod but needs 'unsafe-inline' for dev tools like Swagger UI
        csp_policy = os.getenv("CSP_POLICY", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'")
        response.headers.setdefault("Content-Security-Policy", csp_policy)
        
        # HSTS only makes sense behind HTTPS - don't enable for local HTTP testing
        if os.getenv("HTTPS_ENABLED", "false").lower() == "true":
            hsts_max_age = os.getenv("HSTS_MAX_AGE", "31536000")  # 1 year default
            response.headers.setdefault("Strict-Transport-Security", f"max-age={hsts_max_age}; includeSubDomains; preload")
        
        return response

    @app.get("/", dependencies=security_deps)
    async def root():
        """Root endpoint - just a health check with branding."""
        logger.info("Root endpoint accessed")
        return {
            "app": "The Unicorn Hunter",
            "version": "2.0.0",
            "tagline": "Hunt down your dream unicorn job",
            "message": "Welcome to The Unicorn Hunter - Your AI-powered job hunting companion",
            "docs": "/docs",
            "redoc": "/redoc"
        }

    @app.get("/health", dependencies=security_deps)
    async def health_check():
        """Simple health check for load balancers and monitoring systems."""
        return {"status": "healthy"}

    logger.info("FastAPI application configured successfully")
    return app


# Default application instance for production - uvicorn imports this
# In tests we call create_app() directly to get isolated instances
app = create_app()
