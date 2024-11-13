import json
import logging
import os
from functools import lru_cache
from pprint import pprint

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from requests import post
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf

import env
import logging_util as log_util
from util import log_execution_time, sizeof_fmt

# from storage.storage import get_storage_client
# from storage import storage


@lru_cache
def get_storage_client():
    # TODO do this dynamically
    from storage import azure, minio

    for mod in [azure, minio]:
        print(f"Checking {mod=}")
        if hasattr(mod, "is_valid") and mod.is_valid(env.BLOB_ENDPOINT):
            return mod
    raise Exception(f"No valid storage client found for {env.BLOB_ENDPOINT}!!!!")


def download_file(blob_url):
    stream = get_storage_client().get_object(blob_url)
    logging.info(f"Downloaded file size: {sizeof_fmt(stream.getbuffer().nbytes)}")
    return stream


def notify_callback(callback_url, status, data):
    response = post(callback_url, json={"status": status, "data": data})
    response.raise_for_status()


@log_execution_time
def partition_doc(file, filename, coordinates, strategy, max_characters):
    elements = partition(
        file=file,
        metadata_filename=filename,
        strategy=strategy,
        max_characters=max_characters,
    )

    logging.info(f"partition finished elements len = {len(elements)}")

    for i, element in enumerate(elements):
        elements[i].metadata.filename = os.path.basename(filename)

        if not coordinates and element.metadata.coordinates:
            elements[i].metadata.coordinates = None

        if element.metadata.last_modified:
            elements[i].metadata.last_modified = None

        if element.metadata.file_directory:
            elements[i].metadata.file_directory = None

        if element.metadata.detection_class_prob:
            elements[i].metadata.detection_class_prob = None

    return [e.to_dict() for e in elements]


def retrieve_messages():
    connection_string = env.SERVICE_BUS_CONNECTION_STRING

    with ServiceBusClient.from_connection_string(
        conn_str=connection_string, logging_enable=True
    ) as client:
        with client.get_queue_receiver(queue_name=env.QUEUE_NAME) as receiver:
            messages = receiver.receive_messages()  # defaults to fetch 1 message
            for m in messages:
                receiver.complete_message(m)
                # receiver.defer_message(m) # Defers message to be retrived by id (arco-wally)
            logging.info(json.dumps(messages, indent=2))
            return messages


@log_execution_time
def main():
    # blob_url = env.BLOB_URL
    # filename = env.FILE_NAME
    # coordinates = env.UNSTRUCTURED_COORDINATES
    # strategy = env.UNSTRUCTURED_STRATEGY
    # max_characters = env.UNSTRUCTURED_MAX_CHARACTERS
    # callback_url = env.CALLBACK_URL
    # try:
    #     if not blob_url:
    #         raise ValueError("BLOB_URL environment variable not set")
    #     if not filename:
    #         raise ValueError("FILE_NAME environment variable not set")
    #
    #     coordinates = (
    #         coordinates == "True"
    #     )  # parse coorindates into bool, default to false
    #     if not strategy:
    #         strategy = "auto"
    #     try:
    #         max_characters = int(max_characters)
    #     except:
    #         max_characters = 500
    #
    #     args = {
    #         "blob_url": blob_url,
    #         "filename": filename,
    #         "coordinates": coordinates,
    #         "strategy": strategy,
    #         "max_characters": max_characters,
    #         "callback_url": callback_url,
    #     }
    #
    #     logging.info(f"args = {json.dumps(args, default=str)}")
    #
    #     # file = download_file(blob_url)  # returns ByteIO stream
    #     #
    #     # result = partition_doc(
    #     #     file=file,
    #     #     filename=filename,
    #     #     coordinates=coordinates,
    #     #     strategy=strategy,
    #     #     max_characters=max_characters,
    #     # )
    #     #
    #     # file.close()
    #
    #     logging.info(f"Processing complete.")
    #
    #     if callback_url:
    #         notify_callback(callback_url, status=200, data=result)
    # except Exception as e:
    #     logging.error("Error occured!!!")
    #     logging.error(e)
    #     if callback_url:
    #         notify_callback(callback_url, status=500, data="Internal Server Error")

    for msg in retrieve_messages():
        logging.info(vars(msg))


if __name__ == "__main__":
    log_util.setup()
    logging.info("Starting up")
    main()
