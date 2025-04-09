import json
import logging
import os

from src.storage.storage import get_storage_client
from src.util import (log_execution_time, main_setup, process_messages,
                      sizeof_fmt)
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf


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


@main_setup
@log_execution_time
@process_messages
async def handle_message(blob_url, file_name, coordinates=False, strategy="hi_res", max_characters=500):
    file = download_file(blob_url)  # returns ByteIO stream

    result = await partition_doc(
        file=file,
        filename=file_name,
        coordinates=coordinates,
        strategy=strategy,
        max_characters=max_characters,
    )

    file.close()

    logging.info(f"File '{file_name}' partition complete.")

    return result


if __name__ == "__main__":
    handle_message()
