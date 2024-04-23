FROM downloads.unstructured.io/unstructured-io/unstructured:latest

# Set the working directory in the container
WORKDIR /app

ADD bin/ /bin/

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.in

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable for the port with a default value of 8080
ENV PORT=8080

# Run app.py when the container launches, using the PORT environment variable
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
