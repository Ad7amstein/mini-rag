import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from bson.objectid import ObjectId


class Project(BaseModel):
    _id: Optional[ObjectId]
    project_id: str = Field(..., min_length=1)

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, value: str):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric.")

        return value

    class Config:
        arbitrary_types_allowed = True


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
