"""
Rate Limiting Middleware for API endpoints
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import time
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Rate limit configuration"""
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day


class InMemoryRateLimiter:
    """
    Simple in-memory rate limiter.
    For production, replace with Redis-based implementation.
    """
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests = defaultdict(list)  # key -> list of timestamps
        
    def is_allowed(self, key: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed.
        Returns: (allowed, retry_after_seconds)
        """
        now = time.time()
        
        # Clean old entries
        self.requests[key] = [
            ts for ts in self.requests[key]
            if now - ts < 86400  # Keep last 24h
        ]
        
        # Count requests in different windows
        minute_ago = now - 60
        hour_ago = now - 3600
        day_ago = now - 86400
        
        requests_last_minute = sum(1 for ts in self.requests[key] if ts > minute_ago)
        requests_last_hour = sum(1 for ts in self.requests[key] if ts > hour_ago)
        requests_last_day = sum(1 for ts in self.requests[key] if ts > day_ago)
        
        # Check limits
        if requests_last_minute >= self.config.requests_per_minute:
            retry_after = int(60 - (now - min(self.requests[key][-self.config.requests_per_minute:])))
            return False, retry_after
        
        if requests_last_hour >= self.config.requests_per_hour:
            retry_after = int(3600 - (now - min(self.requests[key][-self.config.requests_per_hour:])))
            return False, retry_after
        
        if requests_last_day >= self.config.requests_per_day:
            retry_after = int(86400 - (now - min(self.requests[key][-self.config.requests_per_day:])))
            return False, retry_after
        
        # Add current request
        self.requests[key].append(now)
        return True, None
    
    def get_limits(self, key: str) -> dict:
        """Get current limit status"""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        day_ago = now - 86400
        
        requests_last_minute = sum(1 for ts in self.requests[key] if ts > minute_ago)
        requests_last_hour = sum(1 for ts in self.requests[key] if ts > hour_ago)
        requests_last_day = sum(1 for ts in self.requests[key] if ts > day_ago)
        
        return {
            "minute": {
                "limit": self.config.requests_per_minute,
                "remaining": max(0, self.config.requests_per_minute - requests_last_minute),
                "reset": int(now + 60)
            },
            "hour": {
                "limit": self.config.requests_per_hour,
                "remaining": max(0, self.config.requests_per_hour - requests_last_hour),
                "reset": int(now + 3600)
            },
            "day": {
                "limit": self.config.requests_per_day,
                "remaining": max(0, self.config.requests_per_day - requests_last_day),
                "reset": int(now + 86400)
            }
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.
    Applies rate limits per API token or IP address.
    """
    def __init__(self, app, config: Optional[RateLimitConfig] = None):
        super().__init__(app)
        self.limiter = InMemoryRateLimiter(config or RateLimitConfig())
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for non-API paths
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Get identifier (token or IP)
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # Use token as key
            identifier = f"token:{auth_header[7:20]}"  # First chars of token
        else:
            # Use IP as fallback
            identifier = f"ip:{request.client.host if request.client else 'unknown'}"
        
        # Check rate limit
        allowed, retry_after = self.limiter.is_allowed(identifier)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please slow down.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.limiter.config.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        limits = self.limiter.get_limits(identifier)
        response.headers["X-RateLimit-Limit"] = str(limits["minute"]["limit"])
        response.headers["X-RateLimit-Remaining"] = str(limits["minute"]["remaining"])
        response.headers["X-RateLimit-Reset"] = str(limits["minute"]["reset"])
        
        return response
