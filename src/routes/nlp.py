import os
from typing import cast, List
import logging
from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from tqdm.auto import tqdm
from routes.schemas import PushRequest, SearchRequest, AnswerRequest
from controllers import NLPController
from models import ProjectModel, DataChunkModel
from models import ResponseSignalEnum

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(prefix="/api/v1/nlp", tags=["api_v1", "nlp"])


@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: int, push_request: PushRequest):
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
        template_parser=request.app.state.template_parser,
    )

    has_records = True
    page_number = 1
    total_inserted_items_count = 0
    idx = 1

    collection_name = nlp_controller.create_collection_name(
        project_id=cast(int, project.project_id)
    )

    _ = await request.app.state.vectordb_client.create_collection(
        collection_name=collection_name,
        embedding_size=request.app.state.embedding_client.embedding_size,
        do_reset=push_request.do_reset,
    )

    _ = await request.app.state.vectordb_client.delete_vector_index(collection_name)

    total_chunks_count = await chunk_model.get_total_chunks_count(
        project_id=cast(int, project.project_id)
    )

    pbar = tqdm(total=total_chunks_count, desc="Vector Inexing", position=0)

    while has_records:
        page_chunks, total_pages = await chunk_model.get_project_chunks(
            project_id=cast(int, project.project_id), page_number=page_number
        )
        if len(page_chunks) > 0:
            page_number += 1
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunk_ids = [chunk.chunk_id for chunk in page_chunks]
        idx += len(page_chunks)

        is_inserted = await nlp_controller.index_into_vectordb(
            project=project,
            chunks=page_chunks,
            chunk_ids=cast(List[int], chunk_ids),
        )
        if not is_inserted:
            return JSONResponse(
                content={"signal": ResponseSignalEnum.INSERT_INTO_VECTORDB_ERROR.value},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        total_inserted_items_count += len(page_chunks)
        pbar.update(len(page_chunks))

    return JSONResponse(
        content={
            "signal": ResponseSignalEnum.INSERT_INTO_VECTORDB_SUCCESS.value,
            "total_inserted_items_count": total_inserted_items_count,
            "total_pages": total_pages,
        }
    )


@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: int):
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
        template_parser=request.app.state.template_parser,
    )

    collection_info = await nlp_controller.get_vectordb_collection_info(project=project)

    return JSONResponse(
        content={
            "signal": ResponseSignalEnum.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info,
        }
    )


@nlp_router.post("/index/search/{project_id}")
async def search_index(
    request: Request, project_id: int, search_request: SearchRequest
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
        template_parser=request.app.state.template_parser,
    )

    results = await nlp_controller.search_vectordb_collection(
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
            "results": [result.dict() for result in results],
        }
    )


@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: int, answer_request: AnswerRequest):
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
        template_parser=request.app.state.template_parser,
    )

    answer, full_prompt, chat_history = await nlp_controller.answer_rag_question(
        project=project, query=answer_request.text, limit=answer_request.limit  # type: ignore
    )

    if not answer:
        return JSONResponse(
            content={"signal": ResponseSignalEnum.RAG_ANSWER_ERROR.value},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return JSONResponse(
        content={
            "signal": ResponseSignalEnum.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history,
        }
    )


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
