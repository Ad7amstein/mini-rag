import os
from fastapi import FastAPI
from dotenv import load_dotenv
from routes import base

load_dotenv(".env", override=True, verbose=True)

app = FastAPI()
app.include_router(base.base_router)


def main():
    """Entry Point for the Program."""
    print(f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module.")


if __name__ == "__main__":
    main()
