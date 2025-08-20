import os
from typing import Optional
import logging
import cohere
from stores.llm.llm_interface import LLMInterface
from stores.llm.llm_enum import CoHereEnums, DocumentTypeEnum


class CoHereProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        default_input_max_tokens: int = 1000,
        default_output_max_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
    ) -> None:
        super().__init__()
        self.api_key = api_key
        self.default_input_max_tokens = default_input_max_tokens
        self.default_output_max_tokens = default_output_max_tokens
        self.default_generation_temperature = default_generation_temperature
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.client = cohere.Client(api_key=self.api_key)
        self.enums = CoHereEnums
        self.logger = logging.getLogger(__class__.__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str) -> str:
        return text[: self.default_input_max_tokens].strip()

    def generate_text(
        self,
        prompt: str,
        chat_history: list = [],
        max_output_tokens: Optional[int] = None,
        temprature: Optional[float] = None,
    ):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")

        max_output_tokens = (
            self.default_output_max_tokens
            if max_output_tokens is None
            else self.default_output_max_tokens
        )
        temprature = (
            self.default_generation_temperature if temprature is None else temprature
        )

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.process_text(prompt),
            temperature=temprature,
            max_tokens=max_output_tokens,
        )

        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere")

        return response.text

    def embed_text(self, text: str, document_type: Optional[str] = None):
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.client:
            self.logger.error("Embedding Model for CoHere was not set")
            return None

        input_type = (
            CoHereEnums.DOCUMENT.value
            if document_type == DocumentTypeEnum.DOCUMENT.value
            else CoHereEnums.QUERY.value
        )

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type,
            embedding_types=["float"],
        )

        if not response or not response.embeddings or not response.embeddings.float:  # type: ignore
            self.logger.error("Error while embedding text using CoHere")
            return None

        return response.embeddings.float[0]  # type: ignore

    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "text": self.process_text(prompt)}


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
