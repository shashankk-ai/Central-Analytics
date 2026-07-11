"""Zoho Analytics REST API connector (OAuth 2.0 refresh-token grant).

Docs: https://www.zoho.com/analytics/api/v2/
"""

from __future__ import annotations

import time

import httpx

from config.settings import Settings


class ZohoAuthError(RuntimeError):
    """Raised when Zoho OAuth token exchange fails."""


class ZohoApiError(RuntimeError):
    """Raised when a Zoho Analytics API call fails."""


class ZohoAnalyticsConnector:
    """Thin async client over the Zoho Analytics v2 REST API.

    Caches the OAuth access token in memory and refreshes it a few seconds
    before Zoho's stated expiry to avoid mid-request 401s.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._access_token: str | None = None
        self._access_token_expires_at: float = 0.0

    async def _fetch_access_token(self) -> str:
        settings = self._settings
        if not (settings.zoho_client_id and settings.zoho_client_secret and settings.zoho_refresh_token):
            raise ZohoAuthError(
                "Missing Zoho OAuth credentials. Set ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET and "
                "ZOHO_REFRESH_TOKEN in backend/.env (see backend/.env.example)."
            )

        token_url = f"{settings.zoho_account_domain}/oauth/v2/token"
        params = {
            "grant_type": "refresh_token",
            "client_id": settings.zoho_client_id,
            "client_secret": settings.zoho_client_secret,
            "refresh_token": settings.zoho_refresh_token,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(token_url, params=params)

        body = response.json()
        if response.status_code != 200 or "access_token" not in body:
            raise ZohoAuthError(
                f"Zoho token exchange failed (HTTP {response.status_code}): {body}. "
                f"Fix: verify ZOHO_CLIENT_ID/ZOHO_CLIENT_SECRET/ZOHO_REFRESH_TOKEN are correct and "
                f"that the refresh token was issued for account domain '{settings.zoho_account_domain}'."
            )

        self._access_token = body["access_token"]
        self._access_token_expires_at = time.monotonic() + float(body.get("expires_in", 3600)) - 60
        return self._access_token

    async def _get_access_token(self) -> str:
        if self._access_token is None or time.monotonic() >= self._access_token_expires_at:
            return await self._fetch_access_token()
        return self._access_token

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        settings = self._settings
        token = await self._get_access_token()
        headers = {
            "Authorization": f"Zoho-oauthtoken {token}",
            **kwargs.pop("headers", {}),
        }
        if settings.zoho_org_id:
            headers["ZANALYTICS-ORGID"] = settings.zoho_org_id

        url = f"{settings.zoho_analytics_domain}{path}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(method, url, headers=headers, **kwargs)

        if response.status_code >= 400:
            raise ZohoApiError(f"Zoho Analytics API error (HTTP {response.status_code}) calling {path}: {response.text}")
        return response

    async def verify_connection(self) -> dict:
        """Confirms OAuth works and the configured workspace is reachable."""
        await self._get_access_token()
        response = await self._request(
            "GET",
            f"/restapi/v2/workspaces/{self._settings.zoho_workspace_id}/views",
        )
        return response.json()

    async def fetch_view_data(self, view_id: str, criteria: str | None = None) -> list[dict]:
        """Fetches row data for a given view (table/query table) as a list of dicts."""
        params = {"CONFIG": '{"responseFormat":"json"}'}
        if criteria:
            params["CONFIG"] = f'{{"responseFormat":"json","criteria":"{criteria}"}}'
        response = await self._request(
            "GET",
            f"/restapi/v2/workspaces/{self._settings.zoho_workspace_id}/views/{view_id}/data",
            params=params,
        )
        payload = response.json()
        return payload.get("data", [])
