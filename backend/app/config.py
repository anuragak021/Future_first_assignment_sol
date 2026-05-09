# AppConfig — loads config.yaml merged with environment variables
import os
from pathlib import Path
from functools import lru_cache
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    secret_key: str = "change_me_in_production"

    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    openrouter_api_key: str = Field(default="", env="OPENROUTER_API_KEY")

    # Set USE_SQLITE=true for local dev without Docker
    use_sqlite: bool = Field(default=False, env="USE_SQLITE")
    sqlite_path: str = Field(default="./insights.db", env="SQLITE_PATH")

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "insights"
    postgres_user: str = "insights_user"
    postgres_password: str = "insights_pass"

    # Set USE_EMBEDDED_CHROMA=true for local dev without Docker
    use_embedded_chroma: bool = Field(default=False, env="USE_EMBEDDED_CHROMA")
    chroma_persist_dir: str = Field(default="./chroma_data", env="CHROMA_PERSIST_DIR")
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        extra = "ignore"

    @property
    def databaseUrl(self) -> str:
        if self.use_sqlite:
            return f"sqlite+aiosqlite:///{self.sqlite_path}"
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def syncDatabaseUrl(self) -> str:
        if self.use_sqlite:
            return f"sqlite:///{self.sqlite_path}"
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def _loadYamlConfig() -> dict:
    configPath = Path(__file__).parent.parent.parent / "config.yaml"
    if configPath.exists():
        with open(configPath) as f:
            return yaml.safe_load(f) or {}
    return {}


@lru_cache()
def getSettings() -> Settings:
    return Settings()


@lru_cache()
def getYamlConfig() -> dict:
    return _loadYamlConfig()
