import os
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from models.base_data_model import BaseDataModel
from models.db_schemas import Asset
from models import DataBaseEnum


class AssetModel(BaseDataModel):
    def __init__(self, db_client: AsyncIOMotorClient) -> None:
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorClient):
        instance = cls(db_client)
        await instance.init_collections()
        return instance

    async def init_collections(self):
        all_collections = await self.db_client.list_collection_names()  # type: ignore
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:  # type: ignore
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"], name=index["name"], unique=index["unique"]
                )

    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(
            asset.model_dump(by_alias=True, exclude_unset=True)
        )
        asset.id = result.inserted_id
        return asset

    async def get_or_create_asset(self, asset_id: str):
        record = await self.collection.find_one({"project_id": asset_id})
        if record is None:
            asset = await self.create_asset(Asset(asset_id=asset_id))  # type: ignore
        else:
            asset = Asset(**record)

        return asset

    async def get_all_project_assets(self, asset_project_id: str):
        return await self.collection.find(
            {
                "asset_project_id": (
                    ObjectId(asset_project_id)
                    if isinstance(asset_project_id, str)
                    else asset_project_id
                )
            }
        ).to_list(length=None)


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
