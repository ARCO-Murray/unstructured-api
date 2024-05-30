import logging
from fastapi import FastAPI, File, UploadFile, Form
from unstructured.partition.auto import partition

app = FastAPI(docs_url='/')

@app.post('/elements')
async def post_elements(upload: UploadFile = File(description='File to convert to elements'), strategy:str=Form('hi_res')):
    logging.info(f"Converting {upload.filename} to elements")
    elements = partition(file=upload.file, metadata_filename=upload.filename, strategy=strategy)
    return {
        'data': [elm.to_dict() for elm in elements]
    }

@app.post('/texts')
async def post_texts(upload: UploadFile = File(description='File to convert to text')):
    logging.info(f"Converting {upload.filename} to text")
    elements = partition(file=upload.file, metadata_filename=upload.filename)
    return {
        'data': "\n\n".join([str(el) for el in elements])
    }
