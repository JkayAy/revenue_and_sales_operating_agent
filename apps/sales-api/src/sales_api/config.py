from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mock_tools: bool = True
    playbook_config_path: str = "config/playbook.yaml"
    admin_api_key: str = ""
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    sales_api_host: str = "127.0.0.1"
    sales_api_port: int = 8000
    database_url: str = ""
    default_org_id: str = "00000000-0000-0000-0000-000000000001"

    hubspot_access_token: str = ""
    hubspot_webhook_secret: str = ""
    hubspot_client_id: str = ""
    hubspot_client_secret: str = ""
    hubspot_redirect_uri: str = "http://127.0.0.1:8000/v1/integrations/hubspot/callback"

    llm_draft_enabled: bool = False
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    rate_limit_per_minute: int = 60
    otel_enabled: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def hubspot_oauth_configured(self) -> bool:
        return bool(
            self.hubspot_client_id and self.hubspot_client_secret and self.hubspot_redirect_uri
        )


settings = Settings()
