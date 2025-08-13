import os
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routes import base, data
from utils import get_settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    app.state.settings = settings
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]
    print("MongoDB connection established.")

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
