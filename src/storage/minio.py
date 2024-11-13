import logging
from io import BytesIO
from urllib.parse import urlparse

from minio import Minio

from src import env

CACHE_TTL = 60 * 60 * 24 * 365  # 1 year

minio_parts = urlparse(env.BLOB_ENDPOINT)
minoi_domain = minio_parts.hostname or "localhost"
logging.info(f"Connecting to Minio at {minoi_domain}")

client = Minio(
    f"{minio_parts.netloc}",
    access_key=env.BLOB_ACCESS_KEY,
    secret_key=env.BLOB_SECRET_KEY,
    secure=env.BLOB_ENDPOINT.startswith("https"),
)


def is_valid(endpoint: str = env.BLOB_ENDPOINT) -> bool:
    return "minio" in endpoint


def full_url(document_id) -> str:
    return f"{env.BLOB_ENDPOINT}/{env.BLOB_BUCKET}/{document_id}"


def put_object(document_id: str, handle) -> str:
    client.put_object(
        env.BLOB_BUCKET, document_id, handle, length=handle.getbuffer().nbytes
    )
    return full_url(document_id)


def get_object(uri: str):
    bucket_name = uri.split(f"/")[-2]
    object_name = uri.split(f"/")[-1]
    return BytesIO(client.get_object(bucket_name, object_name).read())


def list_objects():
    return client.list_objects(env.BLOB_BUCKET)
