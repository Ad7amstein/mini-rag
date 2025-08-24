import os
from typing import Callable, Sequence, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from models.base_data_model import BaseDataModel
from models.db_schemas import Project

SessionMaker = Callable[[], AsyncSession]


class ProjectModel(BaseDataModel):
    def __init__(self, db_client: SessionMaker) -> None:
        super().__init__(db_client)
        self.db_client = self.db_client

    @classmethod
    async def create_instance(cls, db_client: SessionMaker):
        instance = cls(db_client)
        return instance

    async def create_project(self, project: Project) -> Project:
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)

            return project

    async def get_or_create_project(self, project_id: int) -> Project:
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()

                if project is None:
                    project = await self.create_project(
                        project=Project(project_id=project_id)
                    )
                    return project
                else:
                    return project

    async def get_all_projects(self, page: int = 1, page_size: int = 10) -> Tuple[Sequence[Project], int]:
        async with self.db_client() as session:
            async with session.begin():
                total_documents = await session.execute(
                    select(func.count(Project.project_id))  # pylint: disable=[E1102]
                )
                total_documents = total_documents.scalar_one()

                total_pages = total_documents // page_size
                if not total_documents % page_size == 0:
                    total_pages += 1

                query = select(Project).offset((page - 1) * page_size).limit(page_size)

                result = await session.execute(query)
                projects = result.scalars().all()

                return projects, total_pages


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
