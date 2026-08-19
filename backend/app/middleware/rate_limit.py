import time
from collections import defaultdict, deque

import redis.asyncio as aioredis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config import settings


class RateLimiter:
    """Token-window limiter. Uses Upstash Redis when configured, otherwise in-memory.

    Redis failures are transient: a failed connection is retried after a short
    cooldown instead of disabling the shared limiter forever.
    """

    def __init__(self, limit: int = 300, window: int = 60) -> None:
        self.limit = limit
        self.window = window
        self._redis = None
        self._redis_down_until = 0.0
        self._memory: dict[str, deque[float]] = defaultdict(deque)
        self._lock = __import__("threading").Lock()

    async def _get_redis(self):
        if self._redis is None and settings.redis_url:
            if time.time() >= self._redis_down_until:
                try:
                    self._redis = aioredis.from_url(settings.redis_url, decode_responses=True)
                except Exception:  # noqa: BLE001
                    self._redis_down_until = time.time() + 10
                    self._redis = None
        return self._redis or None

    async def check(self, key: str) -> None:
        redis_client = await self._get_redis()
        now = time.time()

        if redis_client is not None:
            try:
                min_score = now - self.window
                pipe = redis_client.pipeline()
                pipe.zremrangebyscore(f"rl:{key}", 0, min_score)
                pipe.zadd(f"rl:{key}", {f"{now:.6f}": now})
                pipe.zcard(f"rl:{key}")
                pipe.expire(f"rl:{key}", self.window)
                results = await pipe.execute()
                if int(results[2]) > self.limit:
                    raise PermissionError("rate_limited")
                return
            except PermissionError:
                raise
            except Exception:  # noqa: BLE001
                # Treat a transient Redis failure as "allow" rather than 429ing everyone.
                return

        with self._lock:
            bucket = self._memory[key]
            while bucket and bucket[0] < now - self.window:
                bucket.popleft()
            if len(bucket) >= self.limit:
                raise PermissionError("rate_limited")
            bucket.append(now)


limiter = RateLimiter(limit=300, window=60)
auth_limiter = RateLimiter(limit=20, window=60)


def _client_ip(request: Request) -> str:
    """Client IP honoring X-Forwarded-For (leftmost untrusted hop) behind proxies."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        first = forwarded.split(",")[0].strip()
        if first:
            return first
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith("/api/v1"):
            return await call_next(request)
        # Provider webhooks retry on failure; never throttle them.
        if path.startswith("/api/v1/webhooks"):
            return await call_next(request)
        # Only enforce limits in production; local/dev and CI stay friction-free.
        if not settings.is_production:
            return await call_next(request)

        ip = _client_ip(request)
        try:
            if path.startswith("/api/v1/auth"):
                await auth_limiter.check(f"auth:{ip}")
            else:
                await limiter.check(f"ip:{ip}")
        except PermissionError:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )
        return await call_next(request)
