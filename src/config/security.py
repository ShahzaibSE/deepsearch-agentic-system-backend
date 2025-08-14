from typing import List, Optional, Callable
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import hashlib
import logging

from .settings import settings
from .redis_cache import redis_cache

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Security middleware for CORS, rate limiting, and other security features."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_cors()
        self.setup_trusted_hosts()
        self.setup_rate_limiting()
    
    def setup_cors(self):
        """Setup CORS middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=["*"],
            expose_headers=["Content-Length", "X-Total-Count"],
        )
        logger.info("CORS middleware configured")
    
    def setup_trusted_hosts(self):
        """Setup trusted host middleware for production."""
        if settings.is_production:
            trusted_hosts = ["*"]  # Configure based on your domain
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=trusted_hosts
            )
            logger.info("Trusted host middleware configured for production")
    
    def setup_rate_limiting(self):
        """Setup rate limiting middleware."""
        @self.app.middleware("http")
        async def rate_limit_middleware(request: Request, call_next: Callable):
            # Get client IP
            client_ip = self.get_client_ip(request)
            
            # Check rate limits
            if not await self.check_rate_limit(client_ip):
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": "Too many requests. Please try again later."
                    }
                )
            
            # Add rate limit headers
            response = await call_next(request)
            await self.add_rate_limit_headers(response, client_ip)
            
            return response
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers first (for proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"
    
    async def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limits."""
        try:
            # Check per-minute limit
            minute_key = f"rate_limit:minute:{client_ip}"
            minute_count = await redis_cache.get(minute_key, 0)
            
            if minute_count >= settings.RATE_LIMIT_PER_MINUTE:
                logger.warning(f"Rate limit exceeded for IP {client_ip}: {minute_count} requests per minute")
                return False
            
            # Check per-hour limit
            hour_key = f"rate_limit:hour:{client_ip}"
            hour_count = await redis_cache.get(hour_key, 0)
            
            if hour_count >= settings.RATE_LIMIT_PER_HOUR:
                logger.warning(f"Rate limit exceeded for IP {client_ip}: {hour_count} requests per hour")
                return False
            
            # Increment counters
            await redis_cache.increment(minute_key, 1)
            await redis_cache.increment(hour_key, 1)
            
            # Set TTL for counters
            await redis_cache.expire(minute_key, 60)  # 1 minute
            await redis_cache.expire(hour_key, 3600)  # 1 hour
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Allow request if rate limiting fails
            return True
    
    async def add_rate_limit_headers(self, response: Response, client_ip: str):
        """Add rate limit headers to response."""
        try:
            minute_key = f"rate_limit:minute:{client_ip}"
            hour_key = f"rate_limit:hour:{client_ip}"
            
            minute_count = await redis_cache.get(minute_key, 0)
            hour_count = await redis_cache.get(hour_key, 0)
            
            minute_ttl = await redis_cache.ttl(minute_key)
            hour_ttl = await redis_cache.ttl(hour_key)
            
            response.headers["X-RateLimit-Limit-Minute"] = str(settings.RATE_LIMIT_PER_MINUTE)
            response.headers["X-RateLimit-Limit-Hour"] = str(settings.RATE_LIMIT_PER_HOUR)
            response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, settings.RATE_LIMIT_PER_MINUTE - minute_count))
            response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, settings.RATE_LIMIT_PER_HOUR - hour_count))
            response.headers["X-RateLimit-Reset-Minute"] = str(minute_ttl)
            response.headers["X-RateLimit-Reset-Hour"] = str(hour_ttl)
            
        except Exception as e:
            logger.error(f"Error adding rate limit headers: {e}")


class SecurityHeadersMiddleware:
    """Middleware to add security headers to responses."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_security_headers()
    
    def setup_security_headers(self):
        """Setup security headers middleware."""
        @self.app.middleware("http")
        async def security_headers_middleware(request: Request, call_next: Callable):
            response = await call_next(request)
            
            # Security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # Content Security Policy (adjust based on your needs)
            if settings.is_production:
                response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
            
            # HSTS for production
            if settings.is_production:
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            return response


def setup_security(app: FastAPI):
    """Setup all security middleware for the FastAPI app."""
    SecurityMiddleware(app)
    SecurityHeadersMiddleware(app)
    logger.info("Security middleware setup complete")


# Rate limiting decorator for individual endpoints
def rate_limit(
    requests_per_minute: Optional[int] = None,
    requests_per_hour: Optional[int] = None
):
    """Decorator to apply rate limiting to specific endpoints."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get request object (assuming it's the first argument)
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # If no request object found, just call the function
                return await func(*args, **kwargs)
            
            # Check rate limits
            client_ip = SecurityMiddleware.get_client_ip(None, request)
            
            # Use endpoint-specific limits or fall back to global settings
            minute_limit = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
            hour_limit = requests_per_hour or settings.RATE_LIMIT_PER_HOUR
            
            # Check limits
            minute_key = f"rate_limit:endpoint:minute:{client_ip}:{func.__name__}"
            hour_key = f"rate_limit:endpoint:hour:{client_ip}:{func.__name__}"
            
            minute_count = await redis_cache.get(minute_key, 0)
            hour_count = await redis_cache.get(hour_key, 0)
            
            if minute_count >= minute_limit or hour_count >= hour_limit:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded for this endpoint"
                )
            
            # Increment counters
            await redis_cache.increment(minute_key, 1)
            await redis_cache.increment(hour_key, 1)
            await redis_cache.expire(minute_key, 60)
            await redis_cache.expire(hour_key, 3600)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# IP whitelist decorator
def ip_whitelist(allowed_ips: List[str]):
    """Decorator to restrict access to specific IP addresses."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                return await func(*args, **kwargs)
            
            client_ip = SecurityMiddleware.get_client_ip(None, request)
            
            if client_ip not in allowed_ips:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: IP not in whitelist"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Request logging middleware
class RequestLoggingMiddleware:
    """Middleware to log all requests for security monitoring."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_logging()
    
    def setup_logging(self):
        """Setup request logging middleware."""
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next: Callable):
            start_time = time.time()
            
            # Log request
            client_ip = SecurityMiddleware.get_client_ip(None, request)
            logger.info(
                f"Request: {request.method} {request.url.path} "
                f"from {client_ip} - User-Agent: {request.headers.get('user-agent', 'Unknown')}"
            )
            
            # Process request
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                f"Response: {response.status_code} for {request.method} {request.url.path} "
                f"took {process_time:.3f}s"
            )
            
            return response


def setup_request_logging(app: FastAPI):
    """Setup request logging middleware."""
    RequestLoggingMiddleware(app)
    logger.info("Request logging middleware setup complete")
