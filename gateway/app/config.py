from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_keys: str = Field(default="sk-demo", alias="API_KEYS")
    vllm_base_url: str = Field(default="http://localhost:8000", alias="VLLM_BASE_URL")
    default_model: str = Field(default="Qwen/Qwen2.5-0.5B-Instruct", alias="DEFAULT_MODEL")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    upstream_timeout_seconds: float = Field(default=120.0, alias="UPSTREAM_TIMEOUT_SECONDS")

    @property
    def allowed_api_keys(self) -> set[str]:
        return {key.strip() for key in self.api_keys.split(",") if key.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
