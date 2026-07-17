from app.main import app


def test_openapi_contains_foundation_routes() -> None:
    paths = app.openapi()["paths"]
    assert "/api/v1/campaigns" in paths
    assert "/api/v1/campaigns/{campaign_id}/sessions" in paths
    assert "/api/v1/campaigns/{campaign_id}/events" in paths
    assert "/api/v1/campaigns/{campaign_id}/dice-logs" in paths


def test_historical_records_have_no_mutation_routes() -> None:
    paths = app.openapi()["paths"]
    event_methods = paths["/api/v1/campaigns/{campaign_id}/events"]
    assert "patch" not in event_methods
    assert "delete" not in event_methods
