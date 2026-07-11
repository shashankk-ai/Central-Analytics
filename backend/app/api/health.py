from fastapi import APIRouter

from app.connectors.zoho import ZohoAnalyticsConnector, ZohoApiError, ZohoAuthError
from config.settings import get_settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/zoho")
async def check_zoho_connection() -> dict:
    """Verifies the Zoho Analytics OAuth connection and workspace access.

    Returns the exact error and fix when the connection fails, per the
    build brief's environment-setup requirement.
    """
    settings = get_settings()
    connector = ZohoAnalyticsConnector(settings)
    try:
        await connector.verify_connection()
    except (ZohoAuthError, ZohoApiError) as exc:
        return {"connected": False, "error": str(exc)}
    return {"connected": True, "workspace_id": settings.zoho_workspace_id}
