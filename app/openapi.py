from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def build_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=app.servers,
    )
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["ApiKeyAuth"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "Campaign API key stored as a secret in the calling client.",
    }
    schema["security"] = [{"ApiKeyAuth": []}]
    for path in ("/health", "/ready", "/openapi.json"):
        for operation in schema.get("paths", {}).get(path, {}).values():
            if isinstance(operation, dict):
                operation["security"] = []
    schema["x-chatgpt-instructions"] = {
        "purpose": "Persistent memory for multi-generational Pendragon campaigns.",
        "rules": [
            "Never invent UUIDs. List or create the required parent record first.",
            "Treat events, ledgers, ancestry, inheritance transfers, and family history "
            "as append-only.",
            "Use the campaign_id from the selected campaign on every campaign-scoped call.",
            "Record significant narrative changes as events and link domain records "
            "when supported.",
            "Respect knowledge scope: gm_only data must not be disclosed to players.",
        ],
    }
    app.openapi_schema = schema
    return schema
