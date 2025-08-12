import os
from fastapi import APIRouter, UploadFile, status
from fastapi.responses import JSONResponse
from controllers import DataController

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile):
    is_valid, result_signal = DataController().validate_uploaded_file(file)

    if not is_valid:
        response = JSONResponse(
            content={"signal": result_signal}, status_code=status.HTTP_400_BAD_REQUEST
        )
    else:
        response = JSONResponse(
            content={"signal": result_signal}, status_code=status.HTTP_200_OK
        )

    return response


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
