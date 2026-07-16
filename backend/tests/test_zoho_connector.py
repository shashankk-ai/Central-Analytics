import asyncio

import pytest

from app.connectors.zoho import ZohoAnalyticsConnector, get_shared_connector
from config.settings import Settings


def _settings() -> Settings:
    return Settings(
        zoho_client_id="id",
        zoho_client_secret="secret",
        zoho_refresh_token="refresh",
    )


def test_get_shared_connector_returns_the_same_instance():
    settings = _settings()
    first = get_shared_connector(settings)
    second = get_shared_connector(settings)
    assert first is second


@pytest.mark.asyncio
async def test_concurrent_requests_only_refresh_the_token_once(monkeypatch):
    """Regression test: every API route used to build a fresh connector
    per request, so its token cache never helped and every request paid
    for its own OAuth exchange — enough of those in a short window is
    exactly what tripped Zoho's 'too many requests' throttle."""
    connector = ZohoAnalyticsConnector(_settings())
    call_count = 0

    async def fake_fetch_access_token():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.05)  # simulate network latency
        connector._access_token = "token"
        connector._access_token_expires_at = float("inf")
        return "token"

    monkeypatch.setattr(connector, "_fetch_access_token", fake_fetch_access_token)

    results = await asyncio.gather(*[connector._get_access_token() for _ in range(10)])

    assert call_count == 1
    assert all(r == "token" for r in results)


@pytest.mark.asyncio
async def test_cached_token_is_reused_without_refetching(monkeypatch):
    connector = ZohoAnalyticsConnector(_settings())
    connector._access_token = "cached"
    connector._access_token_expires_at = float("inf")

    async def fail_if_called():
        raise AssertionError("should not refetch a still-valid token")

    monkeypatch.setattr(connector, "_fetch_access_token", fail_if_called)

    assert await connector._get_access_token() == "cached"
