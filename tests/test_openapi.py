from app.main import app


def test_openapi_contains_foundation_routes() -> None:
    paths = app.openapi()["paths"]
    assert "/api/v1/campaigns" in paths
    assert "/api/v1/campaigns/{campaign_id}/sessions" in paths
    assert "/api/v1/campaigns/{campaign_id}/events" in paths
    assert "/api/v1/campaigns/{campaign_id}/dice-logs" in paths
    assert "/api/v1/campaigns/{campaign_id}/characters" in paths
    assert "/api/v1/campaigns/{campaign_id}/characters/{character_id}/glory" in paths
    assert "/api/v1/campaigns/{campaign_id}/locations" in paths
    assert "/api/v1/campaigns/{campaign_id}/manors" in paths


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
