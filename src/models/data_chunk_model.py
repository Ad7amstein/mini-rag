import os
from typing import Callable, Sequence, Tuple
from sqlalchemy.future import select
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.base_data_model import BaseDataModel
from models.db_schemas import DataChunk

SessionMaker = Callable[[], AsyncSession]


class DataChunkModel(BaseDataModel):
    def __init__(self, db_client: SessionMaker) -> None:
        super().__init__(db_client)
        self.db_client = self.db_client

    @classmethod
    async def create_instance(cls, db_client: SessionMaker):
        instance = cls(db_client)
        return instance

    async def create_chunk(self, chunk: DataChunk) -> DataChunk:
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk

    async def get_chunk(self, chunk_id: int) -> DataChunk | None:
        async with self.db_client() as session:
            query = select(DataChunk).where(DataChunk.chunk_id == chunk_id)
            result = await session.execute(query)
            chunk = result.scalar_one_or_none()

        return chunk

    async def insert_many_chunks(self, chunks: list, batch_size: int = 100) -> int:
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i : i + batch_size]
                    session.add_all(batch)
            await session.commit()
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: int) -> int:
        async with self.db_client() as session:
            query = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(query)
            await session.commit()
        return result.rowcount

    async def get_project_chunks(
        self, project_id: int, page_number: int = 1, page_size: int = 50
    ) -> Tuple[Sequence[DataChunk], int]:
        async with self.db_client() as session:
            total_chunks = await session.execute(
                select(
                    func.count(  # pylint: disable=[E1102]
                        DataChunk.chunk_project_id == project_id
                    )
                )
            )
            total_chunks = total_chunks.scalar_one()
            total_pages = total_chunks // page_size
            if not total_chunks % page_size == 0:
                total_pages += 1

            query = (
                select(DataChunk)
                .where(DataChunk.chunk_project_id == project_id)
                .offset((page_number - 1) * page_size)
                .limit(page_size)
            )
            result = await session.execute(query)
            chunks = result.scalars().all()
        return chunks, total_pages


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
