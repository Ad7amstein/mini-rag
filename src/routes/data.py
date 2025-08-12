import os
import logging
import aiofiles
from fastapi import APIRouter, UploadFile, status, Depends
from fastapi.responses import JSONResponse
from controllers import DataController, ProjectController
from utils.config_utils import get_settings, Settings
from models import ResponseSignal

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id}")
async def upload_data(
    project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)
):
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file)

    if not is_valid:
        return JSONResponse(
            content={"signal": result_signal}, status_code=status.HTTP_400_BAD_REQUEST
        )

    project_dir_path = ProjectController().get_project_path(project_id)
    file_path = os.path.join(
        project_dir_path,
        data_controller.generate_unique_filename(
            original_file_name=file.filename, project_id=project_id  # type: ignore
        ),
    )
    print(f"[INFO]: File Path: {file_path}")

    try:
        async with aiofiles.open(file_path, mode="wb") as f:  # type: ignore
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except OSError as exc:
        logger.error("Error while uploading file: %s", exc)
        return JSONResponse(
            content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return JSONResponse(
        content={"signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value},
        status_code=status.HTTP_200_OK,
    )


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
