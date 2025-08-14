import os
from motor.motor_asyncio import AsyncIOMotorClient
from utils import get_settings


class BaseDataModel:
    def __init__(self, db_client: AsyncIOMotorClient) -> None:
        self.db_client = db_client
        self.app_settings = get_settings()


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
