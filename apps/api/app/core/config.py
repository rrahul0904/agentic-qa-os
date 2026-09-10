from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentic QA OS"
    app_env: str = "local"
    cors_origins: str = "http://localhost:3000"
    database_url: str = "postgresql://agentic_qa:agentic_qa@localhost:5432/agentic_qa"
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
