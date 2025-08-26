import os
from typing import Callable, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from stores.vectordb.providers import QDrantDBProvider, PGVectorProvider
from stores.vectordb import VectorDBInterface
from utils.config_utils import get_settings, Settings
from stores.vectordb import VectorDBEnum
from controllers.base_controller import BaseController

SessionMaker = Callable[[], AsyncSession]


class VectorDBProviderFactory:
    def __init__(
        self,
        config: Settings = get_settings(),
        db_client: Optional[SessionMaker] = None,
    ) -> None:
        self.config = config
        self.db_client = db_client
        self.base_controller = BaseController()

    def creat(self, provider: str) -> VectorDBInterface | None:
        if provider == VectorDBEnum.QDRANT.value:
            return QDrantDBProvider(
                db_client=self.base_controller.get_database_path(
                    db_name=self.config.VECTOR_DB_PATH
                ),
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD,
            )
        if provider == VectorDBEnum.PGVECTOR.value:
            return PGVectorProvider(
                db_client=self.db_client,  # type: ignore
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD,
            )

        return None

def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
