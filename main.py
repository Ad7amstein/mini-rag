import os
from fastapi import FastAPI

app = FastAPI()


@app.get("/welcome")
def welcome():
    return {"messge": "Hello, FastAPI!"}


def main():
    """Entry Point for the Program."""
    print(
        f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!"
    )


if __name__ == "__main__":
    main()
