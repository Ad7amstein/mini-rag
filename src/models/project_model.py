import os
from motor.motor_asyncio import AsyncIOMotorClient
from models.base_data_model import BaseDataModel
from models.db_schemas import Project
from models import DataBaseEnum


class ProjectModel(BaseDataModel):
    def __init__(self, db_client: AsyncIOMotorClient) -> None:
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id
        return project

    async def get_or_create_project(self, project_id: str):
        record = await self.collection.find_one({"project_id": project_id})
        if record is None:
            project = await self.create_project(Project(project_id=project_id))  # type: ignore
        else:
            project = Project(**record)

        return project

    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        total_docs = await self.collection.count_documents({})
        total_pages = total_docs // page_size
        if total_docs % page_size != 0:
            total_pages += 1

        cursor = (
            await self.collection.find().skip((page - 1) * page_size).limit(page_size)
        )
        projects = []
        async for doc in cursor:
            projects.append(Project(**doc))

        return projects, total_pages

def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
