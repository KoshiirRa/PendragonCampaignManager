import secrets
from collections.abc import Awaitable, Callable

from pydantic import SecretStr
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

PUBLIC_PATHS = frozenset(
    {
        "/health",
        "/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/openapi-gpt-play.json",
        "/openapi-gpt-dynasty.json",
        "/openapi-gpt-winter.json",
        "/privacy",
    }
)


def api_keys_match(expected: SecretStr | None, provided: str | None) -> bool:
    if expected is None:
        return True
    if not provided:
        return False
    return secrets.compare_digest(expected.get_secret_value(), provided)


class APIKeyMiddleware:
    def __init__(self, app: ASGIApp, api_key: SecretStr | None) -> None:
        self.app = app
        self.api_key = api_key

    async def __call__(
        self,
        scope: dict,
        receive: Callable[[], Awaitable[dict]],
        send: Callable[[dict], Awaitable[None]],
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
            await self.app(scope, receive, send)
            return

        if not api_keys_match(self.api_key, request.headers.get("X-API-Key")):
            response: Response = JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid API key"},
                headers={"WWW-Authenticate": "ApiKey"},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
