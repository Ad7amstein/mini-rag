import os
from stores.vectordb.providers import QDrantDBProvider
from utils.config_utils import get_settings, Settings
from stores.vectordb import VectorDBEnum
from controllers.base_controller import BaseController


class VectorDBProviderFactory:
    def __init__(self, config: Settings = get_settings()) -> None:
        self.config = config
        self.base_controller = BaseController()

    def creat(self, provider: str):
        if provider == VectorDBEnum.QDRANT.value:
            return QDrantDBProvider(
                db_path=self.base_controller.get_database_path(
                    db_name=self.config.VECTOR_DB_PATH
                ),
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
            )


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
