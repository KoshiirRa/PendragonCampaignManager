from fastapi.testclient import TestClient

from app.main import app
from app.openapi import (
    GPT_DYNASTY_OPERATION_IDS,
    GPT_PLAY_OPERATION_IDS,
    GPT_WINTER_OPERATION_IDS,
    build_gpt_dynasty_openapi,
    build_gpt_play_openapi,
    build_gpt_winter_openapi,
)


def test_openapi_contains_foundation_routes() -> None:
    document = app.openapi()
    paths = document["paths"]
    assert "/api/v1/campaigns" in paths
    assert "/api/v1/campaigns/{campaign_id}/sessions" in paths
    assert "/api/v1/campaigns/{campaign_id}/player-view" in paths
    assert "/api/v1/campaigns/by-slug/{slug}/player-view" in paths
    assert "/api/v1/campaigns/{campaign_id}/events" in paths
    assert "/api/v1/campaigns/{campaign_id}/dice-logs" in paths
    assert "/api/v1/campaigns/{campaign_id}/characters" in paths
    assert "/api/v1/campaigns/{campaign_id}/characters/{character_id}/glory" in paths
    assert "/api/v1/campaigns/{campaign_id}/characters/{character_id}/foundry-snapshot" in paths
    assert "/api/v1/campaigns/{campaign_id}/locations" in paths
    assert "/api/v1/campaigns/{campaign_id}/manors" in paths
    assert "/api/v1/campaigns/{campaign_id}/families" in paths
    assert "/api/v1/campaigns/{campaign_id}/parentage" in paths
    assert "/api/v1/campaigns/{campaign_id}/inheritance-cases" in paths
    assert "/api/v1/campaigns/{campaign_id}/families/{family_id}/history" in paths
    assert "/api/v1/campaigns/{campaign_id}/source-references" in paths
    assert "/api/v1/campaigns/{campaign_id}/winter-phases" in paths
    assert "/api/v1/campaigns/{campaign_id}/characters/{character_id}/history" in paths
    assert "/api/v1/campaigns/{campaign_id}/characters/{character_id}/wounds" in paths
    assert "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/annual-resolutions" in paths
    assert "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/treasury" in paths
    assert "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/household" in paths
    assert "/api/v1/campaigns/{campaign_id}/characters/{character_id}/squire-services" in paths
    assert "/api/v1/campaigns/{campaign_id}/squires/{squire_id}/states" in paths
    assert "/api/v1/campaigns/{campaign_id}/squires" in paths
    assert "/api/v1/campaigns/{campaign_id}/years/{year}/chronicle" in paths
    assert "/api/v1/campaigns/{campaign_id}/years/{year}/chronicle/generate" in paths
    assert "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/tenures" in paths
    assert "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/improvements" in paths
    assert (
        "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/improvements/{improvement_id}/ledger"
        in paths
    )
    assert "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/assets/{asset_id}/ledger" in paths
    player_view = document["components"]["schemas"]["CampaignPlayerView"]
    assert player_view["properties"]["people"]["items"]["$ref"].endswith("/PlayerPerson")


def test_historical_records_have_no_mutation_routes() -> None:
    paths = app.openapi()["paths"]
    event_methods = paths["/api/v1/campaigns/{campaign_id}/events"]
    assert "patch" not in event_methods
    assert "delete" not in event_methods


def test_historical_ledgers_have_no_destructive_routes() -> None:
    paths = app.openapi()["paths"]
    glory = paths["/api/v1/campaigns/{campaign_id}/characters/{character_id}/glory"]
    assert "patch" not in glory
    assert "delete" not in glory
    snapshot = paths["/api/v1/campaigns/{campaign_id}/characters/{character_id}/foundry-snapshot"]
    assert set(snapshot) == {"post"}
    history = paths["/api/v1/campaigns/{campaign_id}/families/{family_id}/history"]
    assert "patch" not in history
    assert "delete" not in history
    character_history = paths["/api/v1/campaigns/{campaign_id}/characters/{character_id}/history"]
    assert set(character_history) == {"get"}
    wounds = paths["/api/v1/campaigns/{campaign_id}/characters/{character_id}/wounds"]
    assert set(wounds) == {"get"}


def test_openapi_is_ready_for_chatgpt_actions() -> None:
    schema = app.openapi()
    assert schema["components"]["securitySchemes"]["ApiKeyAuth"]["name"] == "X-API-Key"
    assert schema["security"] == [{"ApiKeyAuth": []}]
    operation_ids = [
        operation["operationId"]
        for path in schema["paths"].values()
        for operation in path.values()
        if isinstance(operation, dict) and "operationId" in operation
    ]
    assert len(operation_ids) == len(set(operation_ids))
    assert schema["servers"][0]["url"]
    assert schema["x-chatgpt-instructions"]["rules"]


def test_gpt_play_openapi_has_exactly_thirty_focused_operations() -> None:
    schema = build_gpt_play_openapi(app)
    operation_ids = {
        operation["operationId"] for path in schema["paths"].values() for operation in path.values()
    }
    assert operation_ids == GPT_PLAY_OPERATION_IDS
    assert len(operation_ids) == 30
    assert schema["info"]["title"] == "Pendragon Campaign Play Action"
    assert schema["x-chatgpt-instructions"]["action_scope"] == "campaign-play"


def test_gpt_play_openapi_omits_destructive_and_specialist_operations() -> None:
    schema = build_gpt_play_openapi(app)
    operation_ids = {
        operation["operationId"] for path in schema["paths"].values() for operation in path.values()
    }
    assert "archive_campaign" not in operation_ids
    assert "archive_character" not in operation_ids
    assert "create_winter_phase" not in operation_ids
    assert "create_inheritance_case" not in operation_ids
    assert "create_annual_resolution" not in operation_ids


def test_gpt_play_openapi_endpoint_is_public() -> None:
    response = TestClient(app).get("/openapi-gpt-play.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Pendragon Campaign Play Action"


def test_gpt_dynasty_openapi_has_exactly_thirty_focused_operations() -> None:
    schema = build_gpt_dynasty_openapi(app)
    operation_ids = {
        operation["operationId"] for path in schema["paths"].values() for operation in path.values()
    }
    assert operation_ids == GPT_DYNASTY_OPERATION_IDS
    assert len(operation_ids) == 30
    assert schema["info"]["title"] == "Pendragon Dynasty Action"
    assert schema["x-chatgpt-instructions"]["action_scope"] == "dynasty"


def test_gpt_dynasty_openapi_omits_destructive_and_unrelated_operations() -> None:
    schema = build_gpt_dynasty_openapi(app)
    operation_ids = {
        operation["operationId"] for path in schema["paths"].values() for operation in path.values()
    }
    assert "archive_campaign" not in operation_ids
    assert "archive_character" not in operation_ids
    assert "create_winter_phase" not in operation_ids
    assert "create_annual_resolution" not in operation_ids
    assert "add_treasury_entry" not in operation_ids


def test_gpt_dynasty_openapi_endpoint_is_public() -> None:
    response = TestClient(app).get("/openapi-gpt-dynasty.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Pendragon Dynasty Action"


def test_gpt_winter_openapi_has_exactly_thirty_focused_operations() -> None:
    schema = build_gpt_winter_openapi(app)
    operation_ids = {
        operation["operationId"] for path in schema["paths"].values() for operation in path.values()
    }
    assert operation_ids == GPT_WINTER_OPERATION_IDS
    assert len(operation_ids) == 30
    assert schema["info"]["title"] == "Pendragon Winter Phase Action"
    assert schema["x-chatgpt-instructions"]["action_scope"] == "winter-phase"


def test_gpt_winter_openapi_omits_destructive_and_dynasty_operations() -> None:
    schema = build_gpt_winter_openapi(app)
    operation_ids = {
        operation["operationId"] for path in schema["paths"].values() for operation in path.values()
    }
    assert "archive_campaign" not in operation_ids
    assert "archive_character" not in operation_ids
    assert "create_inheritance_case" not in operation_ids
    assert "add_marriage" not in operation_ids
    assert "transfer_manor" not in operation_ids


def test_gpt_winter_openapi_endpoint_is_public() -> None:
    response = TestClient(app).get("/openapi-gpt-winter.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Pendragon Winter Phase Action"
