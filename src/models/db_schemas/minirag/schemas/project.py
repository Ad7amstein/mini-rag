import os
import uuid
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .minirag_base import SQLAlchemyBase


class Project(SQLAlchemyBase):
    __tablename__ = "projects"
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_uuid = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=[E1102]
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),  # pylint: disable=[E1102]
        nullable=True,
    )

    chunks = relationship("DataChunk", back_populates="project")
    assets = relationship("Asset", back_populates="project")

def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
