from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "ForgeEval"
    environment: str = "development"
    secret_key: str = "dev-only-change-me"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./forgeeval.db"
    redis_url: str = "redis://localhost:6379/0"
    evaluation_mode: str = "inline"
    cors_origins: str = "http://localhost:5173"

settings = Settings()
