import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class RateLimiter:
    """Allows max_requests per window_seconds for each key (we use the IP)."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.hits = defaultdict(deque)

    def check(self, key: str) -> bool:
        now = time.monotonic()
        recent = self.hits[key]
        while recent and now - recent[0] > self.window_seconds:
            recent.popleft()
        if len(recent) >= self.max_requests:
            return False
        recent.append(now)
        return True

    def reset(self):
        self.hits.clear()


report_limiter = RateLimiter(max_requests=10, window_seconds=60)


def limit_reports(request: Request):
    ip = request.client.host if request.client else "unknown"
    if not report_limiter.check(ip):
        raise HTTPException(
            status_code=429,
            detail="Too many reports. Please wait a minute and try again.",
        )