import os
from typing import Optional


class TemplateParser:
    def __init__(
        self, language: Optional[str] = None, default_language: str = "en"
    ) -> None:
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        self.set_language(language)  # type: ignore

    def set_language(self, language: str):
        if not language:
            self.language = self.default_language

        language_path = os.path.join(self.current_path, "locales", language)
        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    def get(self, group: str, key_: str, vars_: dict = {}) -> str | None:
        if not group or not key_:
            return None

        group_path = os.path.join(
            self.current_path, "locales", self.language, f"{group}.py"  # type: ignore
        )
        targeted_language = self.language
        if not os.path.exists(group_path):
            group_path = os.path.join(
                self.current_path, "locales", self.default_language, f"{group}.py"
            )
            targeted_language = self.default_language
        if not os.path.exists(group_path):
            return None

        module = __import__(
            f"stores.llm.templates.locales.{targeted_language}.{group}",
            fromlist=[group],
        )
        if not module:
            return None

        key_attribute = getattr(module, key_)
        return key_attribute.substitute(vars_)


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
