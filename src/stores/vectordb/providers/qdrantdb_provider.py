import os
import logging
from qdrant_client import models, QdrantClient
from stores.vectordb import VectorDBInterface
from stores.vectordb import DistanceMethodEnum


class QDrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: str) -> None:
        self.db_path = db_path
        self.distance_method = None
        self.client = None

        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnum.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__class__.__name__)

    def connect(self):
        self.client = QdrantClient(self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)  # type: ignore

    def list_all_collections(self) -> models.List:
        return self.client.get_collections()  # type: ignore

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)  # type: ignore

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)  # type: ignore

    def create_collection(
        self, collection_name: str, embedding_size: int, do_resent: bool = False
    ):
        if do_resent:
            _ = self.delete_collection(collection_name=collection_name)

        if not self.is_collection_existed(collection_name=collection_name):
            self.client.create_collection(  # type: ignore
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size, distance=self.distance_method  # type: ignore
                ),
            )
            return True
        return False

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict | None = None,
        record_id: str | None = None,
    ):
        if not self.is_collection_existed(collection_name=collection_name):
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
                        vector=vector, payload={"text": text, "metadata": metadata}
                    )
                ],
            )
        except Exception as exc:
            self.logger.error("Error while inserting record: %s", exc)
            return False
        return True

    def insert_many(
        self,
        collection_name: str,
        texts: models.List[str],
        vectors: models.List[list],
        metadatas: models.List[dict] | None = None,
        record_ids: models.List[str] | None = None,
        batch_size: int = 50,
    ):
        if metadatas is None:
            metadatas = [None] * len(texts)  # type: ignore
        if record_ids is None:
            record_ids = [None] * len(texts)  # type: ignore

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_text = texts[i:batch_end]
            batch_vector = vectors[i:batch_end]
            batch_metadata = metadatas[i:batch_end]  # type: ignore
            batch_records = [
                models.Record(  # type: ignore
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

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        return self.client.search(  # type: ignore
            collection_name=collection_name, query_vector=vector, limit=limit
        )


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
