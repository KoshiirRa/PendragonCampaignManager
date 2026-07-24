from copy import deepcopy
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

GPT_PLAY_OPERATION_IDS = frozenset(
    {
        "list_campaigns",
        "get_campaign",
        "list_sessions",
        "create_session",
        "update_session",
        "list_events",
        "create_event",
        "create_dice_log",
        "list_characters",
        "create_character",
        "get_character",
        "update_character",
        "list_notes",
        "add_note",
        "glory_summary",
        "add_glory",
        "create_passion",
        "add_passion_entry",
        "add_skill_entry",
        "list_status_history",
        "add_status",
        "add_trait_entry",
        "list_skill_definitions",
        "list_trait_definitions",
        "list_character_history",
        "list_character_wounds",
        "list_locations",
        "list_manors",
        "list_families",
        "get_player_view",
    }
)

GPT_DYNASTY_OPERATION_IDS = frozenset(
    {
        "list_campaigns",
        "get_campaign",
        "list_sessions",
        "list_events",
        "create_event",
        "list_characters",
        "create_character",
        "get_character",
        "update_character",
        "list_character_history",
        "list_notes",
        "add_note",
        "glory_summary",
        "add_glory",
        "list_families",
        "create_family",
        "list_history",
        "add_history",
        "add_membership",
        "add_marriage",
        "add_parentage",
        "list_sources",
        "create_source",
        "create_inheritance_case",
        "add_heir",
        "transfer_manor",
        "list_locations",
        "list_manors",
        "list_tenures",
        "get_player_view",
    }
)

GPT_WINTER_OPERATION_IDS = frozenset(
    {
        "list_campaigns",
        "get_campaign",
        "list_sessions",
        "list_events",
        "create_event",
        "list_characters",
        "get_character",
        "list_character_history",
        "list_character_wounds",
        "glory_summary",
        "add_glory",
        "list_squires",
        "list_squire_states",
        "list_squire_services",
        "list_winter_phases",
        "create_winter_phase",
        "list_winter_participants",
        "get_annual_chronicle",
        "generate_annual_chronicle",
        "list_manors",
        "list_annual_resolutions",
        "create_annual_resolution",
        "list_treasury",
        "add_treasury_entry",
        "list_household_employment",
        "add_household_employment",
        "list_tenures",
        "add_tenure",
        "list_improvements",
        "add_improvement",
    }
)

NON_CONSEQUENTIAL_OPERATION_IDS = frozenset({"create_event"})


def _referenced_component_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        reference = value.get("$ref")
        if isinstance(reference, str) and reference.startswith("#/components/schemas/"):
            names.add(reference.rsplit("/", 1)[-1])
        for child in value.values():
            names.update(_referenced_component_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(_referenced_component_names(child))
    return names


def _prune_component_schemas(schema: dict[str, Any]) -> None:
    components = schema.get("components", {})
    all_schemas = components.get("schemas", {})
    required = _referenced_component_names(schema.get("paths", {}))
    pending = list(required)
    while pending:
        name = pending.pop()
        for dependency in _referenced_component_names(all_schemas.get(name, {})) - required:
            required.add(dependency)
            pending.append(dependency)
    components["schemas"] = {
        name: definition for name, definition in all_schemas.items() if name in required
    }


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
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            if (
                isinstance(operation, dict)
                and operation.get("operationId") in NON_CONSEQUENTIAL_OPERATION_IDS
            ):
                operation["x-openai-isConsequential"] = False
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


def _build_filtered_openapi(
    app: FastAPI,
    operation_ids: frozenset[str],
    *,
    title: str,
    description: str,
    action_scope: str,
) -> dict[str, Any]:
    schema = deepcopy(build_openapi(app))
    paths: dict[str, Any] = {}
    for path, path_item in schema.get("paths", {}).items():
        filtered = {
            method: operation
            for method, operation in path_item.items()
            if isinstance(operation, dict) and operation.get("operationId") in operation_ids
        }
        if filtered:
            paths[path] = filtered
    schema["paths"] = paths
    schema["info"]["title"] = title
    schema["info"]["description"] = description
    schema["x-chatgpt-instructions"]["action_scope"] = action_scope
    _prune_component_schemas(schema)
    return schema


def build_gpt_play_openapi(app: FastAPI) -> dict[str, Any]:
    """Return the focused Custom GPT schema for ordinary campaign play."""
    return _build_filtered_openapi(
        app,
        GPT_PLAY_OPERATION_IDS,
        title="Pendragon Campaign Play Action",
        description=(
            "Focused Custom GPT Action for sessions, events, characters, advancement, "
            "and read-only campaign context. Historical records remain append-only."
        ),
        action_scope="campaign-play",
    )


def build_gpt_dynasty_openapi(app: FastAPI) -> dict[str, Any]:
    """Return the focused Custom GPT schema for family and inheritance history."""
    return _build_filtered_openapi(
        app,
        GPT_DYNASTY_OPERATION_IDS,
        title="Pendragon Dynasty Action",
        description=(
            "Focused Custom GPT Action for families, ancestry, marriages, parentage, "
            "inheritance, and manor transfers. Historical records remain append-only."
        ),
        action_scope="dynasty",
    )


def build_gpt_winter_openapi(app: FastAPI) -> dict[str, Any]:
    """Return the focused Custom GPT schema for Winter Phase resolution."""
    return _build_filtered_openapi(
        app,
        GPT_WINTER_OPERATION_IDS,
        title="Pendragon Winter Phase Action",
        description=(
            "Focused Custom GPT Action for Winter Phase, annual chronicles, character outcomes, "
            "squires, and manor economy. Historical records remain append-only."
        ),
        action_scope="winter-phase",
    )
