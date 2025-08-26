import os
import logging
from typing import List, Optional, Callable
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text as sql_text
from stores.vectordb import (
    VectorDBInterface,
    PgVectorTableSchemeEnums,
    PgVectorIndexTypeEnums,
    PgVectorDistanceMethodEnums,
    DistanceMethodEnum,
)
from models.db_schemas import RetrievedDocument

SessionMaker = Callable[[], AsyncSession]


class PGVectorProvider(VectorDBInterface):
    def __init__(
        self,
        db_client: SessionMaker,
        default_vector_size: int = 786,
        distance_method: Optional[str] = None,
        index_threshold: int = 100,
    ) -> None:
        super().__init__()
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.pgvector_table_prefix = PgVectorTableSchemeEnums.PREFIX.value
        self.logger = logging.getLogger("uvicorn")
        self.default_index_name = lambda x: f"{x}_vector_idx"
        self.index_threshold = index_threshold

        if distance_method == DistanceMethodEnum.COSINE.value:
            distance_method = PgVectorDistanceMethodEnums.COSINE.value
        elif distance_method == DistanceMethodEnum.DOT.value:
            distance_method = PgVectorDistanceMethodEnums.DOT.value

        self.distance_method = distance_method

    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))
                await session.commit()

    def disconnect(self):
        pass

    async def is_index_existed(self, collection_name: str) -> bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                sql_stmt = sql_text(
                    """
                    SELECT 1
                    FROM pg_indexes
                    WHERE tablename = :collection_name
                    AND indexname = :index_name
                    """
                )
                result = await session.execute(
                    sql_stmt,
                    {"collection_name": collection_name, "index_name": index_name},
                )
                return bool(result.scalar_one_or_none())

    async def create_vector_index(
        self, collection_name: str, index_type: str = PgVectorIndexTypeEnums.HNSW.value
    ):
        is_index_existed = await self.is_index_existed(collection_name)
        if is_index_existed:
            return False

        async with self.db_client() as session:
            async with session.begin():
                count_index_sql_stmt = sql_text(
                    f"SELECT COUNT(*) FROM {collection_name}"
                )
                result = await session.execute(count_index_sql_stmt)
                records_count = result.scalar_one()

                if records_count < self.index_threshold:
                    return False

                self.logger.info(
                    "START: Creating vector index for collection: %s", collection_name
                )
                index_name = self.default_index_name(collection_name)
                create_index_sql_stmt = sql_text(
                    f"CREATE INDEX {index_name} ON {collection_name} "
                    f"USING {index_type} ({PgVectorTableSchemeEnums.VECTOR.value} {self.distance_method})"
                )
                await session.execute(create_index_sql_stmt)
                self.logger.info(
                    "END: Created vector index for collection: %s", collection_name
                )

    async def delete_vector_index(self, collection_name: str):
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                sql_stmt = sql_text(f"DROP INDEX IF EXISTS {index_name}")
                await session.execute(sql_stmt)

    async def is_collection_existed(self, collection_name: str):
        record = None
        async with self.db_client() as session:
            list_tbl = sql_text(
                "SELECT * FROM pg_tables WHERE tablename = :collection_name"
            )
            result = await session.execute(
                list_tbl, {"collection_name": collection_name}
            )
            record = result.scalar_one_or_none()

        return record is not None

    async def list_all_collections(self):
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text(
                    "SELECT * FROM pg_tables WHERE tablename LIKE :prefix"
                )
                result = await session.execute(
                    list_tbl, {"prefix": PgVectorTableSchemeEnums.PREFIX.value}
                )
                collections = result.scalars().all()

        return collections

    async def get_collection_info(self, collection_name: str):
        async with self.db_client() as session:
            async with session.begin():
                table_info_stmt = sql_text(
                    """
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                    FROM pg_tables
                    WHERE tablename = :collection_name
                    """
                )

                count_sql = sql_text(f"SELECT COUNT(*) FROM {collection_name}")
                table_info = await session.execute(
                    table_info_stmt, {"collection_name": collection_name}
                )
                record_count = await session.execute(count_sql)
                table_data = table_info.fetchone()

                if not table_data:
                    return None
                return {
                    "table_info": {
                        "schemaname": table_data[0],
                        "tablename": table_data[1],
                        "tableowner": table_data[2],
                        "tablespace": table_data[3],
                        "hasindexes": table_data[4],
                    },
                    "record_count": record_count.scalar_one(),
                }

    async def delete_collection(self, collection_name: str):
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info("Deleting collection: %s", collection_name)

                delete_sql = sql_text(f"DROP TABLE IF EXISTS {collection_name}")
                await session.execute(delete_sql)
            await session.commit()

        return True

    async def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        if do_reset:
            _ = await self.delete_collection(collection_name)

        is_collection_existed = await self.is_collection_existed(collection_name)
        if not is_collection_existed:
            self.logger.info("Creating Collection %s", collection_name)

            async with self.db_client() as session:
                async with session.begin():
                    create_sql = sql_text(
                        f"CREATE TABLE {collection_name} ("
                        f"{PgVectorTableSchemeEnums.ID.value} bigserial PRIMARY KEY,"
                        f"{PgVectorTableSchemeEnums.TEXT.value} text, "
                        f"{PgVectorTableSchemeEnums.VECTOR.value} vector({embedding_size}), "
                        f"{PgVectorTableSchemeEnums.METADATA.value} jsonb DEFAULT '{{}}' , "
                        f"{PgVectorTableSchemeEnums.CHUNK_ID.value} integer, "
                        f"FOREIGN KEY ({PgVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)"
                        ")"
                    )
                    await session.execute(create_sql)
                    await session.commit()
            return True
        return False

    async def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List,
        record_id: int,
        metadata: dict | None = None,
    ):
        is_collection_existed = await self.is_collection_existed(collection_name)
        if not is_collection_existed:
            self.logger.error(
                "Can't insert to non-existed collection: %s", collection_name
            )
            return False

        if not record_id:
            self.logger.error(
                "Can't insert a new record without chunk_id: %s", collection_name
            )
            return False

        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(
                    f"INSERT INTO {collection_name}"
                    f"({PgVectorTableSchemeEnums.TEXT.value},"
                    f"{PgVectorTableSchemeEnums.VECTOR.value},"
                    f"{PgVectorTableSchemeEnums.METADATA.value},"
                    f"{PgVectorTableSchemeEnums.CHUNK_ID.value}) "
                    f"VALUES (:text, :vector, :metadata, :chunk_id)"
                )
                metadata_json = (
                    json.dumps(metadata, ensure_ascii=False)
                    if metadata is not None
                    else "{}"
                )
                await session.execute(
                    insert_sql,
                    {
                        "text": text,
                        "vector": "["
                        + ",".join([str(value) for value in vector])
                        + "]",
                        "metadata": metadata_json,
                        "chunk_id": record_id,
                    },
                )
                await session.commit()

        await self.create_vector_index(collection_name)

        return True

    async def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        vectors: List[List],
        record_ids: List[str],
        metadatas: List[dict] | None = None,
        batch_size: int = 50,
    ):
        is_collection_existed = await self.is_collection_existed(collection_name)
        if not is_collection_existed:
            self.logger.error(
                "Can't insert to non-existed collection: %s", collection_name
            )
            return False

        if len(vectors) != len(record_ids):
            self.logger.error("Invalid data items for collection: %s", collection_name)
            return False

        if not metadatas or len(metadatas) == 0:
            metadatas = [None] * len(texts)

        async with self.db_client() as session:
            async with session.begin():
                for idx in range(0, len(texts), batch_size):
                    batch_end = idx + batch_size
                    batch_text = texts[idx:batch_end]
                    batch_vectors = vectors[idx:batch_end]
                    batch_metadata = metadatas[idx:batch_end]
                    batch_record_ids = record_ids[idx:batch_end]

                    for _text, _vector, _metadata, _record_id in zip(
                        batch_text, batch_vectors, batch_metadata, batch_record_ids
                    ):
                        values = []
                        metadata_json = (
                            json.dumps(_metadata, ensure_ascii=False)
                            if _metadata is not None
                            else "{}"
                        )
                        values.append(
                            {
                                "text": _text,
                                "vector": "["
                                + ",".join([str(value) for value in _vector])
                                + "]",
                                "metadata": metadata_json,
                                "chunk_id": _record_id,
                            },
                        )
                        sql_stmt = sql_text(
                            f"INSERT INTO {collection_name}"
                            f"({PgVectorTableSchemeEnums.TEXT.value},"
                            f"{PgVectorTableSchemeEnums.VECTOR.value},"
                            f"{PgVectorTableSchemeEnums.METADATA.value},"
                            f"{PgVectorTableSchemeEnums.CHUNK_ID.value}) "
                            f"VALUES (:text, :vector, :metadata, :chunk_id)"
                        )
                        await session.execute(sql_stmt, values)

        await self.create_vector_index(collection_name)
        return True

    async def search_by_vector(self, collection_name: str, vector: list, limit: int):
        is_collection_existed = await self.is_collection_existed(collection_name)
        if not is_collection_existed:
            self.logger.error(
                "Can't search for a vector in non-existed collection: %s",
                collection_name,
            )
            return False

        vector_str = "[" + ",".join([str(value) for value in vector]) + "]"

        async with self.db_client() as session:
            async with session.begin():
                sql_stmt = sql_text(
                    f"SELECT {PgVectorTableSchemeEnums.TEXT.value} as text, "
                    f"1 - ({PgVectorTableSchemeEnums.VECTOR.value} <=> :vector) as score "
                    f"FROM {collection_name} "
                    "ORDER BY score DESC "
                    f"LIMIT {limit}"
                )
                result = await session.execute(sql_stmt, {"vector": vector_str})
                records = result.fetchall()
                return [
                    RetrievedDocument(text=record.text, score=record.score)
                    for record in records
                ]


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
