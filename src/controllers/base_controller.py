import os
import random
from utils.config_utils import get_settings
import string


class BaseController:
    def __init__(self) -> None:
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.files_dir = os.path.join(self.base_dir, "assets", "files")

    def generate_random_string(self, length: int = 12):
        return "".join(
            random.choices("".join([string.ascii_lowercase, string.digits]), k=length)
        )


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
