import os
from abc import ABC, abstractmethod
from typing import List, Optional
from models.db_schemas import RetrievedDocument


class VectorDBInterface(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def is_collection_existed(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    async def list_all_collections(self) -> List:
        pass

    @abstractmethod
    async def get_collection_info(self, collection_name: str) -> dict:
        pass

    @abstractmethod
    async def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    async def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        pass

    @abstractmethod
    async def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        record_id: int,
        metadata: dict | None = None,
    ):
        pass

    @abstractmethod
    async def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        vectors: List[list],
        metadatas: Optional[List[dict]] = None,
        record_ids: Optional[List[int]] = None,
        batch_size: int = 50,
    ):
        pass

    @abstractmethod
    async def search_by_vector(
        self, collection_name: str, vector: list, limit: int
    ) -> List[RetrievedDocument]:
        pass


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
