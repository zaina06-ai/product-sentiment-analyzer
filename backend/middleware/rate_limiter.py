from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from flask import Flask, request, jsonify


class RateLimiter:
    """Simple in-memory sliding window rate limiter.

    Production deployments should prefer an external store (Redis), but this meets the
    dependency constraint for now.
    """

    def __init__(self, app: Flask, request_limit: int, window_seconds: int):
        self.request_limit = int(request_limit)
        self.window_seconds = int(window_seconds)
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)

        @app.before_request
        def _limit():
            # Allow health and swagger without strict limiting.
            if request.path in {"/health"} or request.path.startswith("/swagger"):
                return None

            ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
            now = time.time()
            q = self._requests[ip]

            # Drop old
            cutoff = now - self.window_seconds
            while q and q[0] < cutoff:
                q.popleft()

            if len(q) >= self.request_limit:
                return (
                    jsonify({
                        "success": False,
                        "message": "Too Many Requests",
                        "data": {},
                        "errors": None,
                    }),
                    429,
                )

            q.append(now)
            return None

