import asyncio
import json
import logging
import os
from pprint import pprint

from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf

import logging_util as log_util
from src.azure_queue import retrieve_messages
from src.storage.storage import get_storage_client
from util import log_execution_time, notify_callback, sizeof_fmt


def download_file(blob_url):
    stream = get_storage_client().get_object(blob_url)
    logging.info(f"Downloaded file size: {sizeof_fmt(stream.getbuffer().nbytes)}")
    return stream


@log_execution_time
async def partition_doc(file, filename, coordinates, strategy, max_characters):
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


@log_execution_time
async def main():
    try:
        messages = await retrieve_messages()
    except Exception as e:
        logging.error("Failed to retrieve messages")
        return

    if not len(messages):
        logging.info("No messages fetched")

    for data in messages:
        # if (key := data.get("api_key")) != env.API_KEY:
        #     logging.info(f"api_key {key} is invalid")
        #     continue
        if not (callback_url := data.get("callback_url")):
            logging.info("No callback_url, not processing message")
            continue
        if not (blob_url := data.get("blob_url")):
            logging.info("No blob_url, not processing message")
            continue

        try:
            file_name = data.get("file_name")
            coordinates = data.get("coordinates", False)
            strategy = data.get("strategy", "auto")
            max_characters = data.get("max_characters", 500)

            args = {
                "blob_url": blob_url,
                "filename": file_name,
                "coordinates": coordinates,
                "strategy": strategy,
                "max_characters": max_characters,
                "callback_url": callback_url,
            }

            logging.info(f"args = {json.dumps(args, default=str)}")

            file = download_file(blob_url)  # returns ByteIO stream

            result = await partition_doc(
                file=file,
                filename=file_name,
                coordinates=coordinates,
                strategy=strategy,
                max_characters=max_characters,
            )

            data["elements"] = result

            file.close()

            logging.info(f"File '{file_name}' partition complete.")

            notify_callback(callback_url, status=200, data=data)

        except Exception as e:
            logging.error(e)
            notify_callback(callback_url, status=500, data="Internal Server Error")


if __name__ == "__main__":
    log_util.setup()
    logging.info("Starting up")
    asyncio.run(main())
