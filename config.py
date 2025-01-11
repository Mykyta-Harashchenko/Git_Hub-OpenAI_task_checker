import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN")
    OPEN_AI_API_KEY: str = os.environ.get("OPEN_AI_API_KEY")
    REDIS_HOST: str = os.environ.get("REDIS_HOST")
    REDIS_PORT: str = os.environ.get("REDIS_PORT")

    class Config:
        env_file = "GitHub+OpenAI/.env"
        env_file_encoding = "utf-8"


config = Settings()
