import os
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import InsertOne
from models.base_data_model import BaseDataModel
from models import DataBaseEnum
from models.db_schemas import DataChunk


class DataChunkModel(BaseDataModel):
    def __init__(self, db_client: AsyncIOMotorClient) -> None:
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(
            chunk.model_dump(by_alias=True, exclude_unset=True)
        )
        chunk.id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        record = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if record is None:
            return None

        return DataChunk(**record)

    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id": project_id})

        return result.deleted_count


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
