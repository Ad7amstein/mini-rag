"""
Utilities for loading and handling configuration files.
"""

import os
from pathlib import Path
from pydantic import Field
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource


class Settings(BaseSettings):
    # .env
    gh_pat: str = Field(..., alias="GH_PAT")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    wsl_pass: str = Field(..., alias="WSL_PASS")
    # .yaml
    app_name: str = Field(..., alias="APP_NAME")
    app_version: str = Field(..., alias="APP_VERSION")
    file_allowed_types: List[str] = Field(..., alias="FILE_ALLOWED_TYPES")
    file_max_size: int = Field(..., alias="FILE_MAX_SIZE")

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

    print(settings.app_name)  # From config.yaml
    print(settings.app_version)  # From config.yaml
    print(settings.gh_pat)  # From .env


if __name__ == "__main__":
    main()
