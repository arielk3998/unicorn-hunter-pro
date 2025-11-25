"""Redis-backed rate limiter with in-memory fallback for multi-instance scaling."""
from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional
import os

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisRateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.redis_client: Optional[redis.Redis] = None
        self.fallback_requests = defaultdict(list)
        
        if REDIS_AVAILABLE:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
            except (redis.ConnectionError, redis.TimeoutError):
                self.redis_client = None
    
    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        
        if self.redis_client:
            await self._check_redis_limit(client_ip)
        else:
            await self._check_memory_limit(client_ip)
    
    async def _check_redis_limit(self, client_ip: str):
        key = f"rate_limit:{client_ip}"
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=1)
        
        # Add current request timestamp
        self.redis_client.zadd(key, {str(now.timestamp()): now.timestamp()})
        
        # Remove old entries outside window
        self.redis_client.zremrangebyscore(key, 0, window_start.timestamp())
        
        # Count requests in window
        count = self.redis_client.zcard(key)
        
        # Set expiry on key
        self.redis_client.expire(key, 120)
        
        if count > self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    async def _check_memory_limit(self, client_ip: str):
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.fallback_requests[client_ip] = [
            req_time for req_time in self.fallback_requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.fallback_requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        self.fallback_requests[client_ip].append(now)


redis_rate_limiter = RedisRateLimiter(requests_per_minute=10)
