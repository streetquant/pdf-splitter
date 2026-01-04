from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv(".env", override=True)


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = ""
    MODEL_NAME: str = "nvidia/nemotron-3-nano-30b-a3b:free"
    SAMPLE_PAGES: int = 3
    OCR_TIMEOUT: int = 300
    CACHE_DIR: Path = Path.home() / ".cache" / "pdfsplitter"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
