from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PULSEWATCH_", env_file=".env")

    database_url: str = "sqlite:///./pulsewatch.db"
    api_key: str | None = None
    alert_latency_ms: float = 1000.0


settings = Settings()
