import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from routes import base, data
from utils import get_settings
from stores.llm import LLMProviderFactory

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    app.state.settings = settings
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]
    logger.info("MongoDB connection established.")

    llm_provider_factory = LLMProviderFactory(app.state.settings)
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

    yield  # The application runs here

    # Shutdown
    app.state.mongo_conn.close()
    print("MongoDB connection closed.")


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)


def main():
    """Entry Point for the Program."""
    print(f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module.")


if __name__ == "__main__":
    main()
