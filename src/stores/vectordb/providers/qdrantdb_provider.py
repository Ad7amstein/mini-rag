import os
from typing import List, Optional
import logging
from qdrant_client import models, QdrantClient
from stores.vectordb import VectorDBInterface
from stores.vectordb import DistanceMethodEnum
from models.db_schemas import RetrievedDocument


class QDrantDBProvider(VectorDBInterface):
    def __init__(
        self,
        db_client: str,
        default_vector_size: int = 786,
        distance_method: Optional[str] = None,
        index_threshold: int = 100,
    ) -> None:
        self.db_client = db_client
        self.distance_method = None
        self.client = None
        self.default_vector_size = default_vector_size
        self.index_threshold = index_threshold

        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnum.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger("uvicorn")

    async def connect(self):
        self.client = QdrantClient(path=self.db_client)

    async def disconnect(self):
        self.client = None

    async def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)  # type: ignore

    async def list_all_collections(self) -> models.List:
        return self.client.get_collections()  # type: ignore

    async def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)  # type: ignore

    async def delete_collection(self, collection_name: str):
        if await self.is_collection_existed(collection_name=collection_name):
            self.logger.info("Deleting collection: %s", collection_name)
            return self.client.delete_collection(collection_name=collection_name)  # type: ignore

    async def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        if do_reset:
            logging.info("Deleting Existing Collection: %s", collection_name)
            _ = self.delete_collection(collection_name=collection_name)

        if not await self.is_collection_existed(collection_name=collection_name):
            logging.info("Creating new QDrant Collection: %s", collection_name)
            self.client.create_collection(  # type: ignore
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size, distance=self.distance_method  # type: ignore
                ),
            )
            return True
        return False

    async def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        record_id: int,
        metadata: dict | None = None,
    ):
        if not await self.is_collection_existed(collection_name=collection_name):
            self.logger.error(
                "Can not insert new record to non-existing collection: %s",
                collection_name,
            )
            return False

        try:
            _ = self.client.upload_records(  # type: ignore
                collection_name=collection_name,
                records=[
                    models.Record(  # type: ignore
                        id=[record_id],  # type: ignore
                        vector=vector,
                        payload={"text": text, "metadata": metadata},
                    )
                ],
            )
        except Exception as exc:
            self.logger.error("Error while inserting record: %s", exc)
            return False
        return True

    async def insert_many(
        self,
        collection_name: str,
        texts: models.List[str],
        vectors: models.List[list],
        record_ids: models.List[int],
        metadatas: models.List[dict] | None = None,
        batch_size: int = 50,
    ):
        if metadatas is None:
            metadatas = [None] * len(texts)  # type: ignore
        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_text = texts[i:batch_end]
            batch_vector = vectors[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]
            batch_metadata = metadatas[i:batch_end]  # type: ignore
            batch_records = [
                models.Record(
                    id=batch_record_ids[i],
                    vector=batch_vector[i],
                    payload={"text": batch_text[i], "metadata": batch_metadata[i]},
                )
                for i in range(len(batch_text))
            ]

            try:
                _ = self.client.upload_records(  # type: ignore
                    collection_name=collection_name, records=batch_records
                )
            except Exception as exc:
                self.logger.error("Error while insertings batch: %s", exc)
                return False

        return True

    async def search_by_vector(
        self, collection_name: str, vector: list, limit: int = 5
    ) -> List[RetrievedDocument] | None:
        results = self.client.search(  # type: ignore
            collection_name=collection_name, query_vector=vector, limit=limit
        )

        if not results or len(results) == 0:
            return None

        return [
            RetrievedDocument(score=result.score, text=result.payload["text"])  # type: ignore
            for result in results
        ]


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
