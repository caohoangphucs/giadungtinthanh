from pydantic_settings import BaseSettings
from pathlib import Path
import os
class Settings(BaseSettings):
    DATABASE_URL: str
    ADMIN_USER: str
    ADMIN_PASSWORD: str
    SECRET: str
    DOMAIN_URL: str
    REDIS_NAME: str
    ROOT_DIR: str = str(Path(__file__).resolve().parent.parent.parent)
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool
    MINIO_PRESIGNED_EXPIRE: int
    model_config = {
        "env_file": os.getenv("ENV_FILE", ".env"),  
        "env_file_encoding": "utf-8",
        "extra": "allow",
    }

class DatabaseSettings(BaseSettings):
    DATABASE_URL: str

    model_config = {
        "env_file": os.getenv("ENV_FILE", ".env"),
        "env_file_encoding": "utf-8",
    }
settings = Settings()
