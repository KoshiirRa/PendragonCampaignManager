from app.main import app


def test_openapi_contains_foundation_routes() -> None:
    paths = app.openapi()["paths"]
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
    assert "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/tenures" in paths
    assert "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/improvements" in paths
    assert (
        "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/improvements/{improvement_id}/ledger"
        in paths
    )
    assert "/api/v1/campaigns/{campaign_id}/manors/{manor_id}/assets/{asset_id}/ledger" in paths


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
