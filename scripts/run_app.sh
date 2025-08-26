#!/bin/bash

CONTAINER_NAME="pgvector_minirag"
IMAGE_NAME="pgvector/pgvector:0.8.0-pg17-trixie"
PASSWORD="minirag2222"
PORT="5432"
VOLUME_NAME="pgvector_data_mini_rag"

# Check if the container exists
if [ "$(docker ps -aq -f name=^${CONTAINER_NAME}$)" ]; then
    echo "Container ${CONTAINER_NAME} already exists."

    # Check if it's running
    if [ "$(docker ps -q -f name=^${CONTAINER_NAME}$)" ]; then
        echo "Container ${CONTAINER_NAME} is already running."
    else
        echo "Starting existing container ${CONTAINER_NAME}..."
        docker start ${CONTAINER_NAME}
    fi
else
    echo "Creating and starting new container ${CONTAINER_NAME}..."
    docker run --name ${CONTAINER_NAME} \
        -e POSTGRES_PASSWORD=${PASSWORD} \
        -p ${PORT}:5432 \
        -v ${VOLUME_NAME}:/var/lib/postgresql/data \
        -d ${IMAGE_NAME}
fi

# Install Python package in editable mode
pip install -e .

# Run FastAPI app
uvicorn main:app --reload --host 0.0.0.0 --port 5000
