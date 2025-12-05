from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
from typing import Dict


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter middleware.

    Limits requests per client IP to `requests` per `window_seconds`.
    Not suitable for multi-process deployment; replace with Redis/Shared store in prod.
    """

    def __init__(self, app, requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.requests = requests
        self.window = window_seconds
        self.clients: Dict[str, Dict] = {}

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "unknown"
        now = int(time.time())
        rec = self.clients.get(client)
        if not rec or now - rec["start"] >= self.window:
            # start new window
            self.clients[client] = {"start": now, "count": 1}
        else:
            rec["count"] += 1
        if self.clients[client]["count"] > self.requests:
            return Response(status_code=429, content="Rate limit exceeded")
        response = await call_next(request)
        return response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Response
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = 120):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.store = {}

    async def dispatch(self, request, call_next):
        client_ip = request.client.host if request.client else "anon"
        now = time.time()
        window = 60
        timestamps = self.store.get(client_ip, [])
        # drop old
        timestamps = [t for t in timestamps if now - t < window]
        if len(timestamps) >= self.calls_per_minute:
            return Response(status_code=429, content="Rate limit exceeded")
        timestamps.append(now)
        self.store[client_ip] = timestamps
        response = await call_next(request)
        return response
