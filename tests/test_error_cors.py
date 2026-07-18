from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.api.errors import UnhandledErrorMiddleware


def test_unhandled_errors_keep_cors_headers() -> None:
    test_app = FastAPI()
    test_app.add_middleware(UnhandledErrorMiddleware)
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://pendragon.dwarvenbard.com"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @test_app.get("/explode")
    async def explode() -> None:
        raise RuntimeError("test failure")

    response = TestClient(test_app, raise_server_exceptions=False).get(
        "/explode", headers={"Origin": "https://pendragon.dwarvenbard.com"}
    )
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert response.headers["access-control-allow-origin"] == "https://pendragon.dwarvenbard.com"
