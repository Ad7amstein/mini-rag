import os
from typing import List
import json
from controllers.base_controller import BaseController
from models.db_schemas import Project, DataChunk
from stores.llm import DocumentTypeEnum


class NLPController(BaseController):
    def __init__(self, vectordb_client, generation_client, embedding_client) -> None:
        super().__init__()
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()

    def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vectordb_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(
            collection_name=collection_name
        )

        return json.loads(json.dumps(collection_info, default=lambda x: x.__dict__))

    def index_into_vectordb(
        self,
        project: Project,
        chunks: List[DataChunk],
        chunk_ids: List[int],
        do_reset: bool = False,
    ):
        collection_name = self.create_collection_name(project_id=project.project_id)
        texts = [chunk.chuk_text for chunk in chunks]
        metadatas = [chunk.chunk_metadata for chunk in chunks]
        vectors = [
            self.embedding_client.embed_text(text, DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            vectors=vectors,
            texts=texts,
            metadatas=metadatas,
            record_ids=chunk_ids,
        )

        return True

    def search_vectordb_collection(self, project: Project, text: str, limit: int = 10):
        collection_name = self.create_collection_name(project_id=project.project_id)
        vector = self.embedding_client.embed_text(text, DocumentTypeEnum.QUERY.value)
        if not vector or len(vector) == 0:
            return None
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name, vector=vector, limit=limit
        )

        if not results:
            return None

        return json.loads(json.dumps(results, default=lambda x: x.__dict__))


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
