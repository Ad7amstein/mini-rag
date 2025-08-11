# mini-rag

This is a minimal implementation of the RAG model for question answering tasks.

## Requirements

- Python 3.8+

### Install python and other dependencies

1) Download the Python installer from the [official website](https://www.python.org/downloads/)

2) Create a virtual environment (recommended) by running the following command in your terminal:

    ```sh
    python3 -m venv .venv
    ```

3) Activate the environment:

    - On Windows:

        ```sh
        source .venv/Scripts/activate
        ```

    - On macOS/Linux:

        ```sh
        source .venv/bin/activate
        ```

## Installation

1) Install the required packages and dependencies:

    ```sh
    pip install -r requirements.txt
    ```

2) Setup the environment variables:

    ```sh
    cp .env.example .env
    ```

    > Set the required environment variables in the `.env` file. Like `OPENAI_API_KEY` value.

## Usage

### Run the FastAPI Server

```sh
sh scripts/run_app.sh
```

### Postman Collection (Optional)

Download the Postman collection file from `assets/mini-rag.postman_collection.json`
