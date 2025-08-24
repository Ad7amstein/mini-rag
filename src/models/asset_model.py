import os
from typing import Callable, Sequence
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.base_data_model import BaseDataModel
from models.db_schemas import Asset

SessionMaker = Callable[[], AsyncSession]


class AssetModel(BaseDataModel):
    def __init__(self, db_client: SessionMaker) -> None:
        super().__init__(db_client)
        self.db_client = self.db_client

    @classmethod
    async def create_instance(cls, db_client: SessionMaker):
        instance = cls(db_client)
        return instance

    async def create_asset(self, asset: Asset) -> Asset:
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset)
            return asset

    async def get_asset_record(
        self, asset_project_id: int, asset_name: str
    ) -> Asset | None:
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(
                    Asset.asset_project_id == asset_project_id,
                    Asset.asset_name == asset_name,
                )
                result = await session.execute(query)
                asset = result.scalar_one_or_none()

        return asset

    async def get_all_project_assets(
        self, asset_project_id: int, asset_type: str
    ) -> Sequence[Asset]:
        async with self.db_client() as session:
            query = select(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.asset_type == asset_type,
            )
            result = await session.execute(query)
            assets = result.scalars().all()
        return assets


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
