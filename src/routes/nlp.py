import os
import logging
from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from routes.schemas import PushRequest, SearchRequest
from models import ProjectModel, DataChunkModel
from controllers import NLPController
from models import ResponseSignalEnum

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(prefix="/api/v1/nlp", tags=["api_v1", "nlp"])


@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    chunk_model = await DataChunkModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_or_create_project(project_id=project_id)
    if not project:
        return JSONResponse(
            content={"signal": ResponseSignalEnum.PROJECT_NOT_FOUND_ERROR.value},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.state.vectordb_client,
        generation_client=request.app.state.generation_client,
        embedding_client=request.app.state.embedding_client,
    )

    has_records = True
    page_number = 1
    inserted_items_count = 0
    idx = 0
    while has_records:
        page_chunks = await chunk_model.get_project_chunks(
            project_id=project.id, page_number=page_number  # type: ignore
        )
        if len(page_chunks) > 0:  # type: ignore
            page_number += 1
        if not page_chunks or len(page_chunks) == 0:  # type: ignore
            has_records = False
            break

        chunk_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = nlp_controller.index_into_vectordb(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset,  # type: ignore
            chunk_ids=chunk_ids,
        )
        if not is_inserted:
            return JSONResponse(
                content={"signal": ResponseSignalEnum.INSERT_INTO_VECTORDB_ERROR.value},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        inserted_items_count += len(page_chunks)  # type: ignore

    return JSONResponse(
        content={
            "signal": ResponseSignalEnum.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count,
        }
    )


@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    project = await project_model.get_or_create_project(project_id=project_id)
    if not project:
        return JSONResponse(
            content={"signal": ResponseSignalEnum.PROJECT_NOT_FOUND_ERROR.value},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    nlp_controller = NLPController(
        vectordb_client=request.app.state.vectordb_client,
        generation_client=request.app.state.generation_client,
        embedding_client=request.app.state.embedding_client,
    )

    collection_info = nlp_controller.get_vectordb_collection_info(project=project)

    return JSONResponse(
        content={
            "signal": ResponseSignalEnum.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info,
        }
    )


@nlp_router.post("/index/search/{project_id}")
async def search_index(
    request: Request, project_id: str, search_request: SearchRequest
):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    project = await project_model.get_or_create_project(project_id=project_id)
    if not project:
        return JSONResponse(
            content={"signal": ResponseSignalEnum.PROJECT_NOT_FOUND_ERROR.value},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    nlp_controller = NLPController(
        vectordb_client=request.app.state.vectordb_client,
        generation_client=request.app.state.generation_client,
        embedding_client=request.app.state.embedding_client,
    )

    results = nlp_controller.search_vectordb_collection(
        project=project, text=search_request.text, limit=search_request.limit  # type: ignore
    )

    if not results:
        return JSONResponse(
            content={"signal": ResponseSignalEnum.VECTORDB_SEARCH_ERROR.value},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return JSONResponse(
        content={
            "signal": ResponseSignalEnum.VECTORDB_SEARCH_SUCCESS.value,
            "results": results,
        }
    )


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
