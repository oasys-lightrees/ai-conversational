"""Application configuration.

Values are loaded from environment variables (or a local ``.env`` file).
See ``.env.example`` for the full list of supported settings.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "AI Conversational Assessment Agent"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # --- Database ---
    # Example: postgresql+psycopg://user:password@localhost:5432/assessment
    database_url: str = (
        "postgresql+psycopg://assessment:assessment@localhost:5432/assessment"
    )

    # --- OpenAI ---
    openai_api_key: str = ""
    # The design docs reference "GPT-5.5"; that model id does not exist, so the
    # default here is a real, currently available model. Override via env.
    openai_model: str = "gpt-4o"

    # --- CORS ---
    # Comma-separated list of allowed origins for the frontend.
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""
    return Settings()


settings = get_settings()
