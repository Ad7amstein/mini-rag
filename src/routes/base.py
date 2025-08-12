import os
from fastapi import APIRouter
from dotenv import load_dotenv
from src.utils.config_utils import load_config

load_dotenv(".env", override=True, verbose=True)
CONFIG = load_config()

base_router = APIRouter(prefix="/api/v1", tags=["api_v1"])


@base_router.get("/")
async def welcome():
    app_name = CONFIG["APP_NAME"]
    app_version = CONFIG["APP_VERSION"]
    return {
        "app_name": app_name,
        "app_version": app_version,
        "message": "Hello, FastAPI",
    }


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
