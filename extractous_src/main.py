import logging
import os
import uuid

from markdownify import markdownify as md

from extractous import Extractor, TesseractOcrConfig
from src.storage.storage import get_storage_client
from src.util import log_execution_time, main_setup, process_messages


@log_execution_time
async def download_file(blob_url, file_name):
    temp_file_name = f"{uuid.uuid4().hex}.tmp"
    stream = get_storage_client().get_object(blob_url)
    with open(temp_file_name, "wb") as file:
        file.write(stream.getbuffer())
    return temp_file_name

@log_execution_time
async def chunk_response(xml_text):
    text = md(xml_text)
    text_list = text.split("\n")
    return [{'element_id': str(uuid.uuid4()), 'text': t} for t in text_list]


# Set reasonable defaults for Extractor
extractor = Extractor()
extractor.set_ocr_config(TesseractOcrConfig().set_language("eng"))
extractor.set_extract_string_max_length(-1)
extractor.set_xml_output(True)


@main_setup
@log_execution_time
@process_messages("extractous")
async def handle_message(blob_url, file_name):
    file = await download_file(blob_url, file_name)  # returns ByteIO stream
    logging.debug(f"temp download file name: {file}")
    try:
        result, metadata = extractor.extract_file_to_string(file)
        logging.debug(f"result type: {type(result)}")
        logging.info(f"File '{file_name}' extraction complete.")
    except Exception as e:
        logging.error(f"File '{file_name}' extraction failed: {e}")
        return None

    os.remove(file)

    return await chunk_response(result)


if __name__ == "__main__":
    handle_message()
