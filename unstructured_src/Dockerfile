FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
	libmagic-dev poppler-utils tesseract-ocr libreoffice pandoc

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY unstructured_src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONPATH=.

CMD ["python3", "unstructured_src/main.py"]
# CMD ["sleep", "infinity"]
