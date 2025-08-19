import os
from enum import Enum


class VectorDBEnum(Enum):
    QDRANT = "QDRANT"


class DistanceMethodEnum(Enum):
    COSINE = "cosine"
    DOT = "dot"


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
