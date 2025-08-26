"""
Utilities for loading and handling configuration files.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource


class Settings(BaseSettings):
    # .env
    GH_PAT: str = Field(...)
    OPENAI_API_KEY: str = Field(...)
    OPENAI_BASE_URL: str
    COHERE_API_KEY: str
    WSL_PASS: str = Field(...)

    # MONGODB_URL: str
    # MONGODB_DATABASE: str

    POSTGRES_USERNAME: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_HOST: str = Field(...)
    POSTGRES_PORT: int = Field(...)
    POSTGRES_MAIN_DATABASE: str = Field(...)

    # .yaml
    APP_NAME: str = Field(...)
    APP_VERSION: str = Field(...)
    FILE_ALLOWED_TYPES: List[str] = Field(...)
    FILE_MAX_SIZE: int = Field(...)
    FILE_DEFAULT_CHUNK_SIZE: int = Field(...)

    GENERATION_MODEL_ID_LITERAL: Optional[List[str]] = Field(None)
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int

    DEFAULT_INPUT_MAX_TOKENS: int
    DEFAULT_GENERATION_MAX_TOKENS: int
    DEFAULT_GENERATION_TEMERATURE: float

    VECTOR_DB_BACKEND_LITERAL: Optional[List[str]] = Field(None)
    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METHOD: str
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: int = 100

    DEFAULT_LANG: str
    PRIMARY_LANGUAGE: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,  # kwargs passed directly to Settings()
            env_settings,  # Environment variables
            dotenv_settings,  # .env file
            YamlConfigSettingsSource(
                settings_cls,
                yaml_file=Path("config/config.yaml"),
                yaml_file_encoding="utf-8",
            ),  # YAML file
            file_secret_settings,  # Secrets from files
        )


def get_settings():
    return Settings()  # type: ignore


def main():
    """Entry Point for the Program."""
    print(f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module.\n")
    # Usage

    settings = get_settings()

    print(settings.APP_NAME)  # From config.yaml
    print(settings.APP_VERSION)  # From config.yaml
    print(settings.GH_PAT)  # From .env


if __name__ == "__main__":
    main()
