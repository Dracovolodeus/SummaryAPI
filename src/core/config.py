from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    flask_port: int = 5000
    url: str = Field(default="http://45.143.203.44:8000")


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    url: str = "/url"
    get: str = "/get"
    create: str = "/create"
    update: str = "/update"
    delete: str = "/delete"
    summary: str = "/summary"


class ApiConfig(BaseModel):
    prefix: ApiPrefix = ApiPrefix()


class AIConfig(BaseModel):
    token: str = ""
    max_text_length: int = 5000
    theads: int = 1


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    run: RunConfig = RunConfig()
    api: ApiConfig = ApiConfig()
    ai: AIConfig = AIConfig()


settings = Settings()
