import os
from enum import Enum


class ProcessingEnum(Enum):
    TXT = ".txt"
    PDF = ".pdf"


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
