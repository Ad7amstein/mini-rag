import os
from abc import ABC, abstractmethod
from typing import Optional


class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        chat_history: list = [],
        max_output_tokens: Optional[int] = None,
        temprature: Optional[float] = None,
    ):
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: Optional[str] = None):
        pass

    @abstractmethod
    def contstruct_prompt(self, prompt: str, role: str):
        pass


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
