import json
import logging
import os
import time
from contextlib import asynccontextmanager
from functools import wraps
from io import BytesIO

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf

import logging_util


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging_util.setup()
    logging.info("Starting up")
    yield


app = FastAPI(lifespan=lifespan, docs_url="/")


async def req_api_key(request: Request):
    if api_key_env := os.environ.get("API_KEY"):
        api_key = request.headers.get("api-key")
        if api_key != api_key_env:
            raise HTTPException(
                detail=f"API key {api_key} is invalid",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )


def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(
            f"Function '{func.__name__}' took {execution_time:.4f} seconds to complete."
        )
        return result

    return wrapper


@log_execution_time
def partition_doc(upload, coordinates, strategy, max_characters):
    file = BytesIO(upload.file.read())
    partition_kwargs = {
        "metadata_filename": upload.filename,
        "strategy": strategy,
        "max_characters": max_characters,
    }
    logging.info(f"partition_kwargs = {json.dumps(partition_kwargs, default=str)}")
    elements = partition(
        file=file,
        metadata_filename=upload.filename,
        strategy=strategy,
    )

    logging.info(f"partition finished elements len = {len(elements)}")

    for i, element in enumerate(elements):
        elements[i].metadata.filename = os.path.basename(upload.filename)

        if not coordinates and element.metadata.coordinates:
            elements[i].metadata.coordinates = None

        if element.metadata.last_modified:
            elements[i].metadata.last_modified = None

        if element.metadata.file_directory:
            elements[i].metadata.file_directory = None

        if element.metadata.detection_class_prob:
            elements[i].metadata.detection_class_prob = None

    return [e.to_dict() for e in elements]


@app.post("/elements", dependencies=[Depends(req_api_key)])
async def post_elements(
    upload: UploadFile = File(description="File to convert to elements"),
    strategy: str = Form("auto"),
    coordinates: bool = Form(False),
    max_characters: int = Form(500),
):
    logging.info(f"Converting {upload.filename} to elements")
    result = partition_doc(
        upload=upload,
        strategy=strategy,
        coordinates=coordinates,
        max_characters=max_characters,
    )
    return result


@app.get("/healthcheck", dependencies=[Depends(req_api_key)])
async def healthcheck():
    return Response(content="Alive!", media_type="text/plain", status_code=200)


# @app.get("/test", dependencies=[Depends(req_api_key)])
# async def test():
#     logging.info("TEST REACHED!!!!")
#     start = time.time()
#     with open("C884.pdf", 'rb') as file:
#         file_read = time.time()
#         print(f"file open took {file_read - start} sec")
#         elements = partition_pdf(file=file, strategy="auto")
#     print(f"took {time.time() - start} sec elements len = {len(elements)}")
#     # logging.info(f"took {time.time() - start} sec elements len = {len(elements)}")
#     return Response(content=f"Took {time.time()-start} seconds", media_type="text/plain", status_code=200)
