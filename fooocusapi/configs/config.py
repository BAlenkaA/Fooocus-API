import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent

ENV_FILE_PATH = os.path.join(BASE_DIR, "configs", ".env")


class InfraSettings(BaseSettings):
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="allow",
    )


infra_settings = InfraSettings()
