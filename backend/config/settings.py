from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Zoho Analytics OAuth 2.0
    zoho_client_id: str = ""
    zoho_client_secret: str = ""
    zoho_refresh_token: str = ""
    zoho_redirect_uri: str = ""
    zoho_account_domain: str = "https://accounts.zoho.in"
    zoho_analytics_domain: str = "https://analyticsapi.zoho.in"
    zoho_org_id: str = ""
    zoho_workspace_id: str = ""
    zoho_workspace_name: str = "SMPLOK"

    # Calculation parameters
    early_pay_rate: float = 0.35

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
