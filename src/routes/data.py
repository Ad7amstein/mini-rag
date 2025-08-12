import os
from fastapi import APIRouter, UploadFile
from controllers import DataController

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile):
    is_valid, result_signal = DataController().validate_uploaded_file(file)

    return {"is valid": is_valid, "signal": result_signal}


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
