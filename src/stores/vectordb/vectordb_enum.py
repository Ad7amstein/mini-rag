import os
from enum import Enum


class VectorDBEnum(Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"


class DistanceMethodEnum(Enum):
    COSINE = "cosine"
    DOT = "dot"


class PgVectorTableSchemeEnums(Enum):
    ID = "id"
    TEXT = "text"
    VECTOR = "vector"
    CHUNK_ID = "chunk_id"
    METADATA = "metadata"
    PREFIX = "pgvector"


class PgVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_12_ops"


class PgVectorIndexTypeEnums(Enum):
    HNSW = "hnsw"
    IVFFLAT = "ivfflat"


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
