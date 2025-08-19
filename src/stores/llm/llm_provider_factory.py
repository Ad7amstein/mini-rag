import os
from stores.llm.llm_enum import LLMEnums
from stores.llm.providers import OpenAIProvider, CoHereProvider
from utils.config_utils import get_settings, Settings


class LLMProviderFactory:
    def __init__(self, config: Settings = get_settings()) -> None:
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                base_url=self.config.OPENAI_BASE_URL,
                default_input_max_tokens=self.config.DEFAULT_INPUT_MAX_TOKENS,
                default_output_max_tokens=self.config.DEFAULT_GENERATION_MAX_TOKENS,
                default_generation_temperature=self.config.DEFAULT_GENERATION_TEMERATURE,
            )
        if provider == LLMEnums.COHERE.value:
            return CoHereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_tokens=self.config.DEFAULT_INPUT_MAX_TOKENS,
                default_output_max_tokens=self.config.DEFAULT_GENERATION_MAX_TOKENS,
                default_generation_temperature=self.config.DEFAULT_GENERATION_TEMERATURE,
            )

        return None


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
