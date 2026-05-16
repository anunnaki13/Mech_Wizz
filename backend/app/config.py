from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./mechwiz.db"
    jwt_secret: str = "change_this_secret"
    upload_dir: str = "./uploads"
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-5.2"
    openrouter_site_url: str = "http://localhost:3000"
    openrouter_app_name: str = "MECH WIZ AI Digital Twin"
    llm_max_context_chars: int = 12000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
