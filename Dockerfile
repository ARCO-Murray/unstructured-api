FROM downloads.unstructured.io/unstructured-io/unstructured:latest

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONPATH=.

CMD ["python3", "src/main.py"]
