import os
import logging
import aiofiles
from fastapi import APIRouter, UploadFile, status, Depends
from fastapi.responses import JSONResponse
from controllers import DataController, ProcessController
from utils.config_utils import get_settings, Settings
from models import ResponseSignal
from routes.schemas import ProcessRequest

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

    file_path, file_name = data_controller.generate_unique_filepath(
        original_file_name=file.filename, project_id=project_id  # type: ignore
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
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "filename": file_name,
        },
        status_code=status.HTTP_200_OK,
    )


@data_router.post("/process/{project_id}")
async def process_data(project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    process_controller = ProcessController(project_id)
    file_content = process_controller.get_file_content(file_id)
    file_chunks = process_controller.process_file_content(
        file_content=file_content,  # type: ignore
        file_id=file_id,
        chunk_size=chunk_size,  # type: ignore
        overlap_size=overlap_size,  # type: ignore
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            content={"signal": ResponseSignal.PROCESSING_FAILED.value},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return file_chunks


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
