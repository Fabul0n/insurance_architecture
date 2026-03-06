import logging
from typing import Final

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

AUTH_PATHS: Final[set[str]] = {
    "/api/insurance/auth/register",
    "/api/insurance/auth/login",
}


class AuthLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger: logging.Logger) -> None:
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        should_log = request.method == "POST" and request.url.path in AUTH_PATHS
        if not should_log:
            return await call_next(request)

        try:
            response = await call_next(request)
        except Exception:
            self.logger.exception(
                "event=%s method=%s path=%s status=%s ip=%s user_agent=%s",
                "auth_register_error" if request.url.path.endswith("/register") else "auth_login_error",
                request.method,
                request.url.path,
                500,
                request.client.host if request.client else "unknown",
                request.headers.get("user-agent", "unknown"),
            )
            raise

        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        self.logger.info(
            "event=%s method=%s path=%s status=%s ip=%s user_agent=%s",
            "auth_register" if request.url.path.endswith("/register") else "auth_login",
            request.method,
            request.url.path,
            response.status_code,
            client_ip,
            user_agent,
        )
        return response
