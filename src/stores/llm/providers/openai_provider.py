import os
from typing import Optional
from openai import OpenAI
from stores.llm.llm_interface import LLMInterface
from stores.llm.llm_enum import OpenAIEnum
import logging


class OpenAIProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        default_input_max_tokens: int = 1000,
        default_output_max_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
    ) -> None:
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url
        self.default_input_max_tokens = default_input_max_tokens
        self.default_output_max_tokens = default_output_max_tokens
        self.default_generation_temperature = default_generation_temperature
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
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

        chat_history.append(
            self.contstruct_prompt(prompt=prompt, role=OpenAIEnum.USER.value)
        )

        response = self.client.chat.completions.create(
            model=self.generation_model_id,  # type: ignore
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temprature,
        )

        if (
            not response
            or not response.choices
            or len(response.choices) == 0
            or not response.choices[0].message
        ):
            self.logger.error("Error while generating text with OpenAI")
            return None

        return response.choices[0].message.content

    def contstruct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": self.process_text(prompt)}

    def embed_text(self, text: str, document_type: Optional[str] = None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        if not self.client:
            self.logger.error("Embedding Model for OpenAI was not set")
            return None

        response = self.client.embeddings.create(
            model=self.embedding_model_id, input=text  # type: ignore
        )

        if (
            not response
            or not response.data
            or len(response.data) == 0
            or not response.data[0].embedding
        ):
            self.logger.error("Error while embedding text with OpenAI")
            return None
        return response.data[0].embedding


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
