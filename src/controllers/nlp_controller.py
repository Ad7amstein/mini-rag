import os
from typing import List, Sequence, cast
import json
from controllers.base_controller import BaseController
from models.db_schemas import Project, DataChunk
from stores.llm import DocumentTypeEnum, LLMInterface
from stores.llm.templates.template_parser import TemplateParser
from stores.vectordb import VectorDBInterface


class NLPController(BaseController):
    def __init__(
        self,
        vectordb_client: VectorDBInterface,
        generation_client: LLMInterface,
        embedding_client: LLMInterface,
        template_parser: TemplateParser,
    ) -> None:
        super().__init__()
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: int):
        return f"collection_{self.vectordb_client.default_vector_size}_{str(project_id)}".strip()  # type: ignore

    async def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_collection_name(
            project_id=cast(int, project.project_id)
        )
        return await self.vectordb_client.delete_collection(
            collection_name=collection_name
        )

    async def get_vectordb_collection_info(self, project: Project):
        collection_name = self.create_collection_name(
            project_id=cast(int, project.project_id)
        )
        collection_info = await self.vectordb_client.get_collection_info(
            collection_name=collection_name
        )

        return json.loads(json.dumps(collection_info, default=lambda x: x.__dict__))

    async def index_into_vectordb(
        self,
        project: Project,
        chunks: Sequence[DataChunk],
        chunk_ids: List[int],
    ):
        collection_name = self.create_collection_name(
            project_id=cast(int, project.project_id)
        )
        texts = [chunk.chunk_text for chunk in chunks]
        metadatas = [chunk.chunk_metadata for chunk in chunks]
        vectors = self.embedding_client.embed_text(
            cast(str, texts), DocumentTypeEnum.DOCUMENT.value
        )

        _ = await self.vectordb_client.insert_many(
            collection_name=collection_name,
            vectors=vectors,
            texts=texts,
            metadatas=metadatas,
            record_ids=chunk_ids,
        )

        return True

    async def search_vectordb_collection(
        self, project: Project, text: str, limit: int = 10
    ):
        collection_name = self.create_collection_name(
            project_id=cast(int, project.project_id)
        )
        vectors = self.embedding_client.embed_text(text, DocumentTypeEnum.QUERY.value)

        if not vectors or len(vectors) == 0:
            return None

        query_vector = vectors[0]

        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name, vector=query_vector, limit=limit
        )

        if not results:
            return None

        return results

    async def answer_rag_question(self, project: Project, query: str, limit: int = 10):
        answer, full_prompt, chat_history = None, None, None
        retrieved_documents = await self.search_vectordb_collection(
            project=project, text=query, limit=limit
        )
        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history

        system_prompt = self.template_parser.get("rag", "SYSTEM_PROMPT")
        document_prompts = "\n".join(
            [  # type: ignore
                self.template_parser.get(
                    "rag",
                    "DOCUMENT_PROMPT",
                    vars_={
                        "doc_num": idx + 1,
                        "chunk_text": self.generation_client.process_text(
                            document.text
                        ),
                    },
                )
                for idx, document in enumerate(retrieved_documents)
            ]
        )

        footer_prompt = self.template_parser.get(
            "rag", "FOOTER_PROMPT", {"query": query}
        )
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt, role=self.generation_client.enums.SYSTEM.value
            )
        ]

        full_prompt = "\n\n".join([document_prompts, footer_prompt])  # type: ignore
        answer = self.generation_client.generate_text(
            prompt=full_prompt, chat_history=chat_history
        )

        return answer, full_prompt, chat_history


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
