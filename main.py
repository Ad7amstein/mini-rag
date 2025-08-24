import os
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from routes import base, data, nlp
from utils import get_settings
from stores.llm import LLMProviderFactory
from stores.vectordb import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=[W0621]
    # Startup
    settings = get_settings()
    app.state.settings = settings

    postgres_conn_url = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.state.db_engine = create_async_engine(postgres_conn_url)
    app.state.db_client = sessionmaker(
        app.state.db_engine, class_=AsyncSession, expire_on_commit=False  # type: ignore
    )
    logger.info("Postgresql connection established.")

    llm_provider_factory = LLMProviderFactory(app.state.settings)
    vectordb_provider_factory = VectorDBProviderFactory(app.state.settings)

    app.state.generation_client = llm_provider_factory.create(
        app.state.settings.GENERATION_BACKEND
    )

    if app.state.generation_client is None:
        logger.error("Error while creating generation provider")
    app.state.generation_client.set_generation_model(  # type: ignore
        app.state.settings.GENERATION_MODEL_ID
    )

    app.state.embedding_client = llm_provider_factory.create(
        app.state.settings.EMBEDDING_BACKEND
    )
    if app.state.embedding_client is None:
        logger.error("Error while creating embedding provider")
    app.state.embedding_client.set_embedding_model(  # type: ignore
        app.state.settings.EMBEDDING_MODEL_ID, app.state.settings.EMBEDDING_MODEL_SIZE
    )

    app.state.vectordb_client = vectordb_provider_factory.creat(
        app.state.settings.VECTOR_DB_BACKEND
    )
    app.state.vectordb_client.connect()  # type: ignore

    app.state.template_parser = TemplateParser(
        language=app.state.settings.PRIMARY_LANGUAGE
    )

    yield  # The application runs here

    # Shutdown
    await app.state.db_engine.dispose()
    app.state.vectordb_client.disconnect()  # type: ignore
    logger.info("Postgresql connection closed.")


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)


def main():
    """Entry Point for the Program."""
    print(f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module.")


if __name__ == "__main__":
    main()
