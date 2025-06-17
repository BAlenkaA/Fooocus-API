import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent

ENV_FILE_PATH = os.path.join(BASE_DIR, "configs", ".env")


class InfraSettings(BaseSettings):
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="allow",
    )


infra_settings = InfraSettings()
