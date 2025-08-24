import os
import uuid
from pydantic import BaseModel
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .minirag_base import SQLAlchemyBase


class DataChunk(SQLAlchemyBase):
    __tablename__ = "chunks"
    chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_uuid = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False
    )
    chunk_text = Column(String, nullable=False)
    chunk_metadata = Column(JSONB, nullable=False)
    chunk_order = Column(Integer, nullable=False)

    chunk_project_id = Column(
        Integer, ForeignKey("projects.project_id"), nullable=False
    )
    chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)

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

    project = relationship("Project", back_populates="chunks")
    asset = relationship("Asset", back_populates="chunks")

    __table_args__ = (
        Index("ix_chunk_project_id", chunk_project_id),
        Index("ix_chunk_asset_id", chunk_asset_id),
    )


class RetrievedDocument(BaseModel):
    text: str
    score: float


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
