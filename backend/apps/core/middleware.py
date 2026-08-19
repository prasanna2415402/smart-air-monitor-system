import logging
import time

logger = logging.getLogger("apps")


class RequestLoggingMiddleware:
    """Lightweight request/response logger with timing, useful for audit trails."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start) * 1000
        if request.path.startswith("/api/"):
            user = getattr(request, "user", None)
            username = getattr(user, "username", "anonymous") if user else "anonymous"
            logger.info(
                "%s %s -> %s (%.1fms) user=%s",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                username,
            )
        return response
