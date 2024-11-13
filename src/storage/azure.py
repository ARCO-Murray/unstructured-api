from io import BytesIO

from azure.storage.blob import BlobServiceClient

from src import env

# Derive the connection string from ACCESS_KEY and SECRET_KEY
connection_string = f"DefaultEndpointsProtocol=https;AccountName={env.BLOB_ACCESS_KEY};AccountKey={env.BLOB_SECRET_KEY};EndpointSuffix=core.windows.net"

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)


def is_valid(endpoint: str = env.BLOB_ENDPOINT) -> bool:
    return "blob.core.windows.net" in endpoint


def full_url(document_id) -> str:
    return f"{env.BLOB_ENDPOINT}/{env.BLOB_BUCKET}/{document_id}"


def put_object(document_id: str, handle) -> None:
    blob_client = blob_service_client.get_blob_client(env.BLOB_BUCKET, document_id)
    blob_client.upload_blob(handle, overwrite=True)


def get_object(uri: str):
    bucket_name = uri.split(f"/")[-2]
    object_name = uri.split(f"/")[-1]

    stream = BytesIO()
    bucket = blob_service_client.get_container_client(bucket_name)
    bucket.download_blob(object_name).readinto(stream)
    return stream
