from pathlib import Path
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    flask_port: int = 5000
    url: str = f"http://45.143.203.44:{port}"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    url: str = "/url"

    get: str = "/get"
    create: str = "/creat: stre"
    update: str = "/updat: stre"
    delete: str = "/delete"

    summary: str = "/summary"


class ApiConfig(BaseModel):
    prefix: ApiPrefix = ApiPrefix()


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: ApiConfig = ApiConfig()

settings = Settings()
