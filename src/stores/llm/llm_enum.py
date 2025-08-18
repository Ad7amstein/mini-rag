import os
from enum import Enum


class LLMEnums(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"


class OpenAIEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
