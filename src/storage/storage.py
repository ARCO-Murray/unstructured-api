from functools import lru_cache

from src import env


@lru_cache
def get_storage_client():
    # TODO do this dynamically
    from . import azure, minio

    for mod in [azure, minio]:
        print(f"Checking {mod=}")
        if hasattr(mod, "is_valid") and mod.is_valid(env.BLOB_ENDPOINT):
            return mod
    raise Exception(f"No valid storage client found for {env.BLOB_ENDPOINT}!!!!")
